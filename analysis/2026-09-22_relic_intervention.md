# Ring 30 pre-registration and result: a registered intervention on the qualified support — invert the matter at every epoch boundary and see whether the carried contrast follows it

Author: Aldrin Payopay · drafted September 22, committed September 23, 2026 · GPL-3.0-only

**Status of this block: pre-registration, committed and pushed before any of the 28
registered runs existed.** The mechanics pre-flights described below (none scored, none in a
registered directory) preceded it and are disclosed there. Everything in this file as committed
is fixed at that commit and is not edited afterwards; the results are appended below it, under a
new heading "## Results", in a later commit.

**In plain terms.** Each run of this particle chamber carries a lopsidedness — more matter in the
north or the south half — from one ten-second epoch into the next, and the frozen scorer's
"own-relic" signal lives mostly in it. Two things could carry it across the moment the chamber
zooms out: the particles themselves, or the gravity solver's leftover potential, which the page
does not rescale at the zoom-out and which keeps pulling the old way for about a second. This ring
turns the particles inside out through the centre right after every zoom-out. In one arm the
leftover potential is turned with them, a check whose answer is known in advance. In the other it
is left alone, and that arm is the test. If the lopsidedness follows the turned particles, the
particles carry it (MOVED); if it snaps back, the leftover potential does (NULL). Neither outcome
shows memory, and about one time in four or more the rule will not decide.

## What is being asked, and why now

Ring 29 (`analysis/2026-09-21_sg032_third_condition.md`) returned the frozen scorer's first
"qualified" on its nine recorded runs of `spinchladni gl0`, `fieldExp 1.7`, self-gravity
0.3 / 0.32 / 0.35, 4,194,304 particles, 24 epochs, one instrument (`sim_digest 40bfdb68`); item 3
below shows that the word belongs to that recorded orientation of the runs. Detection stayed
sparse (4 of the 9 runs in `memory_sg032_third/`, Ring 29's verdict-bearing directory) and its hits
followed seeds across conditions. Protocol §1 (`docs/halo/2026-09-05_memory_estimator_qualification_protocol.md`) says
no correlation can separate seed-specific persistent structure from "a relic that seeds the
compressed positions and stays there": separating them "needs a registered intervention, not a
correlation". Ring 29's pass branch fixed a registered intervention as the successor. This block fixes the
intervention, the arms, the seeds, the directories, the commands and the decision rule before
the first registered run.

**What an intervention can decide in this chamber.** In this chamber nothing differs between
seeds except the particles' starting positions: the drive, the clocks and every setting are the
same for every seed. Only two things cross an epoch boundary: the particles (positions and
velocities; the force shader reads no other per-particle state) and the self-gravity solver's
warm start (mechanics item 2). So anything a run keeps from its past travels in its particles
or in the solver's leftover potential, and both "seed-specific structure" and "a relic that
seeds the next epoch" travel by those two routes. What an intervention can answer is **which
carrier holds the scored contrast, and whether the contrast follows that carrier when it is
moved**.

**A declared substitution.** Ring 29's pre-registration named the successor "for example" as
a relic-scramble or relic-swap arm; its results and the Ring 29 text appended to the page
(`HELIOS-BRIDGE-ARCHIVE/HELIOS-V501-halo-resonance-chamber.html`, "The pass branch's fixed
successor") drop the words "for example". This ring uses neither, and says why. Read as operations on the scored
relic, both are already inside the frozen scorer: its stranger entries and permutation null
are a relic swap, and its shuffled-relic floor is a relic scramble. Read as operations in the
chamber, a whole-state swap between two runs is a relabelling (the chamber is
bit-deterministic and no random draw reaches it after seeding, so a run given another run's
complete state simply becomes that run), and a whole-state scramble erases every carrier at
once and changes the regime. A swap of one carrier only (one run's particles with another run's
warm start) is neither, but it sets the two carriers against each other only where the two runs'
hemispheres differ; the inversion sets them against each other at every boundary of every run. So
this ring substitutes an in-chamber point inversion of the
matter, and it narrows protocol §1's question: it does not separate seed-specific structure
from relic seeding, which travel together here; it asks which of the two carriers holds the
scored contrast when they are made to disagree.

## What the committed control already shows (computed before this commit; decides nothing)

Read-only computations on the nine Ring 29 control runs (`data/results/halo/memory_sg032_third/`),
the frozen scorer run unchanged; scripts and outputs are committed with this block (outputs
in `data/results/halo/memory_intervention_design/`).

1. **Where the contrast lives** (`experiments/halo/relic_component_decomposition.py` →
   `control_components.json`; its recomputed matrices match the recorded ones to
   1.1 × 10⁻¹⁶). Split the scored field into the parts that are even or odd under the point
   inversion **p** → −**p** through the chamber centre. The odd part carries almost all of the
   additive own-relic contrast of every detected run (0.037 of 0.039, 0.081 of 0.082, 0.049 of
   0.052, 0.129 of 0.140); rescored alone, the even part detects 0 of 9 runs and the odd part 3 of
   the 4 detected ones (not sg0.32 777, p 0.27). The odd part's largest piece is the north–south
   mass profile along the spin axis: 0.177 of the four detected runs' 0.295, and the largest
   single piece in three of the four. The odd part of each run's own relic correlation — call it
   **O** — is positive in all nine runs: 0.037 / 0.021 / 0.023 (sg0.3: seeds 777 / 12345 / 31337),
   0.011 / 0.008 / 0.018 (sg0.32: same seeds), 0.033 / 0.059 / 0.014 (sg0.35: 2718 / 16180 / 57721).
2. **Every run carries its hemisphere** (`experiments/halo/hemisphere_persistence.py` →
   `control_hemisphere.json`). Over the 22 lag-one pairs the scorer reads per run, the
   current's inner-block north/south sign equals the relic's in 16–21 of 22, **157 of 198
   overall**. The split exceeds 0.9 in magnitude in all nine runs at mesh indices 14–17 and 23 (0-based):
   collapses timed by the drive for every seed, into a hemisphere that differs between seeds and
   is usually kept (the same-sign counts above; sg0.3 seed 12345 changes hemisphere between
   meshes 17 and 23).
3. **A detection describes a triple, not a run** (`experiments/halo/memory_orientation_audit.py`
   → `orientation_audit.json`). The chamber's equations of motion are symmetric under the
   point inversion in real arithmetic (mechanics item 4: every force term is odd under it, the
   drive included; the Lab's two fallback re-seatings sit about 10⁻³ off the mirror image), and so
   is the starting ensemble, so a run with all 24 meshes inverted is an equally probable
   realisation. Inverting one run of a triple leaves that run's own correlations unchanged; it
   changes the stranger entries, so the E3 and E5b inputs of the triple can move (here no E1–E4
   flag moved, and E5b moved once, below). Scored in the four orientation classes of the recorded
   triples, the frozen scorer detects **4, 2, 1 and 1** runs (as recorded: sg0.3 777 and 31337,
   sg0.32 777, sg0.35 2718; second seed inverted: sg0.3 777, sg0.32 31337; third inverted:
   sg0.35 16180; second and third inverted: sg0.3 12345), and in the last class the directory's
   verdict is **"insufficient support"**, not "qualified" (sg0.32 12345 fails the seed-balance
   gate E5b). Each condition's outcome depends on its own triple's class alone, so the four
   classes give 4³ = 64 equally valid configurations of the same bytes. In 7 of the 8 detections
   the detected run is the one whose hemisphere is the odd one out of its triple. This ring never
   reads one run's detection as that run's property. **The same holds for Ring 29's verdict:**
   "qualified" belongs to the recorded configuration — 48 of the 64 configurations return it
   (every condition with three measurable runs; F1–F4 pass in every class), the other 16
   "insufficient support" (`rule_power.json`, below). The ring proceeds on the registered verdict;
   the word describes these nine recorded runs, not the support.
4. **The solver's warm start points at the old hemisphere** (`experiments/halo/stale_potential_screen.py`
   → `stale_potential_screen.json`, a static screen: the matter is not moved). Solving the
   page's own Poisson equation on the recorded relics, the potential the zoomed matter moves
   in for the first second of each epoch pulls it toward the relic's hemisphere at 19–23 of
   23 boundaries per run, with a median net pull of 7.5–61 (accelerations in the page's units)
   against a Hubble push of 1.0–4.0 on the centre of mass. A candidate carrier of the hemisphere
   that is not the matter, and that the estimator never sees.
5. **The frame baseline** (`experiments/halo/memory_intervention_frames.py`,
   `experiments/halo/memory_intervention_decide.py` → `control_frame_baseline.json`). Scoring
   the control's meshes with every other mesh inverted (the "inverted frame", defined below)
   gives 0 of 9 detected, 9 of 9 measurable, the same eligible epochs, and S lower than recorded
   in 8 of 9 runs. The rule below classifies the control as preferring the lab frame in all three
   conditions, with L-signatures in five runs (sg0.3 777, *d* −0.065, and 31337, −0.050; sg0.32
   777, −0.061; sg0.35 2718, −0.074, and 16180, −0.070) and no run at *d* ≥ +0.04.
6. **How often the rule can decide** (`experiments/halo/memory_intervention_power.py` →
   `rule_power.json`). The rule below, applied to all 64 equally valid configurations of the
   control's bytes, prefers the lab frame in **48**, none in 16, the inverted frame in **0**. The
   draft of this block counted a signature only if the run was also detected by the frozen scorer
   in the winning frame, without the autocorrelation caveat or an F4 violation; that version
   prefers the lab frame in only **24** of 64 (none in 40, the inverted frame in 0), and a detection
   alone would give 32 (none in 32). A detection compares a run with its strangers, so it depends
   on how the triple's hemispheres happen to line up, not on the frame. In the orientation in which
   a triple's three runs share one hemisphere at the collapse meshes 14–17 (sg0.3 with its third
   seed inverted; sg0.32 and sg0.35 with their second and third inverted), no run of that triple
   reaches ±0.04 (largest |*d*| 0.019, 0.036 and 0.021). The same file confirms item 3's count: in
   48 of the 64 configurations every condition keeps three measurable runs while F1–F4 pass in
   every class involved, which is what "qualified" needs. The rule change is described at the head
   of the decision rule below. **What it means for the outcome:** an intervened run is a fresh
   realisation that lands in a random configuration. If the arms behave like fresh realisations
   of the control, an arm reaches a preference about 3 times in 4; so even with every gate passing,
   NOT DECIDABLE is to be expected about 1 time in 4 if the matter carries the contrast (MOVED needs
   one arm to decide), and about 7 times in 16 or more if the warm start does (NULL needs two arms
   and its F1/F3 condition). These rates come from re-orienting the nine control runs (64
   configurations of the same bytes), not from independent realisations; they are a guide, not a
   guarantee.

## The mechanics, established from the page source before this commit

1. **The zoom-out drifts.** The page's clock is a double that adds 1/20 per tick; replaying it
   reproduces all 2,124 lab-log rows (236 per run) of the nine Ring 29 runs. The zoom-out of
   boundary *k* fires at tick 200*k* + *d_k*, with *d_k* = 0, 0, 0, 1, 2, …, 9 for *k* = 1…12 and 9
   after. The harness stops twice at each boundary: (a) at tick 200*k* − 1, where it exports the
   relic mesh, and (b) at tick 200*k*; the (b) stop is the zoom tick only for *k* ≤ 3.
2. **The solver's warm start carries the relic.** Self-gravity is a 32³ particle-mesh Poisson
   solve, six Jacobi sweeps per tick, warm-started from the previous potential (`state.pm.solver`
   'jacobi', the page default; the page's alternative 'exact' solver carries nothing between
   ticks). On the zoom tick the solve runs on the pre-zoom positions before the substep that
   applies the ×½ rescale, and the potential is never rescaled: for the first second of every
   epoch the zoomed matter moves in the potential of the unzoomed relic. The north–south (dipole)
   error mode of the sweep decays with a time constant of 0.92 s. **So the hook runs right after
   the zoom-out tick of boundary *k***, not at the relic-export stop: there, 6(*d_k*+1) sweeps
   would relax the warm start toward the transformed matter before the zoom, leaving only 0.89
   (*k* ≤ 3) down to 0.16 (*k* ≥ 12) of an opposing dipole — weakest in the late epochs, which
   carry most of the score.
3. **Writes go row by row.** A full-height `renderer.copyTextureToTexture` into a render target
   honours its `flipY` (true in three r128) and lands rows upside down; the first identity
   pre-flight broke byte identity exactly this way. The hook writes each texel row through the
   page's own `__probe.writeRow` (the call the page's Lab uses to re-pair its twins), reads
   every word back, and the run stops on any mismatch.
4. **Symmetry and realisations.** The point inversion is exact for every term of the equations
   of motion in real arithmetic (each drive term has parity (−1)^l, so the Chladni intensity is
   invariant; the two modes of a digit transition are blended as separate forces; the magnetic
   field is the uniform axial one; centres, vessel, overlays and the mode dimer are off). The
   page's Lab, which every run keeps on, re-seats its probe particles (2,048 twins and 384
   volume-meter particles, every half second) along fixed lab directions in two fallback
   branches, placing those particles about 10⁻³ off the mirror image — the same class as the
   rounding below. The y-mirror is not a symmetry: the drive's partner mode breaks it on 75 of
   the run's 120 digit steps. Nothing stays bit-exact once the dynamics runs (summation order,
   cell-edge rounding), and the recorded Lyapunov rate is about 2.4 per second, so every
   intervened run is a fresh realisation within seconds: **an intervened run compared with the
   identity run of the same seed tells nothing**, and every decision below is made within one run,
   between two frames of the same meshes.

## The instrument

- Test page `tests/halo/rc-test.html` sha256 `1a15b987…` (a gitignored build; not rebuilt for
  this ring); `sim_digest 40bfdb68…` (core `50f1e370…`, tick `f887b63f…`), recomputed by
  `experiments/halo/instrument_identity.py` on the test page and on the source page (whose
  whole-file hash is `827fac09…` after Ring 29's comment-only append). Builder `c3a7f5dc…`,
  `three.min.js 9274bbce…`; Chromium 151.0.7922.34, Playwright 1.62.1, node v24.4.1, ANGLE Metal
  on Apple M4 Pro.
- The qualified harness `tests/halo/memory_prereg_run.js` (`e0bc8f6b…`) is unchanged and not
  run. The intervention lives in a new file, `tests/halo/memory_intervention_run.js`
  (sha256 `f2f30d79…`): that harness plus the hook, its extra stops between ticks, a flag
  `--iv`, a required `--out`, a tag suffix `_iv<mode>`, and five added record keys
  (`params.intervention`, `intervention_log`, `instrument.identity` — the page's `sim_digest`,
  recomputed for every run; the harness exits before loading the page if it is not `40bfdb68` on
  page `1a15b987` — `instrument.harness` and `instrument.base_harness_sha256`) plus five read-backs
  in `applied` (`pm`, `dimer_on`, `centers_on`, `vessel_form`, `overlays_on`): the run is refused
  before it starts unless the solver path is 'jacobi'/'ngp' with the mode dimer, centres, vessel
  and overlays off, and every hook re-checks the solver path. Schema stays
  `halo-memory-prereg/1`.
- Scoring runtime: Python 3.13.5 with numpy 2.3.5, the runtime recorded in Ring 29's
  `qualification.json`; gate V3's equality is bit-exact and holds there, and the score script
  refuses any other interpreter.
- Frozen and unmodified: scorer `experiments/halo/memory_estimator_qualify.py` `7619ef6b…`,
  protocol `e55a53a1…`, synthetic receipt `8670e193…`, staticness screen `a0ce66d9…`, manifest
  builder `efe57aba…`. No new estimator: the decision combines the frozen scorer's per-run
  outputs across two frames of the same meshes, with one margin (0.04) on their difference.
- Committed with this block and run after the runs: `experiments/halo/memory_intervention_frames.py`
  (the inverted frame), `memory_intervention_decide.py` (the frame rule), `memory_intervention_gates.py`
  (gates V1–V5 and the branch, by code), `memory_intervention_score.sh` (the scoring order), and
  the drivers `tests/halo/memory_intervention_grid.sh` and `memory_intervention_run.js`.

## The intervention, fixed

At every boundary *k* = 1…23 the harness does its usual relic export (tick 200*k* − 1) and (b)
stop (tick 200*k*), then steps one tick at a time until the page's zoom-out of boundary *k* has
fired (the registered *d_k* ticks), and then, in one `page.evaluate` (no tick can run inside
it), the hook reads the particle state (`posA`, `velA`: 2048 × 2048 float32) and the solver's
potential atlas (`pmPotA`, 256 × 128), flips IEEE sign bits on a `Uint32Array` view — no
floating-point arithmetic, so every value maps exactly — writes back row by row, and reads
back and compares every word. Lab twin and volume-meter rows are inverted in place with every
other texel, so pairs stay paired. No random draw reaches the chamber (three.js object ids
consume the page's `Math.random`, which the chamber never reads after seeding).

| arm (`--iv=`) | particles (position and velocity) | solver warm start | role |
|---|---|---|---|
| `identity` | unchanged | unchanged | re-qualification; the gate arm |
| `invert_all` | (x, y, z) → (−x, −y, −z) | permuted with them, cell (x, y, z) → (31−x, 31−y, 31−z) | positive control: a symmetry of the equations of motion, so the carried contrast must follow |
| `invert_matter` | (x, y, z) → (−x, −y, −z) | **left as it was** (the potential of the pre-zoom relic) | **the decided arm** |

Receipts per boundary, each stopping the run on failure: the solver path is 'jacobi'/'ngp';
the hook ran with the epoch counter at *k* after exactly the registered *d_k* steps; 3 ×
4,194,304 words flipped per texture in the inverting arms and none in identity; zero read-back
mismatches in positions, velocities and potential (this is what pins the GPU state); in the
inverting arms the hash of each particle texture changed (a MurmurHash3-style word hash, which,
unlike the FNV-1a hash of the draft, sees sign flips); the potential moved in `invert_all` only;
a self-check of the CPU transform (angular momentum Σ **r** × **v** bitwise unchanged and Σ **r**,
Σ **v** bitwise negated, unchanged in identity, summed in float64 in texel order; non-finite values
are counted and reported, not a failure);
the deposit after the hook the exact inverted image of the deposit before, up to at most 16,384
particles (1/256 of them) moved by cell-edge rounding — the three central planes of the
32-cell grid are cell edges, so a thin sheet on one of them can put about 1,500 particles within
rounding of an edge, while a write fault moves a large share of all particles — and none in
identity; and, one tick later, the state that tick consumed (`posB`/`velB` after the page's
ping-pong swap) equal to the state written, word for word. Before the record is written the harness also
checks: no page error, the condition applied, the zoom-out schedule at every (b) stop, 23 hook
records. The mesh is written as `<tag>.mesh.f32.partial` and renamed only after all of these
have passed. A run that fails writes `<tag>.void-<n>.json` instead (schema
`halo-memory-intervention-void/1`, which the frozen loader and the manifest builder both skip),
naming the failure kind (`refused` — the page is not the registered instrument or the run is off
the registered path, before the first tick — `receipt`, `schedule`, `record` or `crash`), the page
errors, the hook records so far and the last completed boundary.

**Why `invert_matter` decides.** In `invert_all` the whole carried state is inverted — a symmetry
of the equations of motion — so the carried content must follow the inversion; that is fixed in
advance, and it shows that the pipeline can see a carried contrast in the inverted frame and rules
out a contrast pinned to the lab. In
`invert_matter` the particles are inverted and the stale potential is not: for about a second
the inverted matter sits against a pull toward the old hemisphere. If the matter's hemisphere
wins, the contrast follows the inversion as in `invert_all`; if the stale potential wins, the
contrast stays where the lab frame had it. Nothing in the recorded data settles which, and either
answer changes what the programme should believe about the detections.

## Arms, seeds, directories, order, commands

The nine (condition, seed) pairs of Ring 29's verdict-bearing directory (`memory_sg032_third/`): `sg0.3` × 777, 12345,
31337; `sg0.32` × 777, 12345, 31337; `sg0.35` × 2718, 16180, 57721. Every run: `spinchladni`,
`gl0`, `fieldExp 1.7`, 4,194,304 particles, 24 epochs of 10 s, tick budget 10, step 9028 (the
harness defaults).

| directory | contents | runs |
|---|---|---:|
| `data/results/halo/memory_intervention_identity/` | `--iv=identity` | 9 |
| `data/results/halo/memory_intervention_invert_all/` | `--iv=invert_all` | 9 |
| `data/results/halo/memory_intervention_invert_matter/` | `--iv=invert_matter` | 9 |
| `data/results/halo/memory_intervention_identity_close/` | `--iv=identity` (sg0.32, 777); checked by hash only | 1 |
| `data/results/halo/memory_intervention_<arm>_frame_point/` | the inverted frame of each of the three arm directories | 9 each |

Order, one run at a time, by `sh tests/halo/memory_intervention_grid.sh`: the nine identity runs;
**gate G0** (every identity mesh byte-identical to its Ring 29 mesh — sha256 `632599c2…`,
`bbe6c90a…`, `4ac2b599…`, `ce15f081…`, `47fedfad…`, `dfde7396…`, `fbac35aa…`, `84e69ab7…`,
`cd196ff8…` — or nothing else runs); then, pair by pair in the order above, `invert_all` then
`invert_matter`; then the closing identity run, which must reproduce `ce15f081…` (a mismatch
voids all 28 runs as drift). Besides the harness's own receipts and record checks, the driver
re-checks each record as it is written: no page error; test page `1a15b987`; recorded
`sim_digest 40bfdb68`; the harness, base-harness, builder and three.js hashes pinned above; the
condition, mode and solver/switch path applied; the zoom-out schedule at every (b) stop as in
every Ring 29 record; 23 hook records. The first failure stops the driver; that run is reported.
**Re-issue:** a failure of kind `crash` whose void record shows no page error may be re-issued
once with the identical command (the driver skips every pair whose record already exists and
passes, so re-running it continues where it stopped); a `receipt`, `schedule` or `record`
failure is never re-issued and ends the ring at V1. A `refused` run never started: it is not a
run, and the driver may be run again once the registered instrument or path is restored. An
argument error stops the harness before it launches and writes nothing. Command, per run, from the repository root:

```
node tests/halo/memory_intervention_run.js --iv=MODE --preset=spinchladni --sg=SG --gl=0 --seed=SEED --fieldexp=1.7 --out=DIR
```

**Frames and scoring (after all runs)**, by `sh experiments/halo/memory_intervention_score.sh P`
(P = this commit), every command from the repository root with repo-relative paths (the frozen
scorer writes its `--manifest` argument verbatim into `qualification.json`):

```
python3 experiments/halo/memory_intervention_frames.py DIR --op point --out DIR_frame_point     # each arm DIR
python3 experiments/halo/memory_pilot_manifest.py   X X/manifest.json                           # X = each of the six
python3 experiments/halo/memory_pilot_staticness.py X --json X/staticness.json
python3 experiments/halo/memory_estimator_qualify.py --input-dir X --manifest X/manifest.json \
        --synthetic-json data/results/halo/memory_estimator_qualification/synthetic.json --output X/qualification.json
python3 experiments/halo/memory_intervention_decide.py --arm identity ID/qualification.json ID_frame_point/qualification.json Pi \
        --arm invert_all ... --arm invert_matter ... --json data/results/halo/memory_intervention_decision.json
python3 experiments/halo/memory_intervention_gates.py --prereg-commit P --json data/results/halo/memory_intervention_gates.json
python3 experiments/halo/hemisphere_persistence.py DIR --qualification DIR/qualification.json --json DIR/hemisphere.json   # report only
python3 experiments/halo/relic_component_decomposition.py DIR --json DIR/components.json                                 # report only (O)
```

The gates script re-derives every inverted frame into a temporary directory and requires it
byte-identical to the one scored. The staticness screen of a derived directory measures
similarity across an inversion and is not reported as the runs' staticness.

## Decision rule, fixed before the runs

**One change from the draft, made before this commit.** The draft counted a signature only if the
run was also detected, without the autocorrelation caveat or an F4 violation, in the winning frame.
That condition was dropped, and nothing else changed (the 0.04 margin included), on one input:
`rule_power.json`, computed from the committed Ring 29 control bytes (control item 6), where the
draft decides 24 of 64 equally valid configurations and this rule 48, and neither ever picks the
wrong frame. No registered run existed; the only intervened runs were the six-epoch pre-flights
below, too short for the scorer's 12-epoch floor and never scored (one sign count from their logs
is disclosed there).

**The decided quantity is the `invert_matter` arm's frame preference.** Each run's 24 meshes
are read by the frozen scorer twice, within the run: in the lab frame L (as recorded) and in the
inverted frame Π, D_j = P^j C_j (the inversion applied to the odd-indexed meshes; mesh j has had j
interventions before it). It is the same construction in every arm: in the intervened arms it
undoes the interventions, in the identity arm it introduces them. The identity arm is a gate (V3,
V4), not a comparator; no intervened run is compared with a control run. The per-epoch gates
E1–E4, the eligible epochs and the relabelling and bootstrap draws are identical in the two frames
of a run; the run-level gates E5 and E5b, the shuffled-relic floor and every lag-one correlation
are recomputed per frame, so a run can be measurable in one frame only, and it then carries no
signature.

Per run measurable in both frames: *d* = S_Π − S_L; a **Π-signature** if *d* ≥ +0.04, an
**L-signature** if *d* ≤ −0.04, otherwise none (0.04 is twice the frozen detection floor S_MIN).
A signature does not require a detection (control item 6). Per condition: Π if at least one
Π-signature and no L-signature; L if the reverse; mixed if both; none otherwise. **Preference Φ**
of an arm: Π if at least two conditions are Π and none is L or mixed; L if at least two are L and
none is Π or mixed; none otherwise.

Gates, checked in order by `memory_intervention_gates.py`; the first that fails ends the ring as
NOT DECIDABLE, named:
- **V1 instrument:** every run passed its receipts and checks, with the harness bytes committed
  in this commit and the pinned base harness, builder and three.js; every void record a
  re-issuable crash, re-issued at most once; G0 passed; the closing identity reproduced
  `ce15f081`; every record's `git_rev` descends from this commit.
- **V2 inputs:** every scored directory `inputs_verified`, with nine loaded runs in three loaded
  conditions (measurability is not a V2 condition); every derived frame reproduced byte for byte,
  with the same per-epoch eligibility as its raw directory.
- **V3 the control re-qualifies:** the identity directory returns "qualified", nine of nine
  measurable, F1–F5 passing, and every per-run number equal to Ring 29's (every number and flag in
  each run's entry; names differ only by the `_ividentity` suffix).
- **V4 baseline:** Φ(identity) = L (control item 5, from the Ring 29 bytes).
- **V5 positive control:** Φ(invert_all) ≠ L (Π is reported as "confirmed", none as "silent").

Branches:
1. **MOVED** — Φ(invert_matter) = Π. Reading, fixed now: *the scored point-odd contrast followed
   the matter when the matter alone was inverted and the solver's warm start was left pointing the
   old way.* (Which part of that contrast moved is not tested here; in the control it is mostly the
   north–south profile.) It is a contrast only and does not establish memory:
   in this chamber a carried hemisphere is at once "seed structure" and "a relic that seeds the
   next epoch" (protocol §1's first-named confound, an asymmetry that persists). A MOVED beside a
   silent positive control is reported as such.
2. **NULL** — Φ(invert_matter) = L, **and** Φ(invert_all) = Π, **and** in both `invert_matter`
   directories (the raw directory and its inverted frame) F1 passes and F3 is evaluable and
   passes. Reading, fixed now: *when the matter was inverted right after every zoom-out and the
   solver's un-rescaled warm start was not, the scored contrast stayed with the warm start.* **The
   detection-as-memory reading — that a detection shows the chamber's matter carrying its own past
   across the zoom-out — is retired on this support**: in the one conflict this ring can create,
   what the estimator scores followed the potential that the page's gravity solver leaves
   un-rescaled at the zoom-out (a lag in the page's solver, not a property of the matter and not of
   the estimator), so a detection here is no longer evidence that the matter carries its past. It
   does not show that the matter carries nothing when the two agree, as they do in every
   unperturbed run, and it never licenses "nothing crosses the boundary". NULL needs more than MOVED
   because it retires a reading: it must show that the pipeline can see the inverted frame
   (Φ(invert_all) = Π) and that the estimator keeps its identity check and its power on the
   decided arm's fields (F1; F3).
3. **NOT DECIDABLE** — anything else, with the proximate cause named: the first failed gate;
   Φ(invert_matter) = none; or Φ(invert_matter) = L without the NULL conditions, naming which is
   unmet. A none is reported as none: competing carriers, a regime change and too few signatures
   all produce it and this design cannot tell them apart, so none of them is named as its cause
   (control item 6 gives its base rate). An arm preference of none, whatever mix of conditions
   produced it, is never MOVED or NULL. No rerun (other than the registered re-issue), re-key, added seed,
   substituted arm or new threshold is scored in this ring.

Forbidden at every outcome: a positive memory claim; any comparison of an intervened run with the
identity run of the same seed (different realisations); counts turned into rates or compared with
F2's 5 %; pooling runs, arms, frames or instruments into one statistic or test (counts of runs are
reported as counts); a test across the nine runs; quoting a derived
directory's verdict as a qualification; reading one run's detection as that run's property;
reading O, the hemisphere counts or the gate-failure numbers as MOVED, NULL or a lean; quoting the page's
own in-record memory readouts (`retained`, `memory`, `twoback`) across arms — the page's relic maps
are lab-frame in every arm; any claim off this support.

**Reported for every run of every directory:** measurable, eligible epochs, gate failures, S, p,
the block-bootstrap CI95, the lag-one autocorrelation of Q and its caveat flag, detected, the F4
violation flag, *d* and the signature; per directory F1–F5 and the verdict string (for a derived
directory, as a reading of that frame only); per run O and the hemisphere same-sign count; per arm,
the number of runs failing each gate, beside the identity arm's numbers (descriptive; decides
nothing); per run the hook time and any count of non-finite values.

**Predictions, fixed now.** An arm's preference can also come out none (control item 6).

| if the scored contrast rides on … | `identity` | `invert_all` | `invert_matter` | branch |
|---|---|---|---|---|
| the matter | L | Π (or none) | Π (or none) | MOVED (or NOT DECIDABLE) |
| the solver's stale warm start | L | Π (or none) | L (or none) | NULL (or NOT DECIDABLE) |
| both, competing | L | Π (or none) | none, or the stronger carrier | NOT DECIDABLE, or that carrier's branch |
| a contrast pinned to the lab | L | L | L | NOT DECIDABLE (V5) |
| no carried hemisphere at all | L (it is the Ring 29 data) | none | none | NOT DECIDABLE; disfavoured by the frame baseline (S lower in 8 of 9 runs in Π) |

## Banned, and dead branches (searched before this block)

- **Banned:** a full-state swap between two runs of a triple (a relabelling); "scramble everything
  and call a drop memory" (every carried structure falls, and the regime changes); another point
  in the window, more seeds, or a correlation (Ring 29's pass branch).
- **Dead:** a random half-inversion, or a quarter-turn symmetrisation, of the particles against a
  sham arm. With the warm start left stale it would test whether the potential alone regrows the
  hemisphere, but it has no frame the frozen scorer can read within a run, and comparing counts
  across re-realised arms drowns it in realisation noise; open for a later ring. A rotation about
  the spin axis — the north–south profile, the largest carried piece, is invariant under it, so it
  could move only the smaller pieces (such as the x–z offset of the centre of mass named below); not
  chosen. The
  whole-state y-mirror as the decided arm — it equals the inversion composed with a half-turn about
  the spin axis, so its "moved" outcome is largely predicted by the control's own frame scores,
  and its lab-frame outcome would leave a carried component (the x–z offset of the centre of mass,
  odd under the inversion) intact while claiming a retirement; it is an open question for a later
  ring. The own-coupling O as the decider — it has no synthetic receipt; it is reported. The hook
  at the relic-export stop — see mechanics item 2. The draft's detection-gated signature — see
  control item 6.

## Pre-flight, done before this commit (mechanics only; nothing scored)

- **The draft's pre-flight** (records not kept): `identity` through the hook at 4,194,304 particles
  for 5 epochs — the five meshes byte-identical to the first five of the committed Ring 29 `sg0.32`
  seed 777 run, hooks after 0, 0, 0 and 1 steps, zero mismatches, about 0.37 s per hook — and
  `invert_all` and `invert_matter` at 65,536 particles for 6 epochs, every receipt passing. It ran a
  copy of the draft harness that differed only in how it resolved file paths (sha256 `dfc27715…`).
  At 65,536 particles for 4 epochs an earlier version of the same write path gave meshes, final
  state and lab rows byte-identical to a run without the hook.
- **Re-run on 2026-09-23, three times, as the harness changed under review:** with the draft
  harness (`d8a4d555…`), with the harness after the design panel's changes (`6a0331c1…`), and with
  the registered harness (`f2f30d79…`), whose records are committed in
  `data/results/halo/memory_intervention_design/preflight/` (meshes regenerable, not committed).
  The second review found that the first two used an FNV-1a word hash for the consumption receipt,
  which cannot see an even number of sign flips, so in the inverting arms that receipt could not
  show that the next tick read the inverted state; the registered harness compares the next tick's
  input with the written state word for word and uses a hash that sees sign flips. All three gave the
  same bytes. With the registered harness: `identity` at 4,194,304 particles for 5 epochs (sg0.32,
  seed 777) — its five meshes byte-identical to the first five of the Ring 29 run; hooks after 0, 0, 0
  and 1 steps; zero read-back mismatches; the next tick's input equal to the written state word for
  word at every boundary; no non-finite value; the density receipt exact; about 0.4 s per hook; the
  solver path read back as 'jacobi'/'ngp' with every switch off. `invert_all` and `invert_matter` at
  65,536 particles (1/64 of the support; sg0.3, seed 12345) for 6 epochs: hooks after 0, 0, 0, 1 and 2
  steps; 196,608 words flipped per texture per boundary and each particle texture's hash changed;
  zero read-back mismatches; the next tick's input equal to the written state word for word; the
  potential moved in `invert_all` only; the transform self-check passing; at most 1 particle moved
  by edge rounding; no page error.
- **Disclosed because the logs show it:** in the two 65,536-particle runs, the sign of the y
  centre-of-mass sum that each hook wrote was the sign the next hook found in 3 of 4 cases
  (`invert_all`) and 2 of 4 (`invert_matter`). For `invert_matter` a kept sign points the MOVED way
  (the matter stayed on the side it was put on) and a flipped sign the NULL way. One seed, 1/64 of
  the particles, four boundaries each: nothing about the support is read from it. (The draft's own
  disclosure — the sum changed sign between the pre-hook values of boundaries 1 and 2 in both arms —
  is the first of these boundaries.)

## How a stranger checks the order

The run records carry no wall clock. The order is evidenced by, in decreasing strength: (1) this
commit, **P**, pushed to the public remote before any of the 28 registered runs existed (the
pre-flights above excepted), and every registered run's `instrument.git_rev` being P or a
descendant of it (`memory_intervention_gates.py` checks `git merge-base --is-ancestor P <git_rev>`
for every record and prints the result); (2) each `qualification.json`'s `protocol_commit`; (3)
`measured_at` and file modification times, which are local clocks.

## Results

**Scored once, on 2026-09-23, in the pre-registered order, without editing anything above
this heading.** Eighteen of the 28 registered runs were written between 02:38 and 03:12 PDT
(UTC−7) on 2026-09-23, after P (`b5ae861c`, committed at 02:36:32 PDT = 09:36:32 UTC, and pushed at
09:36:40 UTC). A session wrote
them and ended during the nineteenth: `invert_matter`, `sg0.32`, seed 12345. That run left a
void record (`…ivinvert_matter.void-1.json`, kept): kind `crash`, error "page.waitForFunction:
Target page, context or browser has been closed", no page error, 21 of its 23 hooks done.
That is the one failure the re-issue rule above allows. This ring ran the driver again,
unchanged (`sh tests/halo/memory_intervention_grid.sh`, started at 09:25 PDT). The driver:

- re-checked the 18 existing records, and all passed its checks;
- passed gate G0 again;
- re-issued the voided run once with the identical command. The second attempt passed every
  receipt, and there is no second void;
- ran the eight inverting runs that were left, then the closing identity run: ten runs
  written by this ring in all.

Nothing was regenerated, re-seeded, moved or substituted, and nothing was scored until all 28
runs existed. The scoring script (`sh experiments/halo/memory_intervention_score.sh P`) ran once, at 09:44
PDT. It wrote the six scored directories, the decision and the gates, then stopped in its
last, report-only step. That step and the change it needed are described under "A declared
change after scoring".

### Order and instrument, checked before scoring

| check | result |
|---|---|
| P on the public remote before any registered run | `b5ae861c` is on `origin/main`. GitHub's activity record (`gh api repos/mrdirno/nested-resonance-memory-archive/activity`) has it reaching the remote at 09:36:40 UTC (02:36:40 PDT). By local file times, which git does not keep, that is 7 s before the harness created the first run's output folder (02:36:47 PDT), 12 s before it opened the first mesh file, and 2 minutes before the first record (02:38:43 PDT). Every record file and the void record is newer than the push |
| `instrument.git_rev` | `b5ae861c` (= P) in the 18 records the earlier session wrote; `0df453f7`, a descendant (`git merge-base --is-ancestor` rc 0), in the 10 this ring wrote |
| harness / base harness / builder / `three.min.js` | `f2f30d79` (the bytes committed at P) / `e0bc8f6b` / `c3a7f5dc` / `9274bbce` in all 28 |
| test page / `sim_digest` | `1a15b987` / `40bfdb68` in all 28. Recomputed on the tree after the runs: `40bfdb68` on `tests/halo/rc-test.html` and on the source page (whole file `827fac09` at P and until this ring's comment-only append, which changes the whole-file hash but not `sim_digest`), core `50f1e370`, tick `f887b63f` |
| where the test page comes from | `tests/halo/rc-test.html` is a gitignored build from Ring 26's source page (`2a1cf94a…`, the hash its first line records), not from the `827fac09` page each record names as `source_page_sha256`; both carry `sim_digest 40bfdb68`. `python3 tests/halo/make_test_page.py --from-git f838e509` rebuilds `1a15b987…` exactly (checked after the runs) |
| per-boundary receipts | 23 hook records in every run, every receipt holding: 3 × 4,194,304 words flipped per texture in the inverting arms and none in `identity`; no read-back mismatch; the next tick's input equal to the written state; the density receipt within n/256; the potential moved in `invert_all` only |
| non-finite values | 0 in all 28 runs |
| G0 | 9 of 9 `identity` meshes byte-identical to Ring 29 (`632599c2…` … `cd196ff8…`). The driver checked this before any inverting run, and again on this ring's pass |
| closing identity run | `ce15f081…`, byte-identical to Ring 29's `sg0.32` seed 777 mesh |
| void records | one, re-issued once; the re-issued run passed |
| the re-issued run's file times | its mesh keeps attempt 1's creation time (03:12:23; the harness truncates and reuses the same `.partial` path) and attempt 2's modification time (09:27:24). The void and the re-issue are about 6 h 11 min apart, and the text sets no time limit |
| `git diff b5ae861c 0df453f7` (P against the tree's head at scoring) on `experiments/halo`, `tests/halo`, `docs/halo` and the source page | empty. The Ring 30 commit then changes three of these files: the declared fix to `experiments/halo/relic_component_decomposition.py`, its new test `tests/halo/test_relic_component_mean.py` (both below), and this ring's comment-only append to the source page (`sim_digest` unchanged) |
| `instrument.git_dirty` | `true` in all 28 records, because untracked result files sit on the shared tree. The pins are the file hashes and `sim_digest`, not git cleanliness |
| wall time | 91–132 s per run; the hooks took 9.6–11.4 s of that |
| scoring runtime | Python 3.13.5, numpy 2.3.5 (the score script refuses any other), on macOS 27 arm64 (`runtime.platform` in every `qualification.json`); bit-identical scores are shown on that platform only |

### The gates, by code (`memory_intervention_gates.py`)

All five gates pass:

- **V1 instrument: PASS.** Every run passed its receipts and checks, with the harness bytes
  committed at P and the pinned base harness, builder and `three.min.js`. G0 passed. The
  closing identity run reproduced `ce15f081`. Every `git_rev` descends from P. The one void
  is a re-issuable crash, re-issued once.
- **V2 inputs: PASS.** All six scored directories are `inputs_verified`, each with nine
  loaded runs in three loaded conditions. The gates script re-derived each inverted frame,
  byte for byte. The eligible epochs are the same in the two frames of every arm.
- **V3 the control re-qualifies: PASS.** The `identity` directory returns "qualified", with
  nine of nine runs measurable, F1–F5 passing, and every per-run number equal to Ring 29's.
  So in `identity` mode the intervention harness changes nothing: the extra stops between
  ticks leave every byte and every score the same.
- **V4 baseline: PASS.** Φ(identity) = L in all three conditions, with the five
  L-signatures of control item 5: `sg0.3` 777 (*d* −0.065) and 31337 (−0.050); `sg0.32` 777
  (−0.061); `sg0.35` 2718 (−0.074) and 16180 (−0.070).
- **V5 positive control: PASS, and silent.** Φ(invert_all) = none. That is not L, so the
  gate passes. Under the pre-registered wording it is reported as "silent", not "confirmed".

### The branch

**NOT DECIDABLE. Proximate cause: Φ(invert_matter) = none.** All nine `invert_matter` runs
are measurable in both frames. No run reaches the ±0.04 margin (the largest |*d*| is 0.019,
`sg0.32` seed 777), so all three conditions are none. The gates script also lists the NULL
conditions that are unmet (Φ(invert_all) = none, not Π). Those conditions apply only when
Φ(invert_matter) = L, so they change nothing here.

The reading was fixed before the runs and is repeated here. A none is
reported as none. Competing carriers, a regime change and too few signatures can each produce
it, and this design cannot tell them apart, so none of them is named as its cause. The
outcome is neither MOVED nor NULL. **This ring does not retire the detection-as-memory reading, and it gives no support to that reading either. It decides nothing about memory.** These two sentences only restate what the branch rules and the forbidden list already imply.

**The positive control was silent.** In `invert_all` the whole carried state is inverted,
which is a symmetry of the chamber's equations. That arm reached one Π-signature (`sg0.35`
seed 2718, *d* +0.063) and no L-signature, so its conditions read none, none, Π and its
preference is none. Eight of its nine runs are measurable in both frames. The ninth, `sg0.32`
seed 12345, has 11 eligible epochs, below the frozen floor of 12, in both frames. The
positive control existed to show that the pipeline can see a carried contrast in the inverted
frame. On these realisations it did not show that.

**The base rate of a none, as the pre-registration gave it** (control item 6; computed by
re-orienting the control's bytes, so a guide and not a guarantee): an arm that behaves like a
fresh realisation of the control reaches a preference about 3 times in 4. It is not read
toward either carrier, and nothing further is computed from it here.

### Every scored directory (the frozen scorer, unchanged)

A derived frame's verdict is a reading of that frame only. No directory's string is a
qualification except the `identity` directory's, and that one is V3. The `invert_matter`
directory's string "qualified" is listed because every directory's verdict string is reported.
It is not a qualification, and it is not read as evidence that the estimator had power on that
arm's fields.

| directory | inputs verified | measurable runs | conditions measurable | F1 | F2 | F3 evaluable / pass / median α*_eff | F4 | F5 (cell-epochs) | result |
|---|---|---:|---|---|---|---|---|---|---|
| `memory_intervention_identity` | yes | 9 | 3 | yes | yes | yes / yes / 0.0177 | yes | yes (146/198) | "qualified" |
| `memory_intervention_identity_frame_point` | yes | 9 | 3 | yes | yes | yes / yes / 0.0405 | yes | yes (146/198) | "qualified" |
| `memory_intervention_invert_all` | yes | 8 | 2 | yes | yes | yes / yes / 0.0392 | yes | no (124/198) | "insufficient support" |
| `memory_intervention_invert_all_frame_point` | yes | 8 | 2 | yes | yes | yes / yes / 0.0162 | yes | no (124/198) | "insufficient support" |
| `memory_intervention_invert_matter` | yes | 9 | 3 | yes | yes | yes / yes / 0.0161 | yes | yes (131/198) | "qualified" |
| `memory_intervention_invert_matter_frame_point` | yes | 9 | 3 | yes | yes | yes / yes / 0.0168 | yes | yes (131/198) | "qualified" |

F2 passes in every directory through the 2026-09-06 synthetic receipt. In F4, variant
`e2_pr16` has `measurable_both` 0 in all six directories, so it is vacuous there, as it was
in Ring 29. No F4 variant is unstable in any directory. One variant records one violation, within its allowance of one: `den_0.10` in `memory_intervention_invert_all_frame_point` loses the strong detection of `sg0.35` seed 2718 (p 0.0197, just below the strong threshold 0.02; the table rounds it to 0.020). That is the run with the F4 flag in the `invert_all` table.

### Every run, both frames

*d* = S_Π − S_L. A signature needs |*d*| ≥ 0.04 in a run that is measurable in both frames.
Eligible epochs and gate failures are identical in the two frames by construction (V2).

#### `identity` — preference **L**; conditions sg0.3 L, sg0.32 L, sg0.35 L

| run | frame | measurable | eligible | gate fails e1/e2/e3/e4 | S | p | CI95 (block bootstrap) | ρ₁(Q) | caveat | detected | F4 flag | d = S_Π − S_L | signature |
|---|---|---|---:|---|---:|---:|---|---:|---|---|---|---:|---|
| sg0.3 777 | L | yes | 19 | 3/2/0/0 | 0.042 | 0.022 | [-0.001, 0.084] | 0.43 | yes | yes | no | -0.065 | L |
|  | Π | yes | 19 | 3/2/0/0 | -0.022 | 0.925 | [-0.046, 0.000] | -0.09 | no | no | no |  |  |
| sg0.3 12345 | L | yes | 17 | 4/3/0/0 | 0.006 | 0.096 | [-0.011, 0.034] | 0.20 | no | no | no | -0.011 | - |
|  | Π | yes | 17 | 4/3/0/0 | -0.005 | 0.341 | [-0.008, 0.005] | 0.03 | no | no | no |  |  |
| sg0.3 31337 | L | yes | 17 | 3/5/0/0 | 0.035 | 0.002 | [0.013, 0.057] | -0.19 | no | yes | no | -0.050 | L |
|  | Π | yes | 17 | 3/5/0/0 | -0.014 | 0.969 | [-0.038, 0.021] | -0.06 | no | no | no |  |  |
| sg0.32 777 | L | yes | 16 | 2/5/0/0 | 0.033 | 0.004 | [0.007, 0.052] | 0.08 | no | yes | no | -0.061 | L |
|  | Π | yes | 16 | 2/5/0/0 | -0.028 | 0.985 | [-0.057, -0.001] | 0.12 | no | no | no |  |  |
| sg0.32 12345 | L | yes | 14 | 2/7/0/0 | -0.011 | 0.661 | [-0.052, 0.007] | -0.05 | no | no | no | 0.010 | - |
|  | Π | yes | 14 | 2/7/0/0 | -0.001 | 0.422 | [-0.002, 0.003] | -0.65 | no | no | no |  |  |
| sg0.32 31337 | L | yes | 14 | 1/8/0/0 | 0.009 | 0.384 | [-0.001, 0.024] | -0.14 | no | no | no | -0.011 | - |
|  | Π | yes | 14 | 1/8/0/0 | -0.002 | 0.345 | [-0.013, 0.014] | 0.03 | no | no | no |  |  |
| sg0.35 2718 | L | yes | 16 | 1/6/0/0 | 0.069 | 0.001 | [0.033, 0.114] | 0.24 | no | yes | no | -0.074 | L |
|  | Π | yes | 16 | 1/6/0/0 | -0.004 | 0.836 | [-0.047, 0.060] | -0.02 | no | no | no |  |  |
| sg0.35 16180 | L | yes | 17 | 1/4/0/0 | 0.046 | 0.215 | [0.012, 0.095] | 0.12 | no | no | no | -0.070 | L |
|  | Π | yes | 17 | 1/4/0/0 | -0.024 | 0.886 | [-0.070, 0.007] | -0.15 | no | no | no |  |  |
| sg0.35 57721 | L | yes | 16 | 1/5/0/0 | -0.010 | 0.336 | [-0.016, -0.001] | -0.16 | no | no | no | -0.000 | - |
|  | Π | yes | 16 | 1/5/0/0 | -0.010 | 0.450 | [-0.023, 0.001] | -0.05 | no | no | no |  |  |

#### `invert_all` — preference **none**; conditions sg0.3 none, sg0.32 none, sg0.35 Π

| run | frame | measurable | eligible | gate fails e1/e2/e3/e4 | S | p | CI95 (block bootstrap) | ρ₁(Q) | caveat | detected | F4 flag | d = S_Π − S_L | signature |
|---|---|---|---:|---|---:|---:|---|---:|---|---|---|---:|---|
| sg0.3 777 | L | yes | 14 | 3/6/0/0 | 0.003 | 0.240 | [-0.012, 0.022] | 0.32 | no | no | no | -0.001 | - |
|  | Π | yes | 14 | 3/6/0/0 | 0.002 | 0.526 | [-0.043, 0.042] | -0.19 | no | no | no |  |  |
| sg0.3 12345 | L | yes | 15 | 3/7/0/0 | -0.026 | 0.593 | [-0.123, 0.017] | 0.25 | no | no | no | 0.025 | - |
|  | Π | yes | 15 | 3/7/0/0 | -0.000 | 0.427 | [-0.045, 0.070] | -0.23 | no | no | no |  |  |
| sg0.3 31337 | L | yes | 17 | 1/5/0/0 | -0.007 | 0.489 | [-0.037, 0.012] | 0.14 | no | no | no | 0.021 | - |
|  | Π | yes | 17 | 1/5/0/0 | 0.015 | 0.032 | [0.003, 0.033] | 0.07 | no | no | no |  |  |
| sg0.32 777 | L | yes | 13 | 3/7/0/0 | -0.005 | 0.850 | [-0.011, 0.002] | -0.38 | no | no | no | 0.008 | - |
|  | Π | yes | 13 | 3/7/0/0 | 0.003 | 0.276 | [-0.004, 0.018] | 0.02 | no | no | no |  |  |
| sg0.32 12345 | L | no | 11 | 3/11/0/0 | – | – | – | – | – | – | no | – | unmeasured |
|  | Π | no | 11 | 3/11/0/0 | – | – | – | – | – | – | no |  |  |
| sg0.32 31337 | L | yes | 12 | 2/10/0/0 | -0.002 | 0.745 | [-0.014, 0.002] | 0.42 | no | no | no | -0.004 | - |
|  | Π | yes | 12 | 2/10/0/0 | -0.007 | 0.840 | [-0.022, 0.006] | -0.41 | no | no | no |  |  |
| sg0.35 2718 | L | yes | 17 | 0/5/0/0 | -0.029 | 0.999 | [-0.056, -0.008] | -0.20 | no | no | no | 0.063 | Π |
|  | Π | yes | 17 | 0/5/0/0 | 0.034 | 0.020 | [-0.006, 0.098] | 0.24 | no | yes | yes |  |  |
| sg0.35 16180 | L | yes | 13 | 2/7/3/0 | -0.009 | 0.599 | [-0.020, 0.003] | -0.15 | no | no | no | 0.008 | - |
|  | Π | yes | 13 | 2/7/3/0 | -0.001 | 0.263 | [-0.015, 0.005] | -0.32 | no | no | no |  |  |
| sg0.35 57721 | L | yes | 12 | 0/8/3/0 | -0.019 | 0.849 | [-0.034, -0.006] | -0.27 | no | no | no | 0.007 | - |
|  | Π | yes | 12 | 0/8/3/0 | -0.012 | 0.635 | [-0.041, 0.005] | -0.34 | no | no | no |  |  |

#### `invert_matter` — preference **none**; conditions sg0.3 none, sg0.32 none, sg0.35 none

| run | frame | measurable | eligible | gate fails e1/e2/e3/e4 | S | p | CI95 (block bootstrap) | ρ₁(Q) | caveat | detected | F4 flag | d = S_Π − S_L | signature |
|---|---|---|---:|---|---:|---:|---|---:|---|---|---|---:|---|
| sg0.3 777 | L | yes | 14 | 4/7/0/0 | 0.001 | 0.537 | [-0.012, 0.017] | -0.03 | no | no | no | -0.008 | - |
|  | Π | yes | 14 | 4/7/0/0 | -0.007 | 0.741 | [-0.031, 0.011] | -0.03 | no | no | no |  |  |
| sg0.3 12345 | L | yes | 15 | 3/6/0/0 | -0.006 | 0.889 | [-0.023, 0.005] | -0.19 | no | no | no | 0.003 | - |
|  | Π | yes | 15 | 3/6/0/0 | -0.003 | 0.535 | [-0.011, 0.008] | -0.27 | no | no | no |  |  |
| sg0.3 31337 | L | yes | 18 | 1/4/0/0 | -0.003 | 0.350 | [-0.009, 0.010] | -0.25 | no | no | no | 0.006 | - |
|  | Π | yes | 18 | 1/4/0/0 | 0.003 | 0.365 | [-0.020, 0.027] | -0.53 | no | no | no |  |  |
| sg0.32 777 | L | yes | 16 | 1/5/1/0 | -0.015 | 0.923 | [-0.033, -0.002] | -0.01 | no | no | no | 0.019 | - |
|  | Π | yes | 16 | 1/5/1/0 | 0.004 | 0.316 | [-0.011, 0.016] | -0.01 | no | no | no |  |  |
| sg0.32 12345 | L | yes | 13 | 2/9/1/0 | -0.015 | 0.948 | [-0.052, 0.007] | -0.37 | no | no | no | 0.003 | - |
|  | Π | yes | 13 | 2/9/1/0 | -0.012 | 0.612 | [-0.022, 0.008] | -0.33 | no | no | no |  |  |
| sg0.32 31337 | L | yes | 16 | 2/6/0/0 | 0.005 | 0.218 | [-0.020, 0.016] | -0.15 | no | no | no | -0.010 | - |
|  | Π | yes | 16 | 2/6/0/0 | -0.005 | 0.588 | [-0.033, 0.009] | -0.19 | no | no | no |  |  |
| sg0.35 2718 | L | yes | 12 | 2/8/2/0 | 0.002 | 0.120 | [-0.004, 0.007] | -0.28 | no | no | no | -0.015 | - |
|  | Π | yes | 12 | 2/8/2/0 | -0.013 | 0.990 | [-0.025, 0.001] | -0.11 | no | no | no |  |  |
| sg0.35 16180 | L | yes | 14 | 1/6/2/0 | -0.007 | 0.706 | [-0.014, -0.002] | -0.01 | no | no | no | 0.001 | - |
|  | Π | yes | 14 | 1/6/2/0 | -0.006 | 0.745 | [-0.014, 0.001] | -0.18 | no | no | no |  |  |
| sg0.35 57721 | L | yes | 13 | 1/8/2/0 | -0.005 | 0.704 | [-0.027, 0.005] | -0.01 | no | no | no | 0.001 | - |
|  | Π | yes | 13 | 1/8/2/0 | -0.004 | 0.601 | [-0.010, 0.005] | 0.29 | no | no | no |  |  |

Detection counts, reported as counts:

| arm | lab frame | inverted frame |
|---|---|---|
| `identity` | 4 (the four Ring 29 detections) | 0 |
| `invert_all` | 0 | 1 (`sg0.35` 2718, with an F4 flag) |
| `invert_matter` | 0 | 0 |

No detection is read as a property of its run.

### Reported, decides nothing

The numbers below were fixed as reported numbers. None of them is read as MOVED, NULL or a
lean. Each arm has its own table: no row holds two arms, and no number is compared across
arms or with the identity run of the same seed. O is the point-odd part of a run's own relic
correlation. For the `invert_all` run that is unmeasurable, O is computed over its 11
eligible epochs and was never scored.

#### `identity`

| run | O | same-sign (of 22) | hook s | non-finite |
|---|---:|---:|---:|---:|
| sg0.3 777 | 0.037 | 16 | 9.7 | 0 |
| sg0.3 12345 | 0.021 | 16 | 9.9 | 0 |
| sg0.3 31337 | 0.023 | 17 | 9.6 | 0 |
| sg0.32 777 | 0.011 | 16 | 10.1 | 0 |
| sg0.32 12345 | 0.008 | 18 | 10.0 | 0 |
| sg0.32 31337 | 0.018 | 16 | 9.9 | 0 |
| sg0.35 2718 | 0.033 | 21 | 10.3 | 0 |
| sg0.35 16180 | 0.059 | 20 | 10.2 | 0 |
| sg0.35 57721 | 0.014 | 17 | 10.1 | 0 |

#### `invert_all`

| run | O | same-sign (of 22) | hook s | non-finite |
|---|---:|---:|---:|---:|
| sg0.3 777 | -0.017 | 5 | 10.9 | 0 |
| sg0.3 12345 | -0.014 | 9 | 10.5 | 0 |
| sg0.3 31337 | -0.003 | 7 | 11.0 | 0 |
| sg0.32 777 | -0.009 | 6 | 10.6 | 0 |
| sg0.32 12345 | -0.026 | 6 | 10.4 | 0 |
| sg0.32 31337 | -0.006 | 4 | 11.0 | 0 |
| sg0.35 2718 | -0.024 | 4 | 11.2 | 0 |
| sg0.35 16180 | -0.011 | 2 | 11.4 | 0 |
| sg0.35 57721 | -0.002 | 4 | 11.3 | 0 |

#### `invert_matter`

| run | O | same-sign (of 22) | hook s | non-finite |
|---|---:|---:|---:|---:|
| sg0.3 777 | 0.001 | 11 | 10.7 | 0 |
| sg0.3 12345 | 0.001 | 10 | 10.4 | 0 |
| sg0.3 31337 | -0.013 | 12 | 10.6 | 0 |
| sg0.32 777 | -0.004 | 7 | 10.6 | 0 |
| sg0.32 12345 | -0.001 | 9 | 11.1 | 0 |
| sg0.32 31337 | 0.012 | 11 | 10.5 | 0 |
| sg0.35 2718 | 0.000 | 7 | 11.4 | 0 |
| sg0.35 16180 | -0.004 | 10 | 10.8 | 0 |
| sg0.35 57721 | 0.002 | 12 | 11.1 | 0 |

Per arm, the number of runs failing each gate, beside the identity arm's, as the
pre-registration asks (descriptive; decides nothing). A run counts once for a gate if at least
one of its epochs fails it.

| arm | E1 | E2 | E3 | E4 | E5 collapse | E5b unbalanced | measurable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `identity` | 9 | 9 | 0 | 0 | 0 | 0 | 9 |
| `invert_all` | 7 | 9 | 2 | 0 | 0 | 0 | 8 |
| `invert_matter` | 9 | 9 | 5 | 0 | 0 | 0 | 9 |

For every pair of seeds in a condition, `hemisphere.json` also records how many of the 22
scored meshes put the two seeds in the same hemisphere. Those counts are reported there and
not read here.

### A declared change after scoring (report-only, decides nothing)

The score script's last step runs two report-only diagnostics on each raw arm. By then the
decision, the gates and the branch had already been written. One of the two,
`experiments/halo/relic_component_decomposition.py` (committed at P; it computes O), stopped
on inputs the Ring 29 control never had:

- In one lag-one-eligible epoch of two runs, the frozen scorer recorded the lag-two row as
  JSON null: `invert_all` `sg0.3` 31337 and `invert_matter` `sg0.32` 31337, epoch 15 of
  each. The script's `mean()` already dropped NaN but not null.
- The one unmeasurable `invert_all` run has no recorded S or p.

The fix (in this commit) drops null the way NaN was already dropped, in `mean()` and in the two
stranger means that called `np.mean` directly, and writes None for the recorded S and p of a run
the scorer left unmeasurable. The frozen scorer writes every NaN as null. On every input without a null, its
output is byte-identical: the Ring 29 control and the `identity` arm both give `1cff7160…`,
equal to the file committed at P (`memory_intervention_design/control_components.json`).
`invert_matter` has one null, so it has no unfixed output to compare against. The second part
of the fix leaves its output unchanged at `39204941…`.

A test pins `mean()`'s null handling (`tests/halo/test_relic_component_mean.py`). The two stranger
means and the recorded S/p fallback in `main()` are covered by the byte comparisons above, not by the
test. The remaining
report-only commands were then run exactly as the score script writes them. The two
`hemisphere.json` files already written were re-run and came back unchanged.

### What changes, and what does not

- **Changes:**
  - The registered intervention has run to its end: 28 runs on the pinned instrument, every
    receipt and gate passing, and the pre-registered branch is NOT DECIDABLE. The planning
    metric, "intervention contrasts decided", stays at 0 of 1.
  - The intervention harness is shown to leave the chamber unchanged in `identity` mode: 10
    of 10 meshes are byte-identical to Ring 29, and every per-run number is equal (V3).
- **Does not change:**
  - Nothing about nested resonance memory.
  - The detection-as-memory reading is neither retired nor supported.
  - Ring 29's "qualified" still describes its nine recorded runs and nothing more.
  - No rerun, re-key, added seed, substituted arm or new threshold is scored in this ring.

### Files

Each directory's `manifest.json` pins the sha256 of every file it scored. The `*.mesh.f32`
files are gitignored; how to regenerate and re-check them is below.

| file | sha256 (first 16) |
|---|---|
| `memory_intervention_identity/` manifest · qualification | `dfdefedadcf80c5f` · `6359e7c55846f0cc` |
| `memory_intervention_identity_frame_point/` manifest · qualification | `daa57a2ecdac1c4a` · `7fae9ee3bbd38b19` |
| `memory_intervention_invert_all/` manifest · qualification | `ca1a5e0ea4e29232` · `885a25f529c18a80` |
| `memory_intervention_invert_all_frame_point/` manifest · qualification | `c241f1f45995f8fe` · `0da0376eadf28e78` |
| `memory_intervention_invert_matter/` manifest · qualification | `c9fda586dbe735b8` · `56e9dff77d6406db` |
| `memory_intervention_invert_matter_frame_point/` manifest · qualification | `b88eb8cf1b0c5cd4` · `6eac365a0289b009` |
| `memory_intervention_decision.json` · `memory_intervention_gates.json` | `c40df390e843c8be` · `1aa1f620d40a8a03` |
| `hemisphere.json`: identity · invert_all · invert_matter | `8870db2af48ed5b7` · `04b09fe45a07dbb4` · `cafb9761b8212f23` |
| `components.json`: identity · invert_all · invert_matter | `1cff71608f736cc2` · `897f0c1f783d9c90` · `39204941fd2eda8b` |

The ring on the page is a comment-only append: the source page's whole-file hash moves from
`827fac09` to `457cf783`, and `sim_digest` stays `40bfdb68` (recomputed with
`experiments/halo/instrument_identity.py`). The test page `tests/halo/rc-test.html` is
`1a15b987`, rebuilt from `f838e509` as described below.

### How a stranger re-checks this

- **Re-score a directory:**
  - Copy its nine run records and their meshes into a scratch directory.
  - Run the pre-registration's "Frames and scoring" commands there: manifest, staticness
    screen, frozen scorer.
  - Every scored leaf reproduces. Only leaves that record a path or a time differ.

  Scoring in place instead rewrites the committed files: the manifest builder then lists the
  outputs already in the directory as not manifested.
- **Regenerate the meshes (gitignored):**
  - Build the pinned test page first with
    `python3 tests/halo/make_test_page.py --from-git f838e509`. It gives `1a15b987…`.
  - The builder takes no `--help`. Run without `--from-git`, it rebuilds the page from the
    working tree and overwrites the pinned file, and the harness then refuses to start.
  - Then run each record's harness command (above, "Arms, seeds, directories, order,
    commands") with `--out` set to a scratch directory. That is about two minutes per run
    on the recording GPU.
  - Keep each mesh whose sha256 matches the directory's manifest.

  Byte-identical regeneration is shown at full scale for the identity arm (G0 and the closing
  run). For the inverting arms it is shown only at 65,536 particles, in the pre-flights.
- **Re-run the gates:**
  - With the meshes in place, derive the inverted frames (`memory_intervention_frames.py DIR
    --op point --out DIR_frame_point`).
  - Run `python3 experiments/halo/memory_intervention_gates.py --prereg-commit b5ae861c
    --json <scratch>/gates.json`. It prints the branch above and writes a file byte-identical
    to `memory_intervention_gates.json`.
  - Without the meshes it stops with `FileNotFoundError` before printing a gate.

### Kill-test

Five independent lenses re-derived the result from the files with their own code, read-only,
in one workflow. Any discrepancy a lens reported went to a second agent to reproduce.

- **Scorer reproduction: CONFIRMED.** The six directories were copied to fresh scratch
  directories, their manifests rebuilt and the frozen scorer re-run. Every verdict, run entry,
  F1–F5 field and F4 row is identical. The only leaves that differ record a path or the time of
  the run: the manifest's `input_dir` (and so the manifest's path and sha256 inside
  `qualification.json`), `measured_at` and `seconds`. The void record differs too: the
  repository's manifest lists it as not manifested, and the copy left it out. The decision re-derived from the reproduced files is identical.
- **Frames and rule, own code: CONFIRMED.** All 27 inverted-frame meshes are byte-identical to
  an independent flip of the odd-indexed meshes. Every derived record equals its source except
  for `mesh_file` and the added `derivation`. All 26 values of *d* (the 27th run, `invert_all` `sg0.32` 12345, is unmeasured in both frames
  and has none), every signature, condition label and preference, re-derived from the text's rule,
  equal the decision file. That file
  writes its internal code "X" for a Π-signature.
- **Provenance and order: CONFIRMED.** P reached the public remote at 09:36:40 UTC by
  GitHub's activity record. By local file times, that is 7 seconds before the harness created the
  first run's output folder and 2 minutes before the first record. Other findings:
  - 28 records and 644 hook records, with 0 receipt faults;
  - harness bytes equal to P's in all 28, and the five frozen hashes match;
  - `identity` and closing meshes equal to Ring 29's;
  - at most 27 particles moved by edge rounding in any inverting hook (the limit is 16,384);
  - one void, a crash with no page error;
  - the patched report-only script's output is unchanged on null-free inputs;
  - `sim_digest 40bfdb68` recomputed on the test page.
- **Gates and branch against the text: CONFIRMED.** The gates script re-ran byte-identical.
  V3 was checked independently: 10,832 numeric, boolean and null leaves, 0 differing, and all
  nine tags, each differing only by the `_ividentity` suffix. The branch was derived from the
  text alone: NOT DECIDABLE, with proximate cause Φ(invert_matter) = none. The lens listed 17
  places where the gate code looked looser or stricter than the pre-registered wording. The
  re-check confirmed 15 of them and refuted 2: a NaN comparison that cannot misfire on values
  `json.load` reads, and a density check that is exactly the text's. Examples of the 15:
  - V3 compares with Python equality rather than bit patterns;
  - V2's byte check runs one way only;
  - V5 is coded as "Π or none" rather than "not L";
  - the unmet NULL conditions are printed even when they do not apply.

  None of the 15 could change the branch on these data.
- **Diagnostics: CONFIRMED.** Both report-only scripts re-ran to identical files. The
  hemisphere same-sign counts were re-derived with independent code. The `identity` arm's
  decomposition is byte-identical to the one committed at P from the Ring 29 control.

Each reported discrepancy was reproduced by a second agent. Each traced to a path, a label
or the copy rule, and none touches a number the decision reads.

**Review of this write-up, before commit.** Four more lenses read the new text against the
pre-registration and the files: overclaim, numbers, rails and format, and a stranger's
reproduction. They found two blockers and about a dozen distinct major faults, all fixed
above:

- A table set each identity run beside the intervened runs of its seed. That is the banned
  comparison in form, so it is now three per-arm tables.
- A sentence said no F4 variant records a violation. `den_0.10` loses one strong detection,
  within its allowance.
- Carrier-conditional base rates invited a lean. Only the base rate of a none is kept.
- The `invert_matter` "qualified" was glossed like a qualification.
- The README gave the silent positive control as the cause.
- The count said 27 values of *d*; 26 exist.
- A before-and-after byte identity was claimed for a file the unfixed script cannot produce.
- The test's scope was overstated.
- Nothing said how to rebuild the pinned test page (`--from-git f838e509`), and nothing warned
  that re-scoring in place or re-running the gates on a fresh clone fails.

Minor fixes added time zones, `git_dirty`, the runtime platform and the full banned list.
