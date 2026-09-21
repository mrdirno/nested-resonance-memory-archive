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

