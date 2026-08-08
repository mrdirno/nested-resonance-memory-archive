// src/lib/soundtrack.ts
// -----------------------------------------------------------------------------
// THE SOUNDTRACK — music under the collage.
//
// WHY THIS FILE EXISTS
//   THE MOVE gave a collage of PHOTOGRAPHS a time axis, so a photo collage can
//   finally be exported as a video. That video is necessarily SILENT: every
//   sample this app has ever mixed came out of a video clip's own audio track,
//   and a collage made of photographs has no clips. The one thing anybody wants
//   under a moving reel is music, and there was no way to give it one — the
//   file picker accepted `image/*,video/*` and `ingestFiles` rejected everything
//   else with "images and video only".
//
// THE SHAPE, AND WHY IT IS ALMOST NOTHING
//   A soundtrack is A CLIP WITH NO PICTURE. The Stage's audio architecture is
//   already per-source and complete: an element, a `MediaElementSource`, a gain
//   node into `masterGain` (which is what `captureStream` taps, so the realtime
//   recorder gets it for free), an INTENT flag, and one row out of
//   `describeAudioSources()` for the offline mixer. Music plugs into all five.
//   `offlineAudio.mixSources` needs NO change: it decodes a url, resolves a
//   window through `clipWindow`, and sums under a true-peak limiter — none of
//   which cares whether the container also had pictures in it.
//
//   So this module holds the three decisions that ARE particular to music, and
//   nothing else.
//
// DECISION 1 — A SOUNDTRACK HAS NO PICTURE, SO ITS SPAN IS THE SOUND'S OWN.
//   `OfflineAudioSource.span` exists so a clip's sound lands in the same window
//   as its PICTURE: it is `seekClipTo`'s expression verbatim, carried across so
//   the two timelines cannot round the seek epsilon differently and drift.
//   Music has no picture to agree with, and its container-reported duration is
//   not the decoded buffer's: an mp3 carries encoder delay and padding, so
//   `<audio>.duration` and `decodeAudioData().duration` differ by a hop.
//
//   Handing that hop over as `span` is not merely imprecise, it changes BRANCH:
//   `audioSchedule` compares the window against the decoded length and, when the
//   sound ends INSIDE the window, switches to the LAPPED plan — one non-looping
//   node per picture lap, built for a clip whose audio track is shorter than its
//   video track. Music would then lap at the container's length with a sliver of
//   silence cut into every repeat, forever, because of a rounding difference.
//
//   `span: 0` is the documented "unknown", and the mixer then uses `buf.duration`
//   — the sound's own length, which for music is the only length there is. The
//   sweep asserts this for EVERY duration, sane ones included, so an edit that
//   helpfully passes the real number fails rather than ships a sliver.
//
// DECISION 2 — INTENT IS NOT AUDIBILITY, and this file keeps them adjacent.
//   Written down in `stage.ts` as the bug that made exports silent: `gain` for
//   the FILE is the user's intent (`!muted`); `audible` is a fact about the
//   SPEAKERS, and it carries two conditions that mean nothing to a file — the
//   monitor switch (which starts OFF, because browsers only autoplay muted
//   media) and the realtime decoder budget. A mixer wired to `audible` renders
//   silence for a user who simply never pressed the speaker.
//
//   Both resolutions live here, three lines apart, and the sweep asserts that
//   the export side does not read `soundOn` at all.
//
// DECISION 3 — A CLIP IS A PICTURE THAT HAPPENS TO HAVE SOUND; A SOUNDTRACK IS
//   NOTHING BUT SOUND. Clips arrive MUTED ("a collage that shouts on import is
//   not a nice thing to build" — stage.ts). Music does not: adding it is an
//   explicit act whose entire purpose is the sound, so intent defaults ON and
//   the export carries it. The monitor still starts off, because that is a
//   browser rule rather than a preference.
// -----------------------------------------------------------------------------

/**
 * The one id the mixer, the status row and the UI all use for the music. It is
 * not a clip id and can never collide with one: clip ids are minted as
 * `clip-${Date.now()}-${seq}` / `vid-…`, so the leading `__` is unreachable.
 */
export const SOUNDTRACK_ID = '__soundtrack__';

/**
 * The music, as the app holds it. The URL is a durable `blob:` minted and owned
 * by App.tsx (revoked only when the track is replaced or cleared), exactly like
 * a `LiveClip`'s.
 */
export interface SoundtrackSpec {
  /** Durable `blob:` URL over the audio File. */
  url: string;
  /** The file's own name, shown on the chip. */
  name: string;
  /**
   * Intrinsic length, probed on import for the LABEL only. 0 / NaN / Infinity
   * all mean "not known yet", and nothing about the render depends on it —
   * see DECISION 1.
   */
  durationSec: number;
  /** THE USER'S INTENT: "this music is part of the piece". Absent means NO. */
  muted?: boolean;
}

/**
 * Structurally `offlineAudio.OfflineAudioSource`, declared here rather than
 * imported so this module stays free of the mixer (which pulls in WebCodecs
 * types and a muxer). The sweep asserts the field set matches what
 * `describeAudioSources` emits for a clip.
 */
export interface SoundtrackSource {
  id: string;
  url: string;
  span: number;
  loop: boolean;
  gain: number;
  rate: number;
}

/**
 * Audio-only extensions. DELIBERATELY DISJOINT from `video.ts`'s `VIDEO_EXT`:
 * `.ogg`, `.mp4` and `.webm` are ambiguous containers that already belong to the
 * video bucket, and a file that could be either must land in exactly one place.
 * `.m4a`, `.oga`, `.weba` and `.opus` are the audio-only spellings of those same
 * containers, which is why they are safe to claim.
 */
const AUDIO_EXT = /\.(mp3|m4a|m4b|aac|wav|wave|flac|opus|oga|weba|aif|aiff|caf|amr|wma)$/i;

/** The video bucket's own rule, mirrored so the two can be checked together. */
const VIDEO_EXT = /\.(mp4|m4v|mov|qt|webm|mkv|avi|ogv|ogg|3gp|3g2|mpg|mpeg|ts|m2ts)$/i;

/**
 * Route a picked or dropped file to the MUSIC bucket.
 *
 * EVERY FILE MUST LAND IN EXACTLY ONE BUCKET — the rule `offlineAudio` learned
 * twice and wrote down. `ingestFiles` sorts into music / video / picture /
 * rejected, and the three tests run against the same `File`, so an overlap is a
 * file that is silently both (imported twice) or a file that is neither
 * (rejected with a message naming formats it matches).
 *
 * The rule, in order:
 *   1. A STATED `audio/*` type is believed. This is the ordinary case and it
 *      covers `audio/mpeg`, `audio/mp4` (.m4a), `audio/x-m4a`, `audio/wav`.
 *   2. ANY OTHER STATED TYPE is believed too, and means NOT music — so a
 *      `video/mp4` never reaches the music bucket even though its container can
 *      hold an audio-only stream.
 *   3. An EMPTY type falls back to the extension, and the ambiguous containers
 *      go to VIDEO. Empty types are routine, not exotic: `.mov` off an iPhone
 *      share sheet and files from Android's SAF both arrive with `type === ''`,
 *      which is exactly why `isVideoFile` already has this clause.
 */
export const isAudioFile = (file: { name: string; type: string }): boolean => {
  const type = file.type || '';
  if (type.startsWith('audio/')) return true;
  if (type) return false;
  const name = file.name || '';
  return AUDIO_EXT.test(name) && !VIDEO_EXT.test(name);
};

/**
 * The music, as the OFFLINE MIXER sees it — the export's intent, and nothing
 * about the speakers. Null when there is no track at all; a MUTED track still
 * produces a row, with `gain: 0`, exactly as a muted clip does, so the mixer's
 * reason ladder can tell "you muted everything" from "there was nothing".
 *
 * `loop` is always true (music laps under a take that outruns it, which is what
 * every clip in this app already does) and `rate` is always 1 (video-length sync
 * scales a clip's sound to match its rate-scaled PICTURE; music has none).
 */
export const soundtrackSource = (t: SoundtrackSpec | null | undefined): SoundtrackSource | null => {
  if (!t || !t.url) return null;
  return {
    id: SOUNDTRACK_ID,
    url: t.url,
    // DECISION 1. Never `t.durationSec`.
    span: 0,
    loop: true,
    gain: t.muted ? 0 : 1,
    rate: 1,
  };
};

/**
 * What you can actually HEAR right now. The monitor switch is the only thing
 * here that the export side must never see.
 */
export const soundtrackAudible = (
  t: SoundtrackSpec | null | undefined,
  soundOn: boolean,
): boolean => !!t && !!t.url && !t.muted && !!soundOn;

/**
 * `2:07`, for the chip. Same shape as `video.formatTimecode`, reimplemented in
 * one line rather than imported so this module keeps no dependency on the video
 * pipeline — it is the one part of the app that has nothing to do with pictures.
 */
export const soundtrackLength = (sec: number): string => {
  if (!Number.isFinite(sec) || sec <= 0) return '';
  const total = Math.floor(sec);
  return `${Math.floor(total / 60)}:${String(total % 60).padStart(2, '0')}`;
};
