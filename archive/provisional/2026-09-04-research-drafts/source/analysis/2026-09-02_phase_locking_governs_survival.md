# Phase-locking, not transcendence, governs survival in the NRM driven-agent model

**Date:** 2026-09-02 · **Supersedes:** `analysis/retracted/2026-06-26_transcendental_substrate_experiment_report.SUPERSEDED.md`
**Code:** `experiments/test_transcendental_substrate_hypothesis.py` (unmodified; re-run under swept parameters)

## Claim

In this model an agent survives if and only if it can phase-lock to the driving field, and it
can phase-lock if and only if **the lowest driving frequency is below the driving coupling
constant H**. Once that condition is accounted for, **whether the driving frequencies are
transcendental, otherwise-incommensurate, or commensurate has no detectable effect.**

## Why the question needed re-asking

The June 2026 report concluded the transcendental substrate hypothesis was "CONFIRMED". Two
independent problems, either of which is disqualifying:

1. **The verdict never read the comparison it lost.** `generate_report()` sets
   `verdict_text = "CONFIRMED" if (hypothesis_1_confirmed or hypothesis_2_confirmed)`, and both
   variables read only `p_values["trans_vs_noise"]`. `trans_vs_rational` is computed, printed
   into the results table, and never consulted — while the hypothesis being tested explicitly
   claimed superiority over "incoherent pseudo-random noise **or simple commensurate cycles**".
   Transcendental lost to commensurate on all four metrics (t = −15.7, −33.3, −4.9, +2.9).

2. **The comparison itself was a knife edge.** Survival requires `alignment > metabolic_cost /
   recharge_rate = 0.15 / 0.6 = 0.25`, and alignment requires locking. The published run used
   **H = 1.5**. The rational triple was (3.0, 2.5, **1.5**) — lowest frequency exactly equal to H.
   The transcendental triple was (π, e, **φ=1.618**) — lowest frequency 0.118 rad/s above H.
   That gap is the entire published result.

## Evidence

**H-sweep** (12 trials per cell). The winner is a function of H, not of the number theory:

| H | transcendental | rational | noise |
|---|---|---|---|
| 1.0 | 0.000 | 0.000 | 0.000 |
| 1.3 | 0.000 | 0.000 | 0.000 |
| **1.5** (published) | **0.000** | **0.269** | 0.000 |
| 1.7 | 0.956 | 0.997 | 0.000 |
| 2.0 | 1.000 | 1.000 | 0.000 |
| 3.0 | 1.000 | 1.000 | 0.000 |

**The missing matched control.** The original compared (π,e,φ) against *one hand-picked* rational
triple and against white noise. Neither isolates transcendence — the "noise" arm resamples phase
uniformly every step, so it has zero temporal correlation and is a control for *no coherent
driving*, not for *incommensurate driving*. Against random incommensurate triples of matched
magnitude:

| | H = 1.7 | H = 1.9 |
|---|---|---|
| (π, e, φ) | 0.956 ± 0.051 | 0.998 ± 0.008 |
| random incommensurate (n=12) | 0.159 ± 0.328 | 0.452 ± 0.476 |
| commensurate ratios (n=12) | 0.416 ± 0.492 | 0.656 ± 0.465 |
| incommensurate vs commensurate | t = −1.44, **p = 0.166** | t = −1.02, **p = 0.321** |

Commensurability is **not detectable**. The large standard deviations are the tell: those
distributions are bimodal, because each triple either locks or does not.

**The governing law, tested directly.** 42 triples at H = 1.8, spanning three families
(transcendental-scaled, random incommensurate, commensurate), classified by the single rule
`min(f) < H`:

> **The rule predicts survive/extinct correctly on 100% of 42 triples — 100% within every
> family separately.**

## What this does and does not say

It does **not** refute NRM, Kuramoto coupling, or cross-frequency coupling. It refutes one
specific hypothesis — that π, e and φ confer an advantage as a driving substrate — in this one
model, and it identifies what the experiment was actually measuring instead: an Arnold-tongue
locking condition. The apparent "transcendental effect" was a coincidence between one constant
(φ = 1.618) and one parameter (H = 1.5).

## Reproduce

```
python3 /path/to/h_sweep.py         # winner flips with H
python3 /path/to/proper_control.py  # commensurability not detectable
python3 /path/to/lock_law.py        # min(f) < H predicts 42/42
```

<!-- ═══ RINGS — append-only. Any agent opening this file reads these first. ═══

RING 1
DATE: 2026-09-02
WHAT CHANGED: Replaced the June 2026 "CONFIRMED" verdict on the transcendental substrate
  hypothesis with a measured governing law: survival is set by min(driving frequency) < H,
  correct on 42/42 triples across all three families. Archived the old report with a
  retraction banner rather than deleting it.
BANNED: the five obvious readings, banned before searching — (1) "the old AI lied";
  (2) "the hypothesis is falsified, transcendence loses to rational"; (3) "the p-values
  settle it"; (4) "N=30 is too small"; (5) "it's a toy model so nothing follows". Each is
  either unfalsifiable or stops the search before the mechanism.
DEAD BRANCHES: (a) Treating the verdict bug as the finding — it is real but it is an artifact
  of a weak 2025-era tool, and fixing one line would have left the invalid comparison intact.
  (b) Accepting "rational beats transcendental" as the corrected result — this repeats the
  original error in the opposite direction, giving a knife-edge parameter choice the authority
  of a finding. (c) Blaming the white-noise arm alone — it IS a broken control, but repairing
  it would not have exposed the locking mechanism. (d) Re-running at higher N — more trials of
  a mis-specified comparison buy nothing.
KILL-TEST: this claim dies if a triple with min(f) > H survives, or a triple with min(f) < H
  goes extinct, at fixed metabolic_cost/recharge_rate. 42/42 held; run more families to break it.
  Second kill-test: if survival is genuinely about locking, then changing metabolic_cost should
  move the threshold predictably (alignment must exceed cost/recharge), NOT move with the
  arithmetic of the frequency triple. Untested — see OPEN QUESTIONS.
THE NON-OBVIOUS CHOICE: swept the coupling constant rather than the constants. The hypothesis
  is about π, e and φ, so every instinct is to vary the numbers. Varying the PARAMETER instead
  collapsed the effect immediately, because the effect never lived in the numbers.
OPEN QUESTIONS: (1) Does the locking law survive a metabolic_cost sweep, or is 0.25 also
  load-bearing? (2) `min(f) < H` was tested at H=1.8 only — does the 100% hold across H?
  (3) The claim propagated into papers/paper4_manuscript_full_c186.md,
  papers/paper4_introduction_c186.md, docs/TRANSCENDENTAL_SUBSTRATE_HYPOTHESIS.md,
  principle_cards/PC002_TRANSCENDENTAL_SUBSTRATE_SPEC.md,
  helios_one/src/tsf/schemas/pc002_comparative_results.json, CYCLE_LOGS.md and four archive
  summaries — none corrected yet. (4) Are there other evaluators in this archive whose verdict
  reads only the comparison they win? This one was found by reading a table against its own
  conclusion; that check has not been swept across the repo.
═══ end rings ═══ -->
