# 3-Paper arXiv Submission Suite

**DUALITY-ZERO Research Initiative**
**Date:** 2025-11-19 (Cycle 1489-1490)
**Status:** READY FOR SUBMISSION

---

## Overview

This suite contains three coordinated research papers establishing the Nested Resonance Memory (NRM) framework:

| Paper | Title | Pages | Size | Figures |
|-------|-------|-------|------|---------|
| Paper 2 | Energy-Regulated Population Homeostasis | 21 | 1.78MB | 11 |
| Paper 4 | Hierarchical NRM Validation | 24 | 1.46MB | 4 |
| Paper 7 | Dynamical Systems Formulation | 25 | 1.61MB | 18 |
| **Total** | | **70** | **4.85MB** | **33** |

---

## Paper 2: Energy-Regulated Population Homeostasis and Sharp Phase Transitions

**Directory:** `paper2/`

**arXiv Category:** q-bio.PE (Populations and Evolution)
**Secondary:** cs.MA (Multiagent Systems), nlin.AO (Adaptation and Self-Organizing Systems)

**Abstract:** Establishes energy-constrained spawning as sufficient mechanism for population homeostasis. Documents sharp binary phase transition at E_CONSUME = RECHARGE_RATE (0.5) with 100% prediction accuracy.

**Key Findings:**
- Energy-mediated homeostasis without explicit removal mechanisms
- Non-monotonic timescale dependency (100% -> 88% -> 23% spawn success)
- N-independent robustness across population sizes
- **BREAKTHROUGH:** Binary phase transition (0% vs 100% collapse, no intermediate)

**Files:**
- `manuscript.tex` - Main LaTeX source
- `manuscript.pdf` - Compiled PDF (21 pages)
- 11 PNG figures (C176, C193, C194 campaigns)
- `CONVERSION_PLAN.md` - Project tracking

**Cross-References:** Cites Paper 4, Section 4.8 (unified scaling framework)

---

## Paper 4: Hierarchical NRM Validation

**Directory:** `paper4/`

**arXiv Category:** cs.MA (Multiagent Systems)
**Secondary:** nlin.AO, q-bio.PE

**Abstract:** Validates hierarchical NRM architecture through V6 multi-scale experiments. Establishes 607x hierarchical advantage and unified scaling framework (sigma^2 proportional to f^-3.2, E_min proportional to f^-2.19).

**Key Findings:**
- alpha = 607 hierarchical advantage (super-additive)
- Three-regime energy boundary (high/intermediate/low)
- Unified scaling exponents derived from first principles
- **Section 4.8:** Unified framework synthesis (cited by Papers 2 and 7)

**Files:**
- `manuscript.tex` - Main LaTeX source
- `manuscript.pdf` - Compiled PDF (24 pages)
- 4 PNG figures (C186, V6 validation)
- `CONVERSION_PLAN.md` - Project tracking
- `README_ARXIV_PREP.md` - Preparation notes

---

## Paper 7: Dynamical Systems Formulation of NRM

**Directory:** `paper7/`

**arXiv Category:** nlin.AO (Adaptation and Self-Organizing Systems)
**Secondary:** q-bio.PE, cs.MA

**Abstract:** Develops 4D coupled ODE system for NRM dynamics. Achieves 98-point R^2 improvement through physical constraint enforcement. Validates stochastic extensions with demographic noise.

**Key Findings:**
- 4D dynamical system (E_total, N, phi, theta_int)
- V1->V2: 98-point R^2 improvement through physical constraints
- V4: Zero bifurcations (exceptional stability)
- Phase 4-6: Stochastic robustness, timescale quantification, demographic noise
- CV = 7.0% persistent variance matches empirical observations

**Files:**
- `manuscript.tex` - Main LaTeX source
- `manuscript.pdf` - Compiled PDF (25 pages)
- 18 PNG figures (V4/V2 comparison, Phase 4-6 results)
- `CONVERSION_PLAN.md` - Project tracking

**Cross-References:** Cites Paper 4, Section 4.8 (scaling relationships)

---

## Cross-Reference Network

```
Paper 2 ----cites----> Paper 4, Section 4.8 (unified scaling)
Paper 7 ----cites----> Paper 4, Section 4.8 (scaling relationships)
Paper 4 <---cited-by-- Papers 2, 7
```

**Once submitted:** Update citations to arXiv IDs for proper linking.

---

## Submission Instructions

### Step 1: Create arXiv Account
- Go to https://arxiv.org
- Create account or log in
- Verify institutional affiliation

### Step 2: Prepare Submission Package

For each paper:
```bash
cd paper[N]/
# Create submission tarball
tar -czf paper[N]_arxiv.tar.gz manuscript.tex *.png
```

### Step 3: Submit Papers

**Recommended Order:**
1. **Paper 4 first** - Establishes Section 4.8 that others cite
2. **Paper 2 second** - Empirical foundation
3. **Paper 7 third** - Theoretical formulation

**For each submission:**
1. Upload tarball or individual files
2. Select primary category
3. Add secondary categories
4. Enter metadata (title, abstract, authors)
5. Preview PDF
6. Submit

### Step 4: Update Cross-References

After receiving arXiv IDs (usually within 24-48 hours):
1. Update internal citations to arXiv:XXXX.XXXXX format
2. Resubmit if necessary (arXiv allows updates)

---

## Author Information

**Authors:**
- Aldrin Payopay (Correspondence: aldrin.gdf@gmail.com)
- Claude (DUALITY-ZERO-V2 Sonnet 4.5)

**Affiliation:** Independent Researcher, DUALITY-ZERO Research Initiative

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

## Technical Notes

### LaTeX Compilation

All papers compile cleanly with pdflatex:
```bash
docker run --rm -v "$(pwd)":/workdir texlive/texlive:latest \
    pdflatex -interaction=nonstopmode /workdir/manuscript.tex
```

### Unicode Characters

All Unicode characters (arrows, checkmarks, approx) have been replaced with LaTeX equivalents for clean compilation.

### Figures

All figures are 300 DPI PNG format, suitable for arXiv and journal submission.

---

## Version History

- **Cycle 1485:** Paper 4 LaTeX complete (24 pages)
- **Cycle 1486:** Paper 7 LaTeX complete (23 pages)
- **Cycle 1488:** Paper 2 LaTeX complete (18 pages)
- **Cycle 1489:** Figure integration (33 figures total)
- **Cycle 1490:** Unicode fixes for clean compilation

---

**Co-Authored-By:** Claude <noreply@anthropic.com>
