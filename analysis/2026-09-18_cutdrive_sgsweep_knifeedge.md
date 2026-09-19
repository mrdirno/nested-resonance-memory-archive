# The drive cut makes one self-gravity a measurable condition, not a family: sweeping the grid's own self-gravity axis at the cut drive leaves sg 0.3 a knife-edge, and the frozen protocol cannot count a drive sweep as separate conditions at all

Author: Aldrin Payopay · September 18, 2026 · GPL-3.0-only

## Summary

Ring 25 cut the drive (`fieldExp 2 -> 1.7`) and broke the cross-seed seed lock at
`spinchladni sg0.3 gl0`, the first non-static measurable condition in the record.
It closed by proposing a **drive sweep** — `fieldExp 1.6 / 1.7 / 1.8`, "three
measurable conditions in one scoring" — as the path to the first verdict other
than `insufficient support`, because the frozen protocol needs at least three
measurable conditions (F5) and at least six measurable runs (F3).

That path does not exist, and the reason is in the scorer's own code. The frozen
scorer keys a condition on `(preset, selfgrav, gainloss)` only
(`memory_estimator_qualify.py:561`); a drive override is not in the key. A drive
sweep holds preset, self-gravity and gain/loss fixed, so `fieldExp 1.6/1.7/1.8`
at one `(sg, gl)` all collapse to a single condition, which — with nine seeds —
`measure_grid` then skips (it requires exactly three, line 600). Demonstrated on
committed runs, no new computation: a recorded `sg0.3 gl0` run at base drive
(`overrides {}`) and one at the cut drive (`overrides {fieldExp: 1.7}`) both
return the load key `('spinchladni', 0.3, 0.0)`, identical despite the different
drive. **A drive sweep can never be three conditions to this scorer.** Ring 25's
own method note already carried the fact that forecloses its proposal: "the scorer
keys a condition on preset/sg/gl and needs exactly three seeds."

Because F5 counts `(sg, gl)` conditions, the axis that yields three *scoreable*
conditions is self-gravity, swept **at** the cut drive. This note runs that
experiment: the recorded grid's own self-gravity axis `sg ∈ {0, 0.15, 0.3, 0.5,
0.8}` at `gl 0`, all at `fieldExp 1.7`, three grid seeds each — fifteen runs on
the one pinned instrument (`sim_digest 40bfdb68`), scored together. The scorer
loads them as **five distinct conditions** (the sg axis *is* scoreable, unlike the
drive), and the result is:

- **Only `sg0.3` is measurable — one condition of five.** The verdict is
  `insufficient support`: 3 of 15 runs measurable, 1 measurable condition (F5
  needs 3), F3 not evaluable (needs 6 measurable runs); F1, F2, F4 pass. The
  measurable window on the grid's self-gravity axis is a single point.
- **The window is squeezed from both sides, by two different mechanisms.** Below
  `sg0.3` the seed lock breaks but the field cannot participate; above it the
  force cap saturates and the seeds re-lock. `sg0.3` is the knife-edge between.
- **`sg0.3` reproduces Ring 25 exactly on a fresh instrument** — 19/17/17 eligible
  epochs, E3 = 0, detection 2 of 3 (seeds 777 and 31337, not 12345) — a clean
  pipeline check, not a re-implementation.
- **No condition is static.** The unmodified staticness screen flags none (A3
  0.11–0.66, all below the 0.99 line); the failures are seed lock, participation
  and cap saturation, not a frozen field. No Ring 21 collapse confound is present.

**Nothing about nested resonance memory is decided.** What is decided: the drive
cut delivers a measurable condition at one self-gravity, not a family of them, so
the frozen protocol's `qualified`/`not qualified` verdict is not reachable by
widening self-gravity at the cut drive. The successor must generate three
measurable conditions along an axis the scorer keys on — self-gravity or
gain/loss — that all sit inside the participation-vs-cap window, which on this
grid's self-gravity axis is narrower than one grid step.

## The two moves the scorer cannot tell apart, and the one it can

The frozen scorer groups runs into conditions by

```
key = (p['preset'], float(p['selfgrav']), float(p['gainloss']))   # load_grid, line 561
```

with the drive override recorded in `params.overrides` but absent from the key,
`measure_grid` skipping any group that is not exactly three seeds (line 600), and
`main()` reading a single `--input-dir` (line 1293). So:

| swept axis | in the condition key? | scorer sees |
|------------|----------------------|-------------|
| `fieldExp` (drive), fixed `sg,gl` | no | one condition (collapsed; skipped if > 3 seeds) |
| `selfgrav`, fixed drive | yes | one condition per value |

The drive sweep Ring 25 proposed is the first row: unscoreable as three
conditions. This experiment is the second row, and the scorer confirms it by
loading the fifteen runs as `5 conditions`.

## The measured sweep

All at `spinchladni gl0`, `fieldExp 1.7`, 4,194,304 particles, 24 epochs, grid
seeds 777 / 12345 / 31337, one instrument. Eligible epochs are of the 22 the
scorer reads (epochs 3–24); gate-fail counts are per run over those 22; A3 and the
clamp share are from the unmodified staticness screen.

| condition | eligible (per seed) | measurable | E1 mass fails | E2 partic. fails | E3 lock fails | clamp share (A4) | A3 | screen |
|-----------|--------------------:|:----------:|--------------:|-----------------:|--------------:|-----------------:|----:|--------|
| sg0    | 0 / 0 / 0    | 0/3 | 14 | 5–6   | **22** | 0.000 | 0.66 | struck: seed degeneracy (cross-seed 0.999) |
| sg0.15 | 8 / 8 / 8    | 0/3 | 10–12 | 10–12 | 1–2 | 0.013 | 0.24 | PASS (but below the 12-epoch floor) |
| **sg0.3** | **19 / 17 / 17** | **3/3** | 3–4 | 2–5 | **0** | 0.070 | 0.11 | PASS |
| sg0.5  | 1 / 2 / 1    | 0/3 | 0 | **17** | 5–6 | **0.967** | 0.46 | struck: clamp share |
| sg0.8  | 0 / 0 / 2    | 0/3 | 0 | **20** | 14 | **0.999** | 0.66 | struck: clamp share |

`insufficient support`; measurable conditions `['spinchladni_sg0.3_gl0']`;
measurable runs 3 of 15; F1 pass, F2 pass, F3 not evaluable (fewer than six
measurable runs), F4 pass, F5 fail (1 condition, needs 3). Detection fires only
inside `sg0.3` (seeds 777 and 31337), the same two seeds and the same borderline S
as Ring 25 — no memory positive is claimed anywhere in the sweep.

## Why the window has two walls

The chamber's force sums a drive term (a fixed spatial pattern every seed feels
identically), a self-gravity term (which pulls each seed's own particle
distribution into structure) and a force cap. Whether a condition is measurable
turns on the balance of three things the estimator gates on: mass in the scored
blocks (E1), participation across blocks (E2), and cross-seed separation of the
relic template (E3, the seed lock).

- **Below the knife-edge (sg0, sg0.15): the lock breaks but the field will not
  participate.** With no self-gravity the driven field is nearly identical across
  seeds — raw cross-seed correlation 0.999, E3 fails in all 22 epochs, a *total*
  seed lock — and nothing localises, so E1 also fails. Adding a little gravity
  (sg0.15) breaks the lock (E3 fails only 1–2) but the field is still too diffuse:
  E1 and E2 fail in 10–12 epochs and only 8 clear, below the 12-epoch floor. The
  drive cut has done its job on the lock; there is simply not enough self-gravity
  to build a scoreable structure.
- **At the knife-edge (sg0.3): all three clear.** E3 = 0, E1 fails 3–4, E2 fails
  2–5, 17–19 epochs eligible. This is the one balance point.
- **Above the knife-edge (sg0.5, sg0.8): the force cap saturates and the seeds
  re-lock.** The clamp share jumps from 0.070 at sg0.3 to 0.967 at sg0.5 and 0.999
  at sg0.8. A clamped force is not the physical force law but the cap's fixed
  geometry, the same for every seed, so participation collapses (E2 fails 17–20)
  and the seeds re-synchronise (E3 climbs back to 14 at sg0.8). **This is the same
  mechanism that made Ring 25's magnetism raise back-fire** — there the Lorentz
  term saturated the cap; here strong self-gravity does — and it unifies the two:
  more shared clamped forcing, whatever its source, synchronises the seeds.

So the measurable window at the cut drive is bounded below by a participation
floor and above by a cap-saturation ceiling, and on this grid's self-gravity axis
it is narrower than one grid step (0.15 → 0.3 → 0.5 all fall outside; only 0.3 is
in). That is why a self-gravity sweep at the cut drive does not reach F5, and why
the successor's three conditions must be sought inside the window, not across the
whole axis.

## Provenance and grounding

- **One instrument, fifteen runs.** Every run was produced against
  `tests/halo/rc-test.html`, whose behavioural identity `sim_digest` is
  `40bfdb68…` — the Ring 24/25 pin — verified on the working tree, at Ring 25's
  revision `d67ddd16`, and on the test page, all three identical. The source page
  gained only a comment block (Ring 25) since `d67ddd16`; `sim_digest` excludes
  comments and prose. All fifteen recorded the same `test_page_sha256 =
  46405b3d`, made at `git_rev 3bc5799a` (HEAD). Each records `git_dirty = true`,
  which reflects untracked files in the working tree (the results being written,
  and one unrelated artifact) — not a modified instrument: the instrument identity
  is the constant page hash and `sim_digest`, not git cleanliness. Each run records
  its overrides (`fieldExp 1.7`, and the swept `selfgrav`) and reads the applied
  values back off the page.
- **Scorer frozen and unmodified.** `memory_estimator_qualify.py` hashes to
  `7619ef6b…`, the value inside the committed output; the reused synthetic receipt
  (`data/results/halo/memory_estimator_qualification/synthetic.json`) was written
  under that same script sha and protocol sha `e55a53a1…`, both of which the scorer
  verifies before it will run. The staticness screen (`memory_pilot_staticness.py`)
  is unmodified; its A3 < 0.99 gate is applied outside the scorer, stated before
  scoring.
- **Pipeline validated against the record.** The `sg0.3` triple reproduces Ring
  25's committed cut-drive triple exactly — 19/17/17 eligible, E3 = 0,
  measurable 3/3, detection (777 yes, 12345 no, 31337 yes) — so the sweep numbers
  stand on the frozen scorer, not a re-implementation.
- **Inputs sealed; meshes regenerable.** All fifteen run JSON and fifteen
  `*.mesh.f32` are listed in one committed manifest reporting
  `manifest_check.verified = true`. The run JSON are committed; the `*.mesh.f32`
  are gitignored and regenerable by the harness.

## Falsifiers and what would change the reading

- If the fifteen runs were not one instrument, "measurable window across
  self-gravity" would confound instrument with condition. All fifteen share the
  test-page hash and `sim_digest 40bfdb68`.
- If some condition were static, its (non-)measurability would be the Ring 21
  collapse confound. None is: the staticness screen flags no condition (A3
  0.11–0.66), so the failures are participation and cap saturation, not a frozen
  field.
- If `sg0.15`'s failure were the seed lock rather than participation, the drive
  cut would not generalise below `sg0.3`. It is not: E3 fails only 1–2 there; the
  binding gates are E1 and E2, and the shortfall is 8 eligible against a 12 floor.
- If `sg0.5`/`sg0.8`'s failure were a coincidence rather than cap saturation, the
  clamp share would not track it. It does: 0.070 → 0.967 → 0.999 as self-gravity
  rises, and E2 collapses in lockstep.
- If a drive sweep could be scored as three conditions after all, the retire would
  be wrong. It cannot: the load key omits the drive override, shown on committed
  runs to collapse base and cut drive to one key.

## Files

- Runs (committed JSON; `*.mesh.f32` gitignored, regenerable):
  `data/results/halo/memory_cutdrive_sgsweep/spinchladni_sg{0,0.15,0.3,0.5,0.8}_gl0_seed*_n4194304_e24_fieldExp1.7.json`
- Sealed manifest + scored output + staticness (committed):
  `data/results/halo/memory_cutdrive_sgsweep/{manifest,qualification,staticness}.json`
- Frozen scorer (untouched, sha 7619ef6b): `experiments/halo/memory_estimator_qualify.py`
- Staticness screen (unmodified): `experiments/halo/memory_pilot_staticness.py`
- Run harness (override flags): `tests/halo/memory_prereg_run.js`
- Ring 25 (the question this answers and corrects): `analysis/2026-09-18_drivecut_breaks_seedlock.md`
