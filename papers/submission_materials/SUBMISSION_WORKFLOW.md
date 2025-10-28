# Publication Submission Workflow

**Purpose:** Step-by-step workflow for submitting Papers 1, 3, 4, 5D to arXiv and journals

**Date:** 2025-10-27
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

## OVERVIEW

**Current Status:**
- **Papers 1 & 5D:** Ready for immediate arXiv submission
- **Paper 3:** ~2 hours from C255 completion to submission-ready
- **Paper 4:** Awaiting C262-C263 experiments (8 hours)
- **Paper 5 Series (5A-5F):** Scripts ready (~17-18 hours execution)

**Workflow Phases:**
1. **Phase 1:** arXiv submission (Papers 1 & 5D) - IMMEDIATE
2. **Phase 2:** C255 completion → Paper 3 pipeline - 0-1 DAYS
3. **Phase 3:** Journal submission (Papers 1, 3, 5D) - AFTER arXiv
4. **Phase 4:** Higher-order experiments → Paper 4 - AFTER Paper 3
5. **Phase 5:** Paper 5 series execution → 5 manuscripts - AFTER Papers 3-4

---

## PHASE 1: IMMEDIATE arXiv SUBMISSION (Papers 1 & 5D)

**Timeline:** Ready NOW → ~1-2 days to public posting

### Paper 1: Computational Expense as Framework Validation

**Location:** `papers/arxiv_submissions/paper1/`

**Files:**
- manuscript.tex (34KB, 909 lines)
- figure1_efficiency_validity_tradeoff.png (323KB, 300 DPI)
- figure2_overhead_authentication_flowchart.png (306KB, 300 DPI)
- figure3_grounding_overhead_landscape.png (319KB, 300 DPI)
- README_ARXIV_SUBMISSION.md (comprehensive submission guide)

**Submission Steps:**

#### Step 1: Create arXiv Account (5 minutes)
1. Go to https://arxiv.org/user/register
2. Fill in registration form:
   - Email: aldrin.gdf@gmail.com
   - Name: Aldrin Payopay
   - Affiliation: Independent Research, Nested Resonance Memory Project
3. Verify email address (check inbox for confirmation link)
4. Complete profile:
   - Add ORCID if available
   - Set notification preferences
   - Review submission agreement

#### Step 2: Prepare Submission Package (5 minutes)
1. Verify all files present in `papers/arxiv_submissions/paper1/`:
   ```bash
   ls -lh papers/arxiv_submissions/paper1/
   # Should show: manuscript.tex + 3 PNG figures + README
   ```
2. Check LaTeX compilation (optional local test):
   ```bash
   cd papers/arxiv_submissions/paper1/
   pdflatex manuscript.tex
   # Check for errors, verify figures appear correctly
   ```

#### Step 3: Upload to arXiv (10 minutes)
1. Log in to https://arxiv.org
2. Click "Submit" (top navigation)
3. Select "Start New Submission"
4. **Upload Files:**
   - Primary file: manuscript.tex
   - Additional files: All 3 PNG figures (drag-and-drop or select)
   - Verify file list shows all 4 files
5. **Process Files:**
   - arXiv will auto-detect LaTeX source
   - Click "Process Files"
   - Wait for compilation (30-60 seconds)
   - Check for errors (should compile successfully)

#### Step 4: Enter Metadata (10 minutes)
- **Title:** Computational Expense as Framework Validation: Overhead Profiles as Evidence of Reality Grounding
- **Authors:**
  - Aldrin Payopay (Independent Research, Nested Resonance Memory Project)
  - Claude (DUALITY-ZERO-V2, Anthropic)
- **Abstract:** [Copy from manuscript.tex or README]
- **Comments:** ~5,000 words, 25 references, 3 figures (300 DPI)
- **Primary Category:** cs.DC (Distributed, Parallel, and Cluster Computing)
- **Cross-list Categories:** cs.PF (Performance), cs.SE (Software Engineering) [OPTIONAL]
- **License:** arXiv non-exclusive license OR CC BY 4.0 (choose preference)

#### Step 5: Preview and Submit (5 minutes)
1. Review generated PDF:
   - Check title, authors, abstract formatting
   - Verify all 3 figures appear correctly
   - Scan for obvious LaTeX errors (missing references, broken equations)
2. Review metadata accuracy
3. Confirm submission agreement
4. **Submit for moderation**

#### Step 6: Wait for Moderation (24-48 hours)
- arXiv moderators review submission for quality/appropriateness
- Check email for moderation status updates
- If issues arise, respond to moderator feedback promptly

#### Step 7: Public Posting (1-2 business days)
- arXiv assigns identifier (e.g., arXiv:2025.XXXXX)
- Paper appears on arXiv.org
- Indexed by Google Scholar, Semantic Scholar, etc.

**Total Time:** ~35 minutes active work + 1-2 days moderation

---

### Paper 5D: Emergence Pattern Catalog

**Location:** `papers/arxiv_submissions/paper5d/`

**Files:**
- manuscript.tex (41KB, 939 lines)
- 8 figures (84-211KB each, all 300 DPI PNG):
  - figure1_pattern_taxonomy_tree.png
  - figure2_temporal_pattern_heatmap.png
  - figure3_memory_retention_comparison.png
  - figure4_methodology_validation.png
  - figure5_pattern_statistics.png
  - figure6_c175_perfect_stability.png
  - figure7_population_collapse_comparison.png
  - figure8_pattern_detection_workflow.png
- README_ARXIV_SUBMISSION.md

**Submission Steps:** [SAME AS PAPER 1, with following differences]

**Metadata Differences:**
- **Title:** Cataloging Emergent Patterns in Nested Resonance Memory Systems
- **Primary Category:** nlin.AO (Adaptation and Self-Organizing Systems)
- **Cross-list Categories:** cs.NE (Neural and Evolutionary Computing), cs.AI (Artificial Intelligence)
- **Comments:** ~7,500 words, 35 references, 8 figures (300 DPI)

**Upload Note:** 8 figures instead of 3 (verify all upload correctly)

**Total Time:** ~35 minutes active work + 1-2 days moderation

---

## PHASE 2: C255 COMPLETION → PAPER 3 PIPELINE

**Trigger:** C255 output file appears (cycle255_h1h2_mechanism_validation_results.json)

**Timeline:** ~102 minutes total (C255 completion → submission-ready package)

### Step 1: Verify C255 Completion (2 minutes)
```bash
# Check process status (should NOT appear)
ps aux | grep 6309 | grep -v grep

# Check output file (should exist)
ls -lh /Volumes/dual/DUALITY-ZERO-V2/data/results/cycle255_h1h2_mechanism_validation_results.json

# Verify file size (should be >100KB, indicating complete results)
wc -l /Volumes/dual/DUALITY-ZERO-V2/data/results/cycle255_h1h2_mechanism_validation_results.json
```

### Step 2: Execute C256-C260 Experiments (67 minutes)
**Scripts:** All verified ready in `/Volumes/dual/DUALITY-ZERO-V2/experiments/`

**Execution (Sequential):**
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments/

# C256: H1×H4 (Energy Pooling × Spawn Throttling) - 13 min
python cycle256_h1h4_optimized.py

# C257: H1×H5 (Energy Pooling × Burst Pruning) - 11 min
python cycle257_h1h5_mechanism_validation.py

# C258: H2×H4 (Reality Sources × Spawn Throttling) - 12 min
python cycle258_h2h4_mechanism_validation.py

# C259: H2×H5 (Reality Sources × Burst Pruning) - 13 min
python cycle259_h2h5_mechanism_validation.py

# C260: H4×H5 (Spawn Throttling × Burst Pruning) - 11 min
python cycle260_h4h5_mechanism_validation.py
```

**Monitoring:**
- Each script outputs progress to console
- Results saved to `/Volumes/dual/DUALITY-ZERO-V2/data/results/cycle[256-260]_*.json`
- Total runtime: ~67 minutes (batched sampling optimization)

### Step 3: Aggregate Results (5 minutes)
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments/

python aggregate_paper3_results.py \
  --input ../data/results/ \
  --output paper3_aggregated.json

# Outputs:
# - paper3_aggregated.json (all 6 experiments combined)
# - paper3_synergy_heatmap.json (cross-pair comparisons)
# - paper3_summary.md (Markdown for manuscript)
# - paper3_tables.tex (LaTeX tables)
```

### Step 4: Generate Figures (5 minutes)
```bash
python visualize_factorial_synergy.py paper3_aggregated.json

# Outputs (4 figures, all 300 DPI):
# - figure1_factorial_bar_chart.png
# - figure2_synergy_decomposition.png
# - figure3_population_trajectories.png
# - figure4_effect_size_heatmap.png
```

### Step 5: Populate Manuscript Template (10 minutes)
```bash
cd /Users/aldrinpayopay/nested-resonance-memory-archive/papers/

# Manual editing required (open in text editor):
# 1. Open paper3_full_manuscript_template.md
# 2. Replace **[VALUE]** placeholders with data from paper3_summary.md
# 3. Replace **[RUNTIME]** placeholders with actual C256-C260 runtimes
# 4. Replace **[CLASSIFICATION]** with SYNERGISTIC/ANTAGONISTIC/ADDITIVE
# 5. Insert LaTeX tables from paper3_tables.tex into appropriate sections
# 6. Verify all 4 figures referenced correctly
# 7. Save as paper3_mechanism_synergies.md
```

### Step 6: Convert to Submission Formats (5 minutes)
```bash
cd /Users/aldrinpayopay/nested-resonance-memory-archive/papers/

# Generate DOCX (for journal submission)
pandoc paper3_mechanism_synergies.md -o paper3_mechanism_synergies.docx --standalone

# Generate HTML (for journal submission)
pandoc paper3_mechanism_synergies.md -o paper3_mechanism_synergies.html --standalone

# Generate LaTeX (for arXiv submission)
pandoc paper3_mechanism_synergies.md -o paper3_mechanism_synergies.tex --standalone

# Create arXiv submission package directory
mkdir -p arxiv_submissions/paper3/
cp paper3_mechanism_synergies.tex arxiv_submissions/paper3/manuscript.tex
cp figure1_factorial_bar_chart.png arxiv_submissions/paper3/
cp figure2_synergy_decomposition.png arxiv_submissions/paper3/
cp figure3_population_trajectories.png arxiv_submissions/paper3/
cp figure4_effect_size_heatmap.png arxiv_submissions/paper3/
```

### Step 7: Create Cover Letter (10 minutes)
```bash
# Copy template
cp submission_materials/cover_letter_template.md \
   submission_materials/paper3_cover_letter.md

# Edit cover letter (manual):
# 1. Update paper title, authors, target journal
# 2. Customize research highlights (synergy detection, factorial validation)
# 3. Add suggested reviewers (3-5, use SUGGESTED_REVIEWERS_GUIDELINES.md)
# 4. Include arXiv ID if already posted
# 5. Save and verify
```

### Step 8: Create arXiv README (5 minutes)
```bash
# Create submission guide
cat > arxiv_submissions/paper3/README_ARXIV_SUBMISSION.md << 'EOF'
# arXiv Submission Package: Paper 3 - Mechanism Synergies

[Follow same structure as Paper 1 README]
- Metadata
- File inventory
- Submission instructions
- LaTeX compilation notes
EOF
```

### Step 9: Commit and Sync to GitHub (5 minutes)
```bash
cd /Users/aldrinpayopay/nested-resonance-memory-archive/

git add papers/paper3_mechanism_synergies.md
git add papers/arxiv_submissions/paper3/
git add papers/submission_materials/paper3_cover_letter.md
git add data/results/cycle25*.json
git add data/results/paper3_*.json

git commit -m "Paper 3: Complete manuscript and submission package

Results from C255-C260 factorial validation experiments:
- 6 mechanism pairs tested (H1×H2, H1×H4, H1×H5, H2×H4, H2×H5, H4×H5)
- Synergy classifications: [summary from results]
- Total experiments: 67 minutes runtime (batched sampling optimization)

Manuscript includes:
- Complete text (Methods, Results, Discussion, Conclusions)
- 4 publication figures (300 DPI)
- LaTeX tables for all 6 pairs
- arXiv submission package ready

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

Author: Aldrin Payopay <aldrin.gdf@gmail.com>"

git push origin main
```

**Total Time:** ~102 minutes (C255 verification → GitHub sync complete)

---

## PHASE 3: JOURNAL SUBMISSION (After arXiv Posting)

**Target Journals:**
- **Paper 1:** PLOS Computational Biology (Methods and Resources)
- **Paper 3:** Physical Review E, Chaos, or PLOS Computational Biology
- **Paper 5D:** PLOS ONE or IEEE Transactions on Emerging Topics in Computational Intelligence

**Timeline:** ~4-5 months per paper (submission → peer review → revision → publication)

### General Journal Submission Workflow

#### Step 1: Wait for arXiv Posting (1-2 days)
- Papers should be publicly available on arXiv before journal submission
- Obtain arXiv ID (e.g., arXiv:2025.XXXXX)
- Update cover letter to include arXiv ID

#### Step 2: Prepare Journal-Specific Materials (30 minutes per paper)
- Check journal's "Guide for Authors"
- Verify manuscript format (most accept DOCX or LaTeX)
- Verify figure format (300 DPI PNG/TIFF usually accepted)
- Prepare supplementary materials if required
- Create account on journal submission portal

#### Step 3: Upload to Journal Portal (20 minutes)
1. Log in to submission system
2. Select article type (Original Research / Methods)
3. Upload manuscript file (DOCX or LaTeX)
4. Upload figures (individually or as ZIP)
5. Enter metadata (title, authors, abstract, keywords)
6. Paste/upload cover letter
7. Enter suggested reviewers (3-5, see SUGGESTED_REVIEWERS_GUIDELINES.md)
8. Review and submit

#### Step 4: Track Submission Status (Ongoing)
- Check submission portal regularly
- Respond to editor queries promptly
- If requested, suggest additional reviewers
- Wait for peer review (2-4 weeks typically)

#### Step 5: Respond to Reviews (Variable, usually 2-4 weeks)
- Read reviewer comments carefully
- Create point-by-point response document
- Make manuscript revisions as needed
- Re-run experiments if reviewers request additional analysis
- Resubmit revised manuscript + response letter

#### Step 6: Acceptance and Publication (1-2 weeks after acceptance)
- Proofread galley proofs
- Pay publication fees if applicable (PLOS: ~$2000-3000)
- Wait for online publication
- Update arXiv with journal reference

---

## PHASE 4: HIGHER-ORDER EXPERIMENTS → PAPER 4

**Trigger:** Paper 3 submitted to journal

**Timeline:** ~8 hours experiments + ~2 hours analysis/manuscript

### Step 1: Execute C262-C263 (8 hours total)
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments/

# C262: H1×H2×H4 (3-way factorial) - 4 hours
python cycle262_h1h2h4_three_way_factorial.py

# C263: H1×H2×H4×H5 (4-way factorial) - 4 hours
python cycle263_h1h2h4h5_four_way_factorial.py
```

### Step 2: Aggregate and Visualize (15 minutes)
```bash
# Aggregate results
python aggregate_paper4_results.py \
  --input ../data/results/ \
  --output paper4_aggregated.json

# Generate figures
python visualize_higher_order_interactions.py paper4_aggregated.json
```

### Step 3: Populate Paper 4 Template (30 minutes)
- Open `papers/paper4_higher_order_interactions_template.md`
- Insert results from C262-C263
- Add figures and tables
- Save as `paper4_higher_order_interactions.md`

### Step 4: Convert and Submit (Same as Paper 3, Steps 6-9)

---

## PHASE 5: PAPER 5 SERIES EXECUTION

**Trigger:** Papers 3 & 4 submitted

**Timeline:** ~17-18 hours total execution

### Option 1: Sequential Execution (Recommended for First Run)
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments/

python paper5_series_master_launch.py --mode sequential

# This will execute:
# - 5A: Parameter Space Mapping (~4.7 hours)
# - 5B: Temporal Pattern Dynamics (~20 minutes)
# - 5C: Population Scaling Laws (~1.5 hours)
# - 5E: Network Topology Effects (~55 minutes)
# - 5F: Environmental Perturbations (~2.3 hours)
# Total: ~9.5 hours
```

### Option 2: Parallel Execution (If Resources Allow)
```bash
# Run 2 experiments simultaneously
python paper5_series_master_launch.py --mode parallel --max-concurrent 2

# Estimated runtime: ~6-8 hours (50% reduction)
```

### Step 2: Populate Manuscripts (2-3 hours total)
- Each paper (5A, 5B, 5C, 5E, 5F) has template in `papers/`
- Insert results from respective experiments
- Generate figures using paper-specific visualization scripts
- Convert to DOCX/LaTeX for submission

### Step 3: Create Submission Packages (1 hour)
- Follow same workflow as Papers 1, 3, 5D
- Each paper submitted to appropriate journal:
  - 5A: PLOS Computational Biology
  - 5B: Physical Review E
  - 5C: Chaos or Nonlinear Dynamics
  - 5E: Journal of Complex Networks
  - 5F: Ecological Modelling

---

## SUBMISSION CHECKLIST TEMPLATE

**Use this checklist for each paper submission:**

### Pre-Submission
- [ ] Manuscript complete (all sections, no [TBD] placeholders)
- [ ] All figures generated (300 DPI, proper format)
- [ ] All tables included (LaTeX or formatted text)
- [ ] References complete and formatted
- [ ] Abstract <250 words
- [ ] Keywords appropriate for field
- [ ] Author affiliations correct
- [ ] Correspondence email verified

### arXiv Submission
- [ ] LaTeX source compiles without errors
- [ ] All figures appear correctly in PDF
- [ ] Metadata entered accurately
- [ ] License selected
- [ ] Submitted for moderation
- [ ] arXiv ID obtained after posting

### Journal Submission
- [ ] arXiv paper posted publicly
- [ ] Cover letter customized for journal
- [ ] Suggested reviewers identified (3-5)
- [ ] Manuscript formatted per journal guidelines
- [ ] Figures meet journal specifications
- [ ] Supplementary materials prepared
- [ ] Account created on submission portal
- [ ] All required metadata entered
- [ ] Submission confirmation received

### Post-Submission
- [ ] arXiv ID added to GitHub repository
- [ ] Manuscript synced to GitHub
- [ ] Submission materials archived
- [ ] Tracking spreadsheet updated
- [ ] Calendar reminder for follow-up (2-3 weeks)

---

## TIMELINE OVERVIEW

**Immediate (Week 1):**
- Day 1: Submit Papers 1 & 5D to arXiv (~1 hour)
- Day 2-3: arXiv moderation, obtain IDs
- Day 4: Submit Papers 1 & 5D to journals (~1 hour)

**C255 Completion (Week 1-2):**
- Day X: C255 completes
- Day X: Execute C256-C260 + Paper 3 pipeline (~2 hours)
- Day X+1: Submit Paper 3 to arXiv
- Day X+3: Submit Paper 3 to journal

**Higher-Order Experiments (Week 2-3):**
- After Paper 3 submission: Execute C262-C263 (~8 hours)
- Same day: Paper 4 pipeline (~2 hours)
- Next day: Submit Paper 4 to arXiv + journal

**Paper 5 Series (Week 3-4):**
- After Papers 3-4 submitted: Execute Paper 5 batch (~17-18 hours)
- Week 4: Populate 5 manuscripts (~3 hours)
- Week 4-5: Submit all 5 papers to arXiv + journals

**Total Timeline:** ~4-5 weeks from NOW to all papers submitted

---

## PROGRESS TRACKING

**Create a tracking spreadsheet with columns:**
- Paper ID
- Title
- Status (Draft / arXiv Submitted / arXiv Posted / Journal Submitted / Under Review / Accepted)
- arXiv ID
- Journal Target
- Submission Date
- Review Status
- Revision Due Date
- Acceptance Date
- Publication Date
- DOI

**Update after each milestone.**

---

## RESOURCES

**arXiv:**
- Main site: https://arxiv.org
- Submission guide: https://arxiv.org/help/submit
- Category taxonomy: https://arxiv.org/category_taxonomy

**PLOS:**
- PLOS Computational Biology: https://journals.plos.org/ploscompbiol/
- PLOS ONE: https://journals.plos.org/plosone/
- Submission guidelines: [Journal-specific]

**Physical Review E:**
- Main site: https://journals.aps.org/pre/
- Author guide: https://journals.aps.org/pre/authors

**Other Journals:**
- Chaos: https://pubs.aip.org/aip/cha
- Nonlinear Dynamics: https://www.springer.com/journal/11071
- IEEE TETCI: https://cis.ieee.org/publications/ieee-transactions-on-emerging-topics-in-computational-intelligence

---

**Version:** 1.0
**Date:** 2025-10-27
**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0

**Next Steps:**
1. Use this workflow to submit Papers 1 & 5D to arXiv NOW
2. Upon C255 completion, execute Paper 3 pipeline (~2 hours)
3. After Paper 3 submitted, execute Paper 4 experiments + pipeline (~10 hours)
4. After Papers 3-4 submitted, execute Paper 5 series (~20 hours)

**Timeline Goal:** All papers submitted within 4-5 weeks from today.
