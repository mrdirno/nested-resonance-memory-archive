# Ring 32 pre-registration: a within-run carrier statistic with its own synthetic receipt, and eighteen fresh runs, with two reproduction checks, to count how often its positive control returns the known answer

Author: Aldrin Payopay · September 24, 2026 · GPL-3.0-only

**Status: pre-registration, in two commits, both pushed before any registered run existed.**

1. **The design commit.** It holds this whole file, with the statistic's code, tests, driver and
   scoring script. It was pushed before the receipt was computed for the record (a dry run by
   nearly the same bytes came first; see Disclosures).
2. **The receipt commit, called R below.** It appends one section at the end, "## The receipt,
   computed once from the design commit", and adds the receipt file. The receipt was computed once,
   by the design commit's script bytes; the script refuses to run on any others.

If the receipt had not passed, no fresh run would have been made, and a revised statistic would
be a new ring. The fresh runs' results are appended later under a new heading, "## Results".
Nothing before that heading changes after R.

**In plain terms.** Each run of this particle chamber carries a lopsidedness from one ten-second
epoch into the next. Ring 30 turned the matter inside out through the centre at every epoch
boundary and asked whether that lopsidedness follows it. The scorer it used compares a run with
the two other runs of its condition. What that scorer can see therefore depends on how those three
runs happen to be lopsided relative to one another. Ring 30's positive control (turning everything,
whose answer is known in advance) was silent.

This ring builds a reading that looks inside one run only: does the lopsided part of each epoch
line up with the lopsided part of the epoch before it, or with its mirror image? Lining up means
the run kept the lab's orientation; the mirror image means it followed the inversion. The reading is
checked on recorded runs and synthetic injections, and frozen. Then it is run on eighteen fresh runs,
nine unperturbed and nine with everything inverted, with two reproduction checks. That counts how often the
reading returns the answer known in advance. A near-copy of the reading can already be computed
from numbers Ring 30 published, so the expected answer is known; only the fresh runs count.
Nothing here is about memory.

**Words used below.**

- A run's **strangers** are the two other runs of its condition in a triple.
- The **relic** is the previous epoch's mesh, shrunk by the chamber's zoom-out.
- The **warm start** is the gravity solver's potential, carried from one tick to the next.
- The **hook** is the harness's step at each epoch boundary, right after the zoom-out, where an arm
  inverts (or leaves) the state.
- **Participation** is the effective number of cells a field occupies.
- The **orbit residual** removes, cell by cell, the mean over cells that a symmetry of the cube
  maps onto one another.
- "Protocol §1" is section 1 of `docs/halo/2026-09-05_memory_estimator_qualification_protocol.md`.
- **P** is the point inversion through the chamber's centre.
- **R** is the receipt commit.

## What is being asked, and why now

Ring 30 (`analysis/2026-09-22_relic_intervention.md`) ran a registered intervention. It ran on
the support where Ring 29's nine recorded runs returned "qualified": `spinchladni gl0`,
`fieldExp 1.7`, self-gravity 0.3 / 0.32 / 0.35, 4,194,304 particles, 24 epochs, `sim_digest
40bfdb68`. Its rule read the frozen scorer (`experiments/halo/memory_estimator_qualify.py`,
sha256 `7619ef6b…`) in two frames of each run. It returned **not decidable**, and its positive
control was silent. **Ring 30 does not say why its positive control was silent, and this ring does
not either.** Ring 30's open questions 1 and 2 name this ring:

1. the positive control's power on fresh runs, measured under a pre-registration before a decided
   arm runs again; and
2. a statistic that does not depend on the strangers, fixed before its runs and qualified with its
   own synthetic receipt.

The motive is Ring 30's control item 6, computed before Ring 30's runs. The frozen contrast
compares a run's own relic with a null predicted from the triple's two other runs, so its frame
difference depends on how the triple's hemispheres line up. A statistic read within one run takes
no other run as input, by construction. This block defines one, states its null and its receipt,
and registers the runs that count how often it returns the known answer on fresh runs.

## The statistic

Read from one run's meshes (24 × 32³ float32, `[z][y][x]`, `y` the spin axis), over the frozen
scorer's 22 lag-one pairs. They are kept for comparability with the frozen scorer's scored pairs.
For 1-based current epoch *k* = 3…24, the current is mesh *k*−1 and the relic is mesh *k*−2
(0-based).

- **Fields.** *c* is the current's inner 16³ block (cells 8…23), and *p* is the ×2 relic
  prediction (the 2×2×2 block sum). Both come from the frozen scorer (`sub`, `predicted`),
  imported and not edited, and both then take its orbit residual (the frozen main support).
- **Point-odd part.** odd(*f*) = (*f* − P*f*)/2, where P is the point inversion of the 16³ block
  through its centre. P maps each of the scorer's supports (cube orbits, radial classes, shells,
  none) to itself, so the residual changes only the even part: odd(residual(*f*)) = odd(*f*).
- **Per pair.** ρ_k = ⟨odd(*c*), odd(*p*)⟩ / (|odd(*c*)| |odd(*p*)|). This is the correlation
  between the current's point-odd part and its own relic's.
- **Eligible pairs.** Only the frozen scorer's gates on the run's own fields count:
  - E1: the current's mass in the inner block is at least 1 % of its total.
  - E2, applied to the current and to the run's **own** prediction: participation at least 8, and
    residual variance at least 10⁻⁹ of the block's.
  - The same participation floor (8) on the two point-odd parts, because only they are scored.
  - ρ_k is finite.

  E3, E5 and E5b are gates on the triple and are not used, so no other run enters.
- **The run's number.** *T* is the mean of ρ_k over the eligible pairs, and *n* is their number.
  A run with *n* < 12 (the frozen floor) is unscored.
- **Its p.** The exact two-sided sign-flip *p*, over all 2^*n* sign vectors: *p* = #{*s* : |Σ
  *s*_k ρ_k| ≥ |Σ ρ_k| − 10⁻¹² Σ|ρ_k|} / 2^*n*, and *p* = 1 when Σ ρ_k = 0.
- **The call.** **L** if *T* > 0 and *p* < 0.05; **Π** if *T* < 0 and *p* < 0.05; none
  otherwise.

**Frames.** Ring 30's inverted frame (`memory_intervention_frames.py`, D_j = P^j C_j) inverts
exactly one member of every lag-one pair. So each ρ_k, and *T*, changes sign and nothing else
changes: the eligible pairs and |*T*| stay the same. The within-run frame preference is therefore
the call on the lab frame. **L** means the carried point-odd content kept the lab frame's
orientation across the boundaries. **Π** means it followed the inversion.

**The null.** The null is the random-frame model. Each mesh is inverted, or not, by jointly
independent fair coins that do not depend on the run. Under it the 22 pair signs are independent
fair coins too: each pair sign is the product of two consecutive coins, over the coins of meshes 1
to 23. So the sign-flip test is exact given the |ρ_k|. A call reads "the lab-frame lag-one
orientation products are not fair coins", and its direction comes from the sign of *T*.

The chamber's equations of motion are symmetric under P in real arithmetic, but not exactly in the
machine: the Lab's two fallback re-seatings sit about 10⁻³ off the mirror image, and rounding
breaks bit-exactness (Ring 30 mechanics item 4).

**What the null does not test.** Suppose part of the point-odd structure were pinned to the lab
frame by something not symmetric under P. It would read as L in every arm, and within one run it
looks exactly like carried orientation. Two things can see it. The positive control must read Π,
and a report-only between-run diagnostic tests whether different runs line up at the same epoch
(below).

**Why not a within-run relic shuffle.** Every epoch here continues the one before it, so an
orientation that persists over many epochs is carried orientation too. Pairing a current with a
relic from another epoch of the same run keeps that orientation, so the shuffle is not a sample of
the null. It is reported below as a lag-specificity diagnostic.

## Receipt gates, fixed before the receipt was computed

The receipt reads the Ring 29 control bytes and synthetic injections only. The run meshes are not
in the public repository: they are gitignored, and the receipt identifies each by sha256. The
receipt publishes every control run's per-pair ρ. The runs are the nine
Ring 30 called the control (`data/results/halo/memory_sg032_third/`) plus Ring 29's second
`sg0.32` triple (`memory_sg032_third_r2/`, seeds 2718, 16180 and 57721). That makes twelve
distinct runs; the second directory's other six files are the same bytes as the first's.

- **G1, exactness (a construction check: it fails only on a bug).**
  - For every control pair, |ρ(PC, R) + ρ(C, R)| and |ρ(PC, PR) − ρ(C, R)| are at most 10⁻¹².
  - odd(residual(*f*)) equals odd(*f*) under all five supports, to 10⁻¹² of the field's largest
    value.
  - Every control run's inverted frame gives *T*_Π = −*T*_L to 10⁻¹², with the same eligible pairs.
- **G2, the null end to end (a construction check).** Each control run gets 200 random-frame draws
  (seeded), and the statistic is recomputed from the inverted meshes. Calls (L or Π) over the
  scored null draws may not exceed the upper end of the 95 % binomial band for 0.05. Here that is
  2,400 draws (200 of each of 12 runs), since every control run has at least 12 pairs. The frozen scorer's `binom_interval` overflows a float above n = 1,029,
  so this band is computed the same way in log space. It equals the frozen band wherever the frozen
  one works, and for 2,400 it is [100, 141].

  The test is exact under this null by construction. So G2 checks the code and says nothing about
  the chamber: with correct code it still fails about 2.4 % of the time.
- **G2b, one p two ways (a construction check).** For every control run, and for the first five
  null draws of each, the meet-in-the-middle *p* equals a direct enumeration of every sign vector
  exactly.
- **G3, one run in (a construction check).** Each control run's *T*, *n* and *p*, computed from
  its own mesh file alone, are bitwise identical to the values computed with its directory loaded.
  The function takes one run.
- **G4, recovery: the falsifier.** Each control run gets 20 random-frame draws. A draw already
  called, or unscored, at α = 0 is excluded and counted. The frozen scorer's F3 injection
  (`inject`: the relic prediction mixed into the current's inner block, mass preserved) is applied
  at the frozen α grid 0.002…0.2, with the eligible pairs fixed at α = 0. α* is the smallest α with
  an L call, and a draw never called L counts as 0.2, as frozen F3 counts it. The gate needs three
  things:
  - the lower median over runs of each run's lower median α* is at most 0.10 (the frozen
    ALPHA_FAIL);
  - every run has at least one kept draw, and is called L at α = 0.2 in at least ⌈0.95 × its kept
    draws⌉;
  - no draw at any α > 0 is called Π.

  G4 measures sensitivity to a relic mixed into every pair. It is not power on the chamber, whose
  signal sits in a few collapse pairs.
- **G5, the unperturbed control: reported only.** The twelve control runs are read in the lab
  frame. Their L, Π and none counts are the baseline, and they decide nothing.

The receipt passes when G1, G2, G2b, G3 and G4 pass. "Passed" describes this receipt on these
twelve recorded runs and their synthetic draws. It is not a property of the chamber or of the
support.

**Reported with the receipt, deciding nothing:**

- **Lag specificity.** Each current is paired with a relic drawn at random from the same run's other
  epochs (not the current, its own relic or the epoch right after it), 50 draws per control run,
  seeded.
- **Lab pinning.** *G* is the mean, over pairs of different control runs, of the cosine between
  their inner blocks' point-odd parts at the same mesh index (meshes 1…23). Its exact one-sided *p*
  is taken over every run-level inversion, 2^12 patterns.
- **A planning table.** For one nine-run arm under the aggregation below: the chance that it prefers
  the known answer, that it has at least four calls in that direction, and that it meets
  CONFIRMED's conditions for that arm. The per-run call rates are taken from G5's L count (and half
  of it, and 2 of 9), with contrary-call rates 0, 0.01 and 0.025. The branch also needs the
  identity arm to prefer L. The two arms are not independent, so no joint chance is given. These are
  planning numbers, not thresholds.

## The fresh runs, fixed

**Seeds.** Nine seeds, three per condition, each used once in each arm: the first five
significant digits of √n for the first nine non-square integers n ≥ 2.

| self-gravity | seeds |
|---|---|
| 0.3 | 14142 (√2), 17320 (√3), 22360 (√5) |
| 0.32 | 24494 (√6), 26457 (√7), 28284 (√8) |
| 0.35 | 31622 (√10), 33166 (√11), 34641 (√12) |

No condition shares a seed with another, so the conditions are not three views of one start.
Within a condition, the two arms share their seeds, as in Ring 30. No HALO run has used these
seeds: no file name or record under `data/results/halo/` carries any of them. Every run on this
support so far used 777, 12345, 31337, 2718, 16180 or 57721. Outside HALO, six of the nine (14142,
17320, 22360, 24494, 26457 and 28284) appear as seeds of unrelated older experiments under
`archive/experiments/results/`, which share no state with this chamber. None of the later nine
below appears as a seed anywhere in the repository.

**Seeds of a later decided arm.** If a CONFIRMED licenses one, it uses the next nine √n seeds,
fixed now:

- 36055, 37416, 38729 (self-gravity 0.3);
- 41231, 42426, 43588 (0.32);
- 44721, 45825, 46904 (0.35).

**Conditions:** `spinchladni`, `gl0`, `fieldExp 1.7`, self-gravity 0.3 / 0.32 / 0.35;
4,194,304 particles; 24 epochs of 10 s; tick budget 10; step 9028 (the harness defaults).

**Arms:**

- `identity`: the hook reads the state and writes it back unchanged.
- `invert_all`, the positive control: particles and the solver's warm start are inverted right after
  every zoom-out. This is a symmetry of the chamber's equations, exact in real arithmetic; the Lab's
  fallback re-seatings sit about 10⁻³ off it.

The decided arm, `invert_matter`, does not run in this ring.

| directory | contents | runs |
|---|---|---:|
| `data/results/halo/memory_carrier_canary/` | `identity`, `sg0.32` seed 777: must reproduce Ring 29's mesh `ce15f081…` byte for byte | 1 |
| `data/results/halo/memory_carrier_identity/` | `--iv=identity` on the nine pairs | 9 |
| `data/results/halo/memory_carrier_invert_all/` | `--iv=invert_all` on the nine pairs | 9 |
| `data/results/halo/memory_carrier_identity_close/` | `identity`, `sg0.3` seed 14142 again: must reproduce the first fresh identity mesh byte for byte | 1 |

**Order.** Runs go one at a time, by `sh tests/halo/memory_carrier_power_grid.sh`:

1. the canary;
2. for each pair in the table's order, `identity` then `invert_all`;
3. the closing repeat.

The canary gates everything after it.

**Harness.** The harness is Ring 30's registered `tests/halo/memory_intervention_run.js` (sha256
`f2f30d79…`), unchanged, with every receipt it checks at each boundary.

**Checks on each record.** The driver re-checks each record as it is written, using Ring 30's
checks plus four pins, and stops on the first failure:

- the test page `1a15b987`, `sim_digest 40bfdb68`, and the pinned harness, base-harness, builder
  and `three.min.js` bytes;
- Chromium 151.0.7922.34, Playwright 1.62.1 and node v24.4.1, with the ANGLE Metal renderer on
  Apple M4 Pro (the driver unsets the variable that could point Playwright at another browser);
- the condition, seed and solver/switch path applied, and the zoom-out schedule;
- 23 hook records, and no page error.

**Launch ledger.** Every launch is first appended to `data/results/halo/memory_carrier_launches.tsv`
(UTC time, directory, tag, attempt, commit).

**Re-issue.** This is Ring 30's rule. A failure of kind `crash` whose void record shows no page
error may be re-issued once with the identical command. An attempt killed from outside leaves no
record and no void. It counts as a crashed attempt, and its partial mesh is kept aside. A third
launch of any run is refused. A `receipt`, `schedule` or `record` failure is never re-issued. A
`refused` run never started, so it is not a run.

Console logs are kept outside the repository. The batch runs detached from the session that
launched it. Command per run, from the repository root:

```
node tests/halo/memory_intervention_run.js --iv=MODE --preset=spinchladni --sg=SG --gl=0 --seed=SEED --fieldexp=1.7 --out=DIR
```

## Scoring and the decision rule, fixed before the runs

Nothing is scored before the twentieth record exists. Then `sh
experiments/halo/memory_carrier_score.sh R` runs once, with Python 3.13.5 and numpy 2.3.5, in
three steps:

1. `carrier_statistic.py score` on each arm. It refuses unless all of these hold:
   - the receipt passed, by its own gate fields;
   - the receipt was written by these script bytes, and those bytes are the ones committed at the
     design commit;
   - the frozen scorer, Ring 30's frames and gates scripts, and the Python and numpy versions
     match what the receipt recorded;
   - the arm holds exactly its nine registered runs;
   - the canary and the closing repeat have records.
2. `carrier_statistic.py decide` writes the gates and the branch before anything below runs.
3. Reported, deciding nothing: Ring 30's pipeline, unchanged, on the two fresh arms. That is the
   inverted frame, the manifest, the staticness screen and the frozen scorer on each arm and its
   frame, then Ring 30's frame rule.

Scores are written outside the run directories (`data/results/halo/memory_carrier_scores/`), so
the manifests list only the runs.

**Per run:** *T*, *n*, *p*, the call, *n*_eff = (Σ|ρ_k|)² / Σ ρ_k² and the three largest |ρ_k|'s
share of Σ|ρ_k| (descriptive), and a check that the inverted frame gives −*T* with the same pairs.

**Per condition:** Π if at least one Π call and no L call; L the reverse; mixed if both; none
otherwise.

**Arm preference Φ:** Π if at least two conditions are Π and none is L or mixed; L if at least two
are L and none is Π or mixed; none otherwise. This is Ring 30's aggregation.

**V1, instrument.** Every record and every hook passes Ring 30's checks
(`memory_intervention_gates.run_faults`, reused). Every run also passes the runtime pins. Beyond
that:

- the receipt on disk is the one committed at R, and its design commit is a strict ancestor of R;
- each score was written by these bytes from that receipt. Every run's *T*, *n*, *p* and call is
  re-derived from its mesh and must equal the score, so the score file is not trusted;
- no partial mesh is left beside a record;
- every void is a re-issuable crash, re-issued at most once (a refused void is not a run);
- the launch ledger shows at most two counted launches per run. A second launch comes only after a
  crash void or a kept-aside first attempt;
- every record's `git_rev` descends from R;
- the canary reproduces `ce15f081`, and the closing repeat reproduces its run;
- in each (self-gravity, seed) pair the two arms' first meshes (written before the first hook) are
  byte-identical;
- the nine first meshes are distinct.

**Branches, checked in this order:**

| branch | when | reading, fixed now |
|---|---|---|
| **VOID** | V1 fails | Each failure is named. Nothing is read from the runs. |
| **STATIC** | any fresh run's median lag-one full-field Pearson reaches 0.999, in the lab frame or the inverted frame | A static lopsided field reads L unperturbed and Π under the positive control's alternation, by construction. Nothing is read from the runs. |
| **UNMEASURED** | a condition in either arm has fewer than 2 scored runs | The statistic could not read this support often enough here. It is not a null. |
| **BROKEN** | Φ(identity) = Π, or Φ(invert_all) = L, or 2 or more Π calls in `identity`, or 2 or more L calls in `invert_all` | The statistic reads an orientation that the known answer contradicts: pinned to the lab, or the wrong sign. It is retired. |
| **BASELINE SILENT** | Φ(identity) is not L | The unperturbed runs do not show the carried orientation often enough on fresh seeds for the statistic to decide an arm. No decided arm is scored by it. |
| **CONFIRMED** | Φ(invert_all) = Π, with at least 4 Π calls (Φ = Π already rules out any L call) | On fresh runs the positive control returns its known answer. This licenses one thing only: pre-registering the decided arm, on the seeds named above, scored by this statistic under this rule. |
| **LOW POWER** | Φ(invert_all) = Π with 2 or 3 Π calls | The known answer shows, but a decided arm at this rate would often not decide. No decided arm is licensed. |
| **CONTRARY** | exactly one L call in `invert_all` (Φ(invert_all) is then none) | One run contradicts the known answer. It is named, and no decided arm is licensed. |
| **SILENT** | Φ(invert_all) = none, with no L call | The positive control did not return its known answer on fresh runs. The design does not say whether the hook, the symmetry premise or chance produced it. |

**Reported with every branch, as counts beside each other, never pooled:**

- the Π calls among the scored `invert_all` runs, as "k of the m scored";
- the L calls among the scored `identity` runs, in the same form;
- every run's *T*, *n*, *p* and call;
- the between-run pinning diagnostic for each arm.

The two counts estimate the same per-run rate. In real arithmetic an `invert_all` run's inverted
frame is an identity run, and in each pair the two arms share their first mesh. So the two counts
are not independent, and no test compares them.

**The frozen rule, reported beside the branch.** Ring 30's frame rule on the fresh arms gives each
run's Π and L signatures and each arm's preference Φ under the frozen contrast. That is Ring 30's
open question 1, asked again on fresh runs. It never stands in for this statistic's branch. The
frozen verdict string of each fresh directory is a reading of those nine runs only. It is not a
re-qualification, and it is not compared with Ring 29's.

## Predictions, fixed now

An `invert_all` run's inverted frame reproduces the identity dynamics in real arithmetic, because
the P^j applied at the boundaries cancel in that frame. Floating point and the chamber's Lyapunov
rate (about 2.4 per second) make each run a fresh realisation within seconds. So the positive
control should read Π about as often as unperturbed runs read L. The planning table in the receipt
turns G5's baseline count into the chance of each one-arm outcome. It is a guide, not a guarantee.

| if the carried point-odd content … | `identity` | `invert_all` | branch |
|---|---|---|---|
| is carried, and the statistic reads it often | L | Π, 4 or more calls | CONFIRMED |
| is carried, and the statistic reads it rarely | L or none | Π with 2–3 calls, or none | LOW POWER, SILENT or BASELINE SILENT |
| is pinned to the lab | L | L | BROKEN |
| is carried, but the inversion breaks it | L | none | SILENT |

## Banned

Carried from Ring 30, word for word:

- any memory claim;
- reading NOT DECIDABLE as a null, or as a lean toward either carrier;
- naming a cause for the none;
- comparing an intervened run with the identity run of the same seed (they are different
  realisations after the first boundary);
- reading O, the hemisphere counts, the gate failures or the detection counts as evidence of which
  carrier holds the contrast;
- quoting invert_matter's "qualified", or any inverted frame's verdict, as a qualification;
- turning counts into rates, or pooling runs, arms, frames or instruments;
- a test across the nine runs, or comparing counts with F2's 5 %;
- quoting the page's own in-record memory readouts (retained, memory, twoback) across arms;
- any claim off this support (spinchladni gl0, fieldExp 1.7, sg 0.3/0.32/0.35, 4,194,304 particles,
  24 epochs, sim_digest 40bfdb68);
- rerunning, re-keying, adding seeds or moving the margin to rescue a decision in this ring. Here
  that also covers moving the 0.05 call level, the 12-pair floor or the licence minimum of 4.

**One ban is lifted, for this statistic only.** Ring 30 banned "reading one run's detection as that
run's property", because a frozen-scorer detection compares a run with its strangers. This
statistic takes one run, so its call is that run's reading. It is still not a property of the
seed, and it is never compared across arms for one seed.

Added by this ring:

- reading "power" as a rate: it is a count, k of the m scored;
- calling the fresh runs independent realisations of one another across arms (in each pair the two
  arms share their start);
- stating that this statistic is independent of the strangers, or has a null size, as a finding:
  both hold by construction;
- quoting any Ring 30 number as support for this statistic, as its result, as agreement or as a
  prior. That covers O, the component file's point-odd fields, the hemisphere counts and the
  positive control's one Π-signature;
- computing this statistic on any Ring 30 intervened run;
- "this statistic is more powerful than the frozen contrast": no comparison is registered;
- reading CONFIRMED as the matter, rather than the warm start, carrying anything (`invert_all`
  moves both);
- pooling identity L calls with invert_all Π calls;
- comparing the counts with Ring 30's "about 3 times in 4";
- reading an L call on unperturbed runs as memory. Protocol §1 names this confound first: "an
  asymmetry that persists";
- reading G5's control count, the dry runs, the planning table, the lag specificity or the pinning
  diagnostic as a result about the fresh runs, or comparing the fresh counts with them. The
  Disclosures record what was known; they are not evidence;
- reading "passed" as a property of the chamber or the support;
- reading agreement between the reported frozen rule and this branch as validation of either;
- for any decided arm this ring licenses, the designs Ring 30 banned or left dead stand: a
  whole-state swap or scramble, a rotation about the spin axis, and the y-mirror as the decided arm.

## Dead branches

- **The hemisphere sign alone (the north–south split).** It is coarser than ρ_k: it keeps one of
  the point-odd part's components, and only its sign. In the control's component decomposition
  (Ring 30 control item 1) that split is the largest single piece of the point-odd contrast (0.177
  of the four detected runs' 0.295), not all of it.
- **A blocked sign-flip test,** like the frozen scorer's relabelling in blocks of three. Under the
  null above the pair signs are independent, so blocks would change the test's power, not its
  validity.
- **The same three seeds at every self-gravity.** They would make the nine runs three starts seen
  at three settings.
- **Scoring `invert_matter` in this ring.** The positive control comes first.
- **A pooled Monte Carlo band from the frozen `binom_interval`.** It overflows above n = 1,029.
- **G5 as a gate.** Whether unperturbed runs keep or alternate their orientation is a property of
  the chamber, not of the code, and G4 already fixes the sign convention.

## The instrument

- Test page `tests/halo/rc-test.html` sha256 `1a15b987…`. It is a gitignored build; rebuild it
  with `python3 tests/halo/make_test_page.py --from-git f838e509`. Its `sim_digest` is
  `40bfdb68…`.
- Harness `tests/halo/memory_intervention_run.js` `f2f30d79…`, Ring 30's registered bytes. Base
  harness `e0bc8f6b…`, builder `c3a7f5dc…`, `three.min.js 9274bbce…`.
- Frozen and unmodified: the scorer `7619ef6b…` and its synthetic receipt `8670e193…` (the reported
  comparison only). Ring 30's `memory_intervention_frames.py`, `memory_intervention_decide.py` and
  `memory_intervention_gates.py` are also unmodified.
- New at the design commit: `experiments/halo/carrier_statistic.py`,
  `experiments/halo/memory_carrier_score.sh`, `tests/halo/memory_carrier_power_grid.sh` and
  `tests/halo/test_carrier_statistic.py`.

## Disclosures

- **What was public before this design, and why only the fresh runs count.** *T* is the per-pair
  normalised form of Ring 30's O. The mean of the same ρ_k, over the frozen scorer's eligible
  epochs, was already in the committed component files of all three Ring 30 arms
  (`groups.P_odd.alone_M_own` in each arm's `components.json`). Its sign is positive in the nine
  control runs and negative in eight of the nine `invert_all` runs. O's sign in every `invert_all`
  run was published too. The candidate statistic was named after those results were public. So
  CONFIRMED is the expected outcome. The fresh runs are a replication of a pattern already seen,
  not a blind test, and only they count. None of those Ring 30 numbers is used here, and this
  statistic is not computed on any Ring 30 intervened run.
- **Computations before the design commit.** The statistic was computed on the twelve control runs
  before the design was frozen:
  - two dry runs of an earlier receipt, while the code was written;
  - the design review, whose four read-only reviewers recomputed *T* and ρ_k on the control bytes.

  The review changed the design in these ways:
  - it added the point-odd participation gate;
  - it made G5 report-only and moved the sign check into G4;
  - it added G2b, the log-space band, the between-run pinning diagnostic and the planning table;
  - it replaced three seeds shared across conditions with nine distinct ones;
  - it added the canary, the closing repeat, the runtime pins and the launch ledger;
  - it fixed the full branch table and the licence's minimum of 4 Π calls;
  - it fixed the tie tolerance.

  The two dry runs of the earlier receipt both passed its gates, and it called L in 8 of the 12
  control runs.
- **A dry run of this receipt.** Before the design commit, the receipt was run once more, by the
  script as it stood before the kill-test (sha256 `94cf3ac2…`), with the design-commit check bypassed
  in memory only. It passed. It gave the gate numbers the receipt below reproduces, since the draws
  are seeded: G2 107 of 2,400, G2b 72 of 72, G4 a lower median α* of 0.05, and G5 8 L of 12.

  A three-lens kill-test then read that receipt, the code and this text. It changed these things:
  - `decide` now re-derives every call from the meshes;
  - the receipt is bound to R, and the receipt's own gate fields, pinned scripts and runtime are
    re-checked before scoring;
  - the launch ledger is read, and a refused launch does not count;
  - the STATIC branch was added;
  - scoring waits for the canary and the closing repeat;
  - the lag diagnostic excludes the epoch after the current;
  - the planning rows use exact rates;
  - the seed sentence was corrected, the gap reading contradicted SILENT and was removed, and the
    bans were extended;
  - eleven tests were added for the code the first suite missed.

  None of this changes a gate's arithmetic.
- **Nothing registered has run.** No `memory_carrier_*` directory exists at the design commit.

## How a stranger checks the order

The run records carry no wall clock. The order is evidenced by, in decreasing strength:

1. **The public record.** The design commit reached the public remote before the receipt was
   computed. R reached it before the first launch, and every record's `instrument.git_rev` descends
   from R, which `decide` checks for every record. GitHub's activity record gives the push times.
2. **The receipt.** It records the design commit, and it refuses to run on bytes that differ from
   that commit.
3. **The launch ledger.** Each launch line records its time and the commit it ran on.
4. **File modification times,** which are local clocks.

## The receipt, computed once from the design commit

Computed by `python3 experiments/halo/carrier_statistic.py receipt --design-commit 1e2810a5 --control data/results/halo/memory_sg032_third --control data/results/halo/memory_sg032_third_r2 --json data/results/halo/carrier_statistic/receipt.json`. It ran after the design commit reached the public remote (GitHub's activity record: pushed 11:04:20 UTC on September 24; the receipt's `computed_at`: 11:05:05 UTC), under Python 3.13.5 with numpy 2.3.5. The script checked that it and this file were byte-identical to the design commit before it read any mesh. Receipt sha256 `6ea5c90efca11fc6…`; script sha256 `020eb6549a1ce163…`; frozen scorer `7619ef6bbe7409be…`, unchanged.

| gate | result | pass |
|---|---|---|
| G1 exactness | inverting one member of a pair changes ρ by at most 0 (bitwise) from −ρ, inverting both by at most 0 (bitwise); the odd part of the residual equals the odd part of the field to 5.5e-17 of the field's largest value under all five supports; *T*_Π = −*T*_L to 0 (bitwise), with the same pairs in every run | yes |
| G2 the null end to end | 107 of 2,400 null runs called (47 L, 60 Π), inside the band 100–141 | yes |
| G2b one p two ways | 72 of 72 p-values identical by both enumerations | yes |
| G3 one run in | 12 of 12 runs bitwise identical from their own file alone | yes |
| G4 recovery | lower median α* 0.05 (per-run lower medians 0.02, 0.05, 0.1; limit 0.1); called L at α = 0.2 in 231 of 231 kept draws; 9 of 240 draws excluded at α = 0; 0 Π calls at any α > 0 | yes |

**The receipt passed.** This describes the receipt on these twelve recorded runs and their synthetic draws, nothing about the chamber or the support. The fresh runs may be launched once this section's commit (R) is on the public remote.

**Reported, deciding nothing: the unperturbed control (G5).** L in 8, none in 4, Π in 0 of 12 runs.

| run | *T* | *n* | *p* | call | *n*_eff | top-3 share |
|---|---:|---:|---:|---|---:|---:|
| sg0.3 seed 777 | +0.0677 | 19 | 0.0005 | L | 4.4 | 0.73 |
| sg0.3 seed 12345 | +0.0368 | 17 | 0.0972 | none | 3.5 | 0.72 |
| sg0.3 seed 31337 | +0.0417 | 17 | 0.0048 | L | 5.2 | 0.69 |
| sg0.32 seed 777 | +0.0270 | 17 | 0.0465 | L | 7.2 | 0.54 |
| sg0.32 seed 2718 | +0.0445 | 17 | 0.0092 | L | 10.8 | 0.34 |
| sg0.32 seed 12345 | +0.0424 | 16 | 0.0728 | none | 3.0 | 0.75 |
| sg0.32 seed 16180 | +0.0602 | 17 | 0.0113 | L | 5.1 | 0.69 |
| sg0.32 seed 31337 | +0.0650 | 16 | 0.0203 | L | 3.4 | 0.82 |
| sg0.32 seed 57721 | +0.0467 | 14 | 0.1292 | none | 4.2 | 0.78 |
| sg0.35 seed 2718 | +0.0560 | 17 | 0.0001 | L | 5.4 | 0.69 |
| sg0.35 seed 16180 | +0.0856 | 19 | 0.0019 | L | 6.0 | 0.66 |
| sg0.35 seed 57721 | +0.0237 | 18 | 0.0891 | none | 3.3 | 0.77 |

**Reported: lab pinning on the control.** Mean cosine -0.0071 over 66 pairs of different runs (32 positive), exact one-sided *p* 0.589 over 4,096 run-level inversions.

**Reported: lag specificity** (the relic of a random non-adjacent epoch of the same run, 50 draws per run): mean *T* sg0.3 seed 777 +0.010, sg0.3 seed 12345 -0.007, sg0.3 seed 31337 +0.008, sg0.32 seed 777 +0.004, sg0.32 seed 2718 -0.001, sg0.32 seed 12345 +0.001, sg0.32 seed 16180 -0.006, sg0.32 seed 31337 +0.013, sg0.32 seed 57721 +0.003, sg0.35 seed 2718 +0.039, sg0.35 seed 16180 +0.028, sg0.35 seed 57721 +0.015.

**Reported: the planning table.** The chance, for one nine-run arm under the registered aggregation, that it prefers the known answer (Φ), that it has at least four calls in that direction, and that it meets CONFIRMED's conditions for this arm (both, and no contrary call). The branch also needs the identity arm to prefer L; the two arms are not independent, so no joint chance is given. The per-run rate *q* of calls in the known direction is taken from G5 (and at half of it, and at 2 of 9); *w* is the per-run rate of contrary calls. These are planning numbers, not thresholds.

| *q* | *w* | Φ = known answer | 4 or more calls | this arm meets CONFIRMED's conditions | any contrary call |
|---:|---:|---:|---:|---:|---:|
| 0.667 | 0.0 | 0.996 | 0.958 | 0.958 | 0.000 |
| 0.667 | 0.01 | 0.910 | 0.958 | 0.878 | 0.086 |
| 0.667 | 0.025 | 0.794 | 0.958 | 0.770 | 0.204 |
| 0.333 | 0.0 | 0.789 | 0.350 | 0.350 | 0.000 |
| 0.333 | 0.01 | 0.726 | 0.350 | 0.327 | 0.086 |
| 0.333 | 0.025 | 0.639 | 0.350 | 0.295 | 0.204 |
| 0.222 | 0.0 | 0.544 | 0.118 | 0.118 | 0.000 |
| 0.222 | 0.01 | 0.503 | 0.118 | 0.111 | 0.086 |
| 0.222 | 0.025 | 0.446 | 0.118 | 0.101 | 0.204 |

