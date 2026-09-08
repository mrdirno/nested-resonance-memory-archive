# C3721 — Music travels with the project

Author: Aldrin Payopay · September 7, 2026 · GPL-3.0-only

Status: local verification complete; publication and live verification pending.

Saving a `.collage` now includes the selected music original, its filename and MIME type, and its mute, level, trim and source-window fade settings. Open restores them together. Video files selected through Add music remain their original video containers; they are not transcoded. Use the existing Save project and Open actions; no new permanent controls are added.

The previous public writer was exercised in a muted browser with an original test tone, trim 2–4 seconds, level 25% and fade 0.5 seconds. Its actual downloaded archive contained no soundtrack. This was a demonstrated failed baseline, not an inferred missing feature.

The new archive descriptor is version 1, uses `soundtrack/original`, and carries exact byte count and SHA-256. It accepts originals up to 256 MiB. Missing originals, mismatched size/hash, unpaired/out-of-bounds trim, unknown metadata versions and malformed settings refuse the entire candidate before adoption. Failed saves produce no incomplete download and retain the current work. Old projects without a soundtrack open without retaining a previous project's music.

Open preserves authored motion, restores the music without the import action's autoplay/defaults, and retires preview monitor, solo and audition state. Unknown stored duration is measured again from the original so Trim becomes available. Beat analysis runs locally with URL ownership. Older Open results lose to a newer Open, Clear or music replacement and release their object URLs. Opening is refused while an earlier media import or take owns the current project, and that condition is checked again when an asynchronous read completes.

## Verification

Local gates: 58/58 built-app regression cases across Chromium and Mobile Chrome (art, captions, pins, soundtrack and Solo). After the final strict trim validation and refusal-copy changes, a fresh build passed all 18/18 soundtrack cases in 37.3 seconds. Typecheck and both production builds passed. No WebKit audio tests were run: QA output stayed muted. Source commit and production evidence will be recorded after publication. New regression file: `tests/e2e/project-music.spec.ts`. It reads downloaded ZIPs, reopens original audio/video containers and measures a real exported video for the selected middle tone, 25% gain and repeating source fades. It also exercises malformed archives, save retry, stale Open ownership, legacy projects, unknown duration and preserved Still motion.

The serializer unit suite has 18 passing groups, including bounded ZIP expansion, exact bytes/MIME/hash, strict metadata and URL disposal. Existing project-lock, Art Rack persistence and 2,070 SVG invariants passed. Typecheck passed after integration. Independent review found the intake/take ownership, duration-zero and restored-motion defects; each was repaired before publication.

## Boundaries and next step

This is music-source portability in manually downloaded `.collage` files. Original moving-video clips still reopen as their extracted frames. The private take duration and master take fade are not yet project fields. SVG and incremental crash recovery still omit music bytes. This is not a fully portable audiovisual timeline. Browser profiles are automated coverage, not physical iPhone certification. Already-loaded Studio can reopen its local music without a media network request; cold offline installation is a separate gate.

Next: preserve original video clips and the complete authored take, using the same explicit source contract before building shot sequencing. The local lyric model and deterministic third-party renderer plans remain qualified roadmap work.

## Shared close

C3719's already-deployed Solo release is reconciled in the evolution book with its exact historical evidence; C3720's remote-test comment now distinguishes serial observations from an unproved resource-pressure cause. The existing C3719 anonymous credit is retained with its verified source commit. Its ten Solo browser cases passed again locally in this cycle. The older caption-export test now respects already-open Details instead of toggling it shut; encoded lyric and soundtrack assertions remain intact.

Fleet thread: `persona500-collage-C3721-release`. A stored release message and Codex/Claude read acknowledgement are separate evidence. The weekly task remains the existing Monday 10 a.m. Pacific heartbeat; no duplicate scheduler was created.
