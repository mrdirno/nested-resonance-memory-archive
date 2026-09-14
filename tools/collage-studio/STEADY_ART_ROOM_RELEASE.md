# Art Room feedback that keeps the canvas steady

Author: Aldrin Payopay · September 14, 2026 · GPL-3.0-only

Status: reviewed and verified locally; publication/live checks pending. Existing fleet task T-18986, codex-collage-studio.

## Reused evidence and chosen improvement

C3724 shipped reachable Undo, Help and direct dice, then recorded a roughly 21px desktop stage jump whenever feedback appeared. The September 14 scoped Collage well has no new or building requests. This cycle resumes that explicit unfinished defect rather than opening another feature project. Public source is based on C3724 with the subsequent test-harness repair, current repository HEAD 8472d73c.

A fresh public-page measurement reproduced the failure. At 1280×720, Dice reduced the fitted artwork from 498px to 476.609px high and moved transport from 607px to 585.609px. At 844×390 it reduced artwork from 198px to 179.609px. The conditional footer paragraph consumed additional height when mounted. This was a layout defect, not changing art geometry or rendering time.

## Repair and limits

A persistent feedback slot shares the existing action row between dice and Apply on wide screens. Its 44px height and flexible width are independent of the message. Full success/error text remains in status/alert elements; wrapping and vertical scrolling retain long text, and the occupied region is keyboard focusable. Empty feedback adds no keyboard stop. No extra button, timeout, generator or dependency was added.

Portrait phones reserve two lines above the action row. Their editing canvas retains its fixed height; the desk gives up about 36.8px. Expanded portrait preview gives up the same space once, so a tall, height-limited artwork can be smaller than the previous empty-message view. Subsequent messages no longer move playback. Default width-limited Vibe cards retain their fitted size in the measured phone views. This is a deliberate stability tradeoff, not a claim that every viewport gets larger.

Draft/Apply/history semantics, recipes, renderer and encoded-media contracts are unchanged. Original video portability and global photo/video art overlays remain roadmap work. C3721's strict media validation and source lifecycle are the reusable starting point for video portability; original bytes alone would omit clip bindings and authored trim/speed/mix.

## Gates and production receipt

Independent code review found no data/logic blocker and required explicit portrait-expanded accounting plus narrow-landscape and enlarged-text checks. Typecheck and production build passed; existing Browserslist/chunk warnings remain. Final built-app behavioral gates passed: **34/34** existing Help/UX/audition/export cases on muted Chromium and Mobile Chrome, plus **12/12** new feedback cases across desktop/mobile Chromium and WebKit. Four actual native MP4s fully decode without errors. Existing artGuide invariants passed **4,660 checks**. Rebuilding the exact final source reproduces all five tested runtime artifact hashes. Deployment and public behavioral checks remain pending.

The source task retains measured public baseline, screenshots, browser logs and final receipt under work/weekly-2026-09-14. Prior C3721/C3722 exports and invariants remain evidence of those unchanged contracts; they are not counted as newly run tests.

The new regression fails against the previous live build on its first geometry assertion (artwork x moves 16.747px; independent measurement records the 21.391px height loss). Its initial default-font keyboard-scroll assertion was overstrict because the real Apply message fits two lines. The corrected test explicitly enlarges feedback to 150% and proves full text, real overflow, End/Home scrolling and stable geometry. Both runs are retained. A first test-discovery command selected no tests; it is not negative-control evidence.

Runtime: `index-f7a9d511.js`, `index-8bf057bd.css`, `render.worker-e06f7083.js`, service-worker cache `genart-v3-0a670611c36c`.
