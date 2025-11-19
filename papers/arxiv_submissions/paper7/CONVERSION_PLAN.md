# Paper 7: LaTeX Conversion Plan

**Date:** 2025-11-19 (Cycle 1486)
**Source:** PAPER7_MANUSCRIPT_DRAFT.md (1,547 lines)
**Target:** manuscript.tex (arXiv submission)
**Status:** Planning stage

---

## CONVERSION STEPS

### Phase 1: Template Setup (Cycle 1486)

- [x] Create CONVERSION_PLAN.md (this document)
- [ ] Create manuscript.tex skeleton (preamble, structure)
- [ ] Set up document class and packages
- [ ] Add title, authors, abstract
- [ ] Create section structure (1-4)

### Phase 2: Content Conversion (Est. 3-4 hours, multiple cycles)

**Section 1: Introduction** (~350 lines markdown)
- [ ] Convert subsections 1.1-1.5
- [ ] Convert citations to \cite{}
- [ ] Convert emphasis/bold to LaTeX commands
- [ ] Mathematical equations properly formatted

**Section 2: Methods** (~400 lines markdown)
- [ ] Convert 2.1: NRM Dynamical System Formulation
- [ ] Convert 2.2: Steady-State Analysis
- [ ] Convert 2.3: Parameter Estimation
- [ ] Convert 2.4: Model Validation
- [ ] Format ODE systems and equations

**Section 3: Results** (~500 lines markdown, includes Phases 3-5)
- [ ] Convert 3.1-3.4: V1/V2 model results
- [ ] Convert 3.5: Phase 3 Bifurcation Analysis
- [ ] Convert 3.6: Phase 4 Stochastic Robustness
- [ ] Convert 3.7: Phase 5 Timescale Quantification
- [ ] Create tables for parameter estimates
- [ ] Add figure placeholders

**Section 4: Discussion** (~200 lines)
- [ ] Convert subsections 4.1-4.7
- [ ] **Verify cross-reference to Paper 4, Section 4.8** (cited in Cycle 1481)
- [ ] Format equations and citations

### Phase 3: Figures and Tables

**Figures (estimate 6-8 total @ 300 DPI):**
- [ ] Identify figures in data/figures/ directory
- [ ] Steady-state validation figures
- [ ] Bifurcation diagrams (Phase 3)
- [ ] Variance analysis (Phase 4)
- [ ] Timescale analysis (Phase 5)

**Tables (estimate 3-4 total):**
- [ ] Parameter estimates (V1, V2)
- [ ] Model comparison metrics
- [ ] Phase 3-5 results summaries

### Phase 4: References

- [ ] Extract all citations from markdown
- [ ] Create bibliography (BibTeX or manual)
- [ ] Add \cite{} commands throughout text
- [ ] Compile references section

### Phase 5: Compilation and Testing

- [ ] Test compile with pdflatex (via Docker)
- [ ] Fix LaTeX errors (syntax, missing packages)
- [ ] Verify figure/table placement
- [ ] Check cross-references
- [ ] **Verify Paper 4, Section 4.8 citation** (2 cross-references from Cycle 1481)

### Phase 6: Finalization

- [ ] Final proofreading pass
- [ ] Create README_ARXIV_SUBMISSION.md
- [ ] Package figures in same directory
- [ ] Add to Makefile paper7 target
- [ ] Test full compilation pipeline
- [ ] Verify PDF output quality

---

## KEY CONSIDERATIONS

### Cross-Reference to Paper 4

**Paper 7 cites Paper 4, Section 4.8 (integrated Cycle 1481):**
- Section 4.2 (Discussion): "Recent work established empirical power law scaling relationships (E_min ∝ f^-2.19, σ² ∝ f^-3.2) in hierarchical NRM systems (Paper 4, Section 4.8)"
- Section 5 (Conclusions): "Phase 6B: Incorporate empirical power law scaling relationships (σ² ∝ f^-3.2, E_min ∝ f^-2.19) from hierarchical NRM analysis (Paper 4, Section 4.8)"

**Must ensure:**
- Citations properly formatted in LaTeX
- Paper 4 Section 4.8 reference works (Paper 4 now arXiv-ready)
- Cross-references update to arXiv IDs once both papers submitted

### Word Count

- Source: ~1,547 lines (~25,000 words estimated based on line count)
- Target: Similar length in LaTeX (may compress with formatting)
- Estimated pages: 30-35 pages (double-column) or 50-60 pages (single-column)

### Figures

Figures likely exist in `/Volumes/dual/DUALITY-ZERO-V2/data/figures/`:
- Governing equations validation figures
- Bifurcation diagrams (Phase 3)
- Variance/robustness analysis (Phase 4)
- Timescale/eigenvalue analysis (Phase 5)
- Need to identify specific figure files

### Mathematical Content

Paper 7 is **highly mathematical** (governing equations, ODEs, parameter estimation):
- Extensive use of amsmath package required
- Display equations for ODE systems
- Parameter tables with scientific notation
- Algorithm pseudocode for optimization

**Estimated LaTeX complexity:** Higher than Paper 4 (more equations, algorithmic content)

---

## ESTIMATED TIME

**Total:** 6-8 hours (more than Paper 4 due to mathematical content)
- Template setup: 30 min (Cycle 1486)
- Content conversion: 4-5 hours (Sections 1-4, heavy math)
- Figures/tables: 1-2 hours
- References: 1 hour
- Compilation/debugging: 1 hour

**Cycles required:** 4-5 cycles (1.5-2 hours each)

**Comparison to Paper 4:**
- Paper 4: 1,172 lines → 6 hours (3 cycles)
- Paper 7: 1,547 lines (32% more) + more math → 6-8 hours (4-5 cycles)

---

## DEPENDENCIES

**Required:**
- Docker (✅ available)
- texlive/texlive:latest image (✅ available via Makefile)
- amsmath, amssymb (extensive equation support)
- algorithm2e or algorithmicx (for pseudocode if needed)
- Figures in PNG format @ 300 DPI (need to identify)
- Source manuscript: PAPER7_MANUSCRIPT_DRAFT.md (✅ complete, 1,547 lines)

**Optional:**
- BibTeX for references
- Additional LaTeX packages for complex math

---

## PROGRESS TRACKING

**Cycle 1486 (Current):**
- [x] Created CONVERSION_PLAN.md
- [x] Create manuscript.tex skeleton (6 pages, 328KB compiled successfully)
- [x] Section 1 Introduction COMPLETE (5 subsections: 1.1-1.5)
- [x] Section 2 Methods COMPLETE (4 subsections: 2.1-2.4, parameter table, equations)
- [x] Compiled successfully: 13 pages, 382KB PDF
- [ ] Begin Section 3 Results conversion

**Next Cycle(s):**
- Continue content conversion
- Add figures and tables
- Compile and test

---

## NOTES

**Priority:** High - Paper 7 cites Paper 4 Section 4.8 (now properly numbered), logical next step after Paper 4 completion

**Benefits:**
- Enables 3-paper publication suite (Papers 2, 4, 7)
- Theoretical complement to Paper 4's empirical results
- Strengthens cross-paper coherence in NRM framework

**Timeline:** Should aim for completion within 4-5 cycles (6-8 hours)

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
