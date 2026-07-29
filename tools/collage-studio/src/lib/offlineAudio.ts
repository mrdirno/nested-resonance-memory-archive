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
 * Decode one clip's audio. Individually try/caught on purpose: a clip with no
 * audio track throws `EncodingError` on every engine, and a WebM/Opus source
 * fails on Safari. One undecodable clip must cost THAT CLIP its sound — never
 * the render — exactly as a failed seek costs one frame its motion.
 */
const decodeOne = async (
  ctx: BaseAudioContext, url: string, signal?: AbortSignal,
): Promise<AudioBuffer | null> => {
  try {
    // `decodeAudioData` DETACHES the ArrayBuffer it is given, so a buffer can
    // never be decoded twice. We fetch per clip, so that is fine here — but it
    // is why this must not be refactored to share one buffer.
    const bytes = await fetchBytes(url, signal);
    const decoded = ctx.decodeAudioData(bytes);
    // Old WebKit returns undefined and takes callbacks instead of a promise.
    if (!decoded || typeof (decoded as Promise<AudioBuffer>).then !== 'function') {
      return await new Promise<AudioBuffer | null>((resolve) => {
        try {
          (ctx as unknown as {
            decodeAudioData(b: ArrayBuffer, ok: (x: AudioBuffer) => void, no: () => void): void;
          }).decodeAudioData(bytes, resolve, () => resolve(null));
        } catch { resolve(null); }
      });
    }
    return await within(decoded, DECODE_TIMEOUT_MS, 'decode');
  } catch {
    return null;
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

  try {
    // `startRendering()` is NOT cancellable, so it is raced against a deadline
    // and abandoned rather than awaited bare.
    return await within(ctx.startRendering(), RENDER_TIMEOUT_MS, 'audio render');
  } catch {
    return null;
  }
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

  const encoder = new Enc({
    output: (chunk, meta) => {
      try {
        const data = new Uint8Array(chunk.byteLength);
        chunk.copyTo(data);
        raw.push({ data, type: chunk.type, timestamp: chunk.timestamp, meta });
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
  for (const s of audible) {
    if (opts.signal?.aborted) return { track: null, reason: 'Cancelled.', decoded: decoded.length };
    const buf = await decodeOne(decodeCtx, s.url, opts.signal);
    if (buf && buf.length > 0) decoded.push({ buf, src: s });
  }
  if (!decoded.length) {
    return { track: null, reason: 'None of these clips carry a readable audio track.', decoded: 0 };
  }
  if (decoded.length < audible.length) {
    warnings.push(`${audible.length - decoded.length} clip(s) had no readable sound and were left out.`);
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
