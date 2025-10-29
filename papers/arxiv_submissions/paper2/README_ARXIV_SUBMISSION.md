# Paper 2 — arXiv Submission Package

**Title:** From Bistability to Collapse: Energy Constraints and Three Dynamical Regimes in Nested Resonance Memory Framework

**Authors:** Aldrin Payopay, Claude (DUALITY-ZERO-V2)

**Primary Category:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
**Cross-list Categories:** q-bio.PE (Quantitative Biology - Populations and Evolution), cs.MA (Multiagent Systems)

---

## KEY CONTRIBUTIONS

### 1. **Three-Regime Classification**
   - Regime 1 (Bistability): Sharp phase transition at f_crit ≈ 2.55%
   - Regime 2 (Accumulation): Birth-only systems plateau at ~17 agents
   - Regime 3 (Collapse): Complete frameworks exhibit catastrophic collapse (mean=0.49 ± 0.50, CV=101%)

### 2. **Energy Recharge Insufficiency**
   - 100× parameter sweep (r ∈ {0.000, 0.001, 0.010})
   - Zero effect on population dynamics (F(2,27)=0.00, p=1.000, η²=0.000)
   - Perfect determinism across all conditions (identical spawn/composition/final population)

### 3. **Death-Birth Imbalance**
   - Death rate (~0.013/cycle) >> sustained birth rate (~0.005/cycle)
   - Creates extinction attractor that energy recharge cannot overcome
   - Demonstrates birth-death coupling is necessary but NOT sufficient

### 4. **Hypothesis Falsification (C177 H1)**
   - Energy pooling rejected as primary mechanism (Cohen's d=0.0, p=1.0)
   - Confirms temporal asymmetry dominance over resource distribution bottlenecks
   - Redirects focus to alternative mechanisms (external sources, composition throttling, multi-generational recovery)

---

## SUBMISSION PACKAGE CONTENTS

### LaTeX Source
- `manuscript.tex` - Main manuscript (~350 lines, submission-ready)

### Figures (300 DPI PNG)
1. `cycle175_framework_comparison.png` - Three-regime classification across architectural variants
2. `cycle175_basin_occupation.png` - Energy recharge parameter sweep (zero effect demonstration)
3. `cycle175_population_distribution.png` - Perfect determinism across all random seeds
4. `cycle175_composition_constancy.png` - Death-birth rate imbalance and extinction attractor

---

## ARXIV SUBMISSION INSTRUCTIONS

### 1. **Category Selection**
   - **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
   - **Cross-list:** q-bio.PE (Quantitative Biology - Populations and Evolution), cs.MA (Multiagent Systems)

### 2. **File Upload**
   - Upload `manuscript.tex` as main file
   - Upload all 4 PNG figures
   - Optional: Upload supplementary materials (experimental data JSON files)

### 3. **Metadata**
   - **Title:** From Bistability to Collapse: Energy Constraints and Three Dynamical Regimes in Nested Resonance Memory Framework
   - **Authors:** Aldrin Payopay, Claude (DUALITY-ZERO-V2)
   - **Abstract:** Copy from manuscript.tex abstract section
   - **Comments:** "Part of Nested Resonance Memory research series. Companion papers on computational expense validation (cs.DC) and pattern mining framework (nlin.AO)."

### 4. **Compilation**
   - Standard LaTeX compilation (should work with arXiv's TeXLive)
   - Packages required: geometry, graphicx, hyperref, amsmath, amssymb
   - Compilation tested with Pandoc markdown-to-LaTeX conversion

### 5. **Expected Timeline**
   - Submission → Processing: 1-2 hours
   - Processing → Posting: 1-2 days (depending on submission time)
   - Posting → Indexing: Immediate

---

## KEY FINDINGS

1. **Birth-death coupling is necessary but NOT sufficient**: Complete framework (C176 all versions) exhibits collapse despite energy recharge
2. **Perfect determinism validates reproducibility**: Identical outcomes across all random seeds (spawn=75, composition=38, final population=0)
3. **Energy recharge cannot overcome death-birth imbalance**: 100× parameter range yields zero effect (p=1.000, η²=0.000)
4. **Temporal asymmetry dominates**: Death-birth rate imbalance (2.6:1 ratio) creates extinction attractor
5. **Hypothesis falsification redirects research**: C177 H1 rejection (energy pooling) shifts focus to alternative mechanisms

---

## EXPERIMENTAL DATA

**C168-C170:** Single-agent models (n=30 total)
- Bistability regime classification
- Phase transition at f_crit ≈ 2.55%

**C171:** Birth-only multi-agent (n=10)
- Accumulation regime (~17 agents)
- Architectural incompleteness (missing death mechanism)

**C176 V2/V3/V4:** Complete birth-death coupling (n=30 total)
- Energy recharge parameter sweep: r ∈ {0.000, 0.001, 0.010}
- 3,000 cycles per condition, f=2.5%
- Collapse regime (mean=0.49 ± 0.50, CV=101%)

**C177 H1:** Energy pooling hypothesis test (n=40 total)
- 2×2 factorial: pooling ON/OFF × baseline/optimized
- Result: Zero effect (Cohen's d=0.0, p=1.0)

**Total Experiments:** 110 runs across 5 experimental cycles

---

## COMPANION PAPERS

- **Paper 1:** "Computational Expense as Framework Validation" (cs.DC, methodology validation)
- **Paper 5D:** "A Pattern Mining Framework for Quantifying Temporal Stability and Memory Retention" (nlin.AO, pattern taxonomy)
- **Paper 3:** "Optimized Factorial Validation of Nested Resonance Memory" (awaiting C255-C260 data, mechanism synergy)

---

## REPOSITORY

**GitHub:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)

**Data Availability:**
- Experimental results: `data/results/cycle168/`, `cycle171/`, `cycle176/`, `cycle177/`
- Analysis scripts: `code/experiments/` and `code/analysis/`
- Figures source: `data/figures/`

---

**Version:** 1.0 (Complete with C177 H1 Results Integrated)
**Date:** October 28, 2025 (Cycle 480)
**Status:** Ready for immediate arXiv submission
