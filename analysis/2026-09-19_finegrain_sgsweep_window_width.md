# The measurable self-gravity window at the cut drive has upward width, not a single knife-edge: a finer grid (0.25 / 0.3 / 0.35) makes five of nine runs measurable but still one countable condition, one measurable run short of an evaluable F3

Author: Aldrin Payopay · September 19, 2026 · GPL-3.0-only

## Summary

Ring 26 swept the recorded grid's self-gravity axis at the cut drive
(`sg ∈ {0, 0.15, 0.3, 0.5, 0.8}`, `fieldExp 1.7`, `gl0`) and found exactly one
measurable condition, `sg0.3`. It called `sg0.3` a knife-edge "narrower than one
grid step" and left open its first question: **are there three measurable
conditions inside the window — a finer grid, e.g. `0.25 / 0.3 / 0.35`, each
screened before scoring — that could reach F5 where the coarse grid does not?**
F5 needs at least three measurable conditions; F3 needs at least six measurable
runs; the frozen protocol has never returned anything but `insufficient support`.

This ring runs that finer grid: `sg ∈ {0.25, 0.3, 0.35}` at `fieldExp 1.7`,
`gl0`, three grid seeds each — nine runs on one pinned instrument
(`sim_digest 40bfdb68`), scored together on the frozen scorer (`sha 7619ef6b`).
The answer is a sharper picture than the knife-edge:

- **Five of nine runs are measurable** (Ring 26: three of fifteen), but still
  **one countable condition.** Verdict `insufficient support`: F1, F2, F4 pass;
  F5 fails (1 measurable condition, needs 3); **F3 is one measurable run short of
  evaluable** — it needs six and there are five.
- **The window is not a single point.** `sg0.3` is measurable 3/3 (reproducing
  Rings 25/26 exactly). `sg0.35` is measurable **2 of 3** — a clean moving field,
  **not** cap-saturated (clamp share 0.074, the same as `sg0.3`; A3 0.053). So the
  window has real upward width to at least 0.35; Ring 26's "narrower than one grid
  step" understated the high side.
- **The lower wall is systematic and sits between 0.25 and 0.3.** `sg0.25` is
  measurable 0/3: the seed lock is already broken (E3 = 0) but participation is
  too weak — E2 fails ≈ 10 of 22 in every seed, only 10/10/11 epochs eligible, all
  below the 12-epoch floor. This is the same participation floor as `sg0.15`,
  measured one grid-half closer (10–11 eligible vs `sg0.15`'s 8).
- **Why F5 is still out of reach is different now.** Not "only one point is
  measurable" (Ring 26) but "the second measurable point is 2/3": a condition
  counts toward F5 only when **all** its seeds are measurable
  (`memory_estimator_qualify.py:730`), and `sg0.35`'s seed 12345 lands at 11
  eligible epochs — one epoch short of the floor, on participation variance
  (E2 = 10), not a wall.
- **No condition is static** (A3 0.05–0.09, well below 0.99; the screen flags
  none). No Ring 21 collapse confound. **No memory result is claimed** anywhere:
  detection fires 2/3 in `sg0.3` only (seeds 777 and 31337), not reproduced.

**Nothing about nested resonance memory is decided.** What is measured: at the
cut drive the measurable self-gravity window is one-sided — a sharp participation
wall between 0.25 and 0.3, a gradual upper decay through 0.35 (2/3) toward the
cap-saturation collapse at 0.5 — and the finer grid nearly doubles the measurable
run count without crossing either structural threshold (3 measurable conditions,
6 measurable runs). The most direct path to the first non-`insufficient` verdict
is now a second triple at `sg0.35`: if fresh seeds make it 3/3, two countable
conditions exist and one more inside the window would reach F5, while six
measurable runs would make F3 evaluable. This ring is exploratory measurability
mapping, not a pre-registered confirmatory grid; "upward width to at least 0.35"
rests on two measurable seeds of three at n = 3 per condition, and is exactly what
the proposed fresh `sg0.35` triple would confirm.

## The measured grid

All at `spinchladni gl0`, `fieldExp 1.7`, 4,194,304 particles, 24 epochs, grid
seeds 777 / 12345 / 31337, one instrument. Eligible epochs are of the 22 the
scorer reads (epochs 3–24); gate-fail counts are per run over those 22; A3
(median epoch-to-epoch full-field density correlation) and the clamp share are
from the unmodified staticness screen.

| condition | eligible (777/12345/31337) | measurable | E1 mass fails | E2 partic. fails | E3 lock fails | clamp share | A3 | screen |
|-----------|---------------------------:|:----------:|--------------:|-----------------:|--------------:|------------:|----:|--------|
| sg0.25 | 10 / 10 / 11 | 0/3 | 7 / 5 / 5 | 10 / 10 / 9 | 0 / 0 / 0 | 0.046 | 0.093 | PASS (all below the 12 floor) |
| **sg0.3** | **19 / 17 / 17** | **3/3** | 3 / 4 / 3 | 2 / 3 / 5 | 0 / 0 / 0 | 0.074 | 0.075 | PASS |
| sg0.35 | 15 / 11 / 17 | 2/3 | 1 / 2 / 1 | 6 / 10 / 5 | 0 / 0 / 0 | 0.074 | 0.053 | PASS |

`insufficient support`; measurable conditions `['spinchladni_sg0.3_gl0']`;
measurable runs 5 of 9 (`sg0.3` ×3, `sg0.35` seeds 777 and 31337); F1 pass,
F2 pass, **F3 not evaluable (5 measurable runs, needs 6)**, F4 pass, F5 fail
(1 measurable condition, needs 3). Detection fires only inside `sg0.3` (seeds 777
and 31337) — the same two seeds and borderline S as Rings 25/26. No memory
positive is claimed.

## The window is one-sided: a wall below, a decay above

Measurability turns on mass (E1), participation (E2) and cross-seed separation of
the relic template (E3, the seed lock). Across `0.25 → 0.3 → 0.35` the seed lock
is broken everywhere (E3 = 0 in all nine runs — the drive cut's job, done well
below `sg0.3`). What moves is participation.

- **Below (`sg0.25`): a systematic participation wall.** Every seed fails E2 in
  9–10 of 22 epochs and E1 in 5–7, leaving 10/10/11 eligible — uniformly below the
  12 floor. There is simply not enough self-gravity to build participating
  structure over enough epochs; the uniformity across seeds (not a spread) marks
  it as a wall, not variance. The floor crossing (12 eligible) lies between 0.25
  and 0.3.
- **At `sg0.3`: the balance point.** E3 = 0, E1 fails 3–4, E2 fails 2–5, 17–19
  eligible, 3/3 measurable — reproducing Rings 25/26 on a freshly generated
  triple.
- **Above (`sg0.35`): a gradual decay, not yet cap saturation.** Two seeds (777,
  31337) clear the floor at 15 and 17 eligible and are measurable; seed 12345
  lands at 11 (E2 = 10), one epoch short. The field is **not** cap-saturated —
  clamp share 0.074, identical to `sg0.3`, and A3 0.053, a clean moving field
  (contrast `sg0.5` at Ring 26: clamp 0.967, E2 fails 17, cap-saturated). So the
  0.35 shortfall is per-seed participation variance, not the ceiling that closes
  the window by 0.5.

The two-walled window Ring 26 described is really one sharp lower wall
(participation, between 0.25 and 0.3) and a gradual upper decay (0.3 → 0.35 → 0.5)
whose far end is cap saturation. The knife-edge understated the width above 0.3.

## Provenance and grounding

- **One instrument, nine runs.** Every run records `test_page_sha256`
  `1a15b987…`, `source_page_sha256` `2a1cf94a…`; the working tree's
  `tests/halo/rc-test.html` hashes to `sim_digest 40bfdb68…` /
  `core_digest 50f1e370…` / `tick_digest f887b63f…` — the Ring 24/25/26 pin.
  Rings 24/25/26 ran at `test_page 46405b3d`; `1a15b987` is the **same behavioural
  page with Ring 26's comment block appended** (`sim_digest` excludes comments), so
  the instrument is continuous and this grid is comparable to Ring 26's coarse one.
  Each run records `git_dirty = true`, which is untracked files in the tree (the
  results being written), not a modified instrument.
- **Four runs reused after verification, five generated fresh.** `sg0.25` (all
  three seeds) and `sg0.3` seed 777 were produced by an interrupted run on the
  tree (2026-09-18 23:07–23:16, HEAD `cc8b7c62`) that died mid-`sg0.3`; each was
  verified before reuse — mesh complete (3,145,728 bytes = 24 × 32³ float32),
  parameters exact (`selfgrav`, `gl0`, `fieldExp 1.7`, 4.19M, 24 epochs),
  `test_page 1a15b987`, `pageerrors []`. `sg0.3` seeds 12345 (whose mesh the
  interruption truncated) and 31337, and all three `sg0.35` seeds, were generated
  this cycle (110–133 s each, `pageerrors []`) on the identical instrument. All
  nine share one `test_page` hash. Reuse rests on the chamber being deterministic
  for a fixed seed and page (same seed + `sim_digest` → same mesh); the `sg0.3`
  triple is that check — its reused seed 777 and freshly generated seeds
  12345/31337 together reproduce Rings 25/26's recorded triple exactly (19/17/17),
  which any divergence between reused and fresh runs would have broken.
- **Scorer frozen and unmodified.** `memory_estimator_qualify.py` hashes to
  `7619ef6b…`, the value inside the committed output; the reused synthetic receipt
  (`memory_estimator_qualification/synthetic.json`) carries `script_sha256`
  `7619ef6b…` and `protocol_sha256` `e55a53a1…`, both verified before the scorer
  runs. The staticness screen (`memory_pilot_staticness.py`) and manifest builder
  (`memory_pilot_manifest.py`) are unmodified; the scorer's manifest check
  re-hashed all nine files and set `verdict.inputs_verified = true` (the manifest
  file itself carries no `verified` field — the check runs at score time).
- **Pipeline validated against the record.** `sg0.3` reproduces Ring 25/26's
  committed cut-drive triple exactly — 19/17/17 eligible, E3 = 0, measurable 3/3,
  detection (777 yes, 12345 no, 31337 yes) — so the sweep numbers stand on the
  frozen scorer, not a re-implementation.
- **Inputs sealed; meshes regenerable.** All nine run JSON and one manifest,
  qualification and staticness JSON are committed; the nine `*.mesh.f32` are
  gitignored and regenerable by the harness.

## Falsifiers and what would change the reading

- If some condition were static, its (non-)measurability would be the Ring 21
  collapse confound. None is: A3 0.05–0.09, the screen flags none.
- If `sg0.35`'s 2/3 were cap saturation (the mechanism that closes the window by
  0.5), the clamp share would be high. It is not — 0.074, identical to `sg0.3`;
  `sg0.5` was 0.967. The 0.35 shortfall is participation variance.
- If `sg0.25`'s failure were the seed lock rather than participation, the drive
  cut would not generalise below `sg0.3`. It is not: E3 = 0 in all three seeds;
  E1/E2 are the wall, and the shortfall is 10–11 eligible against a 12 floor.
- If the nine runs were not one instrument, "window across self-gravity" would
  confound instrument with condition. All nine share `test_page 1a15b987` and the
  working tree's `sim_digest 40bfdb68`.
- If `sg0.3` had drifted on the freshly generated triple, the pipeline would be
  suspect. It reproduces Ring 25/26 exactly (19/17/17, E3 = 0, detection
  777/31337).
- If `sg0.35` at 2/3 counted toward F5, the "still one condition" claim would be
  wrong. It does not: F5 counts a condition only when all its seeds are measurable
  (`memory_estimator_qualify.py:730`), and seed 12345 is not.

## Files

- Runs (committed JSON; `*.mesh.f32` gitignored, regenerable):
  `data/results/halo/memory_finegrain_sgsweep/spinchladni_sg{0.25,0.3,0.35}_gl0_seed*_n4194304_e24_fieldExp1.7.json`
- Sealed manifest + scored output + staticness (committed):
  `data/results/halo/memory_finegrain_sgsweep/{manifest,qualification,staticness}.json`
- Frozen scorer (untouched, sha 7619ef6b): `experiments/halo/memory_estimator_qualify.py`
- Staticness screen (unmodified): `experiments/halo/memory_pilot_staticness.py`
- Run harness (override flags): `tests/halo/memory_prereg_run.js`
- Ring 26 (the question this answers): `analysis/2026-09-18_cutdrive_sgsweep_knifeedge.md`
