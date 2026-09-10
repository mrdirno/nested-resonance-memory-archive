# The question ring 17 left could not be answered from the recorded data, and the record that could not name its instrument was naming it by accident

**Author:** Aldrin Payopay · **Date:** 2026-09-09 · **Licence:** GPL-3.0-only

**Inputs (unchanged, read-only):** [`qualification.json`](../data/results/halo/memory_estimator_qualification/qualification.json) (60 runs) · [`scn_qualification.json`](../data/results/halo/memory_pilot/scn_qualification.json) (21 runs) · [`reproduction_probe.json`](../data/results/halo/memory_pilot/reproduction_probe.json) (ring 17's labelled set) · the 81 raw run records in `data/results/halo/memory_prereg/` and `data/results/halo/memory_pilot/scn/`
**New tools:** [`instrument_identity.py`](../experiments/halo/instrument_identity.py) · [`instrument_stamp_audit.py`](../experiments/halo/instrument_stamp_audit.py)
**Receipt:** [`instrument_identity.json`](../data/results/halo/instrument_identity.json)
**No new simulation was run.** Every number below comes from files already in this repository.

---

## 1. What was asked, and what came back

Ring 17 sealed on 2026-09-07 with three open questions. Two of them were meant to be
answerable without registering another grid:

> **Q1.** How much of "measurable" is a threshold crossing on realisation noise, when six
> draws of the best condition spread 2.80 eligible epochs against a floor of 12?
>
> **Q2.** What must a run record carry — starting with the sha256 of the instrument that
> drove it — for a grid to be regenerable at all?

**Q1 cannot be answered from the recorded data, and the reason is a property of the design
rather than a shortage of runs.** The answer is not a number; it is that the quantity is not
identified. §2.

**Q2's answer turns out to be already half-written, twice.** The build was pinned publicly
four days before ring 17 recovered it by re-running, and every record has been carrying a
two-class instrument fingerprint by accident, through a bug. §4, §5.

Two claims are retired: ring 17's "six independent draws" (§2), and "F4 pass" in both scored
arms (§3). One public sentence is corrected: the README's priority claim (§4).

---

## 2. Q1: the quantity ring 17 asked about is not identified in this programme

### 2.1 There is no realisation to vary

Ring 17 read six values — spinchladni sg 0.3 gl 0 at 6, 6, 3 eligible epochs recorded and
10, 10, 9 re-run — as "six independent draws", and reported mean 7.33, sd 2.80, with the
measurability floor of 12 sitting 1.66 sd away. **The arithmetic is right.** Recomputed from
[6, 6, 3, 10, 10, 9]: mean 7.3333, sample sd 2.8048, (12 − 7.3333)/2.8048 = 1.6638.

The label is wrong. Those are **three seeds scored under two instruments**, not six draws.
Matched by seed, every one moved the same way: 777 6→10, 12345 6→10, 31337 3→9, differences
+4, +4, +6. Of the twenty possible ways to split six numbers into two groups of three, the
observed split is the single most extreme, exact one-sided p = 0.05.

Across the whole programme, **exactly two conditions were ever run twice** — spinchladni
sg 0.15 gl 0 ([0,0,0] → [1,1,1]) and spinchladni sg 0.3 gl 0 ([6,6,3] → [10,10,9]) — and
**both changed instrument at the same moment they were re-run.** No condition anywhere has
two realisations on one instrument. Realisation and instrument are perfectly confounded by
construction, so any split of that spread between them estimates an unidentified quantity.
No point estimate of that split is published here, and ring 17's should not be relied on.

The instrument is also bit-deterministic where it was tested: ring 17's "immediate repeat"
control returns the same sha256 as the arm run of the same tag. On the one tag and one pair
where it was measured, repeating a run varies nothing at all.

### 2.2 The three seeds are not three draws either

The frozen gates are not computed per run. E2's clause requires the participation ratio and
residual variance of **all three** predicted fields; E3 reads the shared 3×3 template
correlation matrix; E4 requires all nine of its entries finite
(`experiments/halo/memory_estimator_qualify.py`). Only E1, and the current-field half of E2,
are run-specific.

Measured over the 27 conditions that have three seeds, 22 scored epochs each — **594
condition-epoch cells**:

| the three seeds' eligibility flags | cells | share |
|---|---:|---:|
| all three agree | 568 | 95.6 % |
| — of which all three refused together | 506 | 85.2 % |
| the seeds disagree | 26 | 4.4 % |

So the effective number of independent draws per (condition, arm) is close to one, not three.
A pooled within-condition standard deviation computed across seeds, and any operating
characteristic built on it, would be measuring a shared object three times.

### 2.3 And the threshold Q1 asks about is not the binding gate

**Six of the 81 runs already clear the 12-epoch floor**, and none of them is measurable:

| run | eligible epochs | measurable | E5 collapse | E5b unbalanced |
|---|---:|---|---|---|
| default sg 0.3 gl 0 seed 777 | 19 | no | no | **yes** |
| default sg 0.3 gl 0 seed 12345 | 17 | no | no | **yes** |
| default sg 0.3 gl 0 seed 31337 | 17 | no | no | **yes** |
| default sg 0.5 gl 0 seed 777 | 15 | no | no | **yes** |
| default sg 0.5 gl 0 seed 12345 | 15 | no | no | **yes** |
| default sg 0.5 gl 0 seed 31337 | 15 | no | no | **yes** |

Two whole conditions would commission on epoch count alone. Both are refused by **E5b, the
seed-balance gate** — the gate ring 16 already flagged as fragile because it can turn on the
sign of a null value within one standard error of zero. Characterising the ≥12 rule would have
characterised a gate that is not stopping anything. (Ring 16 states this in prose; it is
restated here because Q1 was written as though the threshold were the obstacle.)

The rest of the distribution is heavily censored: **43 of 81 runs sit at exactly 0 eligible
epochs**, and the median run has 0.

**What would answer Q1.** One condition, one instrument, at least two independent realisations
— which for this estimator means at least two independent *triples*, since a triple is the
unit the gates act on. That is a new arm, and it is not run here.

---

## 3. A claim retired: "F4 pass" is vacuous in both scored arms

Both scored files report `verdict.F4_robustness.pass = true`, and both rings and the README
carry it forward. The tolerance rule, quoted from the files themselves, is

> `violations <= max(1, ceil(0.05 * runs measurable under both))`

and **`measurable_both` is 0 in all 11 variants of both arms — 22 of 22 rows.** With no run
measurable under both the main configuration and a variant, no variant can register a
violation, so F4 passes by construction whenever the main configuration yields nothing.

The robustness gate is blind in exactly the regime the programme has been in since 2026-09-06.
It should be read as **not evaluable**, never as evidence that the result is threshold-robust.

This changes no scored number. It removes a supporting claim from three published statements.

---

## 4. Q2, part one: the pin already existed, and the README says otherwise

`README.md` says of ring 17's seven controlled re-runs that they produced "the first record of
which build produced it". They did not.

`analysis/2026-09-02_cross_epoch_memory_preregistered.md` §13 has carried the build, by
revision **and** by checksum, since commit `155cf805` on **2026-09-03 16:19:55 −0700** — four
days before ring 17 — including the same traps ring 17 rediscovered ("Do not use `--from-git
HEAD`"; today's builder cannot rebuild that instrument at any revision):

```
git show 5cb08e51:tests/halo/make_test_page.py > _mtp_5cb08e51.py
python3 _mtp_5cb08e51.py --from-git 5cb08e51      # THE instrument
md5 rc-test.html                                  # must read e91d5a1d44a1dde519195e4e925fa515
```

`155cf805` is an ancestor of the ring-17 seal `9e7e67c5`, and ring 17 did not touch that file.
The chamber page at `c6cd2cbe` and at `5cb08e51` is byte-identical (`e3736b4c3b99dead…`), so
ring 17's winning control "page c6cd2cbe, builder 5cb08e51" **is** the recipe already written
down. The README sentence is corrected in this commit.

Two notes of care. That pinned md5 belongs to the *rebuilt* old instrument, not to whatever
`tests/halo/rc-test.html` happens to hold: today's build product is a different file
(`6034b2c9…` before this cycle's page edit), and reading the live file as if it were the pin is
a trap this cycle walked into once and caught. And ring 17's receipt licenses less than "the
simulation is reproducible to the byte": it covers **one tag**, and only one of its seven
controls is an actual repeat. The README's wording on that is narrowed too.

---

## 5. Q2, part two: the record has been fingerprinting its instrument by accident

### 5.1 The designed pin, and why a file hash is the wrong one

The chamber carries every sealed ring as one HTML comment, so publishing prose changes the
page's sha256 while changing no simulation. Scored against ring 17's labelled set — four page
revisions in two known behavioural classes:

| identity function | classes produced | wanted | verdict |
|---|---:|---:|---|
| whole-file sha256 of the page | 4 | 2 | **over-reports** |
| `sim_digest` (GLSL + named physics constants + driven presets + `DEFAULTS`) | 2 | 2 | **reproduces the partition** |

`sim_digest` class A = `40bfdb685f82902a…` for `{ring-17 HEAD, 122d0a57, 05dfa4ab}`,
class B = `bf9bd0c373bae727…` for `{c6cd2cbe}` — the build that reproduces the recorded grid.
Two controls, both in the self-test:

* appending ring 17's own comment to the page (`43e5081f` → `9e7e67c5`) leaves `sim_digest`
  unchanged and moves the whole-file sha256;
* **this cycle's own page edit** (§5.3) moves the page from `0fbc8201…` to `b073aa69…` and
  leaves `sim_digest` at `40bfdb68…`.

What ring 13 actually changed is worth stating, because it is not arithmetic: every executed
GLSL function on the default path is byte-identical across it. Two new runtime branches and a
shader refactor make the GPU compile a *different program*, and the two classes are different
trajectories rather than the same one rounded differently — ring 17's own per-epoch
correlations between the classes run from −0.0067 to 0.9957 and end at 0.5135.

**What `sim_digest` does not cover:** JavaScript outside the named constants and `DEFAULTS`. A
change to the tick loop alone does not move it. It is an identity for the GPU program and the
drive, not for the whole page, and a run record must therefore carry the page bytes and the
revision as well — which is what §5.3 does.

### 5.2 The accidental pin, and the bug that made it

`tests/halo/memory_prereg_run.js:170` hardcoded `csv_head` as a 22-name string literal while
`csv_rows` was read live from the page. Ring 13 widened the page's lab-log row from 22 fields
to 28 and the literal did not move. Measured over all 81 records:

| arm | runs | header names | row width | rows | unnamed columns |
|---|---:|---:|---:|---:|---:|
| recorded grid | 60 | 22 | 22 | 14,160 | 0 |
| measurability pilot | 21 | 22 | **28** | 4,956 | **6** |

No run mixes widths, and the split is exactly the class-B / class-A boundary of the labelled
set. So the record *could* always tell you which of the two instruments made it — to two-class
resolution, by accident, through a defect.

The defect is not only a missing name. In the pilot arm the header's 22nd name is `substeps`,
and the 22nd field of the row holds a conservation-ledger value: the published header
**mislabels** the data it heads.

### 5.3 What was changed so the next run does not need this

*The page* now has one lab-log name list. It used to live inside `exportLabLog()` where
nothing else could read it, which is why the harness carried a copy at all; it is hoisted to
`LAB_LOG_HEAD` and exposed through the test probe. Verified in a browser: the probe serves 28
names, and the six formerly-unnamed columns are `H, dH_H0, L, wall_took, substeps, vol_rate,
vol_pred`, with 0 page errors.

*The harness* now takes the header from the page, **refuses to write a record whose header
mislabels its own rows**, and records an `instrument` block: the test page and shipped page
sha256, the builder, the harness, three.js, the git revision and dirty flag, and the
Playwright, browser and Node versions.

The schema string stays `halo-memory-prereg/1` deliberately. The frozen scorer rejects any
other value (`memory_estimator_qualify.py:550`) and patching a frozen script is not permitted,
so the instrument block is an **added key**, not a new schema. Every existing record still
scores unchanged.

### 5.4 What the record still cannot do

**Six tags appear in both arms with byte-identical recorded parameters and different mesh
hashes.** Same preset, same self-gravity, same gain/loss, same seed, same particle count,
same `applied.cosmos` — different output. The run record has never been a sufficient key for
its own output, and that is the sharpest available statement of what Q2 was asking.

### 5.5 One more provenance hole, reported not repaired

`qualification.json` records `inputs.manifest_check` naming
`experiments/results/halo/memory_estimator_qualification/input-provenance.json` with a
sha256 and `verified: true`. **That file does not exist and has never been tracked in Git.**
The check matched 18 entries; `inputs.files` lists 120. So a published `verified: true` covers
18 of 120 inputs and points at an artefact nobody can obtain. Nothing is patched here: the
scored numbers are unaffected, and the missing manifest is the evidence.

---

## 5.6 Correction, same day: what the gate did when this cycle's own commit ran

This section was written after §5.3–5.5 shipped, because the gate they describe
reported on the commit that contains them. Run `34438166745`:

* **`instrument (release)` passed**, 10 m 52 s, smoke at **136 ok, 0 fail, 0 skip**,
  including `ok: saved camera survived the reload (storage, not the page)`. The
  runner's `file://` store **survived this time**, having been lost identically on
  two earlier runs. So the loss is **intermittent**, not the deterministic
  ubuntu-latest property the earlier wording implies. The added assertion did what
  it was for — it would have caught a recurrence — but it also let the job pass,
  which is not what was predicted.
* **`instrument (physics)` reached its own checks for the first time in four runs.**
  The `packages.microsoft.com` 403 that had been taking it down was a flake, not a
  standing break; Chromium installed cleanly. It then failed exactly one assertion,
  and **the fault was this cycle's**: `conserve_test.js` verifies "the Lab log row
  has exactly as many columns as the CSV header" by scraping the page for
  `const head = '…'` — a third copy of the name list, kept as a regex — and §5.3's
  hoist sent it to `headCols: 0`. `integ_test` (28/28) and `mesh_test` (35/35) passed.

That same assertion read `cols 28, headCols 28` on the last green physics run, which
independently confirms §5.2: the **page** was self-consistent all along at 28 names
over 28 columns, and only the harness's hardcoded copy had frozen at 22. The guard is
now read through the probe with a fallback to either constant name, so it no longer
carries a copy of the list either: `conserve_test` 47 passed, 0 failed locally.

The cycle removed one duplicated name list and was immediately caught by a third one
it had not gone looking for. That is the strongest available argument for §5.3's
direction and against trusting any count of how many copies remain.

## 6. Limitations

* Nothing here measures memory. No estimator was run, no scored number moved, and nothing
  about nested resonance memory is decided in either direction.
* The class-B stamp for the recorded grid rests on **one tag** reproducing byte for byte in
  ring 17's receipt. The other 59 recorded runs are stamped by shared provenance, not by
  re-running them.
* `sim_digest` was validated on a labelled set of **four** page revisions in two classes. It
  reproduces that partition and survives a prose-only control; it is not proven correct on
  revisions outside it, and it deliberately does not cover most JavaScript.
* The 95.6 % seed-agreement figure describes eligibility flags, not the scored statistic.
* §2's claim that no condition has two realisations on one instrument is a statement about
  this programme's recorded arms, not about what is possible.
* The two arms were scored by the same frozen script, but made by different instruments; that
  is the confound §2 is about, and it is not removed anywhere in this document.

---

## 7. Reproduction

```bash
python3 experiments/halo/instrument_identity.py --self-test
python3 experiments/halo/instrument_stamp_audit.py
```

The first reproduces ring 17's two-class partition from the committed pages alone and runs the
prose-only control. The second writes
`data/results/halo/instrument_identity.json` and prints the class counts, the per-arm header
and row widths, and the both-arms tag collisions. Neither needs a GPU, a browser or a network.

The tables in §2 come from `runs[].lag1` and `runs[].epochs[].eligible` in the two scored
files; §3 from `verdict.F4_robustness.rows`; §4 from `git log -S` on the pinned checksum.
