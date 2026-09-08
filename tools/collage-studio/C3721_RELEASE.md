# C3721 — Music travels with the project

Author: Aldrin Payopay · September 7, 2026 · GPL-3.0-only

**Shipped and verified live:** [code 1e89d3d9](https://github.com/mrdirno/nested-resonance-memory-archive/commit/1e89d3d92543e9749d96beae9abae52ec873c59e) · [Pages 34184898401](https://github.com/mrdirno/nested-resonance-memory-archive/actions/runs/34184898401) · [Open Studio](https://mrdirno.github.io/nested-resonance-memory-archive/collage/).

Saving a `.collage` now includes the selected music original, its filename and MIME type, and its mute, level, trim and source-window fade settings. Open restores them together. Video files selected through Add music remain their original video containers; they are not transcoded. Use the existing Save project and Open actions; no new permanent controls are added.

The previous public writer was exercised in a muted browser with an original test tone, trim 2–4 seconds, level 25% and fade 0.5 seconds. Its actual downloaded archive contained no soundtrack. This was a demonstrated failed baseline, not an inferred missing feature.

The new archive descriptor is version 1, uses `soundtrack/original`, and carries exact byte count and SHA-256. It accepts originals up to 256 MiB. Missing originals, mismatched size/hash, unpaired trim or trim outside a known stored duration, unknown metadata versions and malformed settings refuse the entire candidate before adoption. Failed saves produce no incomplete download and retain the current work. Old projects without a soundtrack open without retaining a previous project's music.

Open preserves authored motion, restores the music without the import action's autoplay/defaults, and retires preview monitor, solo and audition state. Unknown stored duration is measured again from the original so Trim becomes available. Beat analysis runs locally with URL ownership. Older Open results lose to a newer Open, Clear or music replacement and release their object URLs. Opening is refused while an earlier media import or take owns the current project, and that condition is checked again when an asynchronous read completes.

## Verification

Local gates: 58/58 built-app regression cases across Chromium and Mobile Chrome (art, captions, pins, soundtrack and Solo). After the final strict trim validation and refusal-copy changes, a fresh build passed all 18/18 soundtrack cases in 37.3 seconds. Typecheck and both production builds passed. No WebKit audio tests were run: QA output stayed muted. **58/58 public-site cases passed in 1.9 minutes** against the deployed URL. Archive health run `34184898399` also succeeded for the source commit. The public JS, CSS, render worker and service worker match the final tested build. New regression file: `tests/e2e/project-music.spec.ts`. It reads downloaded ZIPs, reopens original audio/video containers and measures a real exported video for the selected middle tone, 25% gain and repeating source fades. It also exercises malformed archives, save retry, stale Open ownership, legacy projects, unknown duration and preserved Still motion.

The serializer unit suite has 18 passing groups, including bounded ZIP expansion, exact bytes/MIME/hash, strict metadata and URL disposal. Existing project-lock, Art Rack persistence and 2,070 SVG invariants passed. Typecheck passed after integration. Independent review found the intake/take ownership, duration-zero and restored-motion defects; each was repaired before publication.

## Boundaries and next step

This is music-source portability in manually downloaded `.collage` files. Original moving-video clips still reopen as their extracted frames. The private take duration and master take fade are not yet project fields. SVG and incremental crash recovery still omit music bytes. This is not a fully portable audiovisual timeline. Browser profiles are automated coverage, not physical iPhone certification. Already-loaded Studio can reopen its local music without a media network request; cold offline installation is a separate gate.

Next: preserve original video clips and the complete authored take, using the same explicit source contract before building shot sequencing. The local lyric model and deterministic third-party renderer plans remain qualified roadmap work.

## Shared close

C3719's already-deployed Solo release is reconciled in the evolution book with its exact historical evidence; C3720's remote-test comment now distinguishes serial observations from an unproved resource-pressure cause. The existing C3719 anonymous credit is retained with its verified source commit. Its ten Solo browser cases passed again locally and on the public site in this cycle. The older caption-export test now respects already-open Details instead of toggling it shut; encoded lyric and soundtrack assertions remain intact.

Fleet thread: `persona500-collage-C3721-release`. A stored release message and Codex/Claude read acknowledgement are separate evidence. The weekly task remains the existing Monday 10 a.m. Pacific heartbeat; no duplicate scheduler was created.


The public build uses `index-a2107548.js`, `index-cba4b554.css`, `render.worker-fcab2428.js` and service-worker cache `genart-v3-1bc4eca5f605`. JS SHA-256: `8a3f0cbeb8b3ccfd0e66642ec7223d4f2a17e4c9027f4d24a1d8b588b86a2c60`. Both public-site reopened MP4s fully decode without errors: H.264 picture, AAC 48 kHz sound, approximately five seconds. The selected middle tone dominates the excluded tones and the measured source gain is `0.2503843093`; the 2-second source-loop joins fade as authored. Test fixtures are synthetic, and the verification clip contains a test tone.

Repeat the public behavioral gate serially, with Chromium output muted by the project config:

```sh
COLLAGE_BASE_URL=https://mrdirno.github.io/nested-resonance-memory-archive/collage/ npx playwright test tests/e2e/project-music.spec.ts tests/e2e/project-integrity.spec.ts tests/e2e/art-rack.spec.ts tests/e2e/solo.spec.ts tests/e2e/captions.spec.ts --project=chromium --project='Mobile Chrome' --workers=1
```

Evidence retained in the source task's `work/weekly-2026-09-07`: intended failing public baseline, unit receipt, local regression logs, final build log, 18-case final soundtrack run, 58-case live log, matching artifact hashes, decoded media measurements and screenshots. User-facing copies are in that task's `outputs`. Fleet delivery/readback is retained there after posting; a stored message does not establish either peer's acknowledgement.
