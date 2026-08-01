// src/lib/offlineAudio.ts
// -----------------------------------------------------------------------------
// SOUND FOR A RENDER THAT HAS NO CLOCK.
//
// WHY THIS EXISTS
//   `renderOffline` (frameExport.ts) SEEKS every decoder to t = n/fps and draws
//   once. Nothing is playing, so there is nothing to tap: `captureStream` and
//   `MediaStreamAudioDestinationNode` only ever carry what a graph produces in
//   REAL TIME. That is why the offline path shipped silent, and why "just record
//   the audio too" is not available here.
//
//   Sound therefore has to be produced INDEPENDENTLY of the frame loop: decode
//   each clip's compressed audio, mix it on an OfflineAudioContext along the
//   SAME timeline the loop walks, encode it with `AudioEncoder`, and hand the
//   chunks to the same `Muxer`. The frame loop does not change by one line —
//   its evenness is the whole reason the offline renderer exists, and any audio
//   work inside it would reintroduce exactly the stall it was built to remove.
//
// THE SYNC CONTRACT — the only genuinely hard part.
//   `Stage.seekClipTo` (stage.ts:777-780) defines, for output time t, a clip's
//   media position:
//       span   = max(EPS, el.duration - EPS)
//       target = loop ? t % span : min(t, span)
//   Everything below reproduces that exactly, and `span` is passed IN from the
//   Stage rather than recomputed here, so the epsilon has one source and the two
//   timelines cannot drift apart.
//
//   `clip.startTime` is deliberately NOT applied. `seekClipTo` does not apply it
//   either (it is used once, at element creation), so a mixer that "helpfully"
//   honours it would desync the entire export by that offset with nothing on
//   screen to show for it.
//
// THE LADDER — AAC or silence, and it NEVER breaks the video.
//   no sources -> nothing decodable -> everything muted -> no AudioEncoder ->
//   no AAC -> encoder produced nothing. Each rung returns `track: null` with its
//   OWN reason, so a silent file always says WHY it is silent.
//
//   There is NO Opus rung. mp4-muxer will happily write Opus-in-MP4 (it emits a
//   `dOps` box) and Chrome plays it — but QuickTime, Photos and Safari will not
//   open it, and this module's sibling exists precisely to produce "a normal MP4
//   that opens in QuickTime and imports to Photos". A file that will not open is
//   strictly worse than one that is quiet.
//
// KNOWN, ACCEPTED, NOT COMPENSATED
//   AAC-LC encoders emit ~1024 samples (~21 ms at 48 kHz) of priming delay, and
//   mp4-muxer has no edit-list (`elst`) support — so audio can sit ~21 ms early
//   against picture. That is below the ~40 ms perceptual threshold, and the
//   obvious "fix" (dropping the first chunk) trades a small fixed offset for a
//   variable one. It is named here rather than papered over.
// -----------------------------------------------------------------------------

import { demuxAacTrack, toAudioSpecificConfig } from './mp4AudioDemux';

// =============================================================================
// TYPES
// =============================================================================

/**
 * One clip, as the Stage sees it. Everything the mixer needs and nothing it can
 * get wrong: the Stage resolves audibility and `span` itself, because both live
 * behind private state.
 */
export interface OfflineAudioSource {
  id: string;
  /** The clip's durable `blob:` URL. */
  url: string;
  /** stage.ts:777 — `max(EPS, duration - EPS)`. 0 when the duration is unknown. */
  span: number;
  loop: boolean;
  /** 0..1, mirroring `Stage.applyMutes()`. A gain of 0 is NOT a source. */
  gain: number;
}

export interface EncodedAudioRecord {
  data: Uint8Array;
  type: 'key' | 'delta';
  /** µs, derived from the SAMPLE INDEX — never from a clock. */
  timestamp: number;
  /** µs, measured to the NEXT chunk. Never assumed to be 1024 samples. */
  duration: number;
  meta?: EncodedAudioChunkMetadata;
}

export interface OfflineAudioTrack {
  /** mp4-muxer's `AudioOptions.codec` — a MUXER FAMILY name, not a WebCodecs
   *  codec string. The encoder is configured with 'mp4a.40.2'; the muxer is
   *  told 'aac'. Passing either one to the other silently produces a broken
   *  file, so both spellings live here together. */
  codec: 'aac';
  sampleRate: number;
  numberOfChannels: number;
  chunks: EncodedAudioRecord[];
  /** Clips that contributed NON-ZERO signal — never the decode count. */
  sources: number;
  warnings: string[];
}

export interface AudioPrepareResult {
  track: OfflineAudioTrack | null;
  /** Present iff `track` is null: the rung that failed, in user language. */
  reason: string | null;
  /** Decoded successfully, whether or not audible. Diagnostics only. */
  decoded: number;
}

export interface PrepareOptions {
  /** Output start time, matching `renderOffline`'s `startTimeSec`. */
  startAt?: number;
  /** Output length in seconds. */
  seconds: number;
  signal?: AbortSignal;
  bitrate?: number;
}

// =============================================================================
// CONSTANTS
// =============================================================================

/**
 * PINNED at 48 kHz, and it must stay one of the 13 MPEG-4 sampling-frequency
 * indices. mp4-muxer generates the AAC AudioSpecificConfig itself via
 * `frequencyIndices.indexOf(sampleRate)`; a non-standard rate yields index -1
 * and a silently corrupt `esds` — a file that looks fine and plays as noise.
 * Never inherit `AudioContext.sampleRate`: it is device-dependent.
 */
const SAMPLE_RATE = 48_000;
const CHANNELS = 2;
const DEFAULT_BITRATE = 128_000;
/** 0.1 s per AudioData. Bounded churn; the encoder re-frames to 1024 itself. */
const PCM_CHUNK_FRAMES = SAMPLE_RATE / 10;

const FETCH_TIMEOUT_MS = 10_000;
const DECODE_TIMEOUT_MS = 15_000;
const RENDER_TIMEOUT_MS = 30_000;
const FLUSH_TIMEOUT_MS = 15_000;

/** Above this, skip audio rather than risk an OOM on the phone this serves.
 *  120 s of 48 kHz stereo f32 is ~46 MB of PCM held while encoding, on top of
 *  the muxer's in-memory video buffer. */
const MAX_PCM_BYTES = 64 * 1024 * 1024;

const errText = (e: unknown): string => {
  if (!e) return 'Unknown error';
  if (e instanceof Error) return e.name ? `${e.name}: ${e.message}` : e.message;
  if (typeof e === 'string') return e;
  try { return String(e); } catch { return 'Unknown error'; }
};

/** Every wait is deadlined — the same rule the recorder paths already follow. */
const within = <T,>(p: Promise<T>, ms: number, what: string): Promise<T> =>
  Promise.race([
    p,
    new Promise<T>((_, rej) => setTimeout(() => rej(new Error(`${what} timed out`)), ms)),
  ]);

type EncCtor = typeof AudioEncoder;
type DataCtor = typeof AudioData;
type DecCtor = typeof AudioDecoder;
type ChunkCtor = typeof EncodedAudioChunk;
type OACCtor = new (channels: number, length: number, rate: number) => OfflineAudioContext;

const encCtor = (): EncCtor | null => {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as { AudioEncoder?: EncCtor };
  return typeof w.AudioEncoder === 'function' ? w.AudioEncoder : null;
};
const dataCtor = (): DataCtor | null => {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as { AudioData?: DataCtor };
  return typeof w.AudioData === 'function' ? w.AudioData : null;
};
/** WebCodecs decode side. Present on WebKit, which is exactly where the
 *  one-call `decodeAudioData` path gives up. */
const decCtor = (): DecCtor | null => {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as { AudioDecoder?: DecCtor };
  return typeof w.AudioDecoder === 'function' ? w.AudioDecoder : null;
};
const chunkCtor = (): ChunkCtor | null => {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as { EncodedAudioChunk?: ChunkCtor };
  return typeof w.EncodedAudioChunk === 'function' ? w.EncodedAudioChunk : null;
};
const oacCtor = (): OACCtor | null => {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as {
    OfflineAudioContext?: OACCtor; webkitOfflineAudioContext?: OACCtor;
  };
  return w.OfflineAudioContext ?? w.webkitOfflineAudioContext ?? null;
};

/** True when this engine can encode AAC-LC at our pinned format. */
export const isOfflineAudioSupported = (): boolean =>
  !!encCtor() && !!dataCtor() && !!oacCtor();

// =============================================================================
// 1. BYTES
// =============================================================================

/**
 * `fetch` first, `XMLHttpRequest` second. iOS Safari has a history of failing
 * `fetch()` on same-origin `blob:` URLs, and the offline renderer exists to
 * serve that engine specifically — so the fallback is not defensive padding.
 */
const fetchBytes = async (url: string, signal?: AbortSignal): Promise<ArrayBuffer> => {
  try {
    const res = await within(fetch(url, { signal }), FETCH_TIMEOUT_MS, 'fetch');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.arrayBuffer();
  } catch (e) {
    if (signal?.aborted) throw e;
    return new Promise<ArrayBuffer>((resolve, reject) => {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', url, true);
      xhr.responseType = 'arraybuffer';
      xhr.timeout = FETCH_TIMEOUT_MS;
      xhr.onload = () => (xhr.response
        ? resolve(xhr.response as ArrayBuffer)
        : reject(new Error('empty response')));
      xhr.onerror = () => reject(new Error('xhr failed'));
      xhr.ontimeout = () => reject(new Error('xhr timed out'));
      signal?.addEventListener('abort', () => { try { xhr.abort(); } catch { /* ignore */ } }, { once: true });
      xhr.send();
    });
  }
};

// =============================================================================
// 2. DECODE
// =============================================================================

/**
 * SECOND RUNG: demux the AAC track ourselves and decode it with WebCodecs.
 *
 * `decodeAudioData` is not a codec question, it is a CONTAINER question, and
 * WebKit answers it badly — it returns `EncodingError: Decoding failed` for
 * every iPhone `.mov` and for any movie carrying a second media track, while
 * the very same engine reports `AudioDecoder.isConfigSupported({codec:
 * 'mp4a.40.2'}) -> true`. See `mp4AudioDemux.ts` for the measured matrix.
 *
 * So when the one-call path fails we take the file apart by hand and hand the
 * elementary stream to WebCodecs. Returns null (never throws) if this engine
 * has no `AudioDecoder`, the file is not AAC-in-MP4, or the decode produces
 * nothing — the caller then reports honestly instead of guessing.
 */
const decodeViaWebCodecs = async (
  ctx: BaseAudioContext, bytes: ArrayBuffer, signal?: AbortSignal,
): Promise<AudioBuffer | null> => {
  const Dec = decCtor();
  const Chunk = chunkCtor();
  if (!Dec || !Chunk) return null;

  const track = demuxAacTrack(bytes);
  if (!track || !track.samples.length) return null;

  const config: AudioDecoderConfig = {
    codec: track.codec,
    sampleRate: track.sampleRate,
    numberOfChannels: track.numberOfChannels,
    description: track.description,
  };
  try {
    const probe = await Dec.isConfigSupported(config);
    if (!probe.supported) return null;
  } catch { return null; }

  // Planar float per channel, in output order. Held as a list of blocks and
  // concatenated once at the end: an incremental copy into a grown buffer
  // would be quadratic on a two-minute clip.
  const blocks: Float32Array[][] = [];
  let totalFrames = 0;
  let channels = track.numberOfChannels;
  let rate = track.sampleRate;
  let failed: string | null = null;

  const decoder = new Dec({
    output: (data: AudioData) => {
      try {
        channels = data.numberOfChannels || channels;
        rate = data.sampleRate || rate;
        const planes: Float32Array[] = [];
        for (let ch = 0; ch < channels; ch++) {
          // Ask for f32-planar explicitly: the decoder is free to hand back
          // s16 or interleaved, and `copyTo` is the only place a conversion
          // is guaranteed.
          const opts = { planeIndex: ch, format: 'f32-planar' as const };
          const plane = new Float32Array(data.allocationSize(opts) / 4);
          data.copyTo(plane, opts);
          planes.push(plane);
        }
        blocks.push(planes);
        totalFrames += data.numberOfFrames;
      } catch (e) {
        failed = failed ?? errText(e);
      } finally {
        try { data.close(); } catch { /* ignore */ }
      }
    },
    error: (e: Error) => { failed = failed ?? errText(e); },
  });

  try {
    decoder.configure(config);
    for (const s of track.samples) {
      if (signal?.aborted) break;
      // Every AAC access unit is independently decodable — there are no
      // delta frames to mark.
      decoder.decode(new Chunk({
        type: 'key', timestamp: s.timestamp, duration: s.duration, data: s.data,
      }));
    }
    await within(decoder.flush(), DECODE_TIMEOUT_MS, 'webcodecs audio decode');
  } catch (e) {
    failed = failed ?? errText(e);
  }
  try { decoder.close(); } catch { /* ignore */ }

  if (!totalFrames || !blocks.length) return null;

  try {
    const buf = ctx.createBuffer(channels, totalFrames, rate);
    for (let ch = 0; ch < channels; ch++) {
      const dest = buf.getChannelData(ch);
      let at = 0;
      for (const planes of blocks) {
        const src = planes[ch] ?? planes[0];
        if (!src) continue;
        // A short final block is normal; never write past the declared length.
        const n = Math.min(src.length, dest.length - at);
        if (n <= 0) break;
        dest.set(n === src.length ? src : src.subarray(0, n), at);
        at += n;
      }
    }
    return buf;
  } catch {
    return null;
  }
};

/**
 * Decode one clip's audio, and say why if it cannot.
 *
 * Individually try/caught on purpose: one undecodable clip must cost THAT CLIP
 * its sound — never the render — exactly as a failed seek costs one frame its
 * motion. But the reason is now CARRIED OUT rather than swallowed: a bare null
 * made "this file has no audio track", "your blob URL was revoked", "the fetch
 * timed out" and "WebKit will not open this container" indistinguishable, and
 * the message the user got asserted the first one for all four. A message that
 * cannot name which failure fired is not instrumentation.
 */
const decodeOne = async (
  ctx: BaseAudioContext, url: string, signal?: AbortSignal,
): Promise<{ buf: AudioBuffer | null; why: string | null }> => {
  let bytes: ArrayBuffer;
  try {
    bytes = await fetchBytes(url, signal);
  } catch (e) {
    return { buf: null, why: `could not be read (${errText(e)})` };
  }
  if (!bytes.byteLength) return { buf: null, why: 'read back empty' };

  // `decodeAudioData` DETACHES the buffer it is given, so the WebCodecs rung
  // below could never see the bytes again. Keep a copy BEFORE the first
  // attempt — this is the one place a second read is not avoidable.
  const spare = bytes.slice(0);

  const first = await decodeWhole(ctx, bytes, signal);
  if (first.buf) return first;

  const second = await decodeViaWebCodecs(ctx, spare, signal);
  if (second) return { buf: second, why: null };

  return { buf: null, why: first.why ?? 'carries no readable audio track' };
};

/** FIRST RUNG: hand the whole file to the engine and hope it demuxes it. */
const decodeWhole = async (
  ctx: BaseAudioContext, bytes: ArrayBuffer, signal?: AbortSignal,
): Promise<{ buf: AudioBuffer | null; why: string | null }> => {
  void signal;
  try {
    const decoded = ctx.decodeAudioData(bytes);
    // Old WebKit returns undefined and takes callbacks instead of a promise.
    if (!decoded || typeof (decoded as Promise<AudioBuffer>).then !== 'function') {
      return await new Promise<{ buf: AudioBuffer | null; why: string | null }>((resolve) => {
        try {
          (ctx as unknown as {
            decodeAudioData(b: ArrayBuffer, ok: (x: AudioBuffer) => void, no: (e?: unknown) => void): void;
          }).decodeAudioData(
            bytes,
            (b) => resolve({ buf: b, why: null }),
            (e) => resolve({ buf: null, why: e ? errText(e) : 'the browser could not open this file' }),
          );
        } catch (e) { resolve({ buf: null, why: errText(e) }); }
      });
    }
    return { buf: await within(decoded, DECODE_TIMEOUT_MS, 'decode'), why: null };
  } catch (e) {
    return { buf: null, why: errText(e) };
  }
};

// =============================================================================
// 3. MIX
// =============================================================================

/**
 * Lay every clip on one timeline that reproduces `Stage.seekClipTo`.
 *
 *   looping clip : source.loop = true, loopStart = 0, loopEnd = span,
 *                  start(0, startAt % span)
 *                  => at output offset u the media position is
 *                     (startAt + u) mod span, which is `t % span`. Exact.
 *
 *   non-looping  : start(0, min(startAt, span))
 *                  => position startAt + u, running out at the buffer end.
 *                  The video clamps at `span` and then holds its last frame;
 *                  the audio simply stops. Those agree everywhere the video is
 *                  still moving, which is the part that can be out of sync.
 */
const mixSources = async (
  decoded: { buf: AudioBuffer; src: OfflineAudioSource }[],
  startAt: number,
  seconds: number,
): Promise<AudioBuffer | null> => {
  const OAC = oacCtor();
  if (!OAC) return null;
  const length = Math.max(1, Math.ceil(seconds * SAMPLE_RATE));
  const ctx = new OAC(CHANNELS, length, SAMPLE_RATE);

  let wired = 0;
  for (const { buf, src } of decoded) {
    if (src.gain <= 0) continue;
    try {
      const node = ctx.createBufferSource();
      node.buffer = buf;
      const gain = ctx.createGain();
      gain.gain.value = src.gain;
      node.connect(gain).connect(ctx.destination);

      // `span` is the Stage's, not ours — but clamp it into the decoded buffer,
      // because a container's audio and video streams need not be the same
      // length and `loopEnd` past the buffer end is undefined behaviour.
      const span = Math.min(src.span > 0 ? src.span : buf.duration, buf.duration);
      if (src.loop && span > 0.01) {
        node.loop = true;
        node.loopStart = 0;
        node.loopEnd = span;
        node.start(0, startAt % span);
      } else {
        node.start(0, Math.min(Math.max(0, startAt), Math.max(0, buf.duration - 0.001)));
      }
      wired++;
    } catch { /* one clip's failure is that clip's silence */ }
  }
  if (!wired) return null;

  let mixed: AudioBuffer;
  try {
    // `startRendering()` is NOT cancellable, so it is raced against a deadline
    // and abandoned rather than awaited bare.
    mixed = await within(ctx.startRendering(), RENDER_TIMEOUT_MS, 'audio render');
  } catch {
    return null;
  }

  /**
   * TRUE-PEAK LIMIT — N clips at gain 1.0 SUM, and the sum clips.
   *
   * This never mattered while at most one clip could be audible: the old
   * per-clip switch was exclusive, so there was nothing to add. Letting every
   * selected clip into the mix (which is the whole point) makes summing the
   * normal case, and two ordinary clips measured a peak of 2.04 — hard-clipped
   * by the encoder into audible distortion, on an export that had finally
   * stopped being silent.
   *
   * Scaled by the MEASURED peak rather than by a fixed 1/N: the offline render
   * already holds the whole buffer, so the exact number is free, and 1/N would
   * quieten every well-behaved mix to buy headroom nothing needed. A mix that
   * already fits is left untouched, bit for bit.
   *
   * The ceiling is -3 dBFS, not -1, and that number is MEASURED. AAC is lossy,
   * so the decoded waveform is not the one handed to the encoder: limiting the
   * PCM to -1 dBFS still came back at 1.14 on a real two-clip mix — a +2.1 dB
   * codec overshoot that a 16-bit playback path would clip. -3 dBFS absorbs it.
   */
  let peak = 0;
  for (let c = 0; c < mixed.numberOfChannels; c++) {
    const d = mixed.getChannelData(c);
    for (let i = 0; i < d.length; i++) {
      const a = d[i] < 0 ? -d[i] : d[i];
      if (a > peak) peak = a;
    }
  }
  const CEILING = 0.708;
  if (peak > CEILING) {
    const k = CEILING / peak;
    for (let c = 0; c < mixed.numberOfChannels; c++) {
      const d = mixed.getChannelData(c);
      for (let i = 0; i < d.length; i++) d[i] *= k;
    }
  }
  return mixed;
};

// =============================================================================
// 4. ENCODE
// =============================================================================

const encodeAac = async (
  mixed: AudioBuffer, bitrate: number, signal?: AbortSignal,
): Promise<{ chunks: EncodedAudioRecord[]; error: string | null }> => {
  const Enc = encCtor();
  const Data = dataCtor();
  if (!Enc || !Data) return { chunks: [], error: 'no AudioEncoder' };

  const config: AudioEncoderConfig = {
    codec: 'mp4a.40.2',                    // AAC-LC. The MUXER is told 'aac'.
    sampleRate: SAMPLE_RATE,
    numberOfChannels: CHANNELS,
    bitrate,
  };

  // `isConfigSupported` REJECTS on a malformed config rather than resolving
  // false, and `supported` is optional in the typings — so the only correct
  // test is `=== true`, inside its own try/catch.
  try {
    const probe = await Enc.isConfigSupported(config);
    if (probe?.supported !== true) return { chunks: [], error: 'AAC not supported' };
  } catch (e) {
    return { chunks: [], error: `AAC probe failed (${errText(e)})` };
  }

  const raw: { data: Uint8Array; type: 'key' | 'delta'; timestamp: number; meta?: EncodedAudioChunkMetadata }[] = [];
  let encError: string | null = null;

  /**
   * The muxer writes `decoderConfig.description` into `esds` VERBATIM, and the
   * engines do not agree on what that field contains — WebKit hands back an
   * entire ES_Descriptor where Chrome hands back the bare AudioSpecificConfig.
   * Unfixed, every Safari and iOS export carried an audio track that ffprobe
   * reads as "22050 Hz, 0 channels, Audio object type 0" and no player will
   * open. Reduce it to the ASC before it can reach the file.
   */
  const normaliseMeta = (
    meta: EncodedAudioChunkMetadata | undefined,
  ): EncodedAudioChunkMetadata | undefined => {
    const dc = meta?.decoderConfig;
    if (!dc?.description) return meta;
    const src = dc.description as ArrayBuffer | ArrayBufferView;
    const bytes = ArrayBuffer.isView(src)
      ? new Uint8Array(src.buffer, src.byteOffset, src.byteLength)
      : new Uint8Array(src);
    const asc = toAudioSpecificConfig(bytes);
    if (asc === bytes) return meta;
    return { ...meta, decoderConfig: { ...dc, description: asc } };
  };

  const encoder = new Enc({
    output: (chunk, meta) => {
      try {
        const data = new Uint8Array(chunk.byteLength);
        chunk.copyTo(data);
        raw.push({ data, type: chunk.type, timestamp: chunk.timestamp, meta: normaliseMeta(meta) });
      } catch (e) { encError = encError ?? errText(e); }
    },
    error: (e: DOMException) => { encError = encError ?? errText(e); },
  });

  try {
    encoder.configure(config);
  } catch (e) {
    return { chunks: [], error: `configure failed (${errText(e)})` };
  }

  // Planar f32: `getChannelData(ch)` already IS one plane, so a planar layout
  // avoids an interleave pass entirely.
  const total = mixed.length;
  const planes: Float32Array[] = [];
  for (let c = 0; c < CHANNELS; c++) {
    planes.push(mixed.getChannelData(Math.min(c, mixed.numberOfChannels - 1)));
  }

  try {
    for (let i = 0; i < total; i += PCM_CHUNK_FRAMES) {
      if (signal?.aborted) break;
      if (encError) break;
      const n = Math.min(PCM_CHUNK_FRAMES, total - i);
      const flat = new Float32Array(n * CHANNELS);
      for (let c = 0; c < CHANNELS; c++) flat.set(planes[c].subarray(i, i + n), c * n);
      const ad = new Data({
        format: 'f32-planar',
        sampleRate: SAMPLE_RATE,
        numberOfFrames: n,
        numberOfChannels: CHANNELS,
        // FROM THE SAMPLE INDEX, rounded independently every time. Accumulating
        // a per-chunk delta would drift, and the muxer enforces monotonic DTS.
        timestamp: Math.round((i * 1e6) / SAMPLE_RATE),
        data: flat,
      });
      encoder.encode(ad);
      ad.close();
      // Yield so a long encode does not wedge the main thread in one burst.
      if ((i / PCM_CHUNK_FRAMES) % 8 === 7) await new Promise<void>((r) => setTimeout(r, 0));
    }
    await within(encoder.flush(), FLUSH_TIMEOUT_MS, 'audio flush');
  } catch (e) {
    encError = encError ?? errText(e);
  }
  try { encoder.close(); } catch { /* ignore */ }

  if (!raw.length) return { chunks: [], error: encError ?? 'encoder produced nothing' };

  // DURATION IS THE DELTA TO THE NEXT CHUNK — not a guessed 1024/sampleRate.
  // `addAudioChunkRaw` THROWS on a null duration, and `EncodedAudioChunk.duration`
  // is spec-nullable, which is exactly the trap the video path already documents.
  // Because every chunk is buffered before muxing, the delta is free, and it
  // survives an encoder that emits an odd priming or trailing frame.
  raw.sort((a, b) => a.timestamp - b.timestamp);
  const endUs = Math.round((total * 1e6) / SAMPLE_RATE);
  const chunks: EncodedAudioRecord[] = raw.map((r, i) => ({
    data: r.data,
    type: r.type,
    timestamp: r.timestamp,
    duration: Math.max(1, (i + 1 < raw.length ? raw[i + 1].timestamp : endUs) - r.timestamp),
    meta: r.meta,
  }));
  return { chunks, error: encError };
};

// =============================================================================
// 5. THE LADDER
// =============================================================================

/**
 * Produce an encoded AAC track for the offline render, or explain why not.
 * NEVER throws — every rung degrades to a silent-but-valid video.
 */
export const prepareOfflineAudio = async (
  sources: OfflineAudioSource[],
  opts: PrepareOptions,
): Promise<AudioPrepareResult> => {
  const warnings: string[] = [];
  const startAt = Math.max(0, opts.startAt ?? 0);
  const seconds = Math.max(0.05, opts.seconds);

  const audible = (sources ?? []).filter((s) => s && s.url && s.gain > 0);
  if (!sources?.length) {
    return { track: null, reason: 'No clips to take sound from.', decoded: 0 };
  }
  if (!audible.length) {
    return { track: null, reason: 'Every clip is muted, so the video is silent.', decoded: 0 };
  }
  if (!isOfflineAudioSupported()) {
    return { track: null, reason: "This browser can't encode audio.", decoded: 0 };
  }
  if (seconds * SAMPLE_RATE * CHANNELS * 4 > MAX_PCM_BYTES) {
    return { track: null, reason: 'That take is too long to mix sound for on this device.', decoded: 0 };
  }

  const OAC = oacCtor()!;
  // A throwaway context purely for decoding — decodeAudioData resamples into
  // the context's rate, so decoding at the SAME 48 kHz we mix and encode at
  // means no second resample anywhere in the chain.
  let decodeCtx: OfflineAudioContext;
  try {
    decodeCtx = new OAC(CHANNELS, SAMPLE_RATE, SAMPLE_RATE);
  } catch (e) {
    return { track: null, reason: `Could not open an audio context (${errText(e)}).`, decoded: 0 };
  }

  const decoded: { buf: AudioBuffer; src: OfflineAudioSource }[] = [];
  const failures: { id: string; why: string }[] = [];
  for (const s of audible) {
    if (opts.signal?.aborted) return { track: null, reason: 'Cancelled.', decoded: decoded.length };
    const { buf, why } = await decodeOne(decodeCtx, s.url, opts.signal);
    if (buf && buf.length > 0) decoded.push({ buf, src: s });
    else failures.push({ id: s.id, why: why ?? 'carries no readable audio track' });
  }
  if (!decoded.length) {
    // Say what actually happened. This used to assert ONE cause — "no readable
    // audio track" — for a fetch failure, a timeout, a revoked blob URL and a
    // container this engine will not open, which sent the owner looking for a
    // problem in files that turned out to be fine.
    const distinct = Array.from(new Set(failures.map((f) => f.why)));
    const detail = distinct.length === 1 ? distinct[0] : distinct.join('; ');
    return {
      track: null,
      reason: audible.length === 1
        ? `That clip's sound could not be read — it ${detail}.`
        : `None of the ${audible.length} clips' sound could be read — they ${detail}.`,
      decoded: 0,
    };
  }
  if (decoded.length < audible.length) {
    const lost = failures.map((f) => f.why);
    const distinct = Array.from(new Set(lost));
    warnings.push(
      `${failures.length} clip(s) had no readable sound and were left out (${distinct.join('; ')}).`,
    );
  }

  const mixed = await mixSources(decoded, startAt, seconds);
  if (!mixed) {
    return { track: null, reason: 'Mixing the sound failed.', decoded: decoded.length };
  }

  const { chunks, error } = await encodeAac(mixed, opts.bitrate ?? DEFAULT_BITRATE, opts.signal);
  if (!chunks.length) {
    return {
      track: null,
      reason: error ? `Sound could not be encoded (${error}).` : 'Sound could not be encoded.',
      decoded: decoded.length,
    };
  }
  if (error) warnings.push('The sound encoder stopped early; the audio may be short.');

  return {
    track: {
      codec: 'aac',
      sampleRate: SAMPLE_RATE,
      numberOfChannels: CHANNELS,
      chunks,
      sources: decoded.length,
      warnings,
    },
    reason: null,
    decoded: decoded.length,
  };
};

/**
 * Trim an encoded track to the video's ACTUAL length.
 *
 * The mix is rendered for the REQUESTED seconds, but the frame loop can stop
 * early (memory ceiling, encoder error). Audio longer than video makes most
 * players report the longer duration and hold a frozen final frame.
 *
 * The one-chunk floor is deliberate: some players reject a track whose `stts`
 * is empty, so a declared track must never end up with zero samples.
 */
export const truncateAudio = (
  chunks: EncodedAudioRecord[], videoDurationUs: number,
): EncodedAudioRecord[] => {
  if (!chunks.length || videoDurationUs <= 0) return chunks.slice(0, 1);
  const kept = chunks.filter((c) => c.timestamp < videoDurationUs);
  if (!kept.length) return chunks.slice(0, 1);
  const last = kept[kept.length - 1];
  const room = videoDurationUs - last.timestamp;
  if (room > 0 && room < last.duration) {
    kept[kept.length - 1] = { ...last, duration: Math.max(1, room) };
  }
  return kept;
};
