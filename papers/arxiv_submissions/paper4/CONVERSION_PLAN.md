# Paper 4: LaTeX Conversion Plan

**Date:** 2025-11-19 (Cycle 1482)
**Source:** paper4_manuscript_full_c186.md (1172 lines, 12,800 words)
**Target:** manuscript.tex (arXiv submission)
**Status:** Planning stage

---

## CONVERSION STEPS

### Phase 1: Template Setup ✅ (Cycle 1482)

- [x] Create CONVERSION_PLAN.md (this document)
- [ ] Create manuscript.tex skeleton (preamble, structure)
- [ ] Set up document class and packages
- [ ] Add title, authors, abstract
- [ ] Create section structure (1-5)

### Phase 2: Content Conversion (Est. 2-3 hours, multiple cycles)

**Section 1: Introduction** (~21KB markdown)
- [ ] Convert subsections 1.1, 1.2
- [ ] Convert citations to \cite{}
- [ ] Convert emphasis/bold to LaTeX commands

**Section 2: Methods** (from separate markdown files)
- [ ] Identify methods content sources
- [ ] Convert experimental design descriptions
- [ ] Format equations properly

**Section 3: Results** (from separate markdown files)
- [ ] Convert results sections
- [ ] Create tables (3 total)
- [ ] Add figure placeholders (4 total)

**Section 4: Discussion** (~40KB markdown, includes Section 4.8)
- [ ] Convert subsections 4.1-4.8
- [ ] **Ensure Section 4.8 "Unified Scaling Framework" is clearly marked** (cited by Papers 2, 7)
- [ ] Convert equations and citations

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
