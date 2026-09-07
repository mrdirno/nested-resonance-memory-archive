# A measurability pilot: is there a field the frozen memory estimator can measure?

Author: Aldrin Payopay · September 6, 2026 · GPL-3.0-only

**Fixed before any run of the arm it describes.** The commit that carries this file is the
freeze. Nothing in `experiments/halo/memory_estimator_qualify.py` or
`docs/halo/2026-09-05_memory_estimator_qualification_protocol.md` is edited — their value is
that they stay byte-identical, and the synthetic receipt is gated on their hashes.

## 1. What this is for, and what it cannot establish

On 2026-09-06 the frozen estimator was scored once on the recorded 60-run grid and returned
**insufficient support**: 0 of 60 runs measurable, 179 of 1,320 run-epochs eligible
([result](../../analysis/2026-09-06_memory_estimator_qualification.md)). That is a fact about
the grid, not about memory. Before another grid is registered, something has to be shown
measurable.

The pilot asks **one** question: is there a field configuration the page already ships in
which the three seeds' compressed relics genuinely diverge — so E3, the gate that asks for a
null that is not a copy, passes on structure rather than on noise — while the relic still
occupies at least 8 effective cells, so E2 passes?

It **cannot** establish that anything remembers anything. Measurability is eligibility plus
seed balance; detection is a separate test this pilot does not power; and the pilot chooses
its conditions by looking at the gates, so no S, no p, no F1–F5 verdict and not the word
"qualified" from a pilot arm may ever be reported as evidence about nested resonance memory.
It cannot re-certify F2: the frozen receipt's shared-drive controls give the seeds 10–50 % of
the power, and this regime gives them about 0.03 %. It cannot score past epoch 24, because
`FIRST_SCORED, LAST_SCORED = 3, 24` is fixed in the frozen script with no flag — so the
ledger's "run longer than 24 epochs" is not available and is carried below as a question for
the next protocol rather than patched into this one.

## 2. Where the headroom actually is

Read off the frozen script's own result, per run, over the 22 scored epochs:

| Spinning Chladni, gain/loss 0 | eligible /22 | E1 refuses | E2 refuses | E3 refuses | median relic footprint | raw cross-seed correlation |
|---|---|---|---|---|---|---|
| self-gravity 0    | 0, 0, 0 | 1 | 2 | **22** | 250 cells | **0.9987** |
| self-gravity 0.15 | 0, 0, 0 | 3–4 | 4–5 | **20–21** | 176 cells | 0.979–0.994 |
| self-gravity 0.3  | 6, 6, 3 | 2–4 | 8–14 | 8–9 | 79 cells | 0.60 (template) |
| self-gravity 0.5  | 8, 8, 7 | 1–2 | 10–13 | 1–5 | 27 cells | 0.12 (template) |
| self-gravity 0.8  | 1, 1, 1 | 0 | 16 | 5–8 | 6.7 cells | 0.24 (template) |

At low self-gravity **one gate refuses everything** while the relic is 20 to 31 times the size
E2 asks for. At high self-gravity the seeds are apart but the relic has collapsed. The frontier
runs between them, and the axes tried so far — self-gravity, gain/loss, particle count, epoch
length — all move **along** it.

Three of those are already closed, and the pilot does not spend a run on them:

- **Particle count is not a lever, and pushing it is a trap.** Resampling the recorded meshes
  down 256× moves neither the participation ratio nor the template correlation in the Spinning
  Chladni family (flat to 3–4 significant figures). Where it does move something, it moves it
  the wrong way: at low counts the shot-noise share of the predicted residual reaches 34–51 %,
  and that noise *is* the particle realisation, so the own-relic entry starts asking "are these
  the same particles". A static Plummer sphere whose realisation partly persists — a null the
  frozen suite does not contain, because its controls redraw every particle every epoch — is
  detected at 36–50 % against an allowance of 5 in 36. Every pilot run is therefore at
  **4,194,304 particles**, and the shot-noise share is measured, not assumed (screen A5).
- **Epoch length is unavailable below 10 s and redundant above it.** The page clamps it into
  [10, 180] on one line while the driver keeps its own cadence, so asking for 5 gives a page on
  10-second epochs sampled every 5 — half the recorded epochs with no rescale before them, and
  no error. Above 10 s it changes gravitational phase per epoch in proportion to length × √(self-gravity),
  which is the axis self-gravity already swept. Every pilot run uses **10 s**.
- **Self-gravity between 0.3 and 0.6 is a doubly-refused climb.** With E3 forced open and
  nothing else touched, self-gravity 0.5 still yields only 11, 9, 11 eligible epochs against a
  requirement of 12, and the seed-balance gate then fires on all three seeds (null ratios 2.51,
  7.37, 3.04). The relic footprint falls monotonically from 27 cells to 6.7 toward 0.8, and at
  0.8 the force clamp is saturated at 0.993.

**The one axis never tried is the field configuration itself.** The page ships thirty scenarios.
Every one is its own `preset` string, and the frozen script keys a condition on
(preset, self-gravity, gain/loss) — so scenarios give **distinct condition keys by
construction**, which is exactly what F5 needs and what particle count and epoch length cannot
give, since neither is in the key.

## 3. The arm

One directory, `data/results/halo/memory_pilot/scn/`. One scoring invocation of the frozen
script. Every run: gain/loss 0, 4,194,304 particles, 24 epochs, epoch length 10, tick budget 10,
step 9028, real GPU, seeds **777, 12345, 31337**.

| # | preset | what it moves against Spinning Chladni | self-gravity | role |
|---|---|---|---|---|
| 1–3 | `spinchladni` | — | 0.15 | **anchor** |
| 4–6 | `spinchladni` | — | 0.3 | **anchor** |
| 7–9 | `hardprint` | magnetic coupling 0.4 → 0.1 | 0.15 | probe |
| 10–12 | `hardprint` | magnetic coupling 0.4 → 0.1 | 0.3 | probe |
| 13–15 | `stillspindle` | boundary reflect → wrap (the wall removed) | 0.15 | probe |
| 16–18 | `goldstair` | field exponent 2 → 0.15, damping 1 → 2.8, magnetic 0.4 → 0, expansion 1.2 → 0.25, twist off, helix 0.8 → 0 | 0.15 | **primary** |
| 19–21 | `goldstair` | as above | 0.3 | **primary** |

21 runs, 7 condition keys. `goldstair` is the primary because it is the only shipped
configuration that cuts the imposed drive by more than an order of magnitude while keeping
enough expansion that the halving is re-inflated rather than compounded. The two anchors are
recorded conditions re-run on the current build: they measure instrument drift, and they are
**excluded from the success count by construction**.

Cost, from the recorded grid's own wall times (Spinning Chladni gain/loss 0: 24 s at
self-gravity 0, 66 s at 0.15, 71–80 s at 0.3, all 24 epochs at 4,194,304 particles) plus about
8 s of browser start per run: **about 27 minutes**, envelope 45. Disk about 67 MB of mesh, which
`.gitignore` already excludes.

## 4. The measurability diagnostic, fixed before any run

**D1–D6 are read out of the frozen script's own result document.** Nothing is recomputed and
nothing can change a verdict.

- **D1** eligible epochs per run (`runs[*].lag1.eligible_epochs`); a run needs 12.
- **D2** per-gate refusal counts (`gate_fail_counts.e1/e2/e3/e4`), which say what to attack next.
- **D3** median mass in the inner block, median participation ratio of the current field, median
  **minimum over the three seeds** of the predicted field's participation ratio, and median
  largest template correlation. The predicted-field numbers must be assembled across all three
  runs, because E2 is a condition-level AND over the three seeds.
- **D4** the two E5 couplings, reported as numbers and not only as a flag.
- **D5** the three E5b null values **each with its standard error**, and their ratio.
- **D6** **E\***, the primary statistic: the minimum over the three seeds of D1.

**A1–A5 are the pilot's own screens.** They change no gate and no threshold; they decide only
whether a condition counts toward this pilot's headline number, and they are published for every
condition whatever the outcome.

- **A1 seed degeneracy** — median raw cross-seed Pearson of the full 32³ density, worst pair.
  **≥ 0.99 strikes the condition.** Calibration: Spinning Chladni self-gravity 0 reads 0.9987.
- **A2 structural template correlation** — the cross-seed template correlation with the Poisson
  shot-noise power of a 4,194,304-particle deposit removed. For a mesh cell holding value *c* in
  units of particles/1024 the deposit's variance is *c*/1024 in those units, so the noise share
  *f* of a residual's power is Σ(predicted)/1024 divided by Σ(residual²), and the corrected
  correlation is the measured one divided by √((1−*f*ᵢ)(1−*f*ⱼ)). **≥ 0.9 strikes the condition.**
  This is the screen that stops E3 being passed by degrading the estimate instead of separating
  the fields.
- **A3 staticness** — median lag-one Pearson of the full field, and of the monopole-removed
  residual on the inner block. **Full field ≥ 0.99, or residual ≥ 0.70, strikes the condition.**
  Calibration: the recorded static runs read 0.99995–0.99999; every Spinning Chladni run reads
  0.055–0.61.
- **A4 clamp share** — median of the recorded per-epoch `ceiling`. **> 0.5 strikes the condition.**
  Independent of A3: Spinning Chladni self-gravity 0.8 is clamped at 0.993 while being dynamic.
- **A5 particle-identity margin** — the shot-noise share *f* above, per condition. **> 0.01
  strikes the condition.** Expected to be 0.0001–0.0003 at this particle count, which is why the
  pilot runs there; it is measured rather than assumed.

Screens A1, A3 and A4 exist because the pilot's own success metric can otherwise be satisfied by
a field carrying no information: on the recorded grid `default sg0.8 gl0` is a three-way
duplicate sharing one centroid, correlating pairwise at 0.99999, which already passes both
run-level gates with balanced nulls and sits six eligible epochs short of "measurable". No gate
in the frozen protocol names staticness.

## 5. Pre-registered predictions

Eligible epochs are per run, of 22. Anchors are excluded from the success count.

| condition | median min relic footprint | median largest template correlation | structural correlation | eligible per run | measurable | probability |
|---|---|---|---|---|---|---|
| `spinchladni` 0.15 (anchor) | 150–190 | **0.985–1.000** | 0.96–1.00 | 0–1 | No | 0.01 |
| `spinchladni` 0.3 (anchor) | 60–85 | 0.72–0.81 | 0.45–0.60 | 3–9 | No | 0.03 |
| `hardprint` 0.15 | 60–200 | 0.97–1.000 | 0.95–1.00 | 0–3 | No | 0.05 |
| `hardprint` 0.3 | 40–90 | 0.70–0.95 | 0.40–0.85 | 1–8 | No | 0.08 |
| `stillspindle` 0.15 | 40–200 | 0.96–1.000 | 0.93–1.00 | 0–3 | No | 0.05 |
| **`goldstair` 0.15** | **5–45** | **0.35–0.95** | 0.25–0.90 | **2–15** | 50/50 | 0.28 |
| **`goldstair` 0.3** | **4–35** | 0.25–0.85 | 0.15–0.80 | **2–14** | 50/50 | 0.25 |

**The single number that decides the pilot: the median largest template correlation at
`goldstair` self-gravity 0.15, against the 0.9 gate.** The anchor at the same self-gravity reads
0.9952. If cutting the field exponent 13-fold, nearly tripling the damping and removing the
rotation does not bring that number below 0.9, no shipped configuration breaks the drive lock and
this axis is dead.

Four further predictions, falsifiable whatever the headline outcome:

1. `hardprint` moves E3 the **wrong** way — its median largest template correlation is no more
   than 0.02 below `spinchladni` at the same self-gravity. The page's own note says cutting the
   magnetic coupling roughly doubles the azimuthal density contrast, which should lock the seeds
   harder. If `hardprint` instead improves E3, that reading of the magnetic coupling is wrong.
2. E5b is not the binding gate here: every condition reaching 8 eligible epochs returns a null
   ratio below 3, or a largest null below 0.05, or nulls of mixed sign.
3. E5 fires on no run.
4. At least one `goldstair` condition holds median inner-block mass above 0.15, against the
   spinning family's 0.035.

**Probability the pilot reaches three measurable conditions: 0.12.** Five live shots, of which
the two `goldstair` conditions carry almost all the weight and are positively correlated.
Probability of at least one measurable non-anchor condition: about 0.35. **The modal outcome is
zero or one**, and the rule below terminates cleanly on both.

## 6. The decision rule

Scored once, on the whole directory, with the frozen script unchanged, evaluating **E\*** after
striking any condition that fails A1–A5.

**Void first.** (i) `rc-test.html` changes during the arm — re-run what followed the change.
(ii) The arm runner aborted on a page error or a parameter or mesh mismatch — that arm is not
scored. (iii) **Either anchor comes back measurable** — both are pre-registered non-measurable,
so a measurable anchor means the current build is not the instrument the recorded grid describes
and the arm is uninterpretable until that is resolved. Anchor *drift* short of measurability is
reported, not an abort; it is a measurement of build drift.

**Commission a confirmatory grid** if at least **three non-anchor conditions** reach E\* ≥ 12
with E5 and E5b clean and A1–A5 all passing. That grid is then the winning family's drive-strength
neighbours at three rungs plus their two nearest self-gravity values, three seeds, 24 epochs,
4,194,304 particles — with a **fresh seed triple**, because this pilot selected its conditions on
the gates, and with a new F2 control built in this regime.

**Keep piloting** — one further arm, at most 9 runs, and only one — if exactly one of:
(a) `goldstair` 0.15 brings both template correlations below 0.9 but E\* lands at 8–11 because the
relic footprint fell below 8, in which case the next arm is `goldstair` at self-gravity 0.05 and
0.1; or (b) exactly one or two non-anchor conditions reach E\* ≥ 12, in which case the next arm is
the two nearest drive-strength rungs of the winning family (`amphora`, `lacework`) at the winning
self-gravity.

**Retire the plan to run a grid under the frozen protocol** if all of: no non-anchor condition
reaches E\* ≥ 12; `goldstair` 0.15 keeps its median largest template correlation at or above 0.9;
and the anchors reproduce their recorded statistics. Under the predictions above this branch has
probability about 0.55. It would mean preset, self-gravity, gain/loss, particle count, epoch
length and drive strength have each been shown to move along the frontier rather than lift it,
and that the successor is a new protocol rather than another grid under this one.

**The forking-paths safeguard.** Fixed here, before the first run: one directory; one scoring
invocation; one primary statistic (E\*); one decider (the median largest template correlation at
`goldstair` 0.15 against 0.9); two conditions declared anchors and excluded; five live shots,
named. After the arm is scored, no condition may be added, re-run, re-seeded or substituted, and
no second arm may run except through the single keep-piloting branch above. A run that crashes is
re-run once **before** scoring, never after. **All seven conditions' diagnostic lines are
published, in the order of the table in §3, whatever the outcome.** There is no best-arm reporting
because there is one arm.

## 7. Two gate fragilities, carried forward and not patched

**F-1. The seed-balance gate turns on the sign of a number within one standard error of zero.**
The rule is `lo > 0 and hi >= 0.05 and hi/lo > 3`, and `lo > 0` is a hard step: a null of mixed
sign switches the whole gate off. On `default sg0.5 gl0` the odd seed's null is +0.0031 ± 0.0030
under the main configuration (gate fires, all three runs refused) and −0.0015 ± 0.0031 under one
robustness variant (gate off, all three measurable, one detected). Its sibling condition sits on
the same edge and fell the other way (+0.0007 ± 0.0010, did not flip). A third property nobody has
named: E5 and E5b average over each judged run's **own** eligible epochs, so the three runs of one
condition can receive different null triples and opposite verdicts — a direct threat to any metric
of the form "all three seeds measurable". *Pilot obligation:* report every null with its standard
error, never as a boolean. *Question for the successor:* what tolerance band replaces the sign
test, and does the balance gate belong at run level or condition level?

**F-2. E3 compares an estimate, so it can be passed by degrading the estimate.** In the
drive-locked conditions the seed-to-seed template difference is about the size of the shot noise
of a 4,194,304-particle deposit while the shared structure is thousands of times it, and the
effect runs backwards in particle count: more particles make the copies more exact, fewer make a
static sphere with a persistent realisation detectable at 36–50 %. The frozen gate has no
raw-field twin check and no noise correction. *Pilot obligation:* report the structural
correlation, the raw cross-seed correlation and the shot-noise share beside every E3 number, and
strike any condition whose E3 pass is not backed by a structural correlation below 0.9.
*Question for the successor:* does a raw-field twin check belong beside E3, and should the
template correlation be shot-noise-corrected before the comparison?

Two further items stay in the queue and are not this pilot's business: no gate names staticness,
and the script tests support before inputs where the protocol prose orders them the other way.

## 8. Provenance, and what was done before this freeze

Measured this session, before any pilot run:

- repository HEAD at the freeze: recorded in the commit that carries this file
- HALO page `HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html`
  sha256 `d5ad799a293c9c333998f8c6492716801cfd045ea18ec8f76e1891e35e434dda`, 545,216 bytes
- instrument rebuilt from it, `tests/halo/rc-test.html`
  sha256 `03286c6d6760a2a676a283d3513f84c13ba7147eb25c6e184981834b1ca16780`, 547,976 bytes;
  its first line records the page hash above. The copy present before this session was **stale**,
  built from an earlier ring-16 text; every byte of the difference lies inside the sealed-rings
  HTML comment.
- frozen scorer sha256 `7619ef6bbe7409bef03c317076edda5ac6b55820e6c6f955da51783e7575dbd0`
- frozen protocol sha256 `e55a53a1043f31c3aee55ec38e0ed28bb59f270a257719ba66f3bdf6d8a59775`
- the committed synthetic receipt is reused **verbatim**; its script and protocol hashes were
  checked equal to the two above this session
- host: macOS 26.6.1, ANGLE Metal Renderer (Apple GPU), node v24.4.1, playwright 1.62.1,
  python 3.13.5, numpy 2.3.5

**The scoring path was proven end to end before the freeze**: a three-run subset of the recorded
grid scores in 1 s, manifest verified 6 of 6, protocol commit accepted at HEAD, verdict identical
to ring 16 (0 of 3 measurable). The reporter reproduces ring 16's 0 of 60 from the committed
result. The staticness screen independently reproduces ring 16's published numbers, including the
two-site lattice whose odd seed correlates 0.712 at zero shift and 0.99998 one cell along z.

**Probe runs made before this freeze, none of them pilot data.** Seven short runs timed the
harness and verified its flags, in a session scratch directory outside the repository: seeds
424242 to 424250 at 262,144, 524,288, 1,048,576 and 4,194,304 particles, mostly 1–2 epochs. The
frozen scorer scores epochs 3 to 24, so the short ones contain no scoreable epoch. Two of them,
at seed 12345 with 2 epochs, are the flag defect below. One 24-epoch probe exists at seed 424244,
which is not a pilot seed; its measurability diagnostic was deliberately not computed before this
document was committed.

**Three harness defects found while probing, and what was done about each.**

1. *Flags silently ignored.* The runner matches flags by prefix over `process.argv`, and zsh does
   not word-split an unquoted expansion, so a whole flag string passed through one shell variable
   arrives as a single argument: only the first flag is read and every other falls back to its
   default while the run reports success. Two probes were pinned to seed 12345 that way. The arm
   runner now passes every flag as its own word and re-reads each finished run's recorded
   parameters, the page's applied state, the mesh length and every epoch's deposit total,
   aborting on any mismatch.
2. *Epoch length clamped.* Measured: `params.epoch_len` 5, `applied.cosmos.epochLen` 10, one
   halving across two recorded epochs, no error. The gate above now rejects it.
3. *Tag spelling.* The runner names its output with JavaScript's number-to-string of the parsed
   flag, so `--sg=0.40` writes `_sg0.4_`; a loop building its tag from the raw word would re-run
   that cell on every resume. Both values are now normalised before the tag is built.

**One claim made this session and withdrawn.** Reading the rescale counter from the run records, I
concluded that all 60 recorded runs were missing a halving at epoch 4 — the counter reads
1, 2, 3, **3**, 4, 5 — and wrote it down as a defect in the grid. It is not one. The page's own
epoch column shows the boundary firing between t = 39.70 and t = 40.75, and the next between
49.15 and 50.20; the driver reads its instrument row exactly at t = 40, where accumulated
`simTime` is 39.999999999999865, one tick short of the epoch test, so the halving fires on the
following tick, after the read. Every consecutive pair of exported meshes is still separated by
exactly one halving. What lags is the counter as read at the boundary, not the physics. The
retraction is the useful part: that counter is not a witness of whether a rescale happened, and a
pilot gate that flagged a "stall" would have flagged all 60 recorded runs and no pilot run.

**One edit to a non-frozen file, with its equivalence evidence.** `tests/halo/memory_prereg_run.js`
now accepts any shipped scenario as `--preset` and exits with a message on a name the page does
not have. The digit-sequence position stays explicit and defaults to 9028: reading it from the
page after the scenario click — which looked like the tidy generalisation — silently moved the
drive, and a four-epoch A/B at 1,048,576 particles produced different meshes. With the default,
the generalised runner reproduces the previous one **bit for bit** on `spinchladni sg0.3 gl0`
seed 777 (sha256 `9808cdff…` on both mesh files).

## 9. Reproduction

```bash
cd tests/halo
for p in spinchladni hardprint stillspindle goldstair; do
  case $p in stillspindle) S="0.15";; *) S="0.15 0.3";; esac
  OUT=../../data/results/halo/memory_pilot/scn N=4194304 EPOCHLEN=10 EPOCHS=24 \
    PRESET=$p SGS="$S" GLS="0" SEEDS="777 12345 31337" bash memory_pilot_grid.sh
done
cd ..
python3 experiments/halo/memory_pilot_manifest.py data/results/halo/memory_pilot/scn \
  data/results/halo/memory_pilot/scn-manifest.json --note "measurability pilot, one arm"
python3 experiments/halo/memory_estimator_qualify.py \
  --input-dir data/results/halo/memory_pilot/scn \
  --manifest data/results/halo/memory_pilot/scn-manifest.json \
  --synthetic-json data/results/halo/memory_estimator_qualification/synthetic.json \
  --output data/results/halo/memory_pilot/scn_qualification.json
python3 experiments/halo/memory_pilot_report.py data/results/halo/memory_pilot/scn_qualification.json
python3 experiments/halo/memory_pilot_staticness.py data/results/halo/memory_pilot/scn
```

The meshes are not distributed by a clone; a run is reproducible tick for tick from its seed.
