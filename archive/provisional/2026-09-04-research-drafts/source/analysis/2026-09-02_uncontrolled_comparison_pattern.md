# Two headline results, one defect: the winning arm differed in more than one variable

**Date:** 2026-09-02 · **Method:** run the missing control, not re-read the conclusion.

Two of this archive's strongest claims were re-tested by adding the one control each was
missing. **Both fell.** They fell the same way, and that shared shape is the finding.

---

## 1. "Transcendental driving beats commensurate and random"

Missing control: **the coupling constant was never swept.**

Survival requires phase-locking, which requires `min(driving frequency) < H`. The published run
used H = 1.5. The rational triple's lowest frequency is *exactly* 1.5; the transcendental
triple's is φ = 1.618. Sweep H and the winner flips (H=1.5 → rational 0.269 / transcendental
0.000; H ≥ 2.0 → both 1.000). Against matched random-incommensurate triples, commensurability
is **undetectable** (p = 0.17, p = 0.32).

**Replacement law:** `min(f) < H` predicts survive/extinct on **42/42 triples**, 100% within
each of three families. Full write-up: `analysis/2026-09-02_phase_locking_governs_survival.md`.

## 2. "Hebbian structural plasticity raises synchronization"

Missing control: **edge count.**

`archive/experiments/tests/structural_evolution_test.py` — textbook graph Kuramoto, real order
parameter `R = |⟨e^{iθ}⟩|`, ω ~ N(0, 0.5). The reported effect **replicates and strengthens**
under paired seeds (same ω, same initial phases, same initial graph; only rewiring differs):

| | R |
|---|---|
| static topology | 0.1703 ± 0.1096 |
| dynamic (Hebbian rewiring) | 0.3813 ± 0.1624 |

paired t = **+6.92**, p = 2.8e-08, 34/40 seeds, Cohen's dz = 1.11.

**But the dynamic arm ends with 598 edges against the static arm's 233.** In Kuramoto, R rises
with mean degree, so the arms differ in *two* variables: the rewiring rule and the density it
produces. Against a **random static graph with the same final edge count**:

| | R |
|---|---|
| Hebbian-rewired | 0.3813 ± 0.1624 |
| random, same edges | **0.5082 ± 0.2201** |

paired t = **−4.49**, p = 6.2e-05, Wilcoxon p = 6.7e-05, Hebbian wins **8/40** seeds,
Cohen's dz = −0.72.

**The effect is density, not structure — and once density is held fixed, Hebbian rewiring is
significantly WORSE than random wiring.**

### The mechanism, and why it is the more interesting result

"Sync together, link together" adds edges among already-synchronized agents and prunes edges to
desynchronized ones. That is a **modularity-building rule**: it grows densely-connected local
communities and severs the long-range links that would couple them. Local coherence rises;
*global* coherence falls, because the network fragments into well-synced clusters that cannot
see each other. A random graph at the same density spends its edges on long-range connections
and synchronizes better.

Stated positively: **Hebbian phase-based rewiring trades global coherence for modular
structure.** That is a real, counterintuitive, testable claim about when local learning rules
help and when they fragment a system — and it sits closer to work on modularity and multi-scale
individuality than the original "plasticity helps sync" framing ever did.

---

## The pattern (the actual deliverable)

Both failures have one shape:

> **The winning arm differed from the losing arm in more than one variable, so the reported
> cause was never isolated.** Transcendental vs rational differed in commensurability *and* in
> whether `min(f) < H`. Dynamic vs static differed in the rewiring rule *and* in edge count.

Neither is fraud and neither is a coding error — the code does what it says. The experiments
are simply **under-controlled**, and the write-ups then name the variable the author was
interested in as the cause.

**What "recharge the archive" concretely means:** for every comparative claim, state what the
arms differ in and add a control that matches everything except the named variable. That is
mechanical, it needs no new theory, and it is the difference between this archive and a
notebook of plausible stories.

<!-- ═══ RINGS — append-only. Any agent opening this file reads these first. ═══

RING 1
DATE: 2026-09-02
WHAT CHANGED: Re-tested the archive's two strongest comparative claims by adding the single
  control each lacked. Both fell. Extracted the shared defect — arms differing in more than
  one variable — as a methodological finding with a mechanical fix.
BANNED: "the old AI was bad", "the p-values were wrong", "N was too small", "it's a toy model",
  "the author overclaimed". All five stop the search before the mechanism, and none of them
  is actionable.
DEAD BRANCHES: (a) Reporting the structural-evolution result as a WIN — it replicates at
  p=2.8e-08 and would have been the headline, but the arms differ in edge count and the whole
  effect is density. Publishing it would have been the transcendental mistake repeated inside
  the very document correcting the transcendental mistake. (b) Treating the two failures as
  independent — they share one shape, and the shape is worth more than either result.
  (c) Blaming the pairwise-coherence proxy in nrm_core/fractal.py — it IS mislabelled
  (a 1-|dphi|/pi average reported as "coherence", not the Kuramoto order parameter), but
  structural_evolution_test.py uses the REAL order parameter and still fails the control, so
  the metric is not what is carrying the error.
KILL-TEST: this dies if a degree-matched random graph is shown to be an unfair control — e.g.
  if Hebbian rewiring produces a degree DISTRIBUTION whose difference from Erdos-Renyi is the
  point rather than a confound. Test: match degree sequence, not just edge count, and re-run.
  Until that is done, "density explains it" is the strongest supported statement, not the
  final one.
THE NON-OBVIOUS CHOICE: paired seeds. The original compared arms across independent runs, so
  between-seed variance (std ~0.10-0.22) swamped a real within-seed effect. Pairing on
  (omega, initial phases, initial graph) raised t from +3.72 to +6.92 on the same claim — and
  then made the degree-matched refutation unambiguous too. Pairing helped BOTH directions;
  it is not a trick for getting significance.
OPEN QUESTIONS: (1) Degree-sequence-matched control, per the kill-test. (2) Does the
  modularity reading hold — measure Newman modularity Q and mean path length on the rewired
  graphs; the claim predicts Q rises and global R falls together. (3) Sweep the same
  uncontrolled-comparison check across the other ~2,000 experiment files; two for two is not
  a base rate. (4) Only 4 of 2005 files in experiments/ are Kuramoto experiments, and all four
  were committed 2026-06-26 — AFTER the Oct-2025 email that described this work to Levin.
═══ end rings ═══ -->
