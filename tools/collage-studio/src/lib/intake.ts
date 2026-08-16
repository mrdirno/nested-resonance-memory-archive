// src/lib/intake.ts
// -----------------------------------------------------------------------------
// WHICH BUCKET A PICKED FILE LANDS IN — the one copy of that rule.
//
// WHY THIS FILE EXISTS
//   From the field: *"Be able to add music or sound without the video. Right now
//   if you use a video for the sound or import audio from video it just imports
//   video… if you're importing audio it should not display the video."*
//
//   The app has three file buttons — add anything, add video, add MUSIC — and
//   all three fired one `onChange` that called `ingestFiles(list)`. So the app
//   forgot WHICH button was pressed, and routing was a function of the FILE
//   ALONE. Press "Add music", pick a `.mov` (every mobile picker offers them,
//   and an iPhone's share sheet hands them over with an empty MIME type), and
//   `isVideoFile` answered "video" — correctly, for a question nobody asked.
//   The clip landed in the collage as a picture. The user asked for a sound and
//   got a rectangle.
//
//   THE FIX IS NOT A FOURTH PREDICATE. It is that the question was underspecified:
//   "what kind of file is this" has one answer, "what did this person ask for"
//   has another, and only the second one can be wrong. So intake takes the
//   INTENT the button carries, and `.mov` under `'music'` is sound.
//
// WHY IT IS A MODULE AND NOT THREE FILTERS AT THE CALL SITE
//   `ingestFiles` sorted with three inline predicates in a fixed order, and
//   `tests/unit/soundtrack.invariants.mjs` asserted "EXACTLY ONE BUCKET" against
//   a LOCAL COPY of those three lines (`bucketOf`) — a second spelling of one
//   rule, which is the drift this project has already written two scars about
//   (`lib/level.ts` I5: the gain read `t.muted ? 0 : 1` in one emitter and
//   `wanted ? 1 : 0` in the other). The sweep now calls the shipped function, so
//   the cross product it sweeps is a measurement of the app rather than of a
//   paraphrase of it.
//
// DECISION 1 — EXACTLY ONE BUCKET, STILL. The invariant `soundtrack.ts` states
//   and the sweep enforces is unchanged and now holds BY CONSTRUCTION: this is a
//   single ladder with one `return` per rung, so a file cannot be two things and
//   cannot be none. Intent moves a file BETWEEN buckets; it never splits one.
//
// DECISION 2 — `'any'` IS BYTE-IDENTICAL TO WHAT SHIPPED. Every drop, every
//   "add images or video" press and every legacy path routes with `'any'`, and
//   the ladder under `'any'` is `isAudioFile` → `isVideoFile` → `image/*` →
//   rejected, in that order: the three predicates that were inline, verbatim.
//   The sweep asserts this against the old expression for the whole cross
//   product, so "the fix changed nothing for anyone who did not ask for it" is a
//   measurement and not a hope.
//
// DECISION 3 — UNDER `'music'`, A PICTURE IS REFUSED RATHER THAN QUIETLY ADDED.
//   The wish is precisely "I asked for sound and got a picture", so the music
//   button routing a `.jpg` into the collage would be the same defect wearing a
//   different file extension. It is rejected, and `ingestFiles` names it — a
//   refusal that says which file and why is recoverable; a silent picture is
//   the bug being reported.
//
// DECISION 4 — INTENT CANNOT MANUFACTURE SOUND. `'music'` routes a video
//   CONTAINER to the music bucket because a container that can hold pictures can
//   hold sound. Whether this particular file actually HAS an audio track is not
//   a question a file name can answer, and this module does not pretend to: the
//   decoder answers it downstream, and `adoptSoundtrack`'s probe degrades to a
//   chip with no length (`soundtrack.ts` DECISION 1) rather than to a lie.
// -----------------------------------------------------------------------------

import { isAudioFile } from './soundtrack';
import { isVideoFile } from './video';

/**
 * WHAT THE PERSON ASKED FOR, which is not the same question as what the file is.
 *
 * `'any'` — the drop zone, the "add images or video" button, the video button:
 *           the file decides, exactly as it always has.
 * `'music'` — the MUSIC button: this import is about SOUND, so a video container
 *           is a sound file that happens to have pictures in it, and the
 *           pictures are not wanted.
 */
export type IntakeIntent = 'any' | 'music';

/** The four destinations `ingestFiles` has always had. */
export type IntakeBucket = 'music' | 'video' | 'picture' | 'rejected';

/**
 * Route ONE file. Total, pure, and the only place the order of these tests is
 * written down.
 *
 * The parameter is structural (`{ name, type }`) rather than `File` so the sweep
 * can hand it the extension x MIME cross product without minting a thousand
 * blobs — the same reason `isAudioFile` takes that shape.
 */
export const routeIntake = (
  file: { name: string; type: string },
  intent: IntakeIntent = 'any',
): IntakeBucket => {
  // A file that IS audio is music under every intent. Nothing about "add images
  // or video" makes an .mp3 into a picture.
  if (isAudioFile(file)) return 'music';

  // THE ONE LINE THE WISH IS ABOUT. Same file, same predicate, different answer,
  // because the question changed.
  if (isVideoFile(file)) return intent === 'music' ? 'music' : 'video';

  // DECISION 3 — under `'music'` a picture is not a lesser kind of sound.
  if ((file.type || '').startsWith('image/')) return intent === 'music' ? 'rejected' : 'picture';

  return 'rejected';
};

/**
 * The whole pick, sorted — what `ingestFiles` actually needs, so the call site
 * holds no copy of the ladder and no second opinion about its order.
 *
 * Order WITHIN each bucket is the order the files arrived in, which is what
 * makes "the last music file picked wins" mean what it says at the call site.
 */
export interface IntakeSplit {
  music: File[];
  video: File[];
  picture: File[];
  rejected: File[];
}

export const splitIntake = (list: File[], intent: IntakeIntent = 'any'): IntakeSplit => {
  const split: IntakeSplit = { music: [], video: [], picture: [], rejected: [] };
  for (const f of list) split[routeIntake(f, intent)].push(f);
  return split;
};
