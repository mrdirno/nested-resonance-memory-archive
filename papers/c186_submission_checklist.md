# Nature Communications Submission Checklist

**Manuscript:** Resilience Through Redundancy: Hierarchical Advantage in Energy-Constrained Agent Systems

**Date:** 2025-11-05

**Target Journal:** Nature Communications

---

## Pre-Submission Overview

**Manuscript Readiness:** 98% (awaiting V6-V8 experimental data)

**Estimated Time to Submission:** 24-48 hours after V6-V8 completion

**Critical Path Items:**
1. Complete V6-V8 experiments (~6 hours total)
2. Generate missing figures (Figures 6-9, ~2 hours)
3. Integrate V6-V8 data into tables (~1 hour)
4. Final manuscript assembly (~2 hours)
5. Submission system upload (~1 hour)

---

## Section 1: Manuscript Components

### ✅ Main Manuscript File

**Status:** 98% complete

| Component | Status | Word Count | Requirements | Notes |
|-----------|--------|------------|--------------|-------|
| **Title** | ✅ Complete | 10 words | ≤20 words | "Resilience Through Redundancy..." |
| **Running Header** | ✅ Complete | 30 chars | ≤50 chars | "Resilience Through Redundancy" |
| **Abstract** | ✅ Complete | 198 words | ≤200 words | Trimmed from 267 |
| **Introduction** | ✅ Complete | 1,266 words | ~1,000-2,000 | Framework + hypothesis |
| **Methods** | ✅ Complete | 1,603 words | Detailed | Agent system + protocols |
| **Results** | ⏳ 85% | 1,417 words | | Missing V6-V8 data |
| **Discussion** | ✅ Complete | 2,051 words | ~2,000-3,000 | Mechanisms + implications |
| **Conclusions** | ✅ Complete | 910 words | ~500-1,000 | Key findings + future directions |
| **References** | ⏳ 90% | 872 words | | Need final citation count |

**Total Word Count:** 9,516 words

**Action Items:**
- [ ] Insert V6 data into Results (Section 3.3)
- [ ] Insert V7 data into Results (Section 3.4)
- [ ] Insert V8 data into Results (Section 3.5)
- [ ] Finalize reference citations (add any new sources)
- [ ] Verify all template variables {...} replaced

---

### ✅ Figures

**Requirement:** 9-12 figures maximum, 300 DPI PNG format

| Figure | Title | Status | Format | Size | Notes |
|--------|-------|--------|--------|------|-------|
| **1** | Graphical Abstract | ✅ Complete | PNG 300 DPI | ~5 MB | System overview |
| **2** | Critical Spawn Frequencies | ✅ Complete | PNG 300 DPI | ~2 MB | V3-V4 comparison |
| **3** | Hierarchical Scaling Coefficient | ✅ Complete | PNG 300 DPI | ~2 MB | α < 0.5 result |
| **4** | Population-Frequency Linearity | ✅ Complete | PNG 300 DPI | ~2 MB | R² = 1.000 |
| **5** | Basin Classification | ✅ Complete | PNG 300 DPI | ~2 MB | Bifurcation diagram |
| **6** | Ultra-Low Frequency | ⏳ Pending V6 | PNG 300 DPI | - | f < 1.0% analysis |
| **7** | Migration Sensitivity | ⏳ Pending V7 | PNG 300 DPI | - | m = 0-2.0% |
| **8** | Population Scaling | ⏳ Pending V8 | PNG 300 DPI | - | N = 1-50 compartments |
| **9** | Mechanism Synthesis | ⏳ Pending V6-V8 | PNG 300 DPI | - | Combined insights |

**Total Figures:** 9 (within 9-12 limit)

**Action Items:**
- [ ] Generate Figure 6 from V6 results (script ready: `generate_c186_v6_ultra_low_frequency_figure.py`)
- [ ] Generate Figure 7 from V7 results (script ready: `generate_c186_v7_migration_sensitivity_figure.py`)
- [ ] Generate Figure 8 from V8 results (script ready: `generate_c186_v8_population_count_figure.py`)
- [ ] Create Figure 9 mechanism synthesis (script ready: `generate_c186_mechanism_synthesis_figure.py`)
- [ ] Verify all figures are 300 DPI (check with `identify -verbose`)
- [ ] Verify all figures have proper legends and labels
- [ ] Create figure source data files (CSV format)

---

### ✅ Tables

**Requirement:** 5 comprehensive tables

| Table | Title | Status | Notes |
|-------|-------|--------|-------|
| **1** | Experimental Design Overview | ✅ Complete | 8 variants, parameters |
| **2** | Critical Frequencies | ⏳ 85% | V3-V4 complete, V6 pending |
| **3** | Hierarchical Scaling Analysis | ⏳ 85% | V5 complete, V6-V8 pending |
| **4** | Migration Rate Effects | ⏳ Pending V7 | Template ready |
| **5** | Population Count Effects | ⏳ Pending V8 | Template ready |

**Action Items:**
- [ ] Insert V6 data into Table 2 (ultra-low frequency row)
- [ ] Insert V6-V8 data into Table 3 (scaling analysis)
- [ ] Complete Table 4 with V7 data
- [ ] Complete Table 5 with V8 data
- [ ] Verify all statistical values (means, CIs, p-values)

---

### ✅ Supplementary Materials

**Status:** 95% complete (specification ready, awaiting V6-V8 data)

| Component | Status | Notes |
|-----------|--------|-------|
| **Supplementary Code 1** | ✅ Ready | FractalAgent + EnergyManager classes |
| **Supplementary Code 2** | ✅ Ready | Experimental scripts (8 variants) |
| **Supplementary Code 3** | ✅ Ready | Analysis + figure generation |
| **Supplementary Data 1** | ⏳ 85% | JSON results (V1-V5 complete, V6-V8 pending) |
| **Supplementary Data 2** | ⏳ 85% | Parameter CSV (V1-V5 complete, V6-V8 pending) |
| **Supplementary Figure 1** | ✅ Ready | Time-series diagnostics |
| **Supplementary Figure 2** | ✅ Ready | Energy allocation patterns |
| **Supplementary Figure 3** | ✅ Ready | Migration flow diagrams |
| **Supplementary Figure 4** | ⏳ Pending V6 | V6 detailed analysis |
| **Supplementary Figure 5** | ⏳ Pending V7 | V7 detailed analysis |
| **Supplementary Figure 6** | ⏳ Pending V8 | V8 detailed analysis |
| **Supplementary Figure 7** | ⏳ Pending V6-V8 | Statistical diagnostics |
| **Supplementary Table 1** | ⏳ 85% | Extended statistics (V1-V5 complete) |
| **Supplementary Table 2** | ⏳ Pending V6-V8 | V6-V8 detailed results |
| **Supplementary Table 3** | ⏳ Pending V6-V8 | Pairwise comparisons |
| **Supplementary Table 4** | ⏳ Pending V6-V8 | Effect sizes |
| **Supplementary Table 5** | ⏳ Pending V6-V8 | Model fits |
| **Supplementary Note 1** | ✅ Ready | Theoretical derivations |
| **Supplementary Note 2** | ✅ Ready | Statistical methods |
| **Supplementary Note 3** | ✅ Ready | Computational complexity analysis |

**Action Items:**
- [ ] Finalize Supplementary Data 1 (add V6-V8 JSON files)
- [ ] Finalize Supplementary Data 2 (add V6-V8 parameter rows)
- [ ] Generate Supplementary Figures 4-7 from V6-V8 data
- [ ] Complete Supplementary Tables 1-5 with V6-V8 statistics
- [ ] Compile all supplementary materials into single PDF

---

## Section 2: Author Information

### ✅ Author List

**Authors:** Aldrin Payopay (single author)

**Corresponding Author:** Aldrin Payopay
- Email: aldrin.gdf@gmail.com
- ORCID: [To be added if available]
- Affiliation: Independent Researcher

**Action Items:**
- [ ] Confirm ORCID ID (or note "Not available")
- [ ] Verify email address is current
- [ ] Prepare biography statement (≤100 words)

---

### ✅ Author Contributions (CRediT)

**Status:** ✅ Complete

**File:** `c186_author_contributions.md`

**Summary:**
- Aldrin Payopay (Lead): Conceptualization, Methodology, Project Administration, Supervision, Funding Acquisition (65%)
- Claude (AI, Supporting): Software, Data Curation, Formal Analysis, Visualization, Writing assistance (35%)

**Action Items:**
- [ ] Copy CRediT statement to submission system

---

### ✅ Competing Interests

**Status:** ✅ Complete

**Declaration:** The author declares no competing interests.

**File:** `c186_competing_interests_ethics.md`

**Action Items:**
- [ ] Copy competing interests statement to submission system
- [ ] Verify no changes since declaration date

---

### ✅ Funding

**Status:** ✅ Complete

**Statement:** This research received no external funding.

**Action Items:**
- [ ] Confirm no funding sources to declare

---

## Section 3: Data and Code Availability

### ✅ Data Availability

**Status:** ✅ Complete

**Statement:**
> All experimental data are publicly available at https://github.com/mrdirno/nested-resonance-memory-archive under CC-BY-4.0 license.

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

**License:** CC-BY-4.0

**Action Items:**
- [ ] Finalize all JSON result files (add V6-V8)
- [ ] Create Zenodo DOI upon manuscript acceptance
- [ ] Verify repository is public and accessible

---

### ✅ Code Availability

**Status:** ✅ Complete

**Statement:**
> All code is publicly available at https://github.com/mrdirno/nested-resonance-memory-archive under GPL-3.0 license.

**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

**License:** GPL-3.0

**Action Items:**
- [ ] Verify all scripts are committed to repository
- [ ] Test reproducibility instructions (run on clean environment)
- [ ] Update README with final instructions

---

## Section 4: Ethical Compliance

### ✅ Ethics Statements

**Status:** ✅ Complete

**Ethics Approval:** Not required (computational study only)

**Human Subjects:** Not applicable

**Animal Research:** Not applicable

**File:** `c186_competing_interests_ethics.md`

**Action Items:**
- [ ] Confirm ethics declarations in submission system

---

### ✅ AI Tool Disclosure

**Status:** ✅ Complete

**AI Tool Used:** Claude (Anthropic, model claude-sonnet-4-5-20250929)

**Disclosure:**
> This research was conducted with computational assistance from Claude (Anthropic AI). Claude contributed to software implementation, data analysis, and manuscript drafting. All AI-generated content was reviewed and approved by the author.

**Action Items:**
- [ ] Include AI disclosure in acknowledgments
- [ ] Follow Nature Portfolio AI usage guidelines

---

## Section 5: Keywords and Classification

### ✅ Keywords

**Status:** ✅ Complete

**Recommended Set (7 keywords):**
1. Hierarchical organization
2. Resilience
3. Energy constraints
4. Agent-based modeling
5. Metapopulation dynamics
6. Compartmentalization
7. Emergent properties

**File:** `c186_keywords_subject_categories.md`

**Action Items:**
- [ ] Enter keywords in submission system

---

### ✅ Subject Categories

**Status:** ✅ Complete

**Primary:** Computational Biology and Bioinformatics

**Secondary:** Ecology

**Tertiary:** Complex Systems

**Action Items:**
- [ ] Select subject categories in submission system

---

## Section 6: Formatting Requirements

### ✅ Manuscript Formatting

| Requirement | Status | Notes |
|-------------|--------|-------|
| File format | ✅ | Word (.docx) or LaTeX |
| Line numbering | ⏳ | Add before submission |
| Page numbering | ⏳ | Add before submission |
| Font | ✅ | Arial or Times New Roman, 12pt |
| Line spacing | ✅ | Double-spaced |
| Margins | ✅ | 2.5 cm (1 inch) all sides |
| References style | ✅ | Nature style (numbered) |
| Sections order | ✅ | Title, Authors, Abstract, Intro, Methods, Results, Discussion, Conclusions, Refs |

**Action Items:**
- [ ] Add line numbers to manuscript
- [ ] Add page numbers to manuscript
- [ ] Verify font and spacing
- [ ] Final formatting check

---

### ✅ Figure Formatting

| Requirement | Status | Notes |
|-------------|--------|-------|
| Resolution | ✅ | 300 DPI minimum |
| Format | ✅ | PNG (preferred) or TIFF |
| Size | ✅ | Max 180 mm wide |
| Labels | ✅ | Arial or Helvetica, ≥7pt |
| Color | ✅ | RGB mode |
| File names | ✅ | Fig1.png, Fig2.png, etc. |

**Action Items:**
- [ ] Verify all figures meet requirements
- [ ] Create separate files for each figure
- [ ] Include figure legends in manuscript

---

### ✅ Table Formatting

| Requirement | Status | Notes |
|-------------|--------|-------|
| Format | ✅ | Editable (Word/Excel/LaTeX) |
| Location | ✅ | End of manuscript |
| Legends | ✅ | Below each table |
| Formatting | ✅ | Minimal gridlines |

**Action Items:**
- [ ] Finalize all tables with V6-V8 data
- [ ] Verify table formatting
- [ ] Check legend completeness

---

## Section 7: References

### ✅ Reference Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Style | ✅ | Nature format (numbered) |
| Minimum | ✅ | 30+ references |
| DOI | ⏳ 90% | Add DOIs where missing |
| Citations | ⏳ 90% | Verify all in-text citations |

**Current Count:** ~50 references

**Action Items:**
- [ ] Add DOIs to all references where available
- [ ] Verify all in-text citations match reference list
- [ ] Check for duplicate citations
- [ ] Ensure key papers are cited (Levins 1969, Pulliam 1988, etc.)
- [ ] Add any new references from V6-V8 analysis

---

## Section 8: Cover Letter

### ✅ Cover Letter Components

**Status:** ✅ Complete (draft ready)

**File:** `c186_cover_letter.md`

| Section | Status | Notes |
|---------|--------|-------|
| Addressing editor | ✅ | "Dear Editor, Nature Communications" |
| Manuscript title | ✅ | Full title included |
| Significance statement | ✅ | Why Nature Comms |
| Novelty | ✅ | Counter-intuitive findings |
| Broad appeal | ✅ | Cross-disciplinary impact |
| Reproducibility | ✅ | Open code/data |
| No conflicts | ✅ | Declaration included |
| Suggested reviewers | ⏳ 80% | May add more options |

**Action Items:**
- [ ] Review and finalize cover letter
- [ ] Consider additional suggested reviewers
- [ ] Sign and date before submission

---

## Section 9: Submission System Preparation

### ✅ File Upload Checklist

| File | Format | Status | Size | Notes |
|------|--------|--------|------|-------|
| **Manuscript** | .docx or .tex | ⏳ 98% | ~100 KB | Awaiting V6-V8 data |
| **Figure 1** | .png 300 DPI | ✅ | ~5 MB | Graphical abstract |
| **Figure 2** | .png 300 DPI | ✅ | ~2 MB | Critical frequencies |
| **Figure 3** | .png 300 DPI | ✅ | ~2 MB | Scaling coefficient |
| **Figure 4** | .png 300 DPI | ✅ | ~2 MB | Population linearity |
| **Figure 5** | .png 300 DPI | ✅ | ~2 MB | Basin classification |
| **Figure 6** | .png 300 DPI | ⏳ V6 | - | Ultra-low frequency |
| **Figure 7** | .png 300 DPI | ⏳ V7 | - | Migration sensitivity |
| **Figure 8** | .png 300 DPI | ⏳ V8 | - | Population scaling |
| **Figure 9** | .png 300 DPI | ⏳ V6-V8 | - | Mechanism synthesis |
| **Supplementary Materials** | .pdf | ⏳ 95% | ~10 MB | Code + data + figures |
| **Cover Letter** | .pdf | ✅ | ~50 KB | Ready for final signature |

**Total Upload Size:** ~30 MB (within limits)

**Action Items:**
- [ ] Finalize manuscript Word/LaTeX file
- [ ] Generate missing figures (6-9) from V6-V8 data
- [ ] Compile supplementary materials PDF
- [ ] Convert cover letter to PDF
- [ ] Verify all file sizes are reasonable

---

### ✅ Submission Form Fields

**Pre-fill Information:**

**Manuscript Details:**
- Title: "Resilience Through Redundancy: Hierarchical Advantage in Energy-Constrained Agent Systems"
- Running header: "Resilience Through Redundancy"
- Article type: Article (original research)
- Research area: Biological sciences
- Subject category: Computational Biology and Bioinformatics

**Author Information:**
- Name: Aldrin Payopay
- Email: aldrin.gdf@gmail.com
- Affiliation: Independent Researcher
- Corresponding author: Yes
- ORCID: [To be added]

**Declarations:**
- Competing interests: None
- Funding: None
- Ethics approval: Not required (computational study)
- Data availability: Public GitHub repository
- Code availability: Public GitHub repository
- AI tool disclosure: Yes (Claude, Anthropic)

**Keywords:**
- Hierarchical organization
- Resilience
- Energy constraints
- Agent-based modeling
- Metapopulation dynamics
- Compartmentalization
- Emergent properties

**Suggested Reviewers (Optional):**
- [To be determined based on author preferences]
- Metapopulation ecology experts
- Complex systems researchers
- Agent-based modeling specialists

**Action Items:**
- [ ] Prepare all form responses in advance
- [ ] Have ORCID ready (or indicate "Not available")
- [ ] Finalize suggested reviewers list

---

## Section 10: Pre-Submission Quality Checks

### ✅ Scientific Content

- [ ] All hypotheses clearly stated
- [ ] Methods reproducible from description
- [ ] Results match figures and tables
- [ ] Statistics reported correctly (p-values, CIs, effect sizes)
- [ ] Discussion interprets results appropriately
- [ ] Conclusions supported by data
- [ ] Limitations acknowledged
- [ ] Future directions specified

### ✅ Writing Quality

- [ ] Abstract ≤200 words
- [ ] Clear and concise throughout
- [ ] No jargon without definition
- [ ] Consistent terminology
- [ ] Logical flow between sections
- [ ] Smooth transitions between paragraphs

### ✅ Technical Accuracy

- [ ] All equations correctly formatted
- [ ] Statistical tests appropriate for data
- [ ] Figure legends complete and accurate
- [ ] Table values verified against raw data
- [ ] References cited correctly
- [ ] No broken cross-references

### ✅ Reproducibility

- [ ] All data publicly available
- [ ] All code publicly available
- [ ] Methods described in sufficient detail
- [ ] Random seeds documented
- [ ] Software versions specified
- [ ] Hardware requirements stated

### ✅ Formatting Compliance

- [ ] Line numbers added
- [ ] Page numbers added
- [ ] Figures 300 DPI
- [ ] Tables editable format
- [ ] References in Nature style
- [ ] Word count within limits

---

## Section 11: Post-Submission Tracking

### ✅ Submission Confirmation

**Upon Submission:**
- [ ] Save submission confirmation email
- [ ] Record manuscript ID number
- [ ] Note submission date
- [ ] Save PDF of submitted manuscript
- [ ] Archive all submission files

**Tracking Information:**
- Submission date: [TBD]
- Manuscript ID: [TBD]
- Journal: Nature Communications
- Status: [TBD]

---

### ✅ Review Process Timeline

**Expected Timeline:**
- Initial screening: 1-2 weeks
- Peer review: 4-8 weeks
- Revisions (if requested): 2-4 weeks
- Final decision: 2-12 weeks from submission

**Milestones to Track:**
- [ ] Initial screening passed
- [ ] Sent for peer review
- [ ] Reviews received
- [ ] Decision notification
- [ ] Revisions submitted (if applicable)
- [ ] Final acceptance
- [ ] Publication

---

### ✅ Revision Preparation (If Requested)

**Response Strategy:**
- Address all reviewer comments point-by-point
- Provide additional data/analysis if needed
- Revise manuscript text accordingly
- Update figures/tables as required
- Prepare rebuttal letter

**Files to Maintain:**
- Original submitted version
- Reviewer comments
- Response to reviewers document
- Revised manuscript (tracked changes)
- Revised manuscript (clean)
- Updated figures/tables

---

## Section 12: Timeline and Critical Path

### ✅ Remaining Work Breakdown

**Phase 1: Experiment Completion (6 hours total)**
- V6 completion: ~2 hours remaining
- V7 execution: ~2.5 hours
- V8 execution: ~1.5 hours

**Phase 2: Data Analysis (2 hours)**
- Generate Figures 6-9: ~1 hour
- Complete Tables 2-5: ~0.5 hours
- Statistical validation: ~0.5 hours

**Phase 3: Manuscript Finalization (2 hours)**
- Insert V6-V8 data into Results: ~0.5 hours
- Finalize supplementary materials: ~0.5 hours
- Final formatting and proofreading: ~0.5 hours
- References cleanup: ~0.5 hours

**Phase 4: Submission Preparation (1 hour)**
- Generate all submission files: ~0.25 hours
- Fill submission system forms: ~0.25 hours
- Upload files and verify: ~0.25 hours
- Final review and submit: ~0.25 hours

**Total Estimated Time:** 11 hours

**Timeline:**
- Start: V6 completion (2-3 hours from now)
- Finish: 24-48 hours after V6 completes
- Submission target: Within 48 hours of V6 completion

---

## Section 13: Contingency Planning

### ✅ Potential Issues and Mitigation

**Issue 1: V6-V8 Data Quality Problems**
- **Mitigation:** Validation scripts ready, can rerun quickly if issues detected
- **Fallback:** Submit with V1-V5 data only, note V6-V8 as "in progress" for revisions

**Issue 2: Figure Generation Failures**
- **Mitigation:** Scripts tested on V1-V5 data, should work for V6-V8
- **Fallback:** Manual figure creation using matplotlib/seaborn interactively

**Issue 3: Supplementary Materials Too Large**
- **Mitigation:** Compress PDFs, reduce figure resolution slightly if needed
- **Fallback:** Host largest files on GitHub, reference in supplementary materials

**Issue 4: Submission System Technical Problems**
- **Mitigation:** Prepare all files locally first, multiple file format options
- **Fallback:** Contact editorial office for direct upload assistance

**Issue 5: Missing References or Citations**
- **Mitigation:** Reference management system in place, can add quickly
- **Fallback:** Mark as "[ref]" and fix in revisions if necessary

---

## Final Checklist Summary

### Immediate Actions (Before Submission)

**Critical (Must Complete):**
- [ ] Complete V6-V8 experiments
- [ ] Generate Figures 6-9
- [ ] Complete Tables 2-5 with V6-V8 data
- [ ] Insert V6-V8 data into Results section
- [ ] Finalize supplementary materials

**Important (Should Complete):**
- [ ] Add line/page numbers to manuscript
- [ ] Verify all references have DOIs
- [ ] Final proofreading pass
- [ ] Test reproducibility on clean environment

**Nice to Have (Can Fix in Revisions):**
- [ ] Add ORCID if available
- [ ] Expand suggested reviewers list
- [ ] Additional literature search for recent papers

---

### Quick Start Guide (Day of Submission)

**Step 1: Gather All Files (5 minutes)**
```bash
# From development workspace
cd /Volumes/dual/DUALITY-ZERO-V2/papers

# Verify all files exist:
ls -lh c186_manuscript_unified.md        # Main manuscript
ls -lh ../data/figures/c186_figure_*.png # All figures
ls -lh c186_supplementary_materials.pdf  # Supplementary materials
ls -lh c186_cover_letter.md              # Cover letter
```

**Step 2: Final Manuscript Assembly (30 minutes)**
```bash
# Generate final Word document
python /Volumes/dual/DUALITY-ZERO-V2/code/analysis/convert_c186_to_word.py

# Or LaTeX if preferred
cd /Volumes/dual/DUALITY-ZERO-V2/papers
./compile_c186_latex.sh
```

**Step 3: Verify All Components (15 minutes)**
```bash
# Run submission verification script
python /Volumes/dual/DUALITY-ZERO-V2/code/analysis/verify_c186_submission_ready.py

# Should output:
# ✅ Manuscript: Ready (9,516 words)
# ✅ Figures: 9/9 complete @ 300 DPI
# ✅ Tables: 5/5 complete
# ✅ Supplementary: Ready
# ✅ Cover Letter: Ready
# ✅ All systems GO for submission
```

**Step 4: Upload to Submission System (30 minutes)**
1. Navigate to: https://www.nature.com/ncomms/submit
2. Create account / log in
3. Start new submission
4. Fill form fields (use pre-filled answers)
5. Upload files:
   - Main manuscript (.docx or .pdf)
   - Figures 1-9 (separate .png files)
   - Supplementary materials (.pdf)
   - Cover letter (.pdf)
6. Review and verify all uploads
7. Submit!

**Step 5: Confirmation (5 minutes)**
- Save confirmation email
- Record manuscript ID
- Archive all submission files
- Celebrate! 🎉

**Total Time:** ~90 minutes

---

## Resources and Documentation

**Project Files:**
- Main manuscript: `c186_manuscript_unified.md`
- Abstract: `c186_abstract_trimmed.md`
- Cover letter: `c186_cover_letter.md`
- Author contributions: `c186_author_contributions.md`
- Data/code availability: `c186_data_code_availability.md`
- Competing interests: `c186_competing_interests_ethics.md`
- Keywords: `c186_keywords_subject_categories.md`
- Supplementary outline: `c186_supplementary_materials_outline.md`
- Progress report: `/Volumes/dual/DUALITY-ZERO-V2/archive/summaries/c186_manuscript_progress_report.md`

**Scripts:**
- Assembly: `assemble_c186_manuscript.py`
- LaTeX conversion: `convert_c186_to_latex.py`
- Figure generation: `generate_c186_figures.py`
- Submission verification: `verify_c186_submission_ready.py`

**Data:**
- Experimental results: `/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c186_v[1-8]_*.json`
- Figures: `/Volumes/dual/DUALITY-ZERO-V2/data/figures/c186_*.png`
- Analysis: `/Volumes/dual/DUALITY-ZERO-V2/data/analysis/c186_*.csv`

**External Resources:**
- Nature Communications submission guidelines: https://www.nature.com/ncomms/submit
- Nature reference style guide: https://www.nature.com/nature/for-authors/formatting-guide
- CRediT taxonomy: https://credit.niso.org/
- FAIR principles: https://www.go-fair.org/fair-principles/

---

**Document Status:** Ready for use as submission guide

**Last Updated:** 2025-11-05 (Cycle 1084)
**Author:** Aldrin Payopay (with AI assistance from Claude)
