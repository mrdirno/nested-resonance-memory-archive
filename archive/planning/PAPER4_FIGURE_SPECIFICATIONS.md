# Paper 4 Figure Specifications

**Paper:** "Hierarchical Energy Dynamics in Nested Resonance Memory Systems"
**Purpose:** Design templates for validation campaign visualization
**Experiments:** C186-C189 (180 total experiments)
**Target Journal:** Physical Review E or equivalent

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Date:** 2025-11-05 (Cycle 1021)
**License:** GPL-3.0

**Co-Authored-By:** Claude <noreply@anthropic.com>

---

## Figure Budget

**Recommended:** 6-8 figures for comprehensive validation story
**Minimum:** 4 figures for core results

---

## Figure 1: Hierarchical Energy Regulation (C186)

### Purpose
Demonstrate inter-population energy dampening via migration coupling.

### Panel Layout (2×2 grid)
- **(A)** Population size time series (10 populations overlaid)
- **(B)** Basin A occupation percentage (10 seeds, box plot)
- **(C)** Cross-population migration network (chord diagram or force-directed)
- **(D)** Energy regulation vs. single-population control (comparison)

### Data Requirements
- C186 results: 10 experiments × 3000 cycles
- Baseline comparison: Single-population 2.5% frequency results

### Statistical Tests
- One-sample t-test: Basin A % vs. 5% threshold
- Paired t-test: Multi-population vs. single-population Basin A
- Effect size: Cohen's d for hierarchical dampening

### Expected Results (Extension 2 Predictions)
- Basin A < 5% for all seeds (hierarchical regulation)
- Migration count: 10-20 events per experiment
- Energy dampening factor: 2-5× reduction vs. single population

### Implementation Notes
```python
# Figure generation script
generate_c186_hierarchical_regulation_figure(
    results_path="cycle186_metapopulation_hierarchical_validation_results.json",
    baseline_path="cycle171_baseline_results.json",
    output_path="figures/paper4_fig1_hierarchical_regulation.png",
    dpi=300
)
```

### Style
- Color scheme: Viridis or Plasma for population differentiation
- Font: Arial 10pt for labels, 12pt for titles
- Size: 180mm × 180mm (double-column width)
- Format: PNG @ 300 DPI (high resolution for publication)

---

## Figure 2: Network Structure Effects (C187)

### Purpose
Show how network topology modulates hierarchical dynamics.

### Panel Layout (3×2 grid)
- **(A-C)** Population dynamics for 3 topologies (ring, star, fully-connected)
  - Each panel: Time series with shaded uncertainty
- **(D-F)** Basin A statistics by topology (bar charts with error bars)

### Data Requirements
- C187 results: 3 topologies × 10 seeds × 3000 cycles

### Statistical Tests
- One-way ANOVA: Basin A % across topologies
- Post-hoc: Tukey HSD for pairwise comparisons
- Effect size: η² (eta-squared) for topology effect

### Expected Results (Extension 2 Predictions)
- Ring: Moderate dampening (local coupling)
- Star: Strong dampening (central hub regulation)
- Fully-connected: Strongest dampening (maximum coupling)

### Implementation Notes
```python
generate_c187_network_topology_figure(
    results_path="cycle187_network_structure_effects_results.json",
    output_path="figures/paper4_fig2_network_topology.png",
    dpi=300
)
```

### Style
- Color scheme: Topology-specific (blue=ring, red=star, green=fully-connected)
- Network diagrams: GraphViz or NetworkX layouts
- Size: 180mm × 120mm
- Format: PNG @ 300 DPI

---

## Figure 3: Memory Effects (C188)

### Purpose
Demonstrate pattern retention across hierarchical levels.

### Panel Layout (2×3 grid)
- **(A-C)** Memory retention curves for 3 conditions
  - Pattern persistence over time
- **(D)** Memory decay rates (bar chart)
- **(E)** Cross-level memory correlation (scatter plot)
- **(F)** Memory capacity vs. hierarchy depth (line plot)

### Data Requirements
- C188 results: 4 memory conditions × 10 seeds × 3000 cycles

### Statistical Tests
- Linear regression: Memory decay rate
- Correlation: Cross-level memory retention
- ANOVA: Memory capacity across conditions

### Expected Results (Extension 2 Predictions)
- Memory retention: 60-80% after 500 cycles
- Cross-level correlation: r > 0.7
- Hierarchy depth amplifies memory capacity

### Implementation Notes
```python
generate_c188_memory_effects_figure(
    results_path="cycle188_memory_effects_results.json",
    output_path="figures/paper4_fig3_memory_effects.png",
    dpi=300
)
```

### Style
- Color scheme: Colorblind-friendly palette (Wong 2011)
- Exponential decay fits overlaid
- Size: 180mm × 120mm
- Format: PNG @ 300 DPI

---

## Figure 4: Burst Clustering (C189)

### Purpose
Show self-organized criticality in hierarchical burst patterns.

### Panel Layout (2×2 grid)
- **(A)** Burst size distribution (log-log plot, power-law fit)
- **(B)** Burst duration distribution (log-log plot)
- **(C)** Clustering coefficient vs. burst size (scatter)
- **(D)** Avalanche criticality test (finite-size scaling)

### Data Requirements
- C189 results: 10 cluster sizes × 10 seeds × 3000 cycles

### Statistical Tests
- Power-law fit: MLE with KS test (Clauset et al. 2009 method)
- Exponent confidence intervals: Bootstrap resampling
- Criticality test: Finite-size scaling collapse

### Expected Results (Extension 2 Predictions)
- Power-law exponent: α ≈ 2.0-2.5
- Clustering: Scale-free behavior
- Criticality: Evidence for self-organized criticality

### Implementation Notes
```python
generate_c189_burst_clustering_figure(
    results_path="cycle189_burst_clustering_results.json",
    output_path="figures/paper4_fig4_burst_clustering.png",
    dpi=300,
    powerlaw_library=True  # Use powerlaw package for robust fitting
)
```

### Style
- Log-log axes with gridlines
- Power-law fit: Red dashed line with 95% CI
- Size: 180mm × 120mm
- Format: PNG @ 300 DPI

---

## Figure 5: Composite Validation Scorecard

### Purpose
Unified visualization of all 24 validation points across C186-C189.

### Panel Layout (Single panel with heatmap)
- Rows: 24 validation criteria
- Columns: Experiments (C186, C187, C188, C189)
- Color: Green (VALIDATED), Yellow (PARTIAL), Red (REJECTED)
- Annotations: Confidence scores (0-100%)

### Data Requirements
- Composite validation results from post-validation pipeline
- 24-point scorecard JSON

### Statistical Tests
- Overall validation rate: % VALIDATED
- Confidence distribution: Mean ± SD across all criteria
- Per-experiment validation: C186 (5), C187 (6), C188 (7), C189 (6)

### Expected Results (Extension 2 Predictions)
- Overall validation: >75% (≥18/24 VALIDATED)
- High confidence: Mean confidence >80%
- Strong evidence for hierarchical framework

### Implementation Notes
```python
generate_composite_validation_scorecard(
    composite_path="composite_validation_results.json",
    output_path="figures/paper4_fig5_validation_scorecard.png",
    dpi=300
)
```

### Style
- Heatmap: Seaborn or Matplotlib imshow
- Annotations: White text on dark cells, black on light
- Size: 180mm × 240mm (tall format)
- Format: PNG @ 300 DPI

---

## Figure 6: Runtime Variance Analysis (Computational Complexity)

### Purpose
Demonstrate computational complexity amplification in hierarchical systems.

### Panel Layout (2×2 grid)
- **(A)** Runtime distribution across seeds (violin plot)
- **(B)** Runtime vs. CV correlation (scatter with regression)
- **(C)** Runtime vs. migrations correlation (scatter)
- **(D)** Hierarchical amplification factor (bar chart)

### Data Requirements
- C186 runtime data with timestamps
- Dynamical metrics (CV, migrations, populations)

### Statistical Tests
- Pearson correlation: Runtime vs. CV, runtime vs. migrations
- Variance decomposition: ANOVA for seed effects
- Amplification factor: Ratio of hierarchical to single-population variance

### Expected Results (Extension 2 Predictions)
- Runtime CV: >50% (high variance)
- Runtime-CV correlation: r > 0.6
- Amplification: 3-10× variance increase vs. single population

### Implementation Notes
```python
generate_runtime_variance_figure(
    c186_results="cycle186_metapopulation_hierarchical_validation_results.json",
    variance_analysis="C186_VARIANCE_DECOMPOSITION.md",
    output_path="figures/paper4_fig6_runtime_variance.png",
    dpi=300
)
```

### Style
- Violin plots: Show full distribution + quartiles
- Regression lines: 95% CI shaded
- Size: 180mm × 120mm
- Format: PNG @ 300 DPI

---

## Supplementary Figures

### S1: Parameter Sensitivity Analysis
- Spawn frequency scan (0.5% - 10.0%)
- Migration frequency scan (0.1% - 2.0%)
- Population count scan (2-20 populations)

### S2: Convergence Testing
- Results stability vs. cycle count (500-5000 cycles)
- Seed sufficiency analysis (n=5, 10, 20, 50)

### S3: Theoretical Model Comparison
- NRM predictions vs. empirical results
- Alternative models (mean-field, Kuramoto, etc.)

### S4: Control Experiments
- Single-population replication
- Baseline frequency validation
- No-migration control

---

## Figure Generation Pipeline

### Dependencies
```python
# Required packages
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import networkx as nx
import powerlaw  # For power-law fitting
from scipy import stats
from matplotlib import gridspec
```

### Automated Generation
```bash
# Generate all figures
python3 /Volumes/dual/DUALITY-ZERO-V2/experiments/generate_paper4_figures.py

# Output directory
figures/
├── paper4_fig1_hierarchical_regulation.png
├── paper4_fig2_network_topology.png
├── paper4_fig3_memory_effects.png
├── paper4_fig4_burst_clustering.png
├── paper4_fig5_validation_scorecard.png
├── paper4_fig6_runtime_variance.png
├── supplement_s1_parameter_sensitivity.png
├── supplement_s2_convergence_testing.png
├── supplement_s3_theoretical_comparison.png
└── supplement_s4_control_experiments.png
```

---

## Statistical Reporting Standards

### Required for Each Figure
1. **Sample size:** Clearly state n for each condition
2. **Central tendency:** Mean ± SD or Median ± IQR
3. **Statistical test:** Name, test statistic, p-value, effect size
4. **Significance:** * p<0.05, ** p<0.01, *** p<0.001
5. **Error bars:** 95% CI or 1 SD (specify in caption)

### Example Caption
> **Figure 1. Hierarchical Energy Regulation.** (A) Population size dynamics for 10 coupled populations showing synchronized homeostasis. (B) Basin A occupation percentage across 10 random seeds (mean = 0.0% ± 0.0%, n=10), significantly below 5% threshold (one-sample t-test: t(9)=∞, p<0.001, Cohen's d=∞). (C) Cross-population migration network showing sparse coupling (mean degree = 2.8 ± 0.4). (D) Comparison with single-population control showing 4.3× energy dampening (paired t-test: t(9)=8.7, p<0.001, d=2.75). Error bars: 95% CI.

---

## Color Schemes

### Publication-Quality Palettes

**Categorical (up to 10 categories):**
- Colorblind-friendly: Wong 2011 palette
- Default: Tableau 10

**Sequential (continuous scales):**
- Cool: Viridis, Plasma
- Warm: YlOrRd, OrRd

**Diverging (positive/negative):**
- RdBu (red-blue)
- PiYG (pink-yellow-green)

### Accessibility
- Ensure contrast ratio >4.5:1
- Avoid red-green only distinctions
- Test with Color Oracle simulator

---

## Version Control

All figures tracked in git:
```bash
git add data/figures/paper4_*.png
git commit -m "Add Paper 4 figures for validation campaign

Generated from C186-C189 validation experiments (n=180 total).
All figures @ 300 DPI, publication-ready.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Timeline

**Figure Generation Schedule:**
1. **Day 1 (Cycle 1021):** Design specifications (this document)
2. **Day 2:** Implement figure generation scripts
3. **Day 3:** Generate figures from C186-C189 results
4. **Day 4:** Iterate based on peer review feedback
5. **Day 5:** Final publication-ready figures

**Contingency:** Allow 1-2 days buffer for unexpected revisions

---

## Quality Checklist

Before submission, verify:
- [ ] All figures @ 300 DPI minimum
- [ ] Fonts embedded in vector graphics
- [ ] Color schemes accessible
- [ ] Statistical annotations complete
- [ ] Captions comprehensive
- [ ] File sizes <10MB each
- [ ] Consistent style across all figures
- [ ] Supplementary figures prepared
- [ ] Figure permissions documented (all original)
- [ ] Git commits with proper attribution

---

**END OF SPECIFICATIONS**

**Status:** Draft v1.0
**Next Action:** Implement figure generation scripts after C186-C189 complete
**Review Date:** Upon validation campaign completion (~28 hours from Cycle 1021 start)
