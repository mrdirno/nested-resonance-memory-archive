# Game evaluation falsifier

Author: Aldrin Payopay · Local experiment · September 8, 2026

Run `node falsify.mjs` from this folder. The only output is `receipt.json` here.
The script reads Persona500's actual legacy evaluator and one tracked game with
Node standard libraries and read-only Git commands. It makes no network request.

It extracts only the inspected `fingerprintFromText` function, verifies its
SHA-256, and executes those exact bytes with Node crypto. It never imports the
evaluator module or runs its `main`. Missing files, unknown extraction, or a
changed function fail with exit 2. Hash pinning, not Node vm, is the trust boundary.

The negative control appends a comment and blank lines to otherwise identical
gameplay code. The receipt includes exact fixture inputs, an executed three-press
trace, the actual fingerprints, and the real game's Git/source identity plus the
exact appended suffix. Proprietary game/evaluator source stays in Persona500.

The history check compares `HEAD:public/games/pulse-desk/game.js` against the
legacy evaluator's `HEAD:games/pulse-desk/game.js` lookup. A failed legacy lookup
is significant because the evaluator converts missing history into `NEW`.

Exit 0 means the falsifier reproduced, **not** that a game is healthy. Exit 1
means the expected counterexample did not reproduce; it is not a pass. This
experiment measures an evaluation defect and does not certify gameplay,
improvement, browser behavior, production delivery, or scientific validity.

Optional flags: `--repo PATH`, `--evaluator PATH`, `--output NAME.json`. Output
remains inside this folder. Reinspect and repin the function if it changes.

Run `node check-errors.mjs` after the falsifier to verify that a missing evaluator,
unknown extraction, and changed function each exit 2 and preserve the successful
receipt. These three explicit negative controls write `negative-controls.json`.
