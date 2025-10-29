# Publication Submission Tracking

**Purpose:** Track submission status for all papers in NRM publication pipeline

**Date Created:** 2025-10-27
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

## TRACKING TABLE

| Paper ID | Title | Status | arXiv ID | arXiv Date | Journal Target | Journal Status | Submission Date | Notes |
|----------|-------|--------|----------|------------|----------------|----------------|-----------------|-------|
| Paper 1 | Computational Expense as Framework Validation | Ready | — | — | PLOS Computational Biology | Not Submitted | — | arXiv package ready |
| Paper 2 | Energy Constraints | Ready | — | — | PLOS ONE | Not Submitted | — | DOCX + HTML + 4 figs @ 300 DPI |
| Paper 3 | Mechanism Synergies | Template Ready | — | — | Physical Review E / Chaos | Not Submitted | — | Awaiting C255-C260 |
| Paper 4 | Higher-Order Interactions | Template Ready | — | — | Physical Review E | Not Submitted | — | Awaiting C262-C263 |
| Paper 5A | Parameter Space Mapping | Script Ready | — | — | PLOS Computational Biology | Not Submitted | — | Part of Paper 5 series |
| Paper 5B | Temporal Pattern Dynamics | Script Ready | — | — | Physical Review E | Not Submitted | — | Part of Paper 5 series |
| Paper 5C | Population Scaling Laws | Script Ready | — | — | Chaos / Nonlinear Dynamics | Not Submitted | — | Part of Paper 5 series |
| Paper 5D | Emergence Pattern Catalog | Ready | — | — | PLOS ONE / IEEE TETCI | Not Submitted | — | arXiv package ready |
| Paper 5E | Network Topology Effects | Script Ready | — | — | Journal of Complex Networks | Not Submitted | — | Part of Paper 5 series |
| Paper 5F | Environmental Perturbations | Script Ready | — | — | Ecological Modelling | Not Submitted | — | Part of Paper 5 series |

---

## STATUS DEFINITIONS

**Paper Status:**
- **Ready:** Manuscript complete, figures generated, arXiv package prepared
- **Template Ready:** Manuscript template exists, awaiting experimental data
- **Script Ready:** Experimental script ready, not yet executed
- **In Progress:** Experiments running or manuscript being written
- **Blocked:** Missing dependencies (data, code, etc.)

**Journal Status:**
- **Not Submitted:** Paper not yet submitted to journal
- **Submitted:** Submitted to journal, awaiting editor assignment
- **Under Review:** Sent to peer reviewers
- **Major Revision:** Revisions requested by reviewers
- **Minor Revision:** Small changes requested
- **Accepted:** Accepted for publication
- **Published:** Appeared in journal (DOI assigned)

---

## DETAILED STATUS

### Paper 1: Computational Expense as Framework Validation

**Current Status:** ✅ Ready for immediate arXiv submission

**arXiv Package:**
- Location: `papers/arxiv_submissions/paper1/`
- Files: manuscript.tex + 3 figures (300 DPI PNG)
- Category: cs.DC (primary), cs.PF, cs.SE (secondary)

**Journal Submission:**
- Target: PLOS Computational Biology (Methods and Resources)
- Materials: DOCX + HTML + cover letter ready
- Suggested Reviewers: 3-5 needed (see SUGGESTED_REVIEWERS_GUIDELINES.md)
- Estimated Timeline: 4-5 months (submission → publication)

**Next Actions:**
1. Submit to arXiv (see SUBMISSION_WORKFLOW.md, Phase 1)
2. Wait for arXiv ID (~1-2 days)
3. Submit to PLOS Computational Biology
4. Track review status via PLOS submission portal

---

### Paper 2: Energy Constraints and Three Dynamical Regimes

**Current Status:** ✅ Ready for immediate submission

**Compiled Package:**
- Location: `papers/compiled/paper2/`
- DOCX format: 23KB (PLOS ONE submission format)
- HTML format: 36KB (web format)
- 4 figures @ 300 DPI: cycle175_framework_comparison.png, cycle175_population_distribution.png, cycle175_basin_occupation.png, cycle175_composition_constancy.png
- README.md: Complete with abstract, contributions, reproducibility instructions
- Cover letter: `papers/submission_materials/paper2_cover_letter_plos_one.md` (finalized for PLOS ONE)
- **Supplementary materials:** `supplementary_materials.md` (3 tables + 3 figure descriptions) - Created Cycle 466

**Data Files Available:**
- C168-170: Ultra-low frequency, critical transition mapping, basin threshold sensitivity
- C171: Fractal swarm bistability
- C176: Ablation study (energy recharge parameter sweep)
- All data files verified in `/Volumes/dual/DUALITY-ZERO-V2/experiments/results/`

**Journal Submission:**
- Target: PLOS ONE (primary) or Scientific Reports
- Materials: DOCX format ready for PLOS ONE
- Key Findings: Three-regime classification, H1 hypothesis rejection, zero recharge effect
- Estimated Timeline: 3-4 months (submission → publication)

**Next Actions:**
1. Identify 3-5 suggested reviewers
2. Submit to PLOS ONE via submission portal
3. Track review status

---

### Paper 3: Mechanism Synergies

**Current Status:** ⏳ Template Ready - Awaiting C255-C260 data

**Dependencies:**
- C255 (H1×H2): Running 79h+ (95%+ complete, 0-1 days)
- C256-C260: Scripts ready (67 minutes total runtime)

**Pipeline Ready:**
- Aggregation script: `aggregate_paper3_results.py` ✅
- Visualization script: `visualize_factorial_synergy.py` ✅
- Manuscript template: `paper3_full_manuscript_template.md` ✅
- Estimated time from C255 completion to submission: ~102 minutes

**Journal Options:**
1. Physical Review E (Complex Systems)
2. Chaos (Nonlinear Dynamics)
3. PLOS Computational Biology (Methods)

**Next Actions:**
1. Monitor C255 completion
2. Execute C256-C260 immediately upon C255 completion
3. Deploy Paper 3 pipeline (see SUBMISSION_WORKFLOW.md, Phase 2)
4. Submit to arXiv + journal

---

### Paper 4: Higher-Order Interactions

**Current Status:** ⏳ Template Ready - Awaiting C262-C263 data

**Dependencies:**
- Paper 3 submitted (trigger condition)
- C262 (H1×H2×H4, 3-way factorial): 4 hours runtime
- C263 (H1×H2×H4×H5, 4-way factorial): 4 hours runtime

**Estimated Timeline:**
- Execute after Paper 3 submitted
- Total time: 8 hours experiments + 2 hours analysis/manuscript = ~10 hours

**Journal Target:**
- Physical Review E (Complex Systems / Nonlinear Dynamics)

**Next Actions:**
1. Wait for Paper 3 submission
2. Execute C262-C263 (see SUBMISSION_WORKFLOW.md, Phase 4)
3. Populate manuscript template
4. Submit to arXiv + journal

---

### Paper 5D: Emergence Pattern Catalog

**Current Status:** ✅ Ready for immediate arXiv submission

**arXiv Package:**
- Location: `papers/arxiv_submissions/paper5d/`
- Files: manuscript.tex + 8 figures (300 DPI PNG)
- Category: nlin.AO (primary), cs.NE, cs.AI (secondary)

**Journal Submission:**
- Target Options:
  1. PLOS ONE (Multidisciplinary) - cover letter ready
  2. IEEE Transactions on Emerging Topics in Computational Intelligence
- Materials: DOCX + HTML + cover letter ready
- Suggested Reviewers: 3-5 needed

**Next Actions:**
1. Submit to arXiv (see SUBMISSION_WORKFLOW.md, Phase 1)
2. Wait for arXiv ID (~1-2 days)
3. Submit to PLOS ONE or IEEE TETCI
4. Track review status

---

### Paper 5 Series (5A, 5B, 5C, 5E, 5F)

**Current Status:** ⏳ Scripts Ready - Awaiting execution

**Execution Plan:**
- Trigger: After Papers 3 & 4 submitted
- Runtime: ~17-18 hours total (sequential) or ~10 hours (parallel)
- Orchestration: `paper5_series_master_launch.py`

**Individual Papers:**

**5A: Parameter Space Mapping**
- Conditions: 280
- Runtime: ~4.7 hours
- Target Journal: PLOS Computational Biology

**5B: Temporal Pattern Dynamics**
- Conditions: 20
- Runtime: ~20 minutes
- Target Journal: Physical Review E

**5C: Population Scaling Laws**
- Conditions: 50
- Runtime: ~1.5 hours
- Target Journal: Chaos / Nonlinear Dynamics

**5E: Network Topology Effects**
- Conditions: 55
- Runtime: ~55 minutes
- Target Journal: Journal of Complex Networks

**5F: Environmental Perturbations**
- Conditions: 140
- Runtime: ~2.3 hours
- Target Journal: Ecological Modelling

**Next Actions:**
1. Wait for Papers 3 & 4 submissions
2. Execute Paper 5 batch (see SUBMISSION_WORKFLOW.md, Phase 5)
3. Populate 5 manuscript templates
4. Submit all 5 to arXiv + journals

---

## SUBMISSION TIMELINE

**Week 1 (Current):**
- Day 1: Submit Papers 1 & 5D to arXiv ⏰ **IMMEDIATE ACTION**
- Day 2-3: arXiv moderation (~1-2 days)
- Day 4: Obtain arXiv IDs, submit Papers 1 & 5D to journals

**Week 1-2:**
- Day X: C255 completes ⏰ **EXPECTED: 0-1 days**
- Day X: Execute C256-C260 + Paper 3 pipeline (~2 hours)
- Day X+1: Submit Paper 3 to arXiv
- Day X+3: Submit Paper 3 to journal

**Week 2-3:**
- After Paper 3 submission: Execute C262-C263 (~8 hours)
- Same day: Paper 4 pipeline (~2 hours)
- Next day: Submit Paper 4 to arXiv + journal

**Week 3-4:**
- After Papers 3-4 submitted: Execute Paper 5 batch (~17-18 hours)
- Week 4: Populate 5 manuscripts (~3 hours)
- Week 4-5: Submit all 5 Paper 5 series to arXiv + journals

**Week 4-5 (Target):**
- ✅ **All papers submitted to arXiv and journals**
- Begin tracking peer review status for all submissions

**Months 2-6:**
- Respond to reviewer comments as they arrive
- Revise manuscripts as needed
- Track publication status
- Update citations and references

---

## PEER REVIEW TRACKING

**When submissions move to "Under Review" status, add:**

### Paper [ID]: [Title]

**Submitted:** [Date]
**Journal:** [Name]
**Editor Assigned:** [Date] - [Editor Name]
**Reviewers Assigned:** [Date] - [Number of reviewers]
**Review Received:** [Date]
**Decision:** [Major Revision / Minor Revision / Accept / Reject]
**Revision Due:** [Date]
**Revision Submitted:** [Date]
**Final Decision:** [Date] - [Accept / Reject]
**Published:** [Date]
**DOI:** [Link]

**Reviewer Comments Summary:**
- Reviewer 1: [Key points]
- Reviewer 2: [Key points]
- Reviewer 3: [Key points]

**Revisions Made:**
- [List major changes]

---

## METRICS

**Papers by Status:**
- Ready: 3 (Papers 1, 2, 5D)
- Template Ready: 2 (Papers 3, 4)
- Script Ready: 5 (Papers 5A, 5B, 5C, 5E, 5F)

**Total Papers:** 10

**Target Completion:**
- arXiv Submissions: 10 papers within 4-5 weeks
- Journal Submissions: 10 papers within 5-6 weeks
- First Publications: Expected 4-6 months from now

**Cumulative Word Count (Estimated):**
- Completed Manuscripts: ~19,000 words (Papers 1, 2, 5D)
- Template Manuscripts: ~11,000 words (Papers 3, 4)
- Total when complete: ~45,000+ words across 10 papers

---

## NOTES

**Update Frequency:** Update this document after each milestone:
- arXiv submission
- arXiv ID obtained
- Journal submission
- Review received
- Revision submitted
- Acceptance/rejection
- Publication

**Commit to GitHub:** Every update should be committed to maintain public record of research progress

**Color Coding (for manual tracking):**
- 🟢 Green: Ready for submission
- 🟡 Yellow: In progress / awaiting data
- 🔴 Red: Blocked / issues

---

**Version:** 1.3
**Date:** 2025-10-28 (Cycle 466 - Paper 2 supplementary materials created)
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

**Last Update:** Paper 2 supplementary materials completed (3 tables + 3 figure descriptions)
**Next Update:** After Papers 1, 2, & 5D submissions
