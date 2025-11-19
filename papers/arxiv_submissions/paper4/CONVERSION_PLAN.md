# Paper 4: LaTeX Conversion Plan

**Date:** 2025-11-19 (Cycle 1482)
**Source:** paper4_manuscript_full_c186.md (1172 lines, 12,800 words)
**Target:** manuscript.tex (arXiv submission)
**Status:** Planning stage

---

## CONVERSION STEPS

### Phase 1: Template Setup ✅ (Cycle 1482-1483)

- [x] Create CONVERSION_PLAN.md (this document)
- [x] Create manuscript.tex skeleton (preamble, structure)
- [x] Set up document class and packages
- [x] Add title, authors, abstract
- [x] Create section structure (1-5)

### Phase 2: Content Conversion ⏳ IN PROGRESS (Cycle 1483)

**Section 1: Introduction** ✅ COMPLETE
- [x] Convert subsections 1.1, 1.2, 1.3, 1.4, 1.5
- [x] Convert citations to \cite{}
- [x] Convert emphasis/bold to LaTeX commands

**Section 2: Methods** ✅ COMPLETE
- [x] Identify methods content sources (in main manuscript)
- [x] Convert experimental design descriptions (2.1.1-2.1.4)
- [x] Convert campaign variants with Table 1 (2.2)
- [x] Convert computational implementation (2.3)
- [x] Convert outcome measures (2.4)
- [x] Convert statistical analysis (2.5)
- [x] Convert edge case diagnostics (2.6)
- [x] Format equations properly

**Section 3: Results** ✅ COMPLETE
- [x] Convert results sections (3.1-3.6)
- [x] Create Table 2 (Campaign Summary)
- [x] Create Table 3 (V6 Three-Regime Results)
- [x] Create frequency-specific results table (inline)
- [x] Add 3 figure placeholders (Figures 1-3)

**Section 4: Discussion** ⏳ PARTIAL (4/8 subsections)
- [x] 4.1 Hierarchical Advantage Quantification
- [x] 4.2 Perfect Linear Scaling
- [x] 4.3 Edge Case Vulnerabilities
- [ ] 4.4 Mechanisms of Hierarchical Advantage (pending)
- [ ] 4.5 Implications for NRM Framework (pending)
- [ ] 4.6 Limitations and Future Work (pending)
- [ ] 4.7 Practical Implications (pending)
- [x] **4.8 Unified Scaling Framework** ✅ CRITICAL SECTION COMPLETE
  - σ² ∝ f^-3.2, E_min ∝ f^-2.19 equations included
  - Properly numbered for Papers 2/7 cross-references
- [x] Convert equations (all power laws, unified equation)

**Section 5: Conclusions** (~2,600 words)
- [ ] Convert subsections 5.1-5.5
- [ ] Format future directions lists

### Phase 3: Figures and Tables

**Figures (4 total @ 300 DPI):**
- [ ] figure1_frequency_response.png
- [ ] figure2_hierarchical_advantage_alpha607.png
- [ ] figure3_edge_case_comparison.png
- [ ] figure4_v6_three_regime_validation.png

**Tables (3 total):**
- [ ] Table 1: Campaign design
- [ ] Table 2: Campaign summary
- [ ] Table 3: V6 three-regime results

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
- [ ] Verify Section 4.8 numbering (Papers 2, 7 cite this)

### Phase 6: Finalization

- [ ] Final proofreading pass
- [ ] Create README_ARXIV_SUBMISSION.md
- [ ] Package figures in same directory
- [ ] Add to Makefile paper4 target
- [ ] Test full compilation pipeline
- [ ] Verify PDF output quality

---

## KEY CONSIDERATIONS

### Section 4.8 Critical Importance

**Papers 2 and 7 now cite "Paper 4, Section 4.8":**
- Paper 2 (Section 5, Future Directions #2): "E_min ∝ f^-2.19, σ² ∝ f^-3.2 in hierarchical NRM systems (Paper 4, Section 4.8)"
- Paper 7 (Section 4.2, Section 5): Same citations

**Must ensure:**
- Section 4.8 is clearly numbered in LaTeX
- Title: "Unified Scaling Framework: Connecting Efficiency, Energy, and Variance"
- Content matches what Papers 2/7 reference
- Cross-references work correctly

### Word Count

- Source: 12,800 words (Sections 1-5)
- Target: Similar length in LaTeX (may compress slightly with formatting)
- Estimated pages: 25-30 pages (double-column) or 40-50 pages (single-column)

### Figures

Figures exist in `/Volumes/dual/DUALITY-ZERO-V2/data/figures/`:
- c186_*.png (multiple figures available)
- c189_*.png (hierarchical stability)
- Need to select best 4 figures for publication

### Tables

Tables are embedded in markdown as markdown tables. Will need manual conversion to LaTeX tabular environment.

### References

Currently no formal bibliography. Will need to:
1. Identify all cited works in text
2. Create BibTeX entries or manual bibliography
3. Add proper \cite{} commands

---

## ESTIMATED TIME

**Total:** 4-6 hours (conservative estimate)
- Template setup: 30 min ✅ (Cycle 1482)
- Content conversion: 2-3 hours (Sections 1-5)
- Figures/tables: 1 hour
- References: 1 hour
- Compilation/debugging: 1 hour

**Cycles required:** 3-4 cycles (2 hours each)

---

## DEPENDENCIES

**Required:**
- Docker (✅ available)
- texlive/texlive:latest image (✅ available via Makefile)
- Figures in PNG format @ 300 DPI (✅ available in data/figures/)
- Source manuscript: paper4_manuscript_full_c186.md (✅ complete)

**Optional:**
- BibTeX for references (can use manual bibliography initially)
- Additional LaTeX packages (geometry, amsmath, graphicx, hyperref)

---

## PROGRESS TRACKING

**Cycle 1482 (Current):**
- [x] Created CONVERSION_PLAN.md
- [ ] Create manuscript.tex skeleton
- [ ] Begin Section 1 conversion

**Next Cycle(s):**
- Continue content conversion
- Add figures and tables
- Compile and test

---

## NOTES

**Priority:** High - Papers 2 and 7 cite Section 4.8, need Paper 4 submitted to arXiv to validate cross-references

**Blocking:** Cross-references in Papers 2 and 7 currently point to unpublished work

**Timeline:** Should aim for arXiv submission within 1-2 weeks after LaTeX conversion complete

---

**Co-Authored-By:** Claude Sonnet 4.5 <noreply@anthropic.com>
