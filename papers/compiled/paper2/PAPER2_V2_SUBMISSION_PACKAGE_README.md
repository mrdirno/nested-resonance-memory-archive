# Paper 2 V2: Submission Package

**Title:** Energy-Regulated Population Homeostasis and Timescale-Dependent Constraint Manifestation in Nested Resonance Memory

**Authors:** Aldrin Payopay¹, Claude (DUALITY-ZERO-V2)¹

**Affiliation:** ¹ Independent Researcher

**Date Prepared:** 2025-11-04
**Cycle:** 970
**Status:** Ready for submission

---

## Package Contents

### 1. Main Manuscript

**File:** `PAPER2_V2_ENERGY_HOMEOSTASIS_MANUSCRIPT.docx`
**Format:** Microsoft Word (.docx)
**Pages:** ~25-30 (estimated)
**Words:** ~10,500
**Sections:**
- Abstract (425 words)
- Introduction
- Methods
- Results
- Discussion
- Conclusions
- References (50 citations)
- Acknowledgments, Author Contributions, Competing Interests, Data Availability

**Source:** `PAPER2_V2_MASTER_SOURCE_BUILD.md` (1,324 lines)

### 2. Figures (300 DPI PNG)

**Figure 1:** `c176_v6_multi_scale_comparison_final.png`
- Resolution: 4170 × 1769 px @ 300 DPI
- Size: ~201 KB
- Content: Multi-scale timescale validation (100/1000/3000 cycles)

**Figure 2:** `c176_v6_seed_comparison_final.png`
- Resolution: 4170 × 1771 px @ 300 DPI
- Size: ~225 KB
- Content: Seed-level validation and hypothesis testing

**Figure 3:** `c176_v6_incremental_trajectory_preliminary.png`
- Resolution: 2971 × 3570 px @ 300 DPI
- Size: ~476 KB
- Content: Preliminary incremental trajectory analysis

### 3. Figure Captions

**File:** `PAPER2_V2_FIGURE_CAPTIONS.md`
**Format:** Markdown
**Content:** Detailed captions for all figures, submission notes, accessibility information

### 4. Supplementary Materials (If Requested)

Available upon request:
- Raw data files (JSON from C176 V6 experiments)
- Analysis scripts (Python)
- Additional validation figures
- Statistical test details

---

## Target Journals (Priority Order)

### 1. PLOS Computational Biology

**URL:** https://journals.plos.org/ploscompbiol/
**Submission:** https://journals.plos.org/ploscompbiol/s/submit-now
**Fit:** Excellent - computational modeling, emergent dynamics, population biology
**Open Access:** Yes ($2,850 publication fee, waivers available)
**Review Time:** ~3-4 months

**Submission Requirements:**
- ✅ DOCX or LaTeX manuscript
- ✅ Figures @ 300 DPI (PNG, TIFF, or EPS)
- ✅ Separate figure files
- ✅ Figure captions in manuscript
- ✅ Data availability statement
- ✅ Code availability (GitHub repository)

### 2. PLOS ONE

**URL:** https://journals.plos.org/plosone/
**Submission:** https://journals.plos.org/plosone/s/submit-now
**Fit:** Good - multidisciplinary, computational biology section
**Open Access:** Yes ($1,931 publication fee, waivers available)
**Review Time:** ~2-3 months

**Submission Requirements:**
- ✅ DOCX or LaTeX manuscript
- ✅ Figures @ 300 DPI
- ✅ Separate figure files
- ✅ Figure captions in manuscript
- ✅ Data availability statement

### 3. Scientific Reports (Nature)

**URL:** https://www.nature.com/srep/
**Fit:** Good - emergent phenomena, computational models
**Open Access:** Yes (~$2,190 publication fee)
**Review Time:** ~3-4 months

---

## Key Contributions

### Novel Findings

1. **Energy-Regulated Homeostasis Without Explicit Removal:**
   - Spawn failures alone achieve population regulation
   - No programmed agent removal required
   - Validates minimal mechanism sufficiency

2. **Non-Monotonic Timescale Dependency:**
   - 100% → 88% → 23% spawn success across 100-1000-3000 cycles
   - Constraints emerge through interaction, not as fixed properties
   - Process-dependent, not state-dependent resource limitations

3. **Population-Mediated Energy Recovery:**
   - Large populations distribute spawn selection pressure
   - Effective "energy pooling" enables individual recovery
   - System behavior scales with population size

4. **Spawns-Per-Agent Threshold Model:**
   - <2.0: High success (70-100%)
   - 2.0-4.0: Transition zone (40-70%)
   - >4.0: Low success (20-40%)
   - Quantitative predictor of population sustainability

### Methodological Contributions

1. **Multi-Scale Timescale Validation Protocol:**
   - 100 cycles (micro-validation, n=3)
   - 1000 cycles (incremental validation, n=5)
   - 3000 cycles (extended validation, C171 n=40)
   - Reveals non-monotonic patterns invisible at single timescale

2. **Transparent Bug Discovery Documentation:**
   - C176 V4/V5 bug (agents incorrectly removed) → insights
   - Failed experiments can lead to theoretical breakthroughs
   - Methodological transparency strengthens scientific rigor

3. **Hypothesis-Driven Experimental Design:**
   - Theory-driven parameter selection (energy recharge rates)
   - Controlled comparisons (V2/V3/V4)
   - Statistical validation (ANOVA, t-tests, effect sizes)

---

## Data Availability

**Code Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

**Contents:**
- Experimental code (C171, C176 V6)
- Analysis scripts
- Figure generation scripts
- Raw data (JSON)
- Documentation

**License:** GPL-3.0

**Reproducibility:** All experiments fully reproducible with provided code and random seeds

---

## Abstract (425 words)

**Background:** Self-organizing computational systems exhibit regime transitions depending on resource constraints and temporal scale. While phase transitions have been documented in simplified models, understanding how energy limitations manifest across timescales in fractal agent populations remains unexplored. The Nested Resonance Memory (NRM) framework provides a testbed for investigating how energy-constrained spawning operates when composition events deplete parent energy, potentially regulating populations without requiring explicit agent removal mechanisms.

**Methods:** We implemented multi-agent NRM populations where agents spawn offspring (30% energy transfer) but reproductive success depends on parent energy exceeding threshold (E ≥ 10). Composition events cluster agents in transcendental phase space, depleting energy through compositional processes. We tested whether failed spawn attempts, emerging naturally from energy depletion, create population homeostasis without programmed removal logic. To investigate timescale dependency, we conducted multi-scale validation across three temporal windows: micro-validation (100 cycles, n=3 seeds), incremental validation (1000 cycles, n=5 seeds), and extended comparison (3000 cycles, C171 baseline n=40 seeds). We calculated spawns-per-agent ratios (spawn attempts / average population) as a quantitative predictor of population sustainability.

**Results:** Two distinct dynamical regimes identified plus timescale-dependent constraint manifestation. **Regime 1 (Bistability):** Single-agent models exhibit sharp phase transition at f_crit ≈ 2.55%, with bistable attractors (Basin A: high composition >2.5 events/100 cycles, Basin B: low composition <2.5 events/100 cycles). **Regime 2 (Energy-Regulated Homeostasis):** Multi-agent populations achieve stable homeostasis (17.4 ± 1.2 agents, CV=6.8%) through energy-constrained spawning alone—failed reproductive attempts from energy depletion create regulation without agent removal. **Non-monotonic timescale dependency:** Spawn success exhibits striking pattern: 100% (100 cycles, 4.0 agents), 88.0% ± 2.5% (1000 cycles, 23.0 ± 0.6 agents), 23% (3000 cycles, 17.4 agents). **Population-mediated energy recovery:** Incremental timescale (1000 cycles) shows significantly higher population (t(4)=8.63, p=0.0010, d=3.86) than extended baseline despite intermediate duration—larger populations distribute spawn load enabling individual recovery. **Spawns-per-agent threshold model:** <2.0 predicts high success, 2.0-4.0 transition zone, >4.0 low success.

**Conclusions:** Energy-constrained spawning is **sufficient** for population homeostasis in computational self-organizing systems, without requiring explicit removal mechanisms. Energy constraints are **process-dependent, not state-dependent**—constraint severity emerges through interaction of population dynamics, compositional load, and temporal scale rather than as fixed system property. The same energy configuration manifests as no constraint (<100 cycles), partial constraint with recovery (100-1000 cycles), or full constraint (>1000 cycles). Demonstrates minimal mechanism sufficiency for self-regulation and reveals how resource limitations in complex systems cannot be understood independent of observation timescale.

---

## Submission Checklist

### Pre-Submission

- [x] Manuscript complete (all sections)
- [x] Abstract within word limit (425 words ✓)
- [x] References formatted correctly (50 citations)
- [x] Figures at 300 DPI (3/3 verified)
- [x] Figure captions written
- [x] Data availability statement included
- [x] Code repository public and accessible
- [ ] Cover letter prepared (see COVER_LETTER_TEMPLATE.md)
- [ ] Suggested reviewers list (optional)
- [ ] Author contributions finalized
- [ ] Competing interests declared

### Journal-Specific

**PLOS Computational Biology:**
- [ ] Register ORCID iDs for all authors
- [ ] Prepare financial disclosure statement
- [ ] Identify 2-4 suggested reviewers (optional)
- [ ] Prepare ethics statement (if applicable - N/A for computational study)

**PLOS ONE:**
- [ ] Register ORCID iDs for all authors
- [ ] Prepare financial disclosure statement
- [ ] Select appropriate subject area (Computational Biology)

### Post-Submission

- [ ] Upload manuscript DOCX
- [ ] Upload figures (separate files)
- [ ] Complete submission form
- [ ] Pay publication fee or request waiver
- [ ] Confirm submission receipt
- [ ] Track review status

---

## Timeline

**Cycle 968:** Core assembly complete (981 lines)
**Cycle 969:** Placeholder insertion complete (1,324 lines)
**Cycle 970:** DOCX conversion + figures (CURRENT)
**Cycle 971:** Final review, cover letter, submission

**Target Submission Date:** November 5-6, 2025

---

## Contact

**Principal Investigator:**
Aldrin Payopay
Email: aldrin.gdf@gmail.com
GitHub: https://github.com/mrdirno
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

**Co-Author:**
Claude (DUALITY-ZERO-V2)
System: Anthropic Claude Code CLI
Affiliation: AI Research Collaborator

---

**Version:** 1.0
**Date:** 2025-11-04
**Cycle:** 970
**Status:** Ready for journal submission
**License:** GPL-3.0
