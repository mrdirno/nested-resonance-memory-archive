# Ring 34 pre-registration: the decided arm (the matter inverted, the solver's warm start left) on nine named seeds, scored by Ring 32's within-run carrier statistic under Ring 32's rule, beside its untouched gate on the same seeds

Author: Aldrin Payopay · September 24, 2026 · GPL-3.0-only

**Status: pre-registration, one commit, pushed before any registered run existed.** That commit,
called **P** below, holds this whole file with the decided-arm module, its tests, the batch driver
and the scoring script. The driver refuses to launch unless P is on the public remote's main branch
and the registered files on disk are P's bytes. The runs' results are appended later under a new
heading, "## Results". Nothing before that heading changes after P.

**In plain terms.** Each run of this particle chamber carries a lopsidedness from one ten-second
epoch into the next. Ring 32 built a reading that looks inside one run only: does the lopsided part
of each epoch line up with the lopsided part of the epoch before it, or with its mirror image
through the centre? Ring 33 ran that reading on fresh runs of the positive control, which turns
everything inside out at every epoch boundary: the matter and the gravity solver's carried
potential. In 5 of those 9 runs the lopsidedness followed the inversion, and in none did it stay.
That was the known answer, and the reading returned it.

This ring asks the question the control cannot answer. It turns only the matter inside out and
leaves the solver's carried potential as it was. Does the lopsidedness follow the matter, or stay
where the carried potential points? Nine runs of that arm, on seeds named before Ring 32 ran, are
scored beside nine untouched runs on the same seeds, with two reproduction checks. Nothing here is
about memory.

**Words used below.**

- The **relic** is the previous epoch's mesh, shrunk by the chamber's zoom-out.
- The **warm start** is the gravity solver's potential, carried from one tick to the next. The
  page's Jacobi solver starts each tick from it.
- The **hook** is the harness's step at each epoch boundary, right after the zoom-out, where an arm
  inverts (or leaves) the state.
- The **inversion** is the point inversion through the chamber's centre. The **inverted frame, Π**,
  reads mesh *j* (counted from 0: the mesh written after *j* boundaries) after applying the
  inversion *j* times, so it undoes an inversion made at every boundary. The **lab frame, L**, reads
  the meshes as written.
- The **point-odd part** of a field is the part that changes sign under the inversion,
  (f − inverted f)/2. ρ_k is the correlation of the point-odd parts in lag-one pair *k*, and
  *n*_eff = (Σ|ρ_k|)²/Σρ_k².
- **V1** is the instrument check, listed under "Scoring and the decision rule". A run's **STATIC
  number** is the larger of its lab-frame and inverted-frame median lag-one full-field Pearson.
- The **frozen scorer** is `experiments/halo/memory_estimator_qualify.py` (`7619ef6b…`). O is Ring
  30's point-odd part of a run's own-relic contrast, and F2 is the frozen scorer's false-positive
  falsifier.
- The **HALO page** is `HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html`.
- **T** is Ring 32's within-run carrier statistic, defined in Ring 32's pre-registration and
  imported here unchanged.
- **R** is Ring 32's receipt commit, `59d7d4af`. **P** is this ring's registration commit. (Ring 32's
  text used P for the inversion; here that is always written out.)
- "Protocol §1" is section 1 of `docs/halo/2026-09-05_memory_estimator_qualification_protocol.md`.

## What is being asked, and why now

Ring 30 (`analysis/2026-09-22_relic_intervention.md`) ran three arms on the support where Ring 29's
nine recorded runs returned "qualified" (`spinchladni gl0`, `fieldExp 1.7`, self-gravity 0.3 / 0.32
/ 0.35, 4,194,304 particles, 24 epochs, `sim_digest 40bfdb68`): identity, the positive control
`invert_all`, and the decided arm `invert_matter`. Its rule read the frozen scorer in the lab frame
and the inverted frame and returned **not decidable**, with its positive control silent. Ring 30
does not say why, and nothing below does either.

Ring 32 (`analysis/2026-09-24_within_run_carrier_statistic.md`) then fixed a statistic that reads
one run only, qualified it with its own synthetic receipt at R, and registered fresh runs of the
positive control. Ring 33 scored them once (that file's "## Results"): **CONFIRMED**. `invert_all`
called Π in 5 of its 9 scored fresh runs and L in none; `identity` called L in 6 of its 9 and Π in
none; V1 passed. Ring 32's table fixed what CONFIRMED licenses, in these words: "pre-registering
the decided arm, on the seeds named above, scored by this statistic under this rule." This file is
that pre-registration, and it is Ring 33's open questions 1 and 2 on the HALO page.

The question the positive control cannot answer is which part of the state carries the
orientation. `invert_all` inverts both the matter and the warm start, so either could carry it.
Ring 30's control item 4 named the warm start as a candidate: solving the page's own Poisson
equation on the recorded relics, "the potential the zoomed matter moves in for the first second of
each epoch pulls it toward the relic's hemisphere at 19–23 of 23 boundaries per run". That screen
did not move the matter. `invert_matter` sets the two against each other at every boundary: the
matter is inverted and the warm start still points the old way.

## The arms

Both are Ring 30's registered modes of the pinned harness `tests/halo/memory_intervention_run.js`
(sha256 `f2f30d79…`), unchanged. At every boundary *k* = 1…23, right after the zoom-out tick:

- `identity`, the gate: the hook reads the state and writes it back unchanged.
- `invert_matter`, the decided arm: the hook flips the sign of every particle's position and
  velocity about the chamber's centre (IEEE sign bits of `posA` and `velA`), and leaves the solver's
  32³ potential atlas, the warm start, as it was.

The positive control is not run again. Ring 33 ran it on fresh seeds, and the licence names only the
decided arm.

**What a call means for this arm.** T is the mean, over a run's eligible lag-one pairs, of the
correlation between the point-odd part of each epoch's mesh and the point-odd part of its own
relic's prediction. A positive T leans to the lab frame and a negative T to the inverted frame.
The lean is an L or a Π call only when its sign-flip *p* is below 0.05 and the run has at least 12
eligible pairs (below). Ring 32's receipt check G1 showed, on its twelve control runs, that the
inverted frame gives exactly −T with the same pairs, and each run's score here reports that check
again.

- If the orientation carried from one epoch into the next sits in the matter, an `invert_matter`
  run should read Π, as `invert_all` did.
- If it sits in the warm start, and the warm start's pull in the first second of each epoch sets it,
  the run should read L, as an untouched run that carries the orientation does, because the warm
  start was not inverted.
- If both carry it and fight, a run may read either, or none.

These are the design's working readings. The runs can show which state the orientation follows
when the matter and the warm start are set against each other; they cannot show that the other
carries nothing. Each branch's reading below is fixed now.

## The statistic

T, *n*, *p* and the call are `experiments/halo/carrier_statistic.py`'s, imported and unchanged:
sha256 `020eb6549a1ce163…`, the bytes committed at Ring 32's design commit `1e2810a5` and pinned by
the receipt committed at R (`data/results/halo/carrier_statistic/receipt.json`, sha256
`6ea5c90efca11fc6…`). The decided-arm module checks both before it scores. In brief, and exactly as
Ring 32 fixed it:

- the 22 lag-one pairs *k* = 3…24; a pair is eligible by the run's own field gates only;
- *n* is the number of eligible pairs; a run with *n* < 12 is **unscored**;
- *p* is the exact two-sided sign-flip *p* of the eligible correlations;
- the call is **L** if *p* < 0.05 and T > 0, **Π** if *p* < 0.05 and T < 0, **none** otherwise.

The decided-arm module (`experiments/halo/carrier_decided_arm.py`) adds only what this arm needs:
its registered runs, the scoring of its two arms, a V1 (below) that closes the gaps Ring 33's
breaker found, and this arm's branch table. It refuses to score or decide unless its own bytes, this
file's, the batch driver's and the scoring script's are the ones committed at P, and P descends
from R.

## The runs, fixed

**Seeds.** The nine named in Ring 32's pre-registration before any Ring 32 run existed: the first
five significant digits of √n for the next nine non-square integers after Ring 32's.

| self-gravity | seeds |
|---|---|
| 0.3 | 36055 (√13), 37416 (√14), 38729 (√15) |
| 0.32 | 41231 (√17), 42426 (√18), 43588 (√19) |
| 0.35 | 44721 (√20), 45825 (√21), 46904 (√22) |

No condition shares a seed with another. Within a condition the two arms share their seeds. No
HALO run has used these seeds.

**Conditions:** `spinchladni`, `gl0`, `fieldExp 1.7`, self-gravity 0.3 / 0.32 / 0.35; 4,194,304
particles; 24 epochs of 10 s; tick budget 10; step 9028 (the harness defaults).

| directory | contents | runs |
|---|---|---:|
| `data/results/halo/memory_decided_canary/` | `identity`, `sg0.32` seed 777: must reproduce Ring 29's mesh `ce15f081…` byte for byte | 1 |
| `data/results/halo/memory_decided_identity/` | `--iv=identity` on the nine pairs | 9 |
| `data/results/halo/memory_decided_invert_matter/` | `--iv=invert_matter` on the nine pairs | 9 |
| `data/results/halo/memory_decided_close/` | `invert_matter`, `sg0.3` seed 36055 again: must reproduce the first decided run's mesh byte for byte | 1 |

**Order.** Runs go one at a time, by `sh tests/halo/memory_decided_grid.sh P`:

0. the driver refuses unless P is on the public remote's main branch and the checked-out commit
   descends from P; this file, the driver, the decided-arm module, the statistic, the scoring
   script and the harness on disk are the bytes committed at P (each must exist at P); and node
   and Playwright are the pinned versions;
1. the canary, which gates everything after it;
2. for each pair in the table's order, `identity` then `invert_matter`;
3. the closing repeat.

**Checks on each record.** The driver re-checks each record as it is written, with Ring 32's
checks, and stops on the first failure:

- the test page `1a15b987`, `sim_digest 40bfdb68`, and the pinned harness, base-harness, builder
  and `three.min.js` bytes;
- Chromium 151.0.7922.34, Playwright 1.62.1 and node v24.4.1, with the ANGLE Metal renderer on
  Apple M4 Pro;
- the condition, seed and solver/switch path applied, and the zoom-out schedule;
- 23 hook records, and no page error.

**Launch ledger.** Every launch is first appended to `data/results/halo/memory_decided_launches.tsv`
(UTC time, directory, tag, attempt, the commit checked out at launch).

**Re-issue.** Ring 30's rule, as Ring 32 extended it to an attempt killed from outside, with the
kept-aside marker below. A failure of kind `crash` whose void record shows no page
error may be re-issued once with the identical command. An attempt killed from outside leaves no
record and no void; it counts as a crashed attempt, and its partial mesh is kept aside as
`<tag>.attempt1.mesh.f32.partial` (an empty file of that name, if it was killed before its partial
mesh existed). A third counted launch of any run is refused; a launch that ended in a `refused`
void is not counted. A `receipt`, `schedule` or `record` failure is
never re-issued. A `refused` run never started, so it is not a run. The driver also refuses to
launch a run whose directory already holds more voids than the ledger has launches for it. On this
pinned instrument every run checked so far has reproduced byte for byte from its seed (Ring 33's
canary and closing repeat; this ring's canary and closing repeat check it again), so a re-issue is
not expected to give a different result. A kept-aside first attempt stays beside its record, so its
meshes can be compared with the re-issued run's.

**Where it runs.** The batch runs detached from the session that launches it, so closing that
session cannot stop it. Console logs are kept outside the repository, one per launch, named by
directory, tag and launch number, so neither the closing repeat nor a re-issue overwrites an earlier
log (Ring 33's gap). Command per run, from the repository root:

```
node tests/halo/memory_intervention_run.js --iv=MODE --preset=spinchladni --sg=SG --gl=0 --seed=SEED --fieldexp=1.7 --out=DIR
```

**The shared tree.** The harness stamps each record with the commit checked out when it *writes*
the record, not at launch (Ring 33 found this). This repository is shared with other work, which
may commit to main while the batch runs. This ring commits nothing to the repository from launch
until the twentieth record exists. V1 requires every record's commit and every ledger commit to
descend from P. The launch ledger, not a record's commit, is the launch-time evidence.

## Scoring and the decision rule, fixed before the runs

Nothing is scored before the twentieth record exists. Then `sh
experiments/halo/memory_decided_score.sh P` runs once, with Python 3.13.5 and numpy 2.3.5, in three
steps:

1. `carrier_decided_arm.py score` on each arm. It refuses unless all of these hold:
   - the module, this file, the batch driver and the scoring script on disk are the bytes
     committed at P, and P descends from R;
   - the receipt on disk is the one committed at R and passes by its own gate fields; the
     statistic, the frozen scorer, and Ring 30's frames and gates scripts are the bytes the receipt
     records; and the Python and numpy versions are the receipt's;
   - the arm's directory holds exactly its nine registered runs;
   - the canary and the closing repeat have records.
2. `carrier_decided_arm.py decide` writes V1 and the branch before anything below runs.
3. Reported, deciding nothing: Ring 30's pipeline, unchanged, on the two arms. That is the inverted
   frame, the manifest, the staticness screen and the frozen scorer on each arm and its frame, then
   Ring 30's frame rule.

Scores are written outside the run directories (`data/results/halo/memory_decided_scores/`), so
the manifests list only the runs.

**Per run:** T, *n*, *p*, the call, *n*_eff and the three largest |ρ_k|'s share of Σ|ρ_k|
(descriptive), the STATIC number, and a check that the inverted frame gives −T with the same pairs.

**Per condition:** Π if at least one Π call and no L call; L the reverse; mixed if both; none
otherwise.

**Arm preference Φ:** Π if at least two conditions are Π and none is L or mixed; L if at least two
are L and none is Π or mixed; none otherwise. This is Ring 30's and Ring 32's aggregation.

**V1, instrument.** Ring 32's V1, with the gaps Ring 33's breaker named closed:

- every record and every hook passes Ring 30's checks (`memory_intervention_gates.run_faults`,
  reused), including that the record's commit descends from P, and every run passes the runtime
  pins;
- the receipt on disk is the one committed at R (its recorded design commit, `1e2810a5`, is a
  strict ancestor of R, so that clause of Ring 32's V1 holds by construction and is not re-checked);
- each score was written by these bytes from that receipt under P. Every run's T, *n*, *p* and call
  is re-derived from its mesh and must equal the score, so the score file is not trusted. The
  score's runs are exactly the directory's nine registered runs;
- **new:** every record in a run directory is a registered record of that directory, found once,
  under its own tag, with the registered seed, self-gravity, mode and mesh file. A duplicate
  cannot hide behind a key;
- **new:** every partial mesh is the kept-aside first attempt of a re-issued run whose record
  exists. No other partial mesh may sit in a run directory;
- every void belongs to a registered run of its directory (**new**) and is a re-issuable crash,
  re-issued at most once (a refused void is not a run);
- **new:** the launch ledger names only registered runs, on full commit shas that descend from P,
  and every record's commit is a full sha too. Every registered run has a row, and attempts are
  numbered 1, 2, …. There are at most two counted launches per run. A second comes only after a
  crash void or a kept-aside first attempt, and a kept-aside first attempt only with a second
  launch. Every void and every record has a launch row of its own. First launches are in the
  registered order;
- the canary reproduces `ce15f081`, and the closing repeat reproduces the first decided run;
- in each (self-gravity, seed) pair the two arms' first meshes (written before the first hook) are
  byte-identical, and the nine first meshes are distinct.

**Branches, checked in this order:**

| branch | when | reading, fixed now |
|---|---|---|
| **VOID** | V1 fails | Each failure is named. Nothing is read from the runs. |
| **STATIC** | any of the eighteen arm runs' median lag-one full-field Pearson reaches 0.999, in the lab frame or the inverted frame | A static lopsided field reads one frame by construction. Nothing is read from the runs. |
| **UNMEASURED** | a condition in either arm has fewer than 2 scored runs | The statistic could not read this support often enough on these seeds. It is not a null. |
| **BROKEN** | Φ(identity) = Π, or 2 or more Π calls in `identity` | The untouched runs read the inverted frame. In real arithmetic an untouched run is an `invert_all` run seen in its inverted frame, so this is the sign the positive control's known answer excludes. The statistic is retired on this support. |
| **BASELINE SILENT** | Φ(identity) is not L | The untouched runs on these seeds do not show the carried orientation cleanly enough for the statistic to decide the arm: fewer than two conditions read L, or one untouched run reads Π. The decided arm's calls are reported as counts and not read. |
| **FOLLOWS THE MATTER** | Φ(invert_matter) = Π, with at least 4 Π calls (Φ = Π already rules out any L call) | With the warm start left pointing the old way, the orientation carried from one epoch into the next follows the inverted matter, in at least 4 of the scored runs and in no condition against it. On this support, and for this statistic, the inverted matter carries that orientation across the boundary, and the un-inverted warm start does not hold it in the lab frame. It does not say the warm start plays no part. It is not memory: in this chamber a carried orientation is at once seed structure and a relic that seeds the next epoch (protocol §1), so this gives no support to the detection-as-memory reading. |
| **STAYS IN THE LAB FRAME** | Φ(invert_matter) = L, with at least 4 L calls (Φ = L already rules out any Π call) | With the matter inverted at every boundary, the orientation stays where the un-inverted warm start points, in at least 4 of the scored runs and in no condition against it. On this support, and for this statistic, that fits the solver's carried potential setting the orientation over the matter's own arrangement. It does not say the matter plays no part. That would be a property of a numerical scheme's carried state. It is not memory. On this support it would be an instance of the first confound protocol §1 names, "an angular asymmetry that persists in the lab frame". One alternative is not excluded inside this ring: an orientation pinned to the chamber, not carried at all, would also read L. This ring has no positive control to exclude it on these seeds. Ring 33's positive control, on other seeds of this support, read Π in 5 runs and L in none. Each arm's between-run pinning diagnostic is reported beside the branch. |
| **FEW CALLS** | Φ(invert_matter) is Π or L, with only 2 or 3 calls in that direction | Φ names a frame, but with only 2 or 3 calls in that direction, fewer than the 4 that naming a carrier needs. The count and Φ are reported; no carrier is named, and neither is read as a lean toward either carrier. |
| **SPLIT** | Φ(invert_matter) = none, with both Π and L calls | Some runs follow the matter and some stay. This includes a single call against as many as eight the other way; the counts are reported beside it. The design does not say whether chance, a dependence on self-gravity, or the two carriers in competition produced it. No carrier is named. |
| **NO PREFERENCE** | Φ(invert_matter) = none, with calls in at most one direction | The orientation neither follows the matter nor stays often enough for this rule. It is not a null. The design does not say whether the hook, competition between the two carriers, or chance produced it. |

**What each branch licenses.** No branch licenses a memory claim. FOLLOWS THE MATTER names the
matter as what the orientation followed across the boundary when the matter and the warm start were
set against each other. STAYS IN THE LAB FRAME names the un-inverted warm start as the carrier that
fits, and does not exclude an orientation pinned to the chamber on these seeds. Both hold on this
support and for this statistic only. Every other branch names none. Whatever the branch, the next experiment is chosen after the
result and registered as its own ring. No branch licenses re-running these seeds, adding seeds or
moving any threshold.

**Reported with every branch, as counts beside each other, never pooled:**

- the Π calls and the L calls among the scored `invert_matter` runs, each as "k of the m scored";
- the L calls among the scored `identity` runs, in the same form;
- every run's T, *n*, *p* and call, and each condition's label;
- the between-run pinning diagnostic for each arm.

In each pair the two arms share their first mesh, so the arms are not independent, and no test
compares them. `invert_matter` is not a symmetry of the chamber's equations: after the first
boundary its runs follow different dynamics from their `identity` pairs.

**The frozen rule, reported beside the branch.** Ring 30's frame rule on these arms gives each run's
Π and L signatures and each arm's preference under the frozen contrast. That is Ring 30's decided
quantity, the arm's frame preference under the frozen contrast, computed again on fresh seeds.
Ring 30's branches are not evaluated: MOVED and NULL need gates this ring cannot meet (V3 against
Ring 29's runs; V5 and NULL's Φ(invert_all) = Π), and neither word is used for this preference. It
never stands in for this statistic's branch,
and the two are not compared. The frozen verdict string of each fresh directory is a reading of
those nine runs only. It is not a re-qualification.

## Predictions, fixed now

None of the working readings is favoured here, and no branch is predicted. Ring 30's registered
result for this arm (under the frozen contrast, no preference in any condition and no run with a
Π- or L-signature) stands whatever this ring returns. It is not a prediction for this statistic, and
the two are not compared. The Disclosures record what the public near-copy would lead one to
expect; it is not used.

| if the orientation carried into the next epoch … | `identity` | `invert_matter` | branch |
|---|---|---|---|
| sits in the matter, and the statistic reads it often | L | Π, 4 or more calls | FOLLOWS THE MATTER |
| sits in the warm start, and the statistic reads it often | L | L, 4 or more calls | STAYS IN THE LAB FRAME |
| is carried by both, in competition | L | calls both ways, few calls, or 4 or more in the stronger carrier's direction | SPLIT, NO PREFERENCE, FEW CALLS, or the stronger carrier's named branch |
| is read rarely by the statistic on these seeds | L or none | few or no calls | FEW CALLS, NO PREFERENCE or BASELINE SILENT |

A named branch therefore does not tell a sole carrier from the stronger of two.

**Planning numbers, not thresholds** (`carrier_decided_arm.py plan`, exact enumeration of the 3⁹
call vectors of one nine-run arm, with calls independent between runs, given that the identity gate
passes; FEW CALLS pools both directions). If this arm called one direction at an assumed per-run
rate of 5/9 and never the other (5/9 is the value of Ring 33's `invert_all` count; it is used here
only as an assumption, and that count is not read as a rate), the chance that this arm meets the
named branch's conditions in that direction (FOLLOWS THE MATTER or STAYS IN THE LAB FRAME), with
every run scored, would be 0.8426, of FEW CALLS 0.1356 and of NO PREFERENCE 0.0218. At 2 of 9 per run it would be 0.1178, and
FEW CALLS 0.4264, NO PREFERENCE 0.4558. A contrary call rate of 0.025 per run turns 0.2035 of the
5-of-9 mass into SPLIT (the named branch then has 0.6872). The table is symmetric in the two directions. These rates are assumptions;
nothing about this arm's rate is known, and the runs are not independent of their `identity` pairs.

## Banned

Carried from Rings 30 and 32, for every reading of these runs. Three differ from Ring 32's wording:
two are reworded for this arm, and one quotation is corrected to protocol §1's own words (Ring 32
had "an asymmetry that persists"). Every other ban in Ring 32's "## Banned" applies to these runs as
well, and those that bear on this arm are repeated after this list:

- any memory claim;
- reading NOT DECIDABLE as a null, or as a lean toward either carrier;
- naming a cause for the none;
- comparing an intervened run with the identity run of the same seed, beyond the registered
  first-mesh check (they share their first mesh and differ after the first boundary);
- quoting `invert_matter`'s "qualified", or any inverted frame's verdict, as a qualification;
- reading O, the hemisphere counts, the gate failures or the detection counts as evidence of which
  carrier holds the contrast;
- turning counts into rates, or pooling runs, arms, frames or instruments;
- a test across the nine runs, or comparing counts with F2's 5 %;
- quoting the page's own in-record memory readouts (retained, memory, twoback) across arms;
- any claim off this support (spinchladni gl0, fieldExp 1.7, sg 0.3/0.32/0.35, 4,194,304
  particles, 24 epochs, sim_digest 40bfdb68);
- rerunning, re-keying, adding seeds or moving the margin to rescue a decision in this ring. Here
  that also covers moving the 0.05 call level, the 12-pair floor or the licence minimum of 4
  (here, the minimum of 4 calls for a named carrier);
- computing this statistic on any Ring 30 intervened run;
- reading an L call on unperturbed runs as memory. Protocol §1 names this confound first: "an
  angular asymmetry that persists in the lab frame";
- reading "passed" as a property of the chamber or the support.

Repeated from Ring 32's list because they bear on this arm:

- reading "power" as a rate: it is a count, k of the m scored (this covers Ring 33's counts
  wherever they are quoted here);
- "this statistic is more powerful than the frozen contrast": no comparison is registered;
- reading CONFIRMED as the matter, rather than the warm start, carrying anything (`invert_all`
  moves both);
- quoting any Ring 30 number as support for this statistic, as its result, as agreement or as a
  prior. This covers control item 4's stale-potential screen, which motivates the question above
  and is not evidence for any branch;
- calling the two arms' runs independent realisations of one another (in each pair they share
  their start);
- stating that this statistic is independent of the strangers, or has a null size, as a finding:
  both hold by construction;
- comparing the counts with Ring 30's "about 3 times in 4";
- reading the Disclosures, the planning numbers or the pinning diagnostic as a result about these
  runs: the Disclosures record what was known; they are not evidence;
- reading a call as a property of its seed, or comparing calls across arms for one seed;
- reading a frozen-scorer detection in the reported step as that run's property (Ring 32 lifted
  this ban for T only).

Added by this ring:

- reading FOLLOWS THE MATTER as "the matter remembers", or STAYS IN THE LAB FRAME as "the warm start
  remembers". Each says what the orientation followed across one boundary, on this support, for
  this statistic; STAYS IN THE LAB FRAME does not exclude an orientation pinned to the chamber, not
  carried at all;
- reading STAYS IN THE LAB FRAME as a property of the chamber's physics. The warm start belongs to
  the page's numerical solver;
- reading FEW CALLS, SPLIT or NO PREFERENCE as a null, or as a lean toward either carrier;
- comparing this arm's counts with Ring 33's `invert_all` counts, or with Ring 33's `identity`
  counts, as rates, as a test, or as "weaker" or "stronger";
- pooling this ring's `identity` runs with Ring 33's;
- quoting Ring 30's `invert_matter` numbers (its frame rule, O, the component files' point-odd
  fields, the hemisphere counts) as support for any branch, as agreement, as a prior or as a
  replication;
- reading agreement or disagreement between the reported frozen rule and this branch as validation
  of either;
- reading the planning numbers as a prediction of this arm's rate;
- applying Ring 30's MOVED or NULL reading, or NULL's retirement of the detection-as-memory
  reading, to the reported frozen rule on these arms.

## Dead branches

- **Running the positive control again.** Ring 33 ran it on fresh seeds; the licence names only the
  decided arm.
- **Dropping the identity gate.** Without it, BROKEN and BASELINE SILENT could not be checked on these
  seeds, and the same-start check would have nothing to compare.
- **An arm that inverts only the warm start.** It would ask the complementary question, but no ring
  registered it. It is an open design, not part of this ring.
- **A whole-state swap or scramble, a rotation about the spin axis, or the y-mirror as the decided
  arm.** Ring 30 banned or left these dead, and they stay so.
- **Changing the statistic, its receipt or its rule for this arm.** Ring 32 froze them, and CONFIRMED
  was earned under them.

## The instrument

- Test page `tests/halo/rc-test.html` sha256 `1a15b987…`. It is a gitignored build; rebuild it
  with `python3 tests/halo/make_test_page.py --from-git f838e509`. Its `sim_digest` is
  `40bfdb68…`.
- Harness `tests/halo/memory_intervention_run.js` `f2f30d79…`, Ring 30's registered bytes. Base
  harness `e0bc8f6b…`, builder `c3a7f5dc…`, `three.min.js 9274bbce…`.
- A record's `instrument.source_page_sha256` hashes the HALO page in the working tree when the
  record is written. It is not the test page's build source, which the test page's own header names
  (`2a1cf94a`, the page at `f838e509`). Nothing gates on it.
- The statistic `experiments/halo/carrier_statistic.py` `020eb654…` and its receipt `6ea5c90e…`,
  both unchanged since R.
- Frozen and unmodified: the scorer `7619ef6b…`, whose primitives build T and whose bytes the
  receipt pins (its full contrast is the reported frozen rule); Ring 30's
  `memory_intervention_frames.py` (the inverted frame, used by the per-run −T check, STATIC and the
  reported rule) and `memory_intervention_gates.py` (its `run_faults`, reused by V1). For the
  reported frozen rule only: the scorer's synthetic receipt `8670e193…` and Ring 30's
  `memory_intervention_decide.py`.
- New at P: `experiments/halo/carrier_decided_arm.py`, `experiments/halo/memory_decided_score.sh`,
  `tests/halo/memory_decided_grid.sh` and `tests/halo/test_carrier_decided_arm.py`.

## Disclosures

- **What was public before this design, and why only the fresh runs count.** Ring 30's result for
  this arm is public: under the frozen contrast it preferred neither frame, and no run had a Π- or
  L-signature. The
  near-copy of T that Ring 32 disclosed (`groups.P_odd.alone_M_own` in each Ring 30 arm's
  `components.json`, the mean of the same ρ_k over the frozen scorer's eligible epochs) is public for
  this arm too. For Ring 30's nine `invert_matter` runs its sign is positive in 4 and negative in 5,
  and every value is smaller in size than 0.022. The same field is positive in all nine Ring 30
  `identity` runs (0.016 to 0.099; the file is byte-identical to Ring 29's control decomposition)
  and negative in eight of the nine `invert_all` runs. Read as a near-copy, the `invert_matter`
  values follow neither frame: if that pattern carried over to fresh seeds, a branch that names no
  carrier (FEW CALLS, SPLIT or NO PREFERENCE) would be the expected outcome. This records what was
  known; it is not evidence and not a prior for any branch. The author read these fields while
  writing this design. The seeds, the statistic, its call rule and aggregation, and the licence were
  fixed by Ring 32 before any of its runs. What is new here is the decided arm's branch table, its
  conditions as well as its readings (4 or more calls in either direction to name a carrier; FEW
  CALLS, SPLIT and NO PREFERENCE; BROKEN and BASELINE SILENT read on `identity` alone), the closed V1
  gaps and the driver's launch checks. The table was written after the author read those fields.
  So these fresh runs are not a blind test, and only they count. None of those Ring 30 numbers is
  used here, and T is not computed on any Ring 30 intervened run.
- **How this file was written.** An earlier drafting session wrote the decided-arm module and its
  tests and ended before running them. This session ran those tests for the first time (46 of 46
  passed), wrote
  the batch driver, the scoring script and this text, and put the code through a read-only breaker
  before P. The breaker's fixes added five tests; the whole suite passes 51 of 51 on P's bytes.
- **Computations before P.** The planning table above. The module's tests, which build synthetic
  runs and score them, and which replay this module's `decide` on a copy of Ring 32's recorded runs
  (already scored by Ring 33; none is a Ring 30 run). Untouched, that replay returns Ring 33's
  counts: L in 6 of 9 `identity` runs, Π in 5 of 9 `invert_all` runs, V1 passing. Seven faults
  were then planted in the copy, one at a time. Four are the kinds Ring 33's breaker named: a
  duplicate record under another tag, a kept-aside partial mesh with one launch, a ledger commit
  before the registration commit, and a run with no ledger row. Three more are checks this module
  adds: a ledger row for an unregistered run, an attempt numbered 2 with no 1, and first launches
  out of order. Each passes Ring 32's `decide` and is caught by this one. Twenty faults planted in
  a synthetic registered tree each turn V1 to a failure.
- **What the read-only breaker changed.** Four lenses read the code before P: V1's fault coverage,
  the branch logic, the driver and scoring pipeline, and provenance and pins. None edited the
  repository. Their findings changed these things:
  - the driver's step 0 passed when the registered files were missing from P. It now compares each
    file's bytes with P's, checks that the checked-out commit descends from P, and checks node and
    Playwright before the canary;
  - scoring and deciding now also require the driver and the scoring script to be P's bytes;
  - V1 compares the re-derived numbers as the score file stores them (a run with no eligible pair
    would otherwise have voided the batch). It now requires a launch row for every void and record,
    a registered run for every void, and full commit shas;
  - the driver keeps an empty marker aside when a killed attempt left no partial mesh, where it
    used to re-issue into a certain VOID. It refuses a run with more voids than launches, and keeps
    one log per launch;
  - the readings of STAYS IN THE LAB FRAME, SPLIT and BASELINE SILENT, and the planning note, were
    made exact.

  The branch logic matched an independent implementation on 39,690,000 pairs of identity and
  decided-arm summaries, with no disagreement. The planning table matched exact fractions in every
  cell. The module's tests went from 46 to 51.
- **What a review of this text changed.** Three read-only lenses read this text before P: banned
  readings and overclaim, every number against its file, and the text against the code with a leak
  check. They changed these things:
  - the FEW CALLS and STAYS IN THE LAB FRAME readings and the licence paragraph, which had leaned
    toward or named a carrier where the branch cannot;
  - the FOLLOWS THE MATTER reading, which had said the matter sets the orientation "not the warm
    start" and now carries a memory disclaimer;
  - STATIC's scope, now the eighteen arm runs the code screens;
  - the Banned list, which had dropped two of Ring 32's bans and now repeats those that bear on this
    arm, with the protocol §1 quotation corrected;
  - the planning paragraph, which had read Ring 33's count as a rate;
  - the Predictions, which no longer name Ring 30's result as the expectation or predict a branch;
  - this disclosure, which now states the outcome the near-copy would lead one to expect;
  - about a dozen smaller wordings.

  Every number and hash in the file was checked against its source and matched.
- **A known limitation of V1.** Nothing in a record ties a mesh's bytes to it except the file
  name. If two runs' meshes were swapped by hand the same way in both arms and the scores
  regenerated, V1 would not see it. The harness writes each mesh under its run's own name, so no
  step of the registered procedure can do this; the first-mesh check and the score files' mesh
  hashes are the only guards.
- **Nothing registered has run.** No `memory_decided_*` directory and no
  `memory_decided_launches.tsv` exists at P.

## How a stranger checks the order

The run records carry no wall clock. The order is evidenced by, in decreasing strength:

1. **The public record.** P reached the public remote before the first launch. GitHub's activity
   record gives the push time, and the launch ledger gives the first launch's time.
2. **The driver's refusal.** It will not launch unless P is on the public remote's main branch, the
   checked-out commit descends from P, and the registered files on disk are P's bytes.
3. **The launch ledger.** Each launch line records its time and the commit checked out at launch.
   Every ledger commit and every record's commit must descend from P, which `decide` checks.
4. **File modification times,** which are local clocks.
