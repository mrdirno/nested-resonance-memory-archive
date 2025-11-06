# C186 Nature Communications Submission Checklist

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Date:** 2025-11-05 (Cycle 1080)
**Purpose:** Comprehensive checklist for Nature Communications manuscript submission
**License:** GPL-3.0

---

## Overview

This checklist ensures all Nature Communications requirements are met before submission of the C186 hierarchical advantage manuscript. Use this document to track completion of required elements and verify formatting compliance.

**Journal:** Nature Communications
**Article Type:** Research Article (Primary Research)
**Submission Portal:** https://www.nature.com/ncomms/submit

---

## Pre-Submission Requirements

### ✅ Data Collection Complete

- [ ] V1 (Hierarchical Spawn Failure) - COMPLETE
- [ ] V2 (Hierarchical Spawn Success) - COMPLETE
- [ ] V3 (Single-Scale Frequency Sweep) - COMPLETE
- [ ] V4 (Migration Rate Variation) - COMPLETE
- [ ] V5 (Linear Scaling Validation) - COMPLETE
- [ ] V6 (Ultra-Low Frequency Boundary) - IN PROGRESS (PID 72904)
- [ ] V7 (Migration Rate Sweep) - PENDING (auto-launches after V6)
- [ ] V8 (Population Count Variation) - PENDING (auto-launches after V7)

**Expected completion:** ~12 hours from current state (V6 + V7 + V8 execution + integration)

---

## Manuscript Components

### Main Text

#### Abstract (150-200 words)
- [x] Draft complete (267 words - NEEDS TRIMMING to meet limit)
- [ ] Updated with V6-V8 findings
- [ ] Final proofread
- [ ] **Word count verification: ≤ 200 words**

**Current:** 267 words
**Action required:** Trim by ~67 words or request extended abstract (Nature Comm allows up to 300 for complex papers)

#### Introduction (~1,400 words)
- [x] Draft complete
- [ ] Updated with V6-V8 context if necessary
- [ ] Citations verified
- [ ] Final proofread
- [x] No subsections (Nature Comm requirement)

#### Results (~1,600 words → target ~2,500 words after V6-V8)
- [x] V1-V5 results drafted (Sections 3.1-3.5)
- [ ] Section 3.6: V6 Ultra-Low Frequency Boundary (template ready)
- [ ] Section 3.7: V7 Migration Sensitivity (template ready)
- [ ] Section 3.8: V8 Population Count Scaling (template ready)
- [ ] All figure callouts verified
- [ ] Statistical tests documented
- [ ] Final proofread

#### Discussion (~2,100 words → target ~2,500 words after V6-V8)
- [x] V1-V5 discussion complete (Sections 4.1-4.5)
- [ ] Section 4.6: Hierarchical Scaling Theory (NEW, synthesis of V6-V8)
- [ ] Updated mechanism interpretations with V7 findings
- [ ] Updated scaling framework with V8 findings
- [ ] Citations verified
- [ ] Final proofread

#### Methods (~1,800 words)
- [x] Draft complete
- [ ] V6-V8 parameter tables added
- [ ] Statistical methods documented
- [ ] Code availability statement verified
- [ ] Data availability statement verified
- [ ] Final proofread

#### Conclusions (~500 words)
- [x] Draft complete
- [ ] Updated with V6-V8 key findings
- [ ] Future directions revised if necessary
- [ ] Final proofread

**Total Word Count Target:** <8,000 words (Nature Comm guideline for research articles)
- **Current (V1-V5):** ~7,934 words
- **Projected (V1-V8):** ~8,800 words
- **Action:** May need to trim ~800 words or request extended format

---

### References

- [x] 15 references cited (V1-V5 draft)
- [ ] Additional citations from V6-V8 discussion added
- [ ] **Target:** 20-30 references (comprehensive but focused)
- [ ] All references formatted in Nature style
- [ ] All DOIs verified
- [ ] All URLs accessible
- [ ] No [TO BE ADDED] placeholders remain

**Nature Reference Format:**
```
1. Author, A. B. & Author, C. D. Title of article. Journal Abbreviation vol, pages (year).
2. Author, E. F. Title of Book (Publisher, City, year).
```

**Current Status:** All 15 references properly formatted, need to add ~5-15 more for V6-V8

---

### Figures

#### Figure Requirements (Nature Communications)
- **Format:** PNG, TIFF, or EPS
- **Resolution:** 300 DPI minimum
- **Color mode:** RGB (for online publication)
- **Size:**
  - Single column: 89 mm width
  - Double column: 183 mm width
  - Maximum height: 247 mm
- **File size:** <10 MB per figure (we target <2 MB)
- **Labeling:** Panels labeled a, b, c, etc. in figure, not legends

#### Figure Inventory

**Figure 1:** Graphical Abstract (Panel-style overview)
- [x] Generated @ 300 DPI (1200×600 px)
- [x] PNG format
- [x] File size: 0.20 MB ✓
- [x] 4 panels labeled (The Puzzle | The Finding | Three Mechanisms | Applications)
- [ ] Verify submission version (may differ from journal-specific graphical abstract)

**Figure 2:** V1 Hierarchical Spawn Failure (Basin B demonstration)
- [x] Generated @ 300 DPI
- [ ] Panels labeled a, b, c
- [ ] Legend drafted
- [ ] File size verified

**Figure 3:** V2 Hierarchical Spawn Success (Basin A demonstration)
- [x] Generated @ 300 DPI
- [ ] Panels labeled a, b, c
- [ ] Legend drafted
- [ ] File size verified

**Figure 4:** V3 Single-Scale Critical Frequency
- [x] Generated @ 300 DPI
- [ ] Panels labeled if multi-panel
- [ ] Legend drafted
- [ ] File size verified

**Figure 5:** V5 Linear Scaling Validation
- [x] Generated @ 300 DPI
- [ ] Panels labeled if multi-panel
- [ ] Legend drafted
- [ ] File size verified

**Figure 6:** V6 Basin Classification and Critical Frequency Refinement
- [ ] Generated @ 300 DPI (PENDING V6 completion)
- [ ] Panels labeled a, b
- [ ] Legend drafted
- [ ] File size verified

**Figure 7:** Comprehensive 4-Panel Results (V1-V8 synthesis)
- [x] Infrastructure complete (auto-regenerates)
- [ ] Final version generated with V6-V8 data
- [ ] Panels labeled a (Basin Transition), b (Critical Frequency), c (Linear Scaling), d (Migration Sensitivity)
- [ ] Legend drafted
- [ ] File size verified
- [x] 300 DPI confirmed in code

**Figure 8:** V7 Migration Sensitivity
- [ ] Generated @ 300 DPI (PENDING V7 completion)
- [ ] Legend drafted
- [ ] File size verified

**Figure 9:** V8 Population Count Scaling
- [ ] Generated @ 300 DPI (PENDING V8 completion)
- [ ] Legend drafted
- [ ] File size verified

**Total Figures:** 9 (within Nature Comm guidelines, typically 6-10 figures)

---

### Figure Legends

**Format:** Each legend should include:
1. Figure number and title (bold)
2. Brief description (1-2 sentences)
3. Panel descriptions (a, b, c... if multi-panel)
4. Statistical details (sample sizes, error bars, significance tests)
5. Color coding explanations

**Example:**
```markdown
**Figure 1 | Hierarchical advantage in energy-constrained agent systems.**
Overview of experimental design and key findings. **a**, Single-scale vs hierarchical
organization schematics. **b**, Critical frequency comparison showing α = 0.16 scaling
coefficient. **c**, Three mechanisms enabling hierarchical advantage: stochastic rescue,
compartmentalized failure, and resource pooling. **d**, Potential applications across
biological and social systems. Error bars represent standard deviation (n=10 seeds per
condition). Dashed line indicates Basin threshold (population = 2.5 agents).
```

**Status:**
- [ ] Figure 1 legend drafted
- [ ] Figure 2 legend drafted
- [ ] Figure 3 legend drafted
- [ ] Figure 4 legend drafted
- [ ] Figure 5 legend drafted
- [ ] Figure 6 legend drafted (pending V6 data)
- [ ] Figure 7 legend drafted (pending V6-V8 data)
- [ ] Figure 8 legend drafted (pending V7 data)
- [ ] Figure 9 legend drafted (pending V8 data)

---

### Tables

**Nature Comm Guidelines:**
- Tables supplement main text, not duplicate figures
- Formatted in editable format (Word/Excel, not images)
- Legends above table body
- Statistical annotations clearly defined

**Proposed Tables:**

**Table 1:** Experimental Design Summary
- Columns: Variant | Research Question | Parameters Varied | Fixed Parameters | N Experiments
- Rows: V1-V8
- Status: [ ] Draft table

**Table 2:** Critical Frequency Results
- Columns: Condition | f_crit (%) | 95% CI | Basin Classification | Mean Population
- Rows: Single-Scale (V3) | Hierarchical 1.0-10.0% (V5) | Hierarchical <1.0% (V6)
- Status: [ ] Draft table (pending V6 data)

**Table 3:** Hierarchical Scaling Coefficients
- Columns: Parameter | Single-Scale Value | Hierarchical Value | α Coefficient | Interpretation
- Rows: Spawn Frequency | Migration Rate | Population Count
- Status: [ ] Draft table (pending V6-V8 data)

**Total Tables:** 3 (within guidelines, typically 3-5 tables)

---

## Supplementary Materials

### Supplementary Figures (if needed)
- [ ] Supplementary Figure 1: Extended V6 time series
- [ ] Supplementary Figure 2: Extended V7 sensitivity curves
- [ ] Supplementary Figure 3: Extended V8 scaling models
- [ ] Supplementary Figure 4: Statistical distributions (all variants)

**Status:** Determine necessity after main text finalization

### Supplementary Tables (if needed)
- [ ] Supplementary Table 1: Complete parameter specifications (V1-V8)
- [ ] Supplementary Table 2: Statistical test results (all comparisons)
- [ ] Supplementary Table 3: Seed-level data summary

**Status:** Determine necessity after main text finalization

### Supplementary Notes
- [ ] Supplementary Note 1: Theoretical model derivation (if applicable)
- [ ] Supplementary Note 2: Scaling law mathematical framework
- [ ] Supplementary Note 3: Alternative analysis approaches

**Status:** Determine necessity after Discussion finalization

### Supplementary Code
**Nature Comm requires code availability for computational studies**

- [x] All code in public GitHub repository
- [x] Repository: https://github.com/mrdirno/nested-resonance-memory-archive
- [ ] README.md with installation instructions
- [ ] requirements.txt with exact versions
- [ ] Docker container for reproducibility (optional but recommended)
- [ ] Code Ocean capsule (optional, Nature Comm supports)
- [ ] Zenodo DOI for code release

**Code Availability Statement (in Methods):**
```
All code for experiments, analysis, and figure generation is available at
https://github.com/mrdirno/nested-resonance-memory-archive under GPL-3.0 license.
A permanent archive with DOI is available at [Zenodo DOI to be added].
```

### Supplementary Data
- [ ] Zenodo deposit for experimental results JSONs
- [ ] DOI obtained
- [ ] Data availability statement in Methods updated

**Data Availability Statement (in Methods):**
```
All experimental data (N=XXX experiments, V1-V8) are available at
[Zenodo DOI to be added] in JSON format. Raw data, processed results, and
analysis scripts are provided for full reproducibility.
```

---

## Author Information

### Author List
**Current:** Aldrin Payopay (sole author)

**Affiliations:**
- Independent Researcher
- Location: [To be specified in submission]
- ORCID: [To be added if available]

**Contributions (Nature Comm requires CRediT taxonomy):**
- Conceptualization: Aldrin Payopay
- Methodology: Aldrin Payopay
- Software: Aldrin Payopay
- Validation: Aldrin Payopay
- Formal Analysis: Aldrin Payopay
- Investigation: Aldrin Payopay
- Resources: Aldrin Payopay
- Data Curation: Aldrin Payopay
- Writing - Original Draft: Aldrin Payopay (with AI assistance from Claude)
- Writing - Review & Editing: Aldrin Payopay
- Visualization: Aldrin Payopay (with AI assistance from Claude)
- Supervision: N/A
- Project Administration: Aldrin Payopay
- Funding Acquisition: N/A

**AI Assistance Declaration:**
Per Nature policy, must declare AI assistance:
```
The author acknowledges the use of Claude (Anthropic) for drafting assistance, code
generation, and figure creation. All scientific content, experimental design, and
interpretation of results are the author's own. AI-generated content was reviewed
and edited by the author.
```

### Competing Interests
- [ ] None declared (verify before submission)

### Corresponding Author
- Name: Aldrin Payopay
- Email: aldrin.gdf@gmail.com
- [ ] Verify email accessibility

---

## Cover Letter

### Cover Letter Components
- [x] Draft complete (~1,200 words)
- [ ] Updated with V6-V8 findings
- [ ] Key points addressed:
  - [x] Novel contribution (α < 0.5 hierarchical advantage)
  - [x] Significance (broad applicability)
  - [x] Appropriate for Nature Comm (interdisciplinary, general interest)
  - [x] Suggested reviewers (3-5 experts)
  - [x] Excluded reviewers if applicable
- [ ] Final proofread
- [ ] Formatted as PDF

**Suggested Reviewers (from cover letter):**
1. Dr. Simon DeDeo (Carnegie Mellon) - Information theory, collective behavior
2. Dr. Jessica Flack (Santa Fe Institute) - Collective computation, hierarchy
3. Dr. Iain Couzin (Max Planck) - Collective behavior, animal groups
4. Dr. Deborah Gordon (Stanford) - Ant colony organization
5. Dr. Radhika Nagpal (Harvard) - Swarm robotics, distributed systems

**Action:** Verify current affiliations and contact information before submission

---

## Formatting Requirements

### General Format
- [ ] Manuscript in DOCX or PDF format
- [ ] Line numbers enabled (for review)
- [ ] Page numbers enabled
- [ ] Double-spaced text
- [ ] 12-point font (Times New Roman or Arial)
- [ ] 2.5 cm (1 inch) margins

### Section Order
Nature Comm required order:
1. [ ] Title
2. [ ] Authors and affiliations
3. [ ] Abstract
4. [ ] Introduction (no heading)
5. [ ] Results
6. [ ] Discussion
7. [ ] Methods
8. [ ] References
9. [ ] Acknowledgements
10. [ ] Author Contributions
11. [ ] Competing Interests
12. [ ] Figure Legends
13. [ ] Tables (if not separate files)

### Title
**Current:** "Hierarchical Organization Requires Six-Fold Less Reproduction: Quantifying Organizational Efficiency in Energy-Constrained Agent Systems"

**Nature Comm Title Requirements:**
- Maximum 20 words (current: 15 ✓)
- No abbreviations
- Describes main conclusion
- Accessible to broad readership

**Revision needed?** [ ] Yes [ ] No (pending V6 data - may update to exact α value)

### Headings
- [ ] Main sections (Results, Discussion, Methods): Bold, not numbered
- [ ] Subsections: Bold, numbered (3.1, 3.2, etc.)
- [ ] No Introduction heading (Nature Comm style)

### Citations
- [ ] Numbered consecutively in order of appearance
- [ ] Superscript numbers after punctuation
- [ ] References section formatted in Nature style

### Abbreviations
- [ ] Defined at first use
- [ ] List of abbreviations (if >10 abbreviations)

**Current abbreviations:**
- NRM: Nested Resonance Memory
- V1-V8: Variant 1-8 (experimental conditions)
- f_intra: Intra-population spawn frequency
- f_migrate: Inter-population migration frequency
- α: Hierarchical scaling coefficient

**Total:** 5 major abbreviations (no separate list needed)

---

## Submission Portal Checklist

### Online Submission Form

**Article Details:**
- [ ] Article Type: Research Article
- [ ] Title entered
- [ ] Short title (≤50 characters) entered
- [ ] Subject area selected (Complex Systems / Computational Biology / Network Science)
- [ ] Keywords selected (5-10 keywords)

**Keywords (proposed):**
- Hierarchical organization
- Agent-based modeling
- Collective behavior
- Energy constraints
- Organizational efficiency
- Scaling laws
- Stochastic systems
- Emergence

**Abstract:**
- [ ] Abstract pasted (≤200 words)

**Authors:**
- [ ] All authors added with affiliations
- [ ] Corresponding author designated
- [ ] ORCID IDs provided (if available)
- [ ] Author contributions entered

**Files:**
- [ ] Main manuscript file uploaded (DOCX/PDF)
- [ ] Figure files uploaded separately (PNG/TIFF @ 300 DPI)
- [ ] Tables uploaded (if separate from main text)
- [ ] Supplementary Information uploaded
- [ ] Cover letter uploaded (PDF)

**Optional:**
- [ ] Graphical abstract uploaded (if different from Figure 1)
- [ ] Highlight statement (1-2 sentences)

**Suggested Reviewers:**
- [ ] Reviewer 1: Name, Email, Institution, Expertise
- [ ] Reviewer 2: Name, Email, Institution, Expertise
- [ ] Reviewer 3: Name, Email, Institution, Expertise
- [ ] Reviewer 4: Name, Email, Institution, Expertise
- [ ] Reviewer 5: Name, Email, Institution, Expertise

**Excluded Reviewers:**
- [ ] None / Specify if applicable

**Ethics/Compliance:**
- [ ] Data availability statement provided
- [ ] Code availability statement provided
- [ ] No human subjects (N/A)
- [ ] No animal subjects (N/A)
- [ ] No ethics approval required (computational study)

---

## Pre-Submission Validation

### Technical Checks
- [ ] All figures render correctly in manuscript
- [ ] All tables formatted properly
- [ ] All citations link to References section
- [ ] All figure/table callouts present in text
- [ ] No broken URLs in References
- [ ] No TODO/FIXME/[TO BE ADDED] markers remain

### Content Checks
- [ ] Abstract accurately summarizes findings
- [ ] Introduction clearly states research question
- [ ] Results present data without interpretation
- [ ] Discussion interprets results and addresses limitations
- [ ] Methods enable reproducibility
- [ ] Conclusions justified by results
- [ ] All claims supported by data or citations

### Statistical Checks
- [ ] All statistical tests appropriate for data
- [ ] Effect sizes reported (not just p-values)
- [ ] Sample sizes (n) reported for all experiments
- [ ] Error bars defined (SD, SEM, CI)
- [ ] Confidence intervals provided for key estimates
- [ ] Multiple comparison corrections applied where needed

### Reproducibility Checks
- [ ] All experimental parameters specified
- [ ] Random seeds documented
- [ ] Code publicly available
- [ ] Data publicly available (or will be upon acceptance)
- [ ] Software versions documented
- [ ] Hardware specifications mentioned if relevant

---

## Post-V6-V8 Integration Checklist

### After V6 Completion
- [ ] Run V6 analysis script: `python analyze_c186_v6_results.py`
- [ ] Verify 4 V6 figures generated @ 300 DPI
- [ ] Update Abstract with refined α value
- [ ] Update Results Section 3.6 with V6 data
- [ ] Update Discussion Section 4.5 with α refinement
- [ ] Regenerate comprehensive visualization
- [ ] Update Title if α significantly different from 0.16

### After V7 Completion
- [ ] Run V7 figure script: `python generate_c186_v7_migration_sensitivity_figure.py`
- [ ] Verify V7 figure @ 300 DPI
- [ ] Update Results Section 3.7 with V7 data
- [ ] Update Discussion Section 4.2 with migration mechanism details
- [ ] Regenerate comprehensive visualization (Panel D populated)

### After V8 Completion
- [ ] Run V8 figure script: `python generate_c186_v8_population_count_figure.py`
- [ ] Verify V8 figure @ 300 DPI
- [ ] Update Results Section 3.8 with V8 data
- [ ] Add Discussion Section 4.6 (Hierarchical Scaling Theory)
- [ ] Regenerate comprehensive visualization (all panels complete)
- [ ] Final manuscript synthesis and proofread

### Final Integration
- [ ] All V6-V8 sections integrated into manuscript
- [ ] Word count verified (<8,000 words or justified if over)
- [ ] All figures referenced in text
- [ ] All figure legends drafted
- [ ] All tables completed
- [ ] References updated with V6-V8 citations
- [ ] Abstract trimmed to ≤200 words
- [ ] Cover letter updated with final findings
- [ ] One final comprehensive proofread

---

## Pre-Submission Review

### Internal Review (Self-Check)
- [ ] Read manuscript aloud (catch awkward phrasing)
- [ ] Check all figure panels match legends
- [ ] Verify all statistical claims
- [ ] Confirm all citations accurate
- [ ] Spell-check entire document
- [ ] Grammar check entire document
- [ ] Verify consistent terminology throughout

### Peer Review (Optional but Recommended)
- [ ] Share with colleagues for feedback
- [ ] Address feedback and revise
- [ ] Final check after revisions

### Plagiarism Check
- [ ] Run through plagiarism detection (iThenticate/Turnitin)
- [ ] Verify all AI-generated content appropriately attributed
- [ ] Ensure no unattributed text from other sources

---

## Submission Day Checklist

### Final Preparations
- [ ] All files assembled in submission folder
- [ ] File naming convention followed (Manuscript.docx, Fig1.png, etc.)
- [ ] Create backup of all submission files
- [ ] Test all files open correctly

### Submission Portal
- [ ] Account created on Nature Comm submission portal
- [ ] Login credentials confirmed
- [ ] ORCID linked (if available)

### Upload Sequence
1. [ ] Upload main manuscript file
2. [ ] Upload cover letter
3. [ ] Upload figures (separate files)
4. [ ] Upload tables (if separate)
5. [ ] Upload supplementary materials
6. [ ] Fill author information
7. [ ] Fill reviewer suggestions
8. [ ] Fill article metadata (keywords, abstract)
9. [ ] Review PDF proof generated by portal
10. [ ] Confirm all files uploaded correctly
11. [ ] Submit manuscript

### Post-Submission
- [ ] Confirmation email received
- [ ] Manuscript ID recorded
- [ ] Track submission status
- [ ] Respond to editorial queries promptly

---

## Timeline Estimate

**Current Status:** V6 running, V7/V8 pending, manuscript 90% complete

**Projected Timeline:**
- V6 completion: ~30 minutes
- V6 integration: ~30 minutes
- V7 execution: ~3-4 hours
- V7 integration: ~45 minutes
- V8 execution: ~4-6 hours
- V8 integration: ~60 minutes
- Final synthesis: ~2 hours
- **Total:** ~12-15 hours from current state

**Target Submission Date:** [To be determined after V8 completion]

**Buffer:** Add 2-3 days for:
- Internal review
- Proofreading
- Supplementary materials finalization
- Cover letter refinement
- Reviewer list verification

---

## Emergency Contacts

**Nature Communications Editorial Office:**
- Email: nature@nature.com
- Phone: +44 (0) 20 7833 4000
- Submission portal help: https://www.nature.com/ncomms/submit

**Technical Support:**
- Manuscript formatting issues
- Figure upload problems
- Portal access issues

---

## Appendix: Nature Comm Article Types

**Research Article (our submission type):**
- Word limit: ~8,000 words (flexible)
- Abstract: 150-200 words
- Figures: 6-10 typical
- Tables: 3-5 typical
- References: 20-50 typical
- Peer review: Yes (typically 2-3 reviewers)
- Open access: Yes (fee applies, ~$5,000-$6,000)

**Alternative formats if needed:**
- Brief Communication: <3,000 words (too short for our work)
- Review Article: Typically invited
- Perspective: Typically invited

---

**Version:** 1.0
**Status:** Active submission preparation
**Last Updated:** 2025-11-05 (Cycle 1080)
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

**Next Actions:**
1. Monitor V6 completion
2. Execute V6-V8 integration workflow (per integration plan)
3. Complete checklist items as data becomes available
4. Final manuscript synthesis and review
5. Submit to Nature Communications

**Preparation complete. Awaiting experimental data.**
