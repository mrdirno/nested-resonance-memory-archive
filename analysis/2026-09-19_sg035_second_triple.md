# sg0.35's 2-of-3 at the cut drive was realisation variance, not a ceiling: the pre-registered second triple is 3-of-3, giving two countable conditions, six of six measurable runs, and F3 assessable and passing for the first time — the verdict staying "insufficient support" only because F5 needs a third condition

Author: Aldrin Payopay · September 19, 2026 · GPL-3.0-only

## Summary

Ring 27 ran a finer self-gravity grid (`sg ∈ {0.25, 0.3, 0.35}`) at the cut drive
(`fieldExp 1.7`, `gl0`) on the grid seeds 777/12345/31337 and found `sg0.35`
measurable **2 of 3**: seeds 777 and 31337 cleared the 12-epoch floor (15 and 17
eligible), seed 12345 landed at 11 — one epoch short, on participation variance
(E2 = 10), **not** cap saturation (clamp share 0.074, the same as `sg0.3`). It
left open its first question: **is `sg0.35`'s 2/3 realisation variance or a
ceiling?** and pre-registered the test — a second triple at `sg0.35` on the
transcendental-digit seeds **2718 / 16180 / 57721** (e, φ, and the
Euler–Mascheroni constant γ), the set Rings 24/25 used — with the payoff spelled
out: if it makes `sg0.35` 3/3, two conditions are countable, ≥ 6 measurable runs
make F3 assessable, and a third condition inside the window would reach the three
F5 needs.

This ring runs exactly that pre-registered second triple and scores it beside the
reused `sg0.3` triple (777/12345/31337, hash-verified against Ring 27's manifest)
— two conditions, three seeds each, six runs on the one pinned instrument
(`sim_digest 40bfdb68`, `test_page 1a15b987`), on the frozen scorer
(`sha 7619ef6b`). The answer is unambiguous:

- **The second triple is measurable 3 of 3.** All three pre-registered seeds
  clear the 12-epoch floor comfortably — **16 / 17 / 16 eligible epochs** (Ring
  27's grid triple was 15 / 11 / 17, with 12345 one short). So the 2/3 was
  realisation variance in one seed, not a structural ceiling: a different,
  pre-committed seed set puts all three above the floor.
- **Two countable conditions, six of six measurable runs.** With `sg0.3` also 3/3
  (19/17/17, reproducing Rings 25/26/27 exactly), `cond_meas = {sg0.3, sg0.35}` —
  **two** measurable conditions, up from Ring 27's one — and **6 of 6 runs
  measurable**, up from 5 of 9. The only new measurements are the three `sg0.35`
  runs; the `sg0.3` triple is reused bytes (hash-identical to Ring 27), so it is
  the pipeline's determinism check, not independent corroboration.
- **F3 recovery is assessable for the first time in the programme, and passes.**
  The frozen protocol needs ≥ 6 measurable runs before F3 is evaluable
  (`F3_MIN_RUNS = 6`); every prior scoring stopped at ≤ 5 and returned "fewer than
  6 measurable runs". Here `len(measurable) = 6` (three reused `sg0.3` + three
  pre-registered `sg0.35`), so F3 becomes **assessable** and its median effective
  threshold (`α*_eff` median 0.017, well under the 0.10 fail line, 0 runs
  unrecovered) makes it **pass**.
- **The verdict stays "insufficient support" — and that is a structural fact, not
  a falsifier firing.** The result cascade checks F5 first
  (`memory_estimator_qualify.py:833`: `if not f5['pass']: result =
  'insufficient support'`), and F5 needs three measurable conditions
  (`len(cond_meas) >= 3`). With two, the verdict is fixed before F3 is consulted.
  F3 becoming assessable-and-passing changes the `F3_recovery` sub-field, **not**
  `verdict.result`.
- **No memory result is claimed.** Detection fires in 3 of 6 runs (`sg0.35` seed
  2718; `sg0.3` seeds 777 and 31337) — sparse and **not reproduced within any
  single condition** (`sg0.3` 2/3, `sg0.35` 1/3); the two `sg0.3` detections are
  reused Ring 27 bytes, and the new triple's own detection is 1 of 3, the weakest
  non-zero. No condition is static (per-run A3 0.04–0.11, the screen flags none),
  so this is not the Ring 21 collapse confound.

**Nothing about nested resonance memory is decided.** What is measured: the cut
drive's measurable self-gravity window has a genuine second point — `sg0.35` is a
countable condition on a pre-registered second triple, not the knife-edge Ring 26
saw nor the one-seed-short 2/3 Ring 27 saw — and this is the first time the frozen
protocol reaches six measurable runs, two conditions, and an assessable, passing
F3. The one thing still missing for a verdict other than "insufficient support" is
a **third** measurable condition (F5). The most direct next step is a third point
inside the window — `sg0.32` at the cut drive on the same instrument — which, if
also 3/3, makes `cond_meas = 3` and, with F1–F4 already passing, would let the
frozen protocol return "qualified" (the *estimator* qualifying as able to measure
— still not a memory positive) for the first time.

## The measured grid

All at `spinchladni gl0`, `fieldExp 1.7`, 4,194,304 particles, 24 epochs, one
instrument. Eligible epochs are of the 22 the scorer reads (epochs 3–24); the E1
(mass) / E2 (participation) / E3 (seed-lock) gate-fail counts are per run over
those 22. The `A3` column is the staticness screen's per-condition value — the
**most-static seed's** median epoch-to-epoch full-field density correlation (the
maximum over the triple); the median across a triple's three seeds is lower
(`sg0.35` 0.063, `sg0.3` 0.067), both far below the 0.99 static line. `clamp` is
the median clamp share across the triple.

| condition | seeds | eligible | measurable | E1 fails | E2 fails | E3 fails | clamp | A3 (worst seed) | detection |
|-----------|-------|---------:|:----------:|---------:|---------:|---------:|------:|----:|-----------|
| **sg0.35** (pre-registered) | 2718 / 16180 / 57721 | **16 / 17 / 16** | **3/3** | 1 / 1 / 1 | 6 / 4 / 5 | 0 / 0 / 0 | 0.087 | 0.073 | 2718 only (1/3) |
| **sg0.3** (reused, verified) | 777 / 12345 / 31337 | 19 / 17 / 17 | 3/3 | 3 / 4 / 3 | 2 / 3 / 5 | 0 / 0 / 0 | 0.070 | 0.113 | 777, 31337 (2/3) |

Verdict `insufficient support`. Measurable conditions `['spinchladni_sg0.3_gl0',
'spinchladni_sg0.35_gl0']` (2, needs 3 for F5); measurable runs 6 of 6; F1 pass,
F2 pass, **F3 evaluable and pass (median α*_eff 0.017 ≤ 0.10, 6 runs, 0
unrecovered)**, F4 pass, **F5 fail (2 conditions)**. Detection 3 of 6, not
reproduced within a condition. No memory positive is claimed.

## Why the second triple clears where Ring 27's one seed did not

Across `sg0.3` and `sg0.35` at the cut drive the seed lock is broken everywhere
(E3 = 0 in all six runs — the drive cut's job). What separates a measurable run
from a floor-miss is participation (E2) over enough epochs.

- **`sg0.35`'s three pre-registered seeds all clear the floor (16/17/16).** Mass
  is strong (E1 fails only 1 per seed — lower than `sg0.3`'s 3–4, because more
  self-gravity builds more mass); participation varies seed to seed (E2 fails
  4–6), but none of the three falls to the 12-epoch floor. Ring 27's grid triple
  missed on one seed (12345 at 11 eligible, E2 = 10); the pre-registered triple
  does not — the shortfall was that seed, not `sg0.35`.
- **The field is not cap-saturated.** Clamp share 0.087, close to `sg0.3`'s 0.070
  and far from the saturation that closes the window by `sg0.5` (Ring 26: clamp
  0.967). A3 0.073, a clean moving field. So `sg0.35` sits inside the window's
  upward width, exactly as Ring 27's exploratory 2/3 suggested and this
  pre-registered triple now confirms at 3/3.
- **`sg0.3` reproduces the record.** The reused triple scores 19/17/17, E3 = 0,
  3/3 measurable, detection 777/31337 — identical to Rings 25/26/27, which is the
  determinism check on the whole pipeline: same seed + same instrument → same
  mesh → same score.

## What moved, and what did not

| number | Ring 26 | Ring 27 | Ring 28 |
|--------|:-------:|:-------:|:-------:|
| measurable runs | 3 of 15 | 5 of 9 | **6 of 6** |
| measurable conditions | 1 | 1 | **2** |
| F3 recovery | not evaluable | not evaluable | **evaluable, pass** |
| F5 support | fail (1) | fail (1) | fail (2) |
| verdict | insufficient support | insufficient support | insufficient support |
| memory claim | none | none | none |

The verdict has not moved and will not until a third condition is measurable. What
moved is everything F5 gates in front of: the measurable-run count crossed the
F3 threshold, and the condition count doubled.

## Provenance and grounding

- **One instrument, six runs.** Each run records `test_page_sha256` `1a15b987…`;
  the working tree's `tests/halo/rc-test.html` hashes to `sim_digest 40bfdb68…`
  (`core_digest 50f1e370…`, `tick_digest f887b63f…`) — the Ring 24/25/26/27 pin.
  Each run records `git_dirty = true`, which is untracked files in the tree (the
  results being written), not a modified instrument.
- **Three runs generated this cycle, three reused after verification.** The
  `sg0.35` triple (seeds 2718/16180/57721) was generated this cycle (121–131 s each,
  `pageerrors []`, full 3,145,728-byte meshes) on the pinned instrument. The
  `sg0.3` triple (777/12345/31337) was copied from Ring 27's
  `memory_finegrain_sgsweep` after its six JSON+mesh sha256 were verified against
  that manifest; reuse rests on the chamber being deterministic for a fixed seed
  and page, and the `sg0.3` reproduction (19/17/17, detection 777/31337) is that
  check.
- **Pre-registered seeds, not a post-hoc draw.** 2718/16180/57721 are e, φ and the
  Euler–Mascheroni constant γ; they were named in Ring 27's open question ("as
  Rings 24/25 used") **before** this run, and are the same second-triple family
  used at `sg0.3` in the Ring 25 drive-cut work — a pre-committed second
  realisation, distinct from the grid seeds, not an independent random draw
  dressed up as one.
- **Scorer and screen frozen and unmodified.** `memory_estimator_qualify.py`
  hashes to `7619ef6b…`; the reused synthetic receipt carries `script_sha256`
  `7619ef6b…` and `protocol_sha256` `e55a53a1…`, both verified before the scorer
  runs; the scorer's manifest check re-hashed all twelve files and set
  `verdict.inputs_verified = true`. The staticness screen and manifest builder are
  unmodified.
- **Inputs sealed; meshes regenerable.** All six run JSON, the manifest,
  qualification and staticness JSON are committed; the six `*.mesh.f32` are
  gitignored and regenerable by the harness.

## Falsifiers and what would change the reading

- If some condition were static, its (non-)measurability would be the Ring 21
  collapse confound. None is: A3 0.05–0.11, the screen flags none.
- If `sg0.35`'s 3/3 were cap saturation, the clamp share would be high. It is
  0.087, close to `sg0.3`'s 0.070; `sg0.5` was 0.967.
- If the second triple had drifted from `sg0.3`'s recorded behaviour, the pipeline
  would be suspect. The reused `sg0.3` reproduces the record exactly (19/17/17,
  E3 = 0, detection 777/31337).
- If the six runs were not one instrument, "two conditions across self-gravity"
  would confound instrument with condition. All six share `test_page 1a15b987` and
  the tree's `sim_digest 40bfdb68`.
- If F3 being evaluable-and-passing changed the verdict, "insufficient support"
  would be wrong. It does not: F5 gates the result first (`:833`), and with two
  conditions F5 fails before F3 is read.
- If the seeds had been chosen after seeing the result, the 3/3 would be a
  cherry-pick. They were named in Ring 27's public open question before this run.

## Files

- Runs (committed JSON; `*.mesh.f32` gitignored, regenerable):
  `data/results/halo/memory_sg035_triple2/spinchladni_sg0.35_gl0_seed{2718,16180,57721}_n4194304_e24_fieldExp1.7.json`
  and the reused `spinchladni_sg0.3_gl0_seed{777,12345,31337}_…`
- Sealed manifest + scored output + staticness (committed):
  `data/results/halo/memory_sg035_triple2/{manifest,qualification,staticness}.json`
- Frozen scorer (untouched, sha 7619ef6b): `experiments/halo/memory_estimator_qualify.py`
- Run harness: `tests/halo/memory_prereg_run.js`
- Ring 27 (the question this answers): `analysis/2026-09-19_finegrain_sgsweep_window_width.md`
