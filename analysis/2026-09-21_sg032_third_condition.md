# Ring 29 pre-registration and result: a third condition inside the measurable self-gravity window at the cut drive — `sg0.32`, two pre-committed triples, on the Ring 24–28 instrument

Author: Aldrin Payopay · September 21, 2026 · GPL-3.0-only

**Status of this block: pre-registration, committed and pushed before any `sg0.32`
run of this ring existed.** Everything above the heading "## Results" is fixed at
that commit and is not edited afterwards; the results are appended in a later
commit.

## What is being asked, and why now

Ring 28 (`analysis/2026-09-19_sg035_second_triple.md`) left two countable conditions
at the cut drive (`spinchladni`, `fieldExp 1.7`, `gl0`): `sg0.3` on seeds
777/12345/31337 (19/17/17 eligible epochs) and `sg0.35` on seeds 2718/16180/57721
(16/17/16), six of six runs measurable, F1–F4 passing, F3 evaluable for the first
time. The verdict stayed "insufficient support" for one structural reason: the frozen
protocol's F5 needs **three** measurable conditions and the result cascade checks F5
first (`experiments/halo/memory_estimator_qualify.py:833`). Ring 28's open question 1
named the test — **`sg0.32` at the cut drive on the same instrument** — and the
payoff: if it is also 3/3, `cond_meas = 3`, F5 passes, and with F1–F4 passing the
cascade returns the protocol's first **"qualified"**. Ring 28 named the self-gravity
value and **not the seeds**. This block fixes the seeds, the directories, the
commands, the order and the decision rule before the first run.

## The instrument, verified on the tree before this commit

- `tests/halo/rc-test.html` whole-file sha256 `1a15b987…`; `sim_digest 40bfdb68…`
  (`core 50f1e370…`, `tick f887b63f…`) from `experiments/halo/instrument_identity.py`,
  re-run on the tree, not quoted from memory. `git diff 6560d802 HEAD` on `tests/halo`,
  `experiments/halo`, `docs/halo` and the source page is empty apart from this cycle's
  `tests/halo/smoke.js` change (a CI test, not an instrument file, commit `2571e9bb`).
- **One instrument-block value will differ from Ring 28's records, and is declared
  here so it is not read as drift:** `source_page_sha256` will be `cf3fd0f4…` (Ring 28
  recorded `cd80d357…`, Ring 27 `2a1cf94a…`) because commit `6560d802` appended the
  RING 28 comment block to the source page — 59 inserted lines, none of them code or
  GLSL — under the one unchanged `sim_digest`. `test_page_sha256 1a15b987`, harness
  `e0bc8f6b…`, builder `c3a7f5dc…`, `three.min.js 9274bbce…` must all match Ring 28's
  records exactly; `git_dirty` will be `true` (the untracked result files), as in every
  prior ring. `tests/halo/rc-test.html` is not rebuilt at any point in this cycle.
- **Pre-flight, measured before this commit (not only traced in source):** `sg0.32` is the
  first self-gravity value off the page's 0.05 slider grid that the harness has driven.
  The page's only transform of `cosmos.selfgrav` is a clamp to [0, 2]; the slider's
  `step=0.05` is display-only and nothing reads it back. A headless run of the pinned
  test page at 65,536 particles, applying the preset with `selfgrav 0.32`, read back
  `state.cosmos.selfgrav = 0.32`, GPU uniform `uSelfGrav = 0.32`, slider display "0.3",
  no page errors. So a screenshot of the slider reading 0.30 is not evidence against
  the record; the run record's `applied.cosmos.selfgrav` (read from page state) and
  the lab CSV's `selfgrav` column are, and both must read 0.32 in every new run.
- **Instrument identity across all nine records of an arm is asserted on
  `test_page_sha256 = 1a15b987…` and `sim_digest = 40bfdb68…`, never on
  `source_page_sha256`**, which the comment-only append moves.
- **Scorer, frozen and unmodified:** `experiments/halo/memory_estimator_qualify.py`
  sha256 `7619ef6b…`; protocol `docs/halo/2026-09-05_memory_estimator_qualification_protocol.md`
  sha256 `e55a53a1…`; synthetic receipt
  `data/results/halo/memory_estimator_qualification/synthetic.json` (file sha `8670e193…`,
  written 2026-09-06 under script `7619ef6b` / protocol `e55a53a1`). HEAD holds both
  frozen files byte-identical, so the scorer's own `commit_holds_protocol` check will
  pass. Staticness screen `memory_pilot_staticness.py` (`a0ce66d9…`) and manifest
  builder `memory_pilot_manifest.py` (`efe57aba…`) unmodified.

## The experiment, fixed

**Condition.** `spinchladni`, `selfgrav 0.32`, `gainloss 0`, `fieldExp 1.7`,
4,194,304 particles, 24 epochs of 10 s, tick budget 10, step 9028 — every other
coordinate the preset's own, exactly as the `sg0.3` and `sg0.35` triples were run.
The harness installs the seeded generator before the preset is applied and
self-gravity enters only through `st.cosmos.selfgrav`, so a seed fixes the same
initial positions at every self-gravity value (protocol §2 states the same for the
recorded grid): the design is **seed-paired across conditions**.

**Two arms, both run, in this order, whatever the first shows.**

- **Arm 1 — PRIMARY, verdict-bearing.** `sg0.32` on seeds **777 / 12345 / 31337**,
  run in that order. These are the protocol's §2 seeds, the seeds of the reused
  `sg0.3` triple, and the seeds of Ring 27's whole fine grid, so the third condition is
  measured on the same initial positions as the first. Directory
  `data/results/halo/memory_sg032_third/`.
- **Arm 2 — SECONDARY, a pre-committed second realisation of the same condition.**
  `sg0.32` on seeds **2718 / 16180 / 57721** (e, φ, Euler–Mascheroni γ; the
  second-triple family of Rings 24/25/28 and the seeds of the reused `sg0.35` triple),
  run in that order, after Arm 1's three, **unconditionally** — not contingent on Arm
  1's result. Directory `data/results/halo/memory_sg032_third_r2/`.

Neither family has a uniformly better record inside the window: on the record the
grid seeds went 3/3 at `sg0.3` (19/17/17) and 2/3 at `sg0.35` (15/11/17, Ring 27); the
transcendental seeds went 2/3 at `sg0.3` (13/12/10, Ring 25) and 3/3 at `sg0.35`
(16/17/16, Ring 28). The choice of primary is therefore a **declared convention**, not
a selection, and it is fixed here before any `sg0.32` run exists.

**Each arm's directory holds exactly nine runs:** its own three new `sg0.32` runs plus
the twelve files below (the `sg0.3` and `sg0.35` triples, JSON + mesh), which are byte
copies of the files sealed in commit `6560d802` and were staged into both directories
on 2026-09-20 23:50 local, before this commit — a stranger reading modification times
should read those twelve as copies, and can check them by hash. No file is moved
between the two directories; no seed is added, dropped or swapped; no `sg0.32` triple
is composed from both families. The reused triples are the pipeline's determinism
check (expected 19/17/17 and 16/17/16 eligible, detection in 777, 31337 and 2718), not
new evidence, and every count in the ring separates new runs (six) from reused ones.

| reused file (byte copy of commit 6560d802, `data/results/halo/memory_sg035_triple2/`) | sha256 (first 16) | bytes |
|---|---|---:|
| `spinchladni_sg0.35_gl0_seed16180_n4194304_e24_fieldExp1.7.json` | `2a1ea605ca093549` | 55,115 |
| `spinchladni_sg0.35_gl0_seed16180_n4194304_e24_fieldExp1.7.mesh.f32` | `84e69ab7ac4d5ed4` | 3,145,728 |
| `spinchladni_sg0.35_gl0_seed2718_n4194304_e24_fieldExp1.7.json` | `779e9737c653f0eb` | 55,403 |
| `spinchladni_sg0.35_gl0_seed2718_n4194304_e24_fieldExp1.7.mesh.f32` | `fbac35aafb0112b5` | 3,145,728 |
| `spinchladni_sg0.35_gl0_seed57721_n4194304_e24_fieldExp1.7.json` | `2a550e882de4937f` | 55,225 |
| `spinchladni_sg0.35_gl0_seed57721_n4194304_e24_fieldExp1.7.mesh.f32` | `cd196ff8d54c0043` | 3,145,728 |
| `spinchladni_sg0.3_gl0_seed12345_n4194304_e24_fieldExp1.7.json` | `8a62c9fea46c7fc4` | 54,668 |
| `spinchladni_sg0.3_gl0_seed12345_n4194304_e24_fieldExp1.7.mesh.f32` | `bbe6c90acba2454a` | 3,145,728 |
| `spinchladni_sg0.3_gl0_seed31337_n4194304_e24_fieldExp1.7.json` | `48086dbc7cd6b2c4` | 54,737 |
| `spinchladni_sg0.3_gl0_seed31337_n4194304_e24_fieldExp1.7.mesh.f32` | `4ac2b599807f24d3` | 3,145,728 |
| `spinchladni_sg0.3_gl0_seed777_n4194304_e24_fieldExp1.7.json` | `365b170b424951c5` | 54,558 |
| `spinchladni_sg0.3_gl0_seed777_n4194304_e24_fieldExp1.7.mesh.f32` | `632599c214f21075` | 3,145,728 |

**Commands, one per run, in run order** (defaults left implicit are the harness's:
`--n=4194304 --epochs=24 --epochlen=10 --budget=10 --step=9028`; expected tag
`spinchladni_sg0.32_gl0_seed<S>_n4194304_e24_fieldExp1.7`, expected wall time about
120 s, `pageerrors []`; a run that logs a page or console error voids the arm under
protocol §7 gate 4 and the driver stops on the first one):

```
node tests/halo/memory_prereg_run.js --preset=spinchladni --sg=0.32 --gl=0 --seed=777   --fieldexp=1.7 --out=data/results/halo/memory_sg032_third
node tests/halo/memory_prereg_run.js --preset=spinchladni --sg=0.32 --gl=0 --seed=12345 --fieldexp=1.7 --out=data/results/halo/memory_sg032_third
node tests/halo/memory_prereg_run.js --preset=spinchladni --sg=0.32 --gl=0 --seed=31337 --fieldexp=1.7 --out=data/results/halo/memory_sg032_third
node tests/halo/memory_prereg_run.js --preset=spinchladni --sg=0.32 --gl=0 --seed=2718  --fieldexp=1.7 --out=data/results/halo/memory_sg032_third_r2
node tests/halo/memory_prereg_run.js --preset=spinchladni --sg=0.32 --gl=0 --seed=16180 --fieldexp=1.7 --out=data/results/halo/memory_sg032_third_r2
node tests/halo/memory_prereg_run.js --preset=spinchladni --sg=0.32 --gl=0 --seed=57721 --fieldexp=1.7 --out=data/results/halo/memory_sg032_third_r2
```

**Scoring, per arm, in this order, in that arm's directory:**

```
python3 experiments/halo/memory_pilot_manifest.py   DIR DIR/manifest.json
python3 experiments/halo/memory_pilot_staticness.py DIR --json DIR/staticness.json
python3 experiments/halo/memory_estimator_qualify.py --input-dir DIR --manifest DIR/manifest.json \
        --synthetic-json data/results/halo/memory_estimator_qualification/synthetic.json --output DIR/qualification.json
```

Expected of each arm's output: `manifest.runs = 9`, `not_manifested = []`, the twelve
reused hashes above reappearing unchanged; `qualification.inputs.runs = 9`,
`inputs.conditions = 3`, eighteen input files, `verdict.inputs_verified = true`;
`F5.measurable_conditions` listing whichever of `spinchladni_sg0.3_gl0`,
`spinchladni_sg0.32_gl0`, `spinchladni_sg0.35_gl0` are 3/3.

## Decision rule, fixed before the runs

**The verdict of this ring is Arm 1's `verdict.result`, copied verbatim, under every
outcome.** Arm 2's `verdict.result` and per-run table are reported beside it as the
replication of the third condition and are never substituted, averaged or used to
break a tie. The frozen cascade returns one of five strings; each is pre-read here:

1. **"qualified"** (Arm 1 `sg0.32` 3/3 → `cond_meas = 3`, inputs verified, F1–F3
   evaluable, F1–F4 pass): **the frozen estimator is qualified as able to measure on
   three generated conditions — `spinchladni gl0` at the cut drive `fieldExp 1.7`,
   self-gravity 0.3 / 0.32 / 0.35 (three points spanning 0.05 of one axis), 4,194,304
   particles, 24 epochs of 10 s, one instrument (`sim_digest 40bfdb68`)** — and says
   nothing about any other preset, drive, gain/loss, particle count or instrument, and
   nothing about nested resonance memory (protocol §1: "a pass does not establish
   memory"). The ring's first sentence will say so. Its decomposition is also fixed
   here so the word cannot inflate: F1 is a check that cannot fail short of a defective
   implementation; F2 is decided **only** by the 2026-09-06 synthetic receipt and is not
   a statement about these fields; F3's nine-run median of `α*_eff` is bounded at or
   below 0.0383 by the six reused runs (whose values are 0.016–0.039) whatever the
   three new runs yield, so F3 can fail only through an unrecovered run whose template
   correlation is below 0.5; so "qualified" here reduces to **F5 (the third condition
   3/3) plus F4 band stability on nine runs plus manifest verification**. Detection is
   reported as a count over distinct runs and per condition, and is called reproduced
   within a condition only if it is.
2. **"not qualified"** (3/3, but F1, F3 or F4 fails): the third condition is
   countable and a falsifier fired — **a final negative for the estimator at three
   conditions under this protocol version**, reported as such, with no rerun, re-seed
   or Arm 2 substitution. The ring names which falsifier — F1 radialised or Plummer
   fields yielding eligible epochs; F3 an unrecovered run with template correlation
   below 0.5; F4 more than `max(1, ⌈0.05 × n_both⌉) = 1` violation in a variant (the
   allowance does not grow until 21 runs are measurable under both, so nine runs carry
   more band exposure at the same allowance), or an F3 verdict that disagrees between
   main and variant — and the number that fired it. Ring 27's nine-run fine grid
   already spent that whole allowance in two variants (one weak violation each), so
   this branch is live. F4 is reported per variant with `measurable_both`, the
   violations found and the F3 main-versus-variant pair; a variant with
   `measurable_both = 0` (Ring 28's `e2_pr16`) is reported as vacuous, not as passing,
   and a variant whose F3 sub-check has fewer than six runs is reported as not
   evaluable there. Nothing is softened.
3. **"insufficient support"** (Arm 1 `sg0.32` fewer than 3/3): `cond_meas` stays 2
   and the reading is that the window's interior is not uniformly measurable on the
   grid seeds; Arm 2 says whether that is realisation variance.
4. **"not evaluable"** (F5 passes but F1, F2 or F3 cannot be evaluated) and
   **"inputs unverified"** (a manifest mismatch): reported as such; the cause is named;
   no rerun is scored in this ring.

If the arms **disagree** on `sg0.32` measurability or on `verdict.result`, both are
reported in full, the statement is "`sg0.32` measurable in *k* of 2 pre-committed
triples", and the disagreement is the finding — it is not resolved by choosing. Any
statement about realisation variance is triple-level and descriptive only: *k* of the
six triples now on the record at the cut drive are 3/3; two triples per condition; the
six runs of a condition are not independent draws (the seeds fix initial positions,
and the conditions share them seed by seed); no standard deviation, p-value or chance
fraction is estimated (the "six independent draws" error Ring 18 retired).

Also fixed: no re-choosing the self-gravity value after the runs; no pooling of the two
arms into one six-seed condition (the scorer needs exactly three seeds per
`(preset, sg, gl)` key and skips any other group); no rerun of the `sg0.35` grid
triple "to give seed 12345 another chance" (the chamber is bit-deterministic per seed
and page, so it returns 11 eligible again); no memory claim from detection counts at
any outcome.

**Detection, pre-read.** Arm 1 shares its seeds, and therefore its initial positions,
with the reused `sg0.3` triple, and Arm 2 with the reused `sg0.35` triple. If `sg0.32`
detects the same seeds `sg0.3` detected (777 and 31337), that is read as
**seed-specific persistent structure** — the confound protocol §1 names, which "needs a
registered intervention, not a correlation" to separate from memory — and **not** as
reproduction of memory. Every detected run is reported with its mapped and unmapped
contrasts, `p`, the bootstrap interval and the autocorrelation flag; the only
informative direction is a mapped contrast clearly above the unmapped one (protocol §5).
Counts are never converted to a rate or compared with F2's 5 % bound. One reported,
unscored diagnostic is added: for each seed shared between `sg0.3` and `sg0.32`, the
per-epoch full-field Pearson correlation between the two conditions' meshes at the
same epoch (median over the scored epochs), beside the cross-seed same-condition
baseline — computed by an independent script, reported as numbers only.

**One ambiguity, named once.** Protocol §8 lists the result strings "in that order of
precedence" (qualified first); the frozen script's cascade checks F5 first, so a
directory that fails F5 and F4 at once is labelled "insufficient support" by the code
where the literal prose would say "not qualified". The protocol text cannot be edited
mid-programme without invalidating the synthetic receipt, so — as Ring 28 did — the
frozen script is operative, every F sub-field is reported regardless of
`verdict.result`, and in any F5-fail case where F4 also fails the F4 failure leads.

**The two arms are coupled.** They share six of their nine runs, F2 is identical by
receipt, and F3's median is dominated by the shared six; two "qualified" strings would
not be two qualifications. Arm 1 is the headline; Arm 2 is reported as "the second
seed family at `sg0.32` was / was not 3/3 measurable, and its directory returned
<verdict>".

**The next step is fixed for the pass branch.** If the estimator qualifies, the
successor is a **registered intervention** on the qualified support (protocol §1) —
for example a pre-registered relic-scramble or relic-swap arm — not another
correlation, another point in the window, or a memory claim.

## How a stranger checks the order

The run records carry no wall clock. The order is evidenced by, in decreasing
strength: (1) this commit, **P**, pushed to the public remote before any `sg0.32` run
existed, and every new run's `instrument.git_rev` being P or a descendant of it — the
results section prints the six `git_rev` values and the result of
`git merge-base --is-ancestor P <git_rev>` for each, and a run whose `git_rev` does
not descend from P is discarded and regenerated, not scored (Ring 28 has this
precedent: its three new runs record `git_rev da5766df`, a descendant of Ring 27's
commit `fbf45bd9` that named their seeds); (2) each `qualification.json`'s
`protocol_commit`, which the scorer requires to hold the frozen protocol and script;
(3) `measured_at` in each `qualification.json` and the run files' modification times,
which are local clocks and corroboration only.

## Results

**Scored once, on 2026-09-22, in the pre-registered order, without editing anything
above this heading.** The six `sg0.32` runs were generated on 2026-09-21 (file times
00:05–00:13 local, two minutes after commit P `556f017b` at 00:03:44) by a session that
ended before scoring them. This ring re-verified those files and scored them; nothing was
regenerated, re-seeded, moved or substituted.

### Order and instrument, checked before scoring

| check | Arm 1 (777 / 12345 / 31337) | Arm 2 (2718 / 16180 / 57721) |
|---|---|---|
| `instrument.git_rev` of each new run | `556f017b` × 3 (= P) | `556f017b` × 3 (= P) |
| `git merge-base --is-ancestor 556f017b <git_rev>` | rc 0 × 3 | rc 0 × 3 |
| `applied.cosmos.selfgrav` | 0.32 × 3 | 0.32 × 3 |
| `pageerrors` | `[]` × 3 | `[]` × 3 |
| `test_page_sha256` / `source_page_sha256` | `1a15b987` / `cf3fd0f4` (as declared) | same |
| harness / builder / three.min.js | `e0bc8f6b` / `c3a7f5dc` / `9274bbce` | same |
| browser / driver / node / renderer | 151.0.7922.34 / Playwright 1.62.1 / v24.4.1 / ANGLE Metal, Apple M4 Pro — identical to the six reused runs' records | same |
| wall time per run | 93 / 87 / 88 s | 90 / 88 / 89 s (reused runs: 112–131 s) |
| twelve reused files vs the table above and commit `6560d802` | 12 of 12 byte-identical | 12 of 12 byte-identical |
| `instrument.git_dirty` | `true` × 3 (untracked result files on the shared tree; the pin is `test_page_sha256` 1a15b987 and `sim_digest` 40bfdb68, not git cleanliness) | same |
| `sim_digest` recomputed on the tree (`instrument_identity.py`) | `40bfdb68` on both `tests/halo/rc-test.html` and the source page (core `50f1e370`, tick `f887b63f`) | same |
| `git diff 6560d802 HEAD` on `tests/halo`, `experiments/halo`, `docs/halo`, source page | only `tests/halo/smoke.js` (the declared CI-test change) | same |
| frozen files (scorer / protocol / receipt / staticness / manifest) | `7619ef6b` / `e55a53a1` / `8670e193` / `a0ce66d9` / `efe57aba` — all as declared | same |

**Regeneration check (not scored, not committed):** seed 777 at `sg0.32` was regenerated
on 2026-09-22 from the tree into a scratch directory. Its mesh is byte-identical to the
2026-09-21 file (`ce15f081…`, 3,145,728 bytes) and every data field of its JSON is equal
(`applied`, `params`, `epochs`, `csv_rows`, `caps_end`, `mesh_count`); only
`instrument.git_rev` (now `41fe0685`, a descendant of P), `instrument.source_page_sha256`
once the Ring 29 comment block is on the page (`sim_digest` unchanged) and `wall_seconds`
(116 vs 93) differ. The shorter wall time of the 2026-09-21 runs is host throughput, and the bytes do
not depend on it.

### Arm 1 — PRIMARY, verdict-bearing: `sg0.32` on 777 / 12345 / 31337

`manifest.runs = 9`, `not_manifested = []`; `qualification.inputs.runs = 9`,
`inputs.conditions = 3`, 18 input files, `verdict.inputs_verified = true`;
`protocol_commit 41fe0685` (HEAD at scoring, holding the frozen protocol and script);
`measured_at 2026-09-22T16:52:00Z`.

**`verdict.result` = "qualified".**

| run | eligible | measurable | detected | S (own) | p | CI95 (block bootstrap) | lag-1 Q | caveat | contrasts detected | gates failed (e1/e2/e3/e4) |
|---|---:|---|---|---:|---:|---|---:|---|---|---|
| sg0.32 seed 777 | 16 | yes | **yes** | 0.0331 | 0.0040 | [0.0065, 0.0524] | 0.080 | no | additive_only | 2/5/0/0 |
| sg0.32 seed 12345 | 14 | yes | no | −0.0108 | 0.661 | [−0.0517, 0.0071] | −0.052 | no | — | 2/7/0/0 |
| sg0.32 seed 31337 | 14 | yes | no | 0.0094 | 0.384 | [−0.0007, 0.0237] | −0.144 | no | — | 1/8/0/0 |
| sg0.3 seed 777 (reused) | 19 | yes | yes | 0.0422 | 0.0225 | [−0.0010, 0.0840] | 0.428 | **yes** | no_removal | 3/2/0/0 |
| sg0.3 seed 12345 (reused) | 17 | yes | no | 0.0057 | 0.096 | [−0.0113, 0.0341] | 0.200 | no | — | 4/3/0/0 |
| sg0.3 seed 31337 (reused) | 17 | yes | yes | 0.0354 | 0.0020 | [0.0132, 0.0570] | −0.187 | no | all four | 3/5/0/0 |
| sg0.35 seed 2718 (reused) | 16 | yes | yes | 0.0694 | 0.0007 | [0.0333, 0.1142] | 0.244 | no | all four | 1/6/0/0 |
| sg0.35 seed 16180 (reused) | 17 | yes | no | 0.0461 | 0.215 | [0.0120, 0.0946] | 0.116 | no | — | 1/4/0/0 |
| sg0.35 seed 57721 (reused) | 16 | yes | no | −0.0096 | 0.336 | [−0.0162, −0.0009] | −0.159 | no | — | 1/5/0/0 |

The reused six reproduce Ring 28's table exactly. For the one detected new run (777) the
scorer's unmapped arm gives S 0.0258, p 0.215, not detected, and the matched arm S 0.0251,
p 0.181, not detected; only the `additive_only` contrast detects. The two misses are E2
(participation variance: 7 and 8 gate-failed epochs), not saturation. Unmapped arm for the
other detected runs of this arm: `sg0.3` 777 and 31337 — not measurable (E5b seed balance);
`sg0.35` 2718 — S 0.0701, p 0.0007, detected (matched arm S 0.170, p 0.0007).

| falsifier | Arm 1 | number that carries it |
|---|---|---|
| F1 identity | pass | 0 radialised, 0 Plummer, 0 one-cell eligible epochs; 0 radialised detections |
| F2 false positives | pass — **by the 2026-09-06 synthetic receipt only** | e.g. white noise 0/120, deposited sphere 0/30, shared-drive heteroscedastic noise 5/90 (bound 9), amplitude 6/90 (bound 9) |
| F3 recovery | **evaluable, pass** | median α\*\_eff 0.0177 (raw 0.02) over 9 runs ≤ 0.10; 0 unrecovered at α 0.2; none with template ρ < 0.5; new runs 0.0165 / 0.0387 / 0.0397 |
| F4 robustness | pass | 11 variants; `measurable_both` 9 in nine, 8 in `den_0.03`, **0 in `e2_pr16` (vacuous — not evaluable there, as in Ring 28)**; violations 0 in every variant against an allowance of `max(1, ⌈0.05·9⌉) = 1`; symmetric difference 0 everywhere except `classes` = 1 (`sg0.3` seed 777, main p 0.0225 — inside the band, so reported and not scored); F3 main vs variant agree (pass/pass) in every evaluable variant |
| F5 support | **pass** | 3 measurable conditions (`sg0.3`, `sg0.32`, `sg0.35`), 9 of 9 runs, fraction 1.0 each; 146 of 198 cell-epochs eligible |

Detection: 4 of 9 distinct runs — `sg0.3` 777 and 31337; `sg0.32` 777; `sg0.35` 2718.
Per condition 2 / 1 / 1. **Not reproduced within `sg0.32` (1 of 3).**

Staticness screen (`memory_pilot_staticness.py`, unmodified): no static condition.
`sg0.32` per-run full-field epoch-to-epoch medians 0.094 / 0.051 / 0.070 (777 / 12345 /
31337; screen max 0.094, residual max 0.048; thresholds 0.99 / 0.7); worst raw cross-seed
0.038; clamp share 0.087 / 0.073 / 0.073; noise share 2.6 × 10⁻⁵; centroid travel 11.0 /
10.8 / 9.2 cells.

### Arm 2 — SECONDARY, pre-committed second realisation: `sg0.32` on 2718 / 16180 / 57721

`manifest.runs = 9`, `not_manifested = []`; `inputs.runs = 9`, `conditions = 3`, 18 files,
`inputs_verified = true`; `protocol_commit 41fe0685`; `measured_at 2026-09-22T16:52:14Z`.

**`verdict.result` = "qualified"**. In the pre-registered form: the second seed family at
`sg0.32` was 3/3 measurable, and its directory returned "qualified" — reported beside Arm 1,
never substituted.

| run | eligible | measurable | detected | S (own) | p | CI95 | lag-1 Q | caveat | contrasts detected | gates failed |
|---|---:|---|---|---:|---:|---|---:|---|---|---|
| sg0.32 seed 2718 | 15 | yes | **yes** | 0.0260 | 0.0070 | [0.0122, 0.0434] | −0.154 | no | shells_1.0, shells_0.5 | 1/5/1/0 |
| sg0.32 seed 16180 | 15 | yes | **yes** | 0.0443 | 0.0035 | [0.0088, 0.0831] | −0.127 | no | all four | 1/6/1/0 |
| sg0.32 seed 57721 | **12** (at the floor) | yes | no | −0.0105 | 0.964 | [−0.0203, 0.0007] | −0.058 | no | — | 3/9/0/0 |
| reused sg0.3 / sg0.35 six | 19/17/17, 16/17/16 | yes × 6 | 777, 31337, 2718 | as Arm 1 | | | | | | |

F1 pass (same zeros); F2 pass by the same receipt; F3 evaluable, pass — median α\*\_eff
0.0173, 0 unrecovered, new runs 0.0172 / 0.0173 / 0.0412; F4 pass — `measurable_both` 9 in
eight variants, 8 in `classes` and `den_0.03`, 0 in `e2_pr16` (vacuous); **`e1_0.02` and
`e3_0.95` each newly lose one strong detection (2718, p 0.007): one violation = the whole
allowance, in two variants — within the frozen tolerance and reported as such**; `classes`
symmetric difference 1 (an in-band flip, not a violation); F3 main vs variant agree
everywhere evaluable. Unmapped arm for the new detected runs: 2718 and 16180 — not
measurable (E5b seed balance; 2718 also E5 collapse), so no unmapped S or p exists; their
matched arms (S −0.007, p 0.470; S 0.056, p 0.357) are undetected. F5 pass — 3
conditions, 9 of 9 runs, 144 of 198 cell-epochs. Detection 5 of 9 — `sg0.3` 777, 31337;
`sg0.32` 2718, 16180; `sg0.35` 2718; per condition 2 / 2 / 1; **not reproduced within
`sg0.32` (2 of 3)**. Staticness: none static; `sg0.32` medians 0.082 / 0.070 / 0.064 (2718 /
16180 / 57721), residual max 0.018, worst raw cross-seed 0.049, clamp 0.066–0.081.

### The pre-registered decision rule, applied

Arm 1 returned **"qualified"**, branch 1 of the rule above, so the ring's verdict is
"qualified", copied verbatim. What that means was fixed before the runs and is repeated
here without addition: **the frozen estimator is qualified as able to measure on three
generated conditions — `spinchladni gl0` at the cut drive `fieldExp 1.7`, self-gravity
0.3 / 0.32 / 0.35 (three points spanning 0.05 of one axis), 4,194,304 particles, 24 epochs
of 10 s, one instrument (`sim_digest 40bfdb68`) — and says nothing about any other
preset, drive, gain/loss, particle count or instrument, and nothing about nested
resonance memory** (protocol §1: "a pass does not establish memory"). Its decomposition
held: F1 was a check, F2 was decided by the receipt alone, F3's nine-run median (0.0177)
sat under the 0.0383 bound the reused six guaranteed, and the verdict reduced to F5 (the
third condition 3/3) plus F4 band stability on nine runs plus manifest verification.

The two arms agree on `sg0.32` measurability (3/3 and 3/3) and on `verdict.result`, so the
statement is **"`sg0.32` measurable in 2 of 2 pre-committed triples"**. Triple-level and
descriptive only: of the six triples now on the record at the three support conditions
(two per condition), four are 3/3 — `sg0.3` grid (Rings 25–28), `sg0.35` transcendental (Ring 28),
`sg0.32` grid and `sg0.32` transcendental (this ring); the two 2/3 triples are `sg0.3`
transcendental (Ring 25: 13/12/10) and `sg0.35` grid (Ring 27: 15/11/17). No standard
deviation, p-value or chance fraction is estimated from them. The arms are coupled (six
shared runs, one F2 receipt, a shared-dominated F3 median): two "qualified" strings are not
two qualifications.

### Detection, read as pre-registered

Seed 777 detects at `sg0.3` and at `sg0.32`; seed 2718 detects at `sg0.35` and at `sg0.32`.
Each pair shares its initial positions, so these are read as **seed-specific persistent
structure** — the confound protocol §1 names — and **not** as reproduction of memory. Within
a condition, `sg0.32` detects 1 of 3 (Arm 1) and 2 of 3 (Arm 2): not reproduced. Counts are
not converted to rates and not compared with F2's 5 % bound. The only informative direction
(a mapped contrast clearly above the unmapped one, protocol §5) can be read for two of the
five detected runs: Arm 1's 777 has mapped S 0.033 (p 0.004) against unmapped S 0.026
(p 0.215) — above, but with three of four contrasts undetected; the reused `sg0.35` 2718 has
both arms detected (0.069 against 0.070). Arm 2's 16180 and 2718, and the reused `sg0.3`
777 and 31337, have an unmapped arm that is not measurable (`unmapped.measurable = false`,
E5b seed balance; 2718 also E5), so the direction cannot be read there.

**The pre-registered unscored diagnostic** (`experiments/halo/mesh_epoch_correlation.py`,
written for this ring; reads the raw `*.mesh.f32`, Pearson per epoch, median over the
scored epochs 3–24; JSON beside each arm's qualification file):

| pair | same seed, across conditions | different seeds, inside `sg0.32` | different seeds, inside the other condition |
|---|---|---|---|
| Arm 1: `sg0.3` vs `sg0.32` | 777: 0.058 · 12345: 0.210 · 31337: 0.128 (median 0.128) | 0.062 · 0.071 · 0.241 (median 0.071) | `sg0.3`: 0.140 · 0.087 · 0.122 (median 0.122) |
| Arm 2: `sg0.35` vs `sg0.32` | 2718: 0.023 · 16180: 0.049 · 57721: 0.177 (median 0.049) | 0.050 · 0.141 · 0.060 (median 0.060) | `sg0.35`: −0.004 · 0.002 · 0.211 (median 0.002) |

Per-epoch values are far from stationary: single epochs reach 0.73–0.93 in epochs 1–2
(before the scored window) and also 0.70–0.97 inside it — the largest value in either arm,
0.970, is same-seed 12345 (`sg0.3` vs `sg0.32`) at epoch 18, an epoch where different-seed
pairs also rise (`sg0.32` 12345/31337 0.776, `sg0.3` 777/12345 0.702; Arm 2 `sg0.35`
16180/57721 0.891). The scored medians for a seed's field at two self-gravity values (0.058 /
0.210 / 0.128; 0.023 / 0.049 / 0.177) fall inside the range of medians for two seeds' fields
at one value (0.062–0.241 and 0.087–0.140; 0.050–0.141 and −0.004–0.211), with Arm 1's
median of medians (0.128) above the cross-seed ones (0.071, 0.122). Three pairs against
three, no test; numbers only; nothing is decided by them.

### What changes, and what does not

- **Changes:** the programme has its first "qualified" verdict, on a support of three
  conditions × three seeds at one instrument, with two pre-committed triples at the
  third condition. The successor is fixed by the pass branch above: a **registered
  intervention** on this support (protocol §1) — a pre-registered relic-scramble or
  relic-swap arm — not another point in the window, not a correlation.
- **Does not change:** nothing about nested resonance memory. Detection is sparse,
  unreproduced within any condition, and its cross-condition hits follow the seeds.

### Files

New this ring (the `*.mesh.f32` are gitignored and regenerable; their hashes are in each
manifest):

| file | sha256 (first 16) | bytes |
|---|---|---:|
| `memory_sg032_third/spinchladni_sg0.32_gl0_seed777_….json` / `.mesh.f32` | `160dded1fa4f4aed` / `ce15f08155e34fff` | 55,079 / 3,145,728 |
| `memory_sg032_third/…seed12345….json` / `.mesh.f32` | `0f651106656a3b92` / `47fedfad10608fc5` | 54,922 / 3,145,728 |
| `memory_sg032_third/…seed31337….json` / `.mesh.f32` | `4d77a238bbb65a33` / `dfde73964f32e667` | 54,964 / 3,145,728 |
| `memory_sg032_third_r2/…seed2718….json` / `.mesh.f32` | `971c880d98d8b3ee` / `a62158bff9b0a734` | 54,986 / 3,145,728 |
| `memory_sg032_third_r2/…seed16180….json` / `.mesh.f32` | `dca940b65ee4d20e` / `a78ef20d96af2dd8` | 54,995 / 3,145,728 |
| `memory_sg032_third_r2/…seed57721….json` / `.mesh.f32` | `b4e286f2daf42c10` / `059a441acbb57327` | 55,056 / 3,145,728 |

Plus, per arm: `manifest.json`, `staticness.json`, `qualification.json`,
`cross_condition_correlation.json`; and `experiments/halo/mesh_epoch_correlation.py`.
The ring on the page is a comment-only append; `sim_digest` stays `40bfdb68`;
`tests/halo/rc-test.html` was not rebuilt (`1a15b987`; the file is gitignored, so this pin
lives in the run records and on the build tree, not in git).

### Kill-test

Five lenses in one workflow re-derived every verdict-bearing number from the files with
their own code, read-only. **Scorer reproduction:** both arms copied to fresh directories,
manifests rebuilt, the frozen scorer re-run — every `verdict`, run, F1–F5 field and F4 row
identical to the committed files, only the manifest path and the clock differing;
staticness re-run with 0 diffs. **Raw meshes:** the six `sg0.32` epoch-to-epoch medians
reproduced to 10⁻¹⁶ and the 18 diagnostic medians to 5 × 10⁻⁷ against `np.corrcoef`; no
consecutive-epoch pair ≥ 0.99 (worst 0.51). **Provenance:** all 24 reused hashes against
the table and commit `6560d802`; six `git_rev` = P with ancestry rc 0; every frozen hash;
`sim_digest 40bfdb68` invariant across `rc-test.html` and the appended page (the page diff
is +69/−0 lines, all inside the closing comment); the seed-777 regeneration byte-identical.
**Decision rule:** both arms on branch 1; the successor named above matches the frozen
pass branch. **Overclaim critic and rule auditor:** five prose faults in the draft, all
folded here before ship — a sentence placing the diagnostic's per-epoch maxima "only in
epochs 1–2" (false: 0.970 at epoch 18, inside the window); interpretive readings of the
diagnostic ("no more alike", "do not carry field identity") where the pre-registration
fixed it as numbers only, and where Arm 1's same-seed median of medians (0.128) is in fact
above the cross-seed ones (0.071, 0.122); Arm 1's one `classes` flip described as a spent
allowance (it is an in-band run at p 0.0225, 0 violations); "eight" variants at
`measurable_both` 9 (nine); and an open question that proposed comparing detection counts
with F2's controls, which the pre-registration bans. The unmapped arm is now reported for
every detected run, the staticness triples are labelled by seed, and three fixed BANNED
items were restored on the page.
