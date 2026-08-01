// src/lib/mp4AudioDemux.ts
// -----------------------------------------------------------------------------
// PULL THE AAC TRACK OUT OF AN MP4/MOV BY HAND.
//
// WHY THIS EXISTS
//   `decodeAudioData` is the whole decode path in `offlineAudio.ts`, and on
//   WebKit it REFUSES a large and specific class of real files:
//
//     engine     h264+aac .mp4   iPhone HEVC .mov   .MOV w/ 2nd mjpeg track
//     Chromium   decodes         decodes            decodes
//     WebKit     decodes         EncodingError      EncodingError
//
//   (measured, not assumed — Playwright 1.57 chromium + webkit, five real
//   files, September 2026. The two WebKit failures are the ones that matter:
//   every video an iPhone records is HEVC in a .mov, and iOS Safari is WebKit
//   by law. So the owner's own footage was precisely the footage that could
//   not produce sound, and the message said the file had no audio track when
//   `ffprobe` says it has two.)
//
//   The failure is the CONTAINER, not the audio: WebKit's `decodeAudioData`
//   wants a file it can treat as one audio stream, and hands back a flat
//   `EncodingError: Decoding failed` for a multi-track movie. But that same
//   engine ships WebCodecs `AudioDecoder`, and `AudioDecoder.isConfigSupported
//   ({codec:'mp4a.40.2'})` answers TRUE there. The codec was never the problem.
//   So: do the demux ourselves and hand WebCodecs the elementary stream.
//
// SCOPE — deliberately small.
//   AAC (`mp4a`) inside ISO-BMFF/QuickTime. That is what phones, cameras and
//   every consumer editor produce. This is NOT a general MP4 parser: it reads
//   the sample tables of ONE audio track and stops. Anything it does not
//   understand returns null, and the caller falls back to reporting honestly
//   rather than guessing.
//
//   Fragmented MP4 (`moof`/`fMP4`) is NOT handled: the sample tables live in
//   the fragments, not in `moov`, and no capture device this tool serves writes
//   fMP4 to a file you can pick. It returns null rather than a partial read.
// -----------------------------------------------------------------------------

export interface DemuxedAacTrack {
  /** WebCodecs codec string, derived from the AudioSpecificConfig itself. */
  codec: string;
  sampleRate: number;
  numberOfChannels: number;
  /** The AudioSpecificConfig from `esds` — WebCodecs' `description`. */
  description: Uint8Array;
  samples: { data: Uint8Array; timestamp: number; duration: number }[];
}

/** MPEG-4 sampling-frequency index -> Hz. Index 13/14 are reserved. */
const FREQ_TABLE = [
  96000, 88200, 64000, 48000, 44100, 32000, 24000,
  22050, 16000, 12000, 11025, 8000, 7350, 0, 0, 0,
];

/** channelConfiguration -> channel count. 0 means "read the program config". */
const CHANNEL_TABLE = [0, 1, 2, 3, 4, 5, 6, 8];

interface Box { type: string; start: number; end: number; }

/**
 * Walk the boxes directly inside [start, end). Never recurses on its own — the
 * caller decides what is a container, because guessing wrong on a LEAF box
 * means parsing its payload as box headers and wandering off into the file.
 */
const boxesIn = (view: DataView, start: number, end: number): Box[] => {
  const out: Box[] = [];
  let p = start;
  // 8 is the minimum header; anything shorter is trailing slack, not a box.
  while (p + 8 <= end) {
    let size = view.getUint32(p);
    const type = String.fromCharCode(
      view.getUint8(p + 4), view.getUint8(p + 5), view.getUint8(p + 6), view.getUint8(p + 7),
    );
    let head = 8;
    if (size === 1) {
      if (p + 16 > end) break;
      // 64-bit largesize. Beyond 2^53 the arithmetic below stops being exact,
      // but a 9-petabyte box is not a case this tool has.
      const hi = view.getUint32(p + 8);
      const lo = view.getUint32(p + 12);
      size = hi * 2 ** 32 + lo;
      head = 16;
    } else if (size === 0) {
      size = end - p;                       // "to the end of the file"
    }
    // A size that does not advance is the one shape that spins forever.
    if (size < head || p + size > end) break;
    out.push({ type, start: p + head, end: p + size });
    p += size;
  }
  return out;
};

const findBox = (view: DataView, start: number, end: number, type: string): Box | null =>
  boxesIn(view, start, end).find((b) => b.type === type) ?? null;

/**
 * Descend a fixed path of container boxes, e.g. ['mdia','minf','stbl'].
 * Returns null the moment a step is missing rather than searching wider — a
 * `stbl` found somewhere unexpected belongs to a different track.
 */
const descend = (view: DataView, box: Box, path: string[]): Box | null => {
  let cur: Box | null = box;
  for (const step of path) {
    if (!cur) return null;
    cur = findBox(view, cur.start, cur.end, step);
  }
  return cur;
};

/**
 * The AudioSpecificConfig, dug out of `esds`'s nest of MPEG-4 descriptors.
 *
 * Descriptor layout is tag(1) + a base-128 varint length + payload, and the
 * three we traverse are ES_Descr(0x03) -> DecoderConfigDescr(0x04) ->
 * DecoderSpecificInfo(0x05). The last one's payload IS the ASC.
 */
const parseEsds = (bytes: Uint8Array, from = 4): Uint8Array | null => {
  let p = from;                                         // default: skip version + flags
  const readLen = (): number => {
    let len = 0;
    for (let i = 0; i < 4 && p < bytes.length; i++) {
      const b = bytes[p++];
      len = (len << 7) | (b & 0x7f);
      if ((b & 0x80) === 0) break;
    }
    return len;
  };
  while (p < bytes.length) {
    const tag = bytes[p++];
    const len = readLen();
    if (len <= 0 || p + len > bytes.length) return null;
    if (tag === 0x03) {
      // ES_ID(2) + flags(1); the flags can add streamDependence /
      // URL / OCR fields before the nested descriptor.
      const flags = bytes[p + 2];
      let skip = 3;
      if (flags & 0x80) skip += 2;                      // dependsOn_ES_ID
      if (flags & 0x40) skip += 1 + bytes[p + skip];    // URL string
      if (flags & 0x20) skip += 2;                      // OCR_ES_Id
      p += skip;
      continue;                                          // descend, do not skip
    }
    if (tag === 0x04) {
      // objectTypeIndication(1) streamType(1) bufferSize(3) max(4) avg(4)
      p += 13;
      continue;                                          // descend
    }
    if (tag === 0x05) return bytes.subarray(p, p + len); // the ASC
    p += len;                                            // an aunt; step over
  }
  return null;
};

/**
 * Normalise whatever an `AudioEncoder` calls a "description" down to the bare
 * AudioSpecificConfig that a muxer's `esds` needs.
 *
 * WebCodecs says `decoderConfig.description` for AAC is the ASC — and the two
 * engines disagree about that in the most damaging possible way:
 *
 *   Chrome   -> 2 bytes:  11 90                              (the ASC itself)
 *   WebKit   -> 39 bytes: 03 80808022 … 04 … 05 808080 02 11 90 06 …
 *                                                 ^^^^^ the ASC, nested inside
 *                         a COMPLETE ES_Descriptor
 *
 * mp4-muxer writes the description into `esds` verbatim, so on WebKit the
 * finished file carried an `esds` containing a whole second descriptor tree.
 * ffprobe reads that back as `22050 Hz, 0 channels, Audio object type 0` and
 * every decoder refuses it: an MP4 with an audio track that cannot be played.
 * Silently, and only on the engine every iPhone uses.
 *
 * Passing an already-bare ASC through is a no-op, so this is safe on both.
 */
export const toAudioSpecificConfig = (desc: Uint8Array): Uint8Array => {
  // 0x03 is the ES_Descriptor tag. A bare ASC never starts with it: its first
  // byte is (audioObjectType << 3 | …), and AOT 0 is "null", not a real codec.
  if (desc.length < 2 || desc[0] !== 0x03) return desc;
  return parseEsds(desc, 0) ?? desc;
};

/** Read the first bits of the ASC: they define the real rate and channel count. */
const readAsc = (asc: Uint8Array): { codec: string; sampleRate: number; channels: number } | null => {
  if (asc.length < 2) return null;
  let aot = asc[0] >> 3;
  let bitPos = 5;
  const bits = (n: number): number => {
    let v = 0;
    for (let i = 0; i < n; i++) {
      const byte = asc[bitPos >> 3];
      if (byte === undefined) return v << (n - i);
      v = (v << 1) | ((byte >> (7 - (bitPos & 7))) & 1);
      bitPos++;
    }
    return v;
  };
  if (aot === 31) { aot = 32 + bits(6); }               // escape for AOT >= 32
  const freqIdx = bits(4);
  const sampleRate = freqIdx === 0x0f ? bits(24) : FREQ_TABLE[freqIdx];
  const chanCfg = bits(4);
  const channels = CHANNEL_TABLE[chanCfg] ?? 0;
  if (!sampleRate || !channels) return null;
  // 'mp4a.40.N' with N the audio object type — 2 is AAC-LC, 5 is HE-AAC.
  return { codec: `mp4a.40.${aot}`, sampleRate, channels };
};

/**
 * Extract the first AAC track's samples from a whole MP4/MOV file.
 * Returns null for anything not understood; NEVER throws.
 */
export const demuxAacTrack = (buffer: ArrayBuffer): DemuxedAacTrack | null => {
  try {
    const view = new DataView(buffer);
    const bytes = new Uint8Array(buffer);
    const top = boxesIn(view, 0, buffer.byteLength);

    // Fragmented MP4 keeps its sample tables in `moof`, not `moov` — a `stbl`
    // read here would be empty and we would report "no audio" for a file that
    // has plenty. Bail explicitly instead.
    if (top.some((b) => b.type === 'moof')) return null;

    const moov = top.find((b) => b.type === 'moov');
    if (!moov) return null;

    for (const trak of boxesIn(view, moov.start, moov.end).filter((b) => b.type === 'trak')) {
      const hdlr = descend(view, trak, ['mdia', 'hdlr']);
      if (!hdlr) continue;
      // version+flags(4) pre_defined(4) handler_type(4)
      const handler = String.fromCharCode(
        view.getUint8(hdlr.start + 8), view.getUint8(hdlr.start + 9),
        view.getUint8(hdlr.start + 10), view.getUint8(hdlr.start + 11),
      );
      if (handler !== 'soun') continue;

      const mdhd = descend(view, trak, ['mdia', 'mdhd']);
      if (!mdhd) continue;
      const mdhdVer = view.getUint8(mdhd.start);
      const timescale = mdhdVer === 1
        ? view.getUint32(mdhd.start + 20)
        : view.getUint32(mdhd.start + 12);
      if (!timescale) continue;

      const stbl = descend(view, trak, ['mdia', 'minf', 'stbl']);
      if (!stbl) continue;

      // --- the sample description: is it AAC, and what is its ASC? ----------
      const stsd = findBox(view, stbl.start, stbl.end, 'stsd');
      if (!stsd) continue;
      // version+flags(4) entry_count(4), then the entries as boxes.
      const entries = boxesIn(view, stsd.start + 8, stsd.end);
      const mp4a = entries.find((e) => e.type === 'mp4a');
      if (!mp4a) continue;                               // ALAC, PCM, AC-3 — not ours

      // AudioSampleEntry: 6 reserved + 2 data_ref, then version(2) at +8.
      // QuickTime's v1 and v2 sound descriptions insert extra fields before the
      // child boxes, so trust the declared version rather than a fixed 28.
      const sampleEntryVersion = view.getUint16(mp4a.start + 8);
      const extra = sampleEntryVersion === 1 ? 16 : sampleEntryVersion === 2 ? 36 : 0;
      const childStart = mp4a.start + 28 + extra;
      if (childStart >= mp4a.end) continue;

      // `esds` sits directly under `mp4a` in an ISO MP4 — but QuickTime wraps it
      // in a `wave` atom (`wave` > `frma` + `mp4a` + `esds`), and QuickTime is
      // what every .mov is. Looking only at direct children found the config in
      // camera .mp4 files and missed it in every single .mov, which is the exact
      // set of files this fallback was built for.
      const waveBox = findBox(view, childStart, mp4a.end, 'wave');
      const esdsBox = findBox(view, childStart, mp4a.end, 'esds')
        ?? (waveBox ? findBox(view, waveBox.start, waveBox.end, 'esds') : null);
      if (!esdsBox) continue;
      const asc = parseEsds(bytes.subarray(esdsBox.start, esdsBox.end));
      if (!asc || !asc.length) continue;
      const fmt = readAsc(asc);
      if (!fmt) continue;

      // --- sample tables ----------------------------------------------------
      const stts = findBox(view, stbl.start, stbl.end, 'stts');
      const stsz = findBox(view, stbl.start, stbl.end, 'stsz');
      const stsc = findBox(view, stbl.start, stbl.end, 'stsc');
      const stco = findBox(view, stbl.start, stbl.end, 'stco')
        ?? findBox(view, stbl.start, stbl.end, 'co64');
      if (!stts || !stsz || !stsc || !stco) continue;

      // sizes
      const uniform = view.getUint32(stsz.start + 4);
      const sampleCount = view.getUint32(stsz.start + 8);
      const sizeAt = (i: number): number =>
        uniform !== 0 ? uniform : view.getUint32(stsz.start + 12 + i * 4);

      // chunk offsets
      const is64 = stco.type === 'co64';
      const chunkCount = view.getUint32(stco.start + 4);
      const chunkOffset = (i: number): number => (is64
        ? view.getUint32(stco.start + 8 + i * 8) * 2 ** 32 + view.getUint32(stco.start + 12 + i * 8)
        : view.getUint32(stco.start + 8 + i * 4));

      // sample-to-chunk, run-length encoded by FIRST chunk
      const stscCount = view.getUint32(stsc.start + 4);
      const stscEntries: { first: number; perChunk: number }[] = [];
      for (let i = 0; i < stscCount; i++) {
        stscEntries.push({
          first: view.getUint32(stsc.start + 8 + i * 12),
          perChunk: view.getUint32(stsc.start + 12 + i * 12),
        });
      }
      if (!stscEntries.length) continue;

      // durations, run-length encoded
      const sttsCount = view.getUint32(stts.start + 4);
      const deltas: { count: number; delta: number }[] = [];
      for (let i = 0; i < sttsCount; i++) {
        deltas.push({
          count: view.getUint32(stts.start + 8 + i * 8),
          delta: view.getUint32(stts.start + 12 + i * 8),
        });
      }

      // --- walk the samples -------------------------------------------------
      const samples: DemuxedAacTrack['samples'] = [];
      let sampleIdx = 0;
      let dEntry = 0;
      let dLeft = deltas.length ? deltas[0].count : 0;
      let tsTicks = 0;

      for (let c = 0; c < chunkCount && sampleIdx < sampleCount; c++) {
        // The last stsc entry whose `first` (1-based) has been reached governs.
        let perChunk = stscEntries[0].perChunk;
        for (let e = 0; e < stscEntries.length; e++) {
          if (stscEntries[e].first - 1 <= c) perChunk = stscEntries[e].perChunk; else break;
        }
        let off = chunkOffset(c);
        for (let s = 0; s < perChunk && sampleIdx < sampleCount; s++) {
          const size = sizeAt(sampleIdx);
          if (off + size > buffer.byteLength) return samples.length ? finish() : null;
          while (dLeft === 0 && dEntry + 1 < deltas.length) { dEntry++; dLeft = deltas[dEntry].count; }
          const delta = deltas[dEntry]?.delta ?? 1024;
          samples.push({
            // A COPY, not a subarray view: `EncodedAudioChunk` may retain it,
            // and the caller is free to drop the 133 MB source buffer after
            // this returns. A view would pin the whole movie in memory.
            data: bytes.slice(off, off + size),
            timestamp: Math.round((tsTicks / timescale) * 1e6),
            duration: Math.round((delta / timescale) * 1e6),
          });
          tsTicks += delta;
          if (dLeft > 0) dLeft--;
          off += size;
          sampleIdx++;
        }
      }

      function finish(): DemuxedAacTrack {
        return {
          codec: fmt!.codec,
          sampleRate: fmt!.sampleRate,
          numberOfChannels: fmt!.channels,
          description: asc!,
          samples,
        };
      }

      if (!samples.length) continue;
      return finish();
    }
    return null;
  } catch {
    return null;
  }
};
