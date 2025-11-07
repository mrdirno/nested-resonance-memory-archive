# Paper 2: Energy-Regulated Population Homeostasis and Timescale-Dependent Constraint Manifestation

**Title:** Energy-Regulated Population Homeostasis and Timescale-Dependent Constraint Manifestation in Nested Resonance Memory

**Category:** Computational Biology / Multi-agent Systems
**Cross-list:** Complex Systems, Artificial Life

**Status:** Submission-ready (PLOS Computational Biology / PLOS ONE)

---

## Abstract

Self-organizing computational systems exhibit regime transitions depending on resource constraints and temporal scale. The Nested Resonance Memory (NRM) framework provides a reality-grounded platform for studying emergent dynamics in multi-agent systems with measurable energy constraints. We characterize energy-regulated population dynamics across temporal scales to determine how NRM populations self-regulate without explicit removal mechanisms.

Multi-scale validation spanning three temporal scales: micro (100 cycles, n=3 seeds), incremental (1000 cycles, n=5 seeds), and extended (3000 cycles, n=40 seeds from C171 baseline). All experiments used identical BASELINE energy configuration and 2.5% spawn frequency to isolate timescale effects. Energy-constrained spawning implemented via spawn_child() requiring parent energy thresholds—composition events deplete energy, failed spawns regulate population.

**Key Finding:** Multi-scale timescale validation revealed non-monotonic energy constraint manifestation. Spawn success rates followed a U-shaped pattern across timescales: 100% (100 cycles) → 88.0% ± 2.5% (1000 cycles) → 23% (3000 cycles), demonstrating that population-mediated energy recovery dominates at intermediate scales before long-term cumulative depletion overwhelms recovery mechanisms.

---

## Key Contributions

1. **Energy-regulated homeostasis without explicit removal** - Energy-constrained spawning sufficient for population self-regulation
2. **Non-monotonic timescale dependency** - Constraint manifestation depends on temporal window (100% → 88% → 23% across scales)
3. **Population-mediated energy recovery mechanism** - Distributed load balancing at intermediate timescales (1000 cycles)
4. **Spawns-per-agent threshold model** - Generalizable metric predicting spawn success independent of absolute timescale (<2.0, 2.0-4.0, >4.0 zones)
5. **Four-phase trajectory** - Decline → Transition → Stabilization → Recovery pattern documented

---

## Key Findings

- **Regime 1 (Bistability):** Single-agent models exhibit sharp transition at f_crit ≈ 2.55% with bistable attractors (Basin A/B)
- **Regime 2 (Energy-Regulated Homeostasis):** Multi-agent populations with energy-constrained spawning achieve stable homeostasis (C171: 17.4 ± 1.2 agents over 3000 cycles, CV=6.8%) without explicit agent removal
- **Non-monotonic timescale pattern:** 100% spawn success (100 cycles) → 88.0% ± 2.5% (1000 cycles) → 23.0% (3000 cycles)
- **Spawns-per-agent threshold:** <2.0 → 70-100% success, 2.0-4.0 → transition zone, >4.0 → 20-40% success
- **Population-mediated recovery:** Large populations distribute spawn selection pressure, enabling individual energy regeneration between compositional events
- **Connection to Self-Giving Systems:** Populations use their own growth to generate distributed energy pooling that modifies constraint landscape

---

## Figures

- **Figure 1:** `c176_v6_multi_scale_comparison_final.png` (196 KB) - Multi-scale timescale validation (100/1000/3000 cycles)
- **Figure 2:** `c176_v6_seed_comparison_final.png` (219 KB) - Seed-level validation and hypothesis testing (n=5 seeds)
- **Figure 3:** `c176_v6_incremental_trajectory_preliminary.png` (465 KB) - Four-phase trajectory analysis (decline → transition → stabilization → recovery)

All figures @ 300 DPI, publication-ready.

---

## Reproducibility

### Experiments

**C176 V6: Multi-Scale Timescale Validation**

```bash
cd code/experiments
python cycle176_v6_multi_scale_validation.py
```

**Runtime:**
- Micro-validation (100 cycles, n=3): ~5 minutes
- Incremental validation (1000 cycles, n=5): ~45 minutes
- Extended validation (3000 cycles, n=40): ~6 hours (from C171 baseline)

**Expected Results:**
- 100 cycles: 100% spawn success (all seeds)
- 1000 cycles: 88.0% ± 2.5% spawn success, 23.0 ± 0.6 agents, 2.08 spawns/agent
- 3000 cycles: 23% spawn success, 17.4 ± 1.2 agents, 8.38 spawns/agent

### Analysis

**Generate Publication Figures:**

```bash
cd code/analysis
python analyze_c176_v6_final.py
```

**Output:**
- `c176_v6_multi_scale_comparison_final.png` - 3-panel comparison across temporal scales
- `c176_v6_seed_comparison_final.png` - Seed validation with statistics
- CSV files with summary statistics

---

## Citation

```bibtex
@article{payopay2025homeostasis,
  title={Energy-Regulated Population Homeostasis and Timescale-Dependent Constraint Manifestation in Nested Resonance Memory},
  author={Payopay, Aldrin and Claude},
  journal={Submitted to PLOS Computational Biology},
  year={2025},
  note={V2 revision integrating C176 V6 validated findings}
}
```

---

## Files

### Manuscript
- `PAPER2_V2_ENERGY_HOMEOSTASIS_MANUSCRIPT.docx` (44 KB) - Submission-ready manuscript
- `PAPER2_V2_MASTER_SOURCE_BUILD.md` (82 KB) - Complete markdown source (1400 lines)
- `PAPER2_V1_TO_V2_CHANGELOG.md` (15 KB) - Comprehensive V1→V2 changes

### Supporting Documents
- `PAPER2_V2_SUBMISSION_PACKAGE_README.md` (10 KB) - Submission guide
- `PAPER2_V2_FIGURE_CAPTIONS.md` (5 KB) - Figure captions and descriptions
- `PAPER2_V2_COVER_LETTER_PLOS.md` (8 KB) - PLOS Computational Biology cover letter

### Figures (300 DPI)
- `c176_v6_multi_scale_comparison_final.png` (196 KB)
- `c176_v6_seed_comparison_final.png` (219 KB)
- `c176_v6_incremental_trajectory_preliminary.png` (465 KB)

---

## Target Journals (Priority Order)

### 1. PLOS Computational Biology (Primary)
- **URL:** https://journals.plos.org/ploscompbiol/
- **Fit:** Excellent - computational modeling, emergent dynamics, population biology
- **Review Time:** ~3-4 months

### 2. PLOS ONE (Backup)
- **URL:** https://journals.plos.org/plosone/
- **Fit:** Good - multidisciplinary, computational biology section
- **Review Time:** ~2-3 months

---

## Version History

**V2 (Current - 2025-11-04):**
- Complete revision following C176 V6 validation
- Integrates non-monotonic timescale dependency findings
- Removes invalid C176 V2-V4 bug artifacts (collapse narrative)
- New title: "Energy-Regulated Population Homeostasis..."
- New findings: Population-mediated recovery, spawns-per-agent threshold
- Status: Submission-ready

**V1 (Superseded - 2025-10-28):**
- Original manuscript: "From Bistability to Collapse: Three Dynamical Regimes"
- Included invalid C176 V2-V4 results (bug: agents incorrectly removed on composition)
- Superseded after bug discovery and C176 V6 validation

---

## Revision Rationale

Paper 2 underwent major revision following discovery that C176 V2-V4 "collapse" results were bug-induced artifacts (agents incorrectly removed during composition). C176 V6 validated energy-regulated homeostasis with multi-scale timescale validation (100, 1000, 3000 cycles). Scientific integrity requires removal of invalid content and integration of validated findings.

**Key Difference:**
- V1 claimed: "Birth-death coupling leads to collapse, explicit removal required"
- V2 demonstrates: "Energy-constrained spawning sufficient for homeostasis, timescale-dependent manifestation"

---

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
**Contact:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Updated:** 2025-11-07 (Cycle 1168)
