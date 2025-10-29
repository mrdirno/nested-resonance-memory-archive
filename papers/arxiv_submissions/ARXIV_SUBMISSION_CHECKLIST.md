# arXiv Submission Pre-Flight Checklist

**Purpose:** Systematic verification checklist for arXiv submissions to prevent common errors and ensure professional submission handling

**Scope:** Papers 1, 2, 5D (immediate submission-ready), Paper 3 (upon C255-C260 completion)

**Last Updated:** October 29, 2025 (Cycle 486)

---

## OVERVIEW

This checklist provides step-by-step pre-flight verification for arXiv submissions. Complete ALL items in order before submission. Each section includes troubleshooting guidance for common issues.

**Estimated Time:** 15-20 minutes per paper (first submission), 5-10 minutes per paper (subsequent submissions)

---

## PHASE 1: PRE-SUBMISSION VERIFICATION

### 1.1 LaTeX Compilation Check

**Purpose:** Verify manuscript compiles without errors on standard arXiv toolchain

**Steps:**
- [ ] Navigate to paper directory: `cd papers/arxiv_submissions/paperX/`
- [ ] Compile LaTeX manuscript: `pdflatex manuscript.tex`
- [ ] Check for errors: Review compilation log for "Error" or "Fatal"
- [ ] Compile second pass: `pdflatex manuscript.tex` (resolves cross-references)
- [ ] Compile third pass: `pdflatex manuscript.tex` (finalizes references)
- [ ] Verify PDF generated: `ls -lh manuscript.pdf` (should exist, non-zero size)

**Expected Output:**
```
manuscript.pdf  # File size should be >100 KB (indicates figures embedded)
```

**Troubleshooting:**

**Issue 1: "LaTeX Error: File 'X.sty' not found"**
- **Cause:** Missing package in arXiv TeXLive distribution
- **Solution:** Replace with arXiv-compatible package or remove dependency
- **Common packages NOT on arXiv:** Custom .sty files, non-standard fonts
- **Workaround:** Inline package definitions in preamble or use standard packages

**Issue 2: "Undefined control sequence"**
- **Cause:** Custom command not defined or typo in command name
- **Solution:** Check preamble for `\newcommand` definitions, fix typos
- **Common mistake:** Using `\newcommand` after `\begin{document}`

**Issue 3: PDF generated but 0 KB or very small**
- **Cause:** Compilation failed silently, no content rendered
- **Solution:** Check .log file for errors, review .tex syntax
- **Verification:** Open PDF, ensure text visible (not blank pages)

**Pass Criteria:** ✅ Three successful compilations, PDF >100 KB, no errors in log

---

### 1.2 Figure Reference Resolution

**Purpose:** Verify all figure references resolve correctly (no "??" or broken links)

**Steps:**
- [ ] Open compiled PDF: `open manuscript.pdf` (or use PDF viewer)
- [ ] Search for "??" in PDF (indicates unresolved reference)
- [ ] Verify each figure appears: Scroll through document, check all figures render
- [ ] Check figure captions: Ensure captions match figure content
- [ ] Verify figure numbering: Sequential (Figure 1, 2, 3...) with no gaps
- [ ] Check figure resolution: Zoom to 200%, ensure crisp (not pixelated)

**Expected Behavior:**
- All `\ref{fig:X}` commands resolve to figure numbers (e.g., "Figure 1")
- All figures render correctly in PDF (no missing images)
- Figure resolution ≥ 300 DPI (crisp at 200% zoom)

**Troubleshooting:**

**Issue 1: Figure shows "??" instead of number**
- **Cause:** Unresolved cross-reference (need additional LaTeX pass)
- **Solution:** Run `pdflatex manuscript.tex` again (3 passes total recommended)
- **Verification:** Check .aux file for `\newlabel{fig:X}` entries

**Issue 2: Figure missing (blank space or "Image not found")**
- **Cause:** Figure file not in same directory as manuscript.tex
- **Solution:** Copy figure files to paper directory, ensure correct filename
- **Common mistake:** Case-sensitive filenames (figure1.png vs Figure1.png)

**Issue 3: Figure appears pixelated or blurry**
- **Cause:** Low resolution (<300 DPI) or incorrect scaling
- **Solution:** Regenerate figure at 300+ DPI, update LaTeX `\includegraphics` width
- **Verification:** `identify figure.png` (ImageMagick) shows resolution ≥300 DPI

**Issue 4: Figure numbering skips (Figure 1, 3, 4... missing 2)**
- **Cause:** Missing `\label{fig:X}` or duplicate labels
- **Solution:** Check all `\begin{figure}` blocks have unique `\label{fig:X}`
- **Verification:** `grep "label{fig:" manuscript.tex` shows sequential labels

**Pass Criteria:** ✅ No "??" in PDF, all figures render, resolution ≥300 DPI, sequential numbering

---

### 1.3 Metadata Completeness Check

**Purpose:** Verify title, authors, abstract, categories complete and correct

**Steps:**
- [ ] **Title:** Verify title in manuscript.tex matches README (no typos)
- [ ] **Authors:** Check author list complete with affiliations
- [ ] **Abstract:** Verify abstract ≤1920 characters (arXiv limit)
- [ ] **Categories:** Confirm primary category + cross-list categories (if any)
- [ ] **Keywords:** Check keywords present (if required by journal)
- [ ] **Acknowledgments:** Verify funding/AI collaborator credits present

**arXiv Category Requirements:**

**Paper 1: Computational Expense Validation**
- **Primary:** cs.DC (Distributed, Parallel, and Cluster Computing)
- **Cross-list:** cs.PF (Performance), cs.SE (Software Engineering)

**Paper 2: From Bistability to Collapse**
- **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
- **Cross-list:** q-bio.PE (Quantitative Biology - Populations and Evolution), cs.MA (Multiagent Systems)

**Paper 5D: Pattern Mining Framework**
- **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
- **Cross-list:** cs.AI (Artificial Intelligence), cs.MA (Multiagent Systems)

**Paper 3: Mechanism Synergies (Future)**
- **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
- **Cross-list:** physics.comp-ph (Computational Physics), cs.MA (Multiagent Systems)

**Abstract Length Verification:**
```bash
# Count abstract characters (including spaces)
grep -A 20 "\\begin{abstract}" manuscript.tex | grep -B 20 "\\end{abstract}" | wc -m
# Should be ≤ 1920 characters
```

**Troubleshooting:**

**Issue 1: Abstract exceeds 1920 characters**
- **Cause:** arXiv enforces strict character limit
- **Solution:** Condense abstract, remove redundant phrases, focus on key findings
- **Technique:** Remove phrases like "In this paper" (implied), "Our results show" (use active voice)

**Issue 2: Category not found or invalid**
- **Cause:** Typo in category code or deprecated category
- **Solution:** Verify category code at https://arxiv.org/category_taxonomy
- **Common mistake:** Using old category codes (e.g., "cs.DC" is correct, "cs.distributed" is not)

**Issue 3: Author affiliation missing or incorrect**
- **Cause:** Forgot to add affiliation or copy-paste error
- **Solution:** Add `\affil{}` or `\thanks{}` commands after author names
- **Verification:** Check PDF shows affiliation footnotes at bottom of first page

**Pass Criteria:** ✅ Title/authors correct, abstract ≤1920 chars, categories valid, acknowledgments present

---

### 1.4 File Size and Format Check

**Purpose:** Verify file sizes within arXiv limits and formats compatible

**Steps:**
- [ ] Check manuscript.tex size: `ls -lh manuscript.tex` (should be <1 MB)
- [ ] Check each figure size: `ls -lh *.png` (each should be <10 MB)
- [ ] Verify total package size: `du -sh .` (should be <50 MB)
- [ ] Confirm figure format: All figures .png or .pdf (arXiv preferred)
- [ ] Check for auxiliary files: Remove .aux, .log, .out, .synctex.gz (not needed for submission)

**arXiv File Size Limits:**
- **Individual file:** <10 MB (per file)
- **Total package:** <50 MB (all files combined)
- **Manuscript:** <1 MB recommended (LaTeX source)

**Figure Format Recommendations:**
- **Preferred:** PNG (raster), PDF (vector)
- **Acceptable:** JPG (photos only, not plots), EPS (vector, legacy)
- **Avoid:** TIFF (large files), BMP (uncompressed), GIF (low quality)

**File Size Optimization:**
```bash
# Check total size
du -sh papers/arxiv_submissions/paper1/

# Optimize PNG figures (if too large)
optipng -o7 figure*.png  # Lossless compression

# Convert PDF to optimized PDF (if too large)
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/prepress -dNOPAUSE -dQUIET -dBATCH -sOutputFile=figure_optimized.pdf figure.pdf
```

**Troubleshooting:**

**Issue 1: Total package >50 MB**
- **Cause:** Large figures or unnecessary files
- **Solution:** Compress figures, remove auxiliary files, exclude source data
- **Technique:** Use `optipng` for PNG, `gs` for PDF, remove .aux/.log/.out

**Issue 2: Figure >10 MB**
- **Cause:** High resolution (>300 DPI) or uncompressed format
- **Solution:** Reduce to 300 DPI, convert to PNG, apply compression
- **Command:** `convert figure.png -density 300 -compress Zip figure_compressed.png`

**Issue 3: Unsupported figure format (e.g., .svg)**
- **Cause:** arXiv doesn't accept SVG directly
- **Solution:** Convert to PDF (vector) or PNG (raster)
- **Command:** `inkscape figure.svg --export-pdf=figure.pdf`

**Pass Criteria:** ✅ manuscript.tex <1 MB, each figure <10 MB, total <50 MB, formats .png/.pdf

---

### 1.5 Ancillary Files Check (If Applicable)

**Purpose:** Verify supplementary materials (if any) are properly formatted

**Steps:**
- [ ] Check if ancillary files needed: Code, data, videos, supplements
- [ ] Verify file format: ZIP archive (arXiv requirement for multiple files)
- [ ] Check archive size: <50 MB (combined with main submission)
- [ ] Verify archive structure: Flat or one level deep (no nested directories)
- [ ] Test archive extraction: `unzip -t ancillary.zip` (verify no corruption)

**Ancillary File Guidelines:**

**When to Include:**
- ✅ Code for reproducibility (Paper 1: minimal_package_with_experiments.zip)
- ✅ Supplementary data (too large for main manuscript)
- ✅ Videos or animations (compressed, <10 MB each)
- ❌ Source code for paper itself (manuscript.tex already in main submission)
- ❌ Redundant figures (already in main manuscript)

**Archive Structure:**
```
minimal_package_with_experiments.zip
├── README.md (describes contents)
├── core/
│   ├── reality_interface.py
│   └── transcendental_bridge.py
├── experiments/
│   ├── overhead_check.py
│   └── replicate_patterns.py
└── requirements.txt (dependencies)
```

**Creating Archive:**
```bash
cd papers/minimal_package_with_experiments/
zip -r minimal_package_with_experiments.zip . -x "*.pyc" -x "__pycache__/*"
mv minimal_package_with_experiments.zip ../arxiv_submissions/paper1/
```

**Troubleshooting:**

**Issue 1: Archive >50 MB (combined with manuscript)**
- **Cause:** Too much supplementary data or large files
- **Solution:** Host data on external repository (GitHub, Zenodo), link in manuscript
- **Alternative:** Submit data to journal separately (not via arXiv)

**Issue 2: Archive structure too deep (nested directories)**
- **Cause:** Preserved original directory structure with many levels
- **Solution:** Flatten structure to 1-2 levels max
- **Command:** `zip -r archive.zip . -i "*.py" -i "*.md"` (include only needed files)

**Issue 3: Archive extraction fails**
- **Cause:** Corrupted ZIP or unsupported compression
- **Solution:** Recreate archive with standard ZIP compression
- **Verification:** `unzip -t archive.zip` (should show "No errors detected")

**Pass Criteria:** ✅ Archive <50 MB, structure flat, extraction succeeds, README included

---

## PHASE 2: ARXIV SUBMISSION PROCESS

### 2.1 Account and Login

**Purpose:** Access arXiv submission system

**Steps:**
- [ ] Navigate to arXiv.org: https://arxiv.org
- [ ] Click "Login" (top-right corner)
- [ ] Enter credentials: Username/email + password
- [ ] Verify login successful: Username displayed in header

**Account Requirements:**
- **Registration:** Required (free, no fees)
- **Endorsement:** Required for first submission in category (if no prior submissions)
- **Affiliation:** Optional (but recommended for institutional association)

**Endorsement (If Required):**
- If submitting to new category for first time, arXiv may require endorsement
- Request endorsement from researcher in field (co-author, advisor, colleague)
- Endorser must have submitted ≥1 paper in same category
- Endorsement typically granted within 24-48 hours

**Troubleshooting:**

**Issue 1: Login fails ("Invalid credentials")**
- **Cause:** Incorrect username/password or account not activated
- **Solution:** Reset password via "Forgot password" link
- **Verification:** Check email for activation link (if new account)

**Issue 2: Account suspended or restricted**
- **Cause:** Policy violation or spam detection
- **Solution:** Contact arXiv support (help@arxiv.org) for clarification
- **Prevention:** Follow arXiv policies (no duplicate submissions, proper attribution)

**Pass Criteria:** ✅ Successfully logged in, username displayed

---

### 2.2 Start New Submission

**Purpose:** Initiate submission workflow

**Steps:**
- [ ] Click "Submit" (top navigation bar)
- [ ] Select "Start New Submission"
- [ ] Review submission agreement: Read and accept terms
- [ ] Confirm understanding: Check "I agree" box
- [ ] Click "Continue" to proceed

**Submission Agreement Key Points:**
- **Original work:** Must be your own research (no plagiarism)
- **Preprint status:** Can be submitted simultaneously to journal
- **Permanent record:** Cannot delete after posted (can replace with new version)
- **License:** Default non-exclusive license to distribute

**Pass Criteria:** ✅ Submission agreement accepted, workflow started

---

### 2.3 Enter Metadata

**Purpose:** Provide paper information for arXiv indexing

**Steps:**
- [ ] **Title:** Enter full paper title (no abbreviations)
- [ ] **Authors:** Add all authors in order, with affiliations
- [ ] **Abstract:** Paste abstract text (≤1920 characters, verified in Phase 1.3)
- [ ] **Comments:** Optional field (e.g., "Submitted to PLOS Computational Biology")
- [ ] **Report Number:** Optional (leave blank unless assigned by institution)
- [ ] **Journal Reference:** Leave blank (will add after publication)
- [ ] **DOI:** Leave blank (will add after publication)

**Title Guidelines:**
- ✅ Full title, sentence case (first word capitalized)
- ✅ Mathematical symbols in LaTeX (e.g., $N=17$)
- ❌ ALL CAPS (looks unprofessional)
- ❌ Abbreviations without definition

**Author Guidelines:**
- ✅ First name + Last name format
- ✅ Affiliations for all authors
- ✅ Corresponding author marked
- ❌ Initials only (use full first name)

**Abstract Guidelines:**
- ✅ Self-contained (no references to figures/tables)
- ✅ Structured: Background, Methods, Results, Conclusions
- ✅ ≤1920 characters (verified in Phase 1.3)
- ❌ Citations (abstract should be self-contained)
- ❌ Equations (use text description instead)

**Comments Field Examples:**
- "Submitted to PLOS Computational Biology"
- "12 pages, 7 figures, code available at https://github.com/..."
- "Part of Nested Resonance Memory research series"

**Troubleshooting:**

**Issue 1: Abstract rejected ("Exceeds 1920 characters")**
- **Cause:** Abstract too long (verified in Phase 1.3 should prevent this)
- **Solution:** Condense abstract, remove redundant phrases
- **Prevention:** Verify character count before submission

**Issue 2: Author name not accepted**
- **Cause:** Special characters or unusual format
- **Solution:** Use ASCII characters only (no diacritics in submission form, can be in PDF)
- **Workaround:** Add diacritics in manuscript.tex, use ASCII in arXiv form

**Pass Criteria:** ✅ All metadata fields complete, abstract ≤1920 chars, authors with affiliations

---

### 2.4 Select Categories

**Purpose:** Choose primary and cross-list categories for paper

**Steps:**
- [ ] Select primary category: Choose most relevant category from dropdown
- [ ] Add cross-list categories: (Optional) Select 1-2 additional categories
- [ ] Verify category relevance: Ensure categories match paper content
- [ ] Click "Continue" to proceed

**Category Selection Guidelines:**

**Primary Category:**
- Choose category that best describes paper's main contribution
- Cannot change after submission (cross-lists can be modified)
- Determines which arXiv mailing list announces paper

**Cross-List Categories:**
- Optional but recommended for interdisciplinary work
- Maximum 2-3 cross-lists (avoid over-categorization)
- Choose categories where paper provides novel contribution

**Paper-Specific Recommendations:**

**Paper 1: Computational Expense Validation**
- **Primary:** cs.DC (Distributed, Parallel, and Cluster Computing)
- **Cross-list:** cs.PF (Performance), cs.SE (Software Engineering)
- **Rationale:** Method paper for computational validation, applicable to distributed systems and software engineering

**Paper 2: From Bistability to Collapse**
- **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
- **Cross-list:** q-bio.PE (Quantitative Biology - Populations and Evolution), cs.MA (Multiagent Systems)
- **Rationale:** Nonlinear dynamics paper with applications to population dynamics and multiagent systems

**Paper 5D: Pattern Mining Framework**
- **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
- **Cross-list:** cs.AI (Artificial Intelligence), cs.MA (Multiagent Systems)
- **Rationale:** Pattern mining in nonlinear systems with AI and multiagent applications

**Paper 3: Mechanism Synergies (Future)**
- **Primary:** nlin.AO (Nonlinear Sciences - Adaptation and Self-Organizing Systems)
- **Cross-list:** physics.comp-ph (Computational Physics), cs.MA (Multiagent Systems)
- **Rationale:** Factorial validation of nonlinear mechanisms with computational physics methods

**Troubleshooting:**

**Issue 1: Category requires endorsement**
- **Cause:** First submission to category, no prior submissions
- **Solution:** Request endorsement from researcher in field (see Phase 2.1)
- **Timeline:** Endorsement typically granted within 24-48 hours

**Issue 2: Unsure which category to choose**
- **Cause:** Interdisciplinary work spans multiple categories
- **Solution:** Browse recent papers in candidate categories, choose where similar work appears
- **Resource:** arXiv category taxonomy: https://arxiv.org/category_taxonomy

**Pass Criteria:** ✅ Primary category selected, cross-lists (if any) relevant, no endorsement blockers

---

### 2.5 Upload Files

**Purpose:** Submit manuscript and figures to arXiv

**Steps:**
- [ ] Select upload method: "Upload files" (not "Submit TeX source")
- [ ] Upload manuscript.tex: Click "Choose File", select manuscript.tex
- [ ] Upload figures: Select all .png/.pdf figures (multi-select with Ctrl/Cmd)
- [ ] Upload ancillary files: (If applicable) Upload .zip archive
- [ ] Verify file list: Check all files present, correct names
- [ ] Click "Process Files" to continue

**File Upload Guidelines:**

**Required Files:**
- `manuscript.tex` (main LaTeX source)
- All figure files (referenced in manuscript.tex)

**Optional Files:**
- `bibliography.bib` (if using BibTeX)
- `custom.sty` (if using custom LaTeX package)
- `ancillary.zip` (supplementary materials)

**File Naming:**
- ✅ Simple names: `manuscript.tex`, `figure1.png`, `figure2.png`
- ✅ Lowercase or consistent case: `figure1.png` (not `Figure1.png`)
- ❌ Spaces in names: `figure 1.png` → `figure1.png`
- ❌ Special characters: `figure#1.png` → `figure1.png`

**Troubleshooting:**

**Issue 1: File upload fails ("File too large")**
- **Cause:** File exceeds 10 MB limit (per file) or 50 MB total
- **Solution:** Compress figures (Phase 1.4), remove unnecessary files
- **Prevention:** Verify file sizes in Phase 1.4 before submission

**Issue 2: LaTeX compilation error during processing**
- **Cause:** Missing package, undefined command, or syntax error
- **Solution:** Review error log, fix errors in manuscript.tex, reupload
- **Prevention:** Test compilation locally (Phase 1.1) before upload

**Issue 3: Figure not found during compilation**
- **Cause:** Figure filename mismatch in manuscript.tex vs uploaded file
- **Solution:** Check `\includegraphics{X}` matches uploaded filename exactly (case-sensitive)
- **Prevention:** Verify figure references (Phase 1.2) before upload

**Pass Criteria:** ✅ All files uploaded, no upload errors, file list complete

---

### 2.6 Preview Compilation

**Purpose:** Verify arXiv compilation matches local compilation

**Steps:**
- [ ] Wait for processing: arXiv compiles uploaded files (~1-5 minutes)
- [ ] Review compilation log: Check for errors or warnings
- [ ] Download preview PDF: Click "View" or "Download" PDF
- [ ] Compare to local PDF: Verify figures, formatting, references match
- [ ] Check page count: Ensure page count matches expectations
- [ ] Verify figure quality: Zoom to 200%, check resolution

**Common Compilation Issues:**

**Issue 1: "Missing figure" error**
- **Cause:** Figure filename mismatch or not uploaded
- **Solution:** Go back, upload missing figure, or fix filename in manuscript.tex
- **Prevention:** Double-check file list before processing

**Issue 2: "Package not found" error**
- **Cause:** Package not in arXiv TeXLive distribution
- **Solution:** Replace with arXiv-compatible package or inline definitions
- **Common packages NOT on arXiv:** Custom .sty files, proprietary fonts

**Issue 3: PDF looks different from local compilation**
- **Cause:** Different LaTeX version or package versions
- **Solution:** Usually minor differences acceptable; if major, revise manuscript.tex
- **Example:** Line breaks may differ slightly, but content should be identical

**Red Flags (Requires Action):**
- ❌ Missing figures (blank spaces)
- ❌ Unresolved references ("??" in text)
- ❌ Incorrect formatting (misaligned equations, broken tables)
- ❌ Compilation errors (PDF not generated)

**Acceptable Differences:**
- ✅ Minor line break differences
- ✅ Slightly different font rendering
- ✅ Page count ±1 page (due to different margins)

**Pass Criteria:** ✅ Preview PDF generated, no major differences from local PDF, figures present

---

### 2.7 Submit for Moderation

**Purpose:** Finalize submission and send to arXiv moderators

**Steps:**
- [ ] Review all metadata: Title, authors, abstract, categories correct
- [ ] Confirm files: All files present, compilation successful
- [ ] Add optional comment: (If needed) Note for moderators
- [ ] Check license: Default non-exclusive license (or select alternative)
- [ ] Click "Submit" to finalize

**Final Review Checklist:**
- ☐ Title correct (no typos)
- ☐ Authors complete with affiliations
- ☐ Abstract ≤1920 characters
- ☐ Categories appropriate
- ☐ Figures all present and high-quality
- ☐ Compilation successful
- ☐ License understood and accepted

**Optional Comment for Moderators:**
- Use if paper has unusual features needing explanation
- Example: "This paper uses custom notation defined in Section 2"
- Example: "Figure 3 is intentionally large (full-page heatmap)"
- Usually not needed for standard submissions

**License Options:**
- **Default:** arXiv.org perpetual, non-exclusive license (recommended)
- **CC BY 4.0:** Creative Commons Attribution (allows reuse with attribution)
- **CC BY-NC-SA 4.0:** Creative Commons Non-Commercial Share-Alike
- **Public Domain:** No restrictions

**Most Common:** Default arXiv license (perpetual, non-exclusive, allows journal publication)

**Pass Criteria:** ✅ All metadata verified, submission confirmed, confirmation email received

---

## PHASE 3: POST-SUBMISSION MONITORING

### 3.1 Processing Phase (1-2 hours)

**Purpose:** Monitor arXiv processing and respond to issues

**Timeline:**
- **Immediate:** Submission confirmation email received
- **1-2 hours:** Processing complete (announced or on-hold)
- **If issues:** Moderator may request revisions (email notification)

**Expected Email:** "Your submission has been received and is being processed"

**What arXiv Does:**
- Compiles manuscript with standard TeXLive
- Checks for policy violations (plagiarism, inappropriate content)
- Verifies metadata completeness
- Assigns paper ID (e.g., 2501.XXXXX)

**Actions:**
- [ ] Confirm submission email received (check spam folder if not in inbox)
- [ ] Note paper ID: Save for tracking (e.g., 2501.12345)
- [ ] Monitor email: Check for moderator requests or errors

**Troubleshooting:**

**Issue 1: No confirmation email after 30 minutes**
- **Cause:** Email filter or typo in email address
- **Solution:** Check spam folder, verify email in arXiv profile, check submission status on arXiv.org
- **Contact:** Email arXiv support (help@arxiv.org) if no confirmation after 2 hours

**Issue 2: Compilation error email**
- **Cause:** LaTeX compilation failed on arXiv servers (despite local success)
- **Solution:** Review error log, fix errors, resubmit (use "Replace" option)
- **Common cause:** Missing package or unsupported LaTeX feature

**Issue 3: Moderator hold email**
- **Cause:** Moderator flagged submission for review (unusual content, policy check)
- **Solution:** Wait for moderator review (24-72 hours), respond to requests if any
- **Common triggers:** Very large file, unusual category choice, first submission

**Pass Criteria:** ✅ Confirmation email received, paper ID assigned, no error emails

---

### 3.2 Announcement Phase (1-2 days)

**Purpose:** Wait for arXiv announcement and public posting

**Timeline:**
- **Submission cutoff:** Sunday-Thursday 14:00 US Eastern Time (ET)
- **Announcement:** Next business day 20:00 ET (Sunday-Thursday submissions)
- **Friday/Saturday submissions:** Announced Monday 20:00 ET
- **Holidays:** May be delayed 1-2 days

**Example Timelines:**
- **Submit Monday 10:00 ET:** Announced Tuesday 20:00 ET (~34 hours)
- **Submit Thursday 15:00 ET:** Announced Friday 20:00 ET (~29 hours)
- **Submit Friday 10:00 ET:** Announced Monday 20:00 ET (~82 hours)

**Actions:**
- [ ] Check announcement schedule: arXiv.org/help/availability
- [ ] Monitor email: Announcement notification email
- [ ] Check arXiv.org: Search for paper ID after announcement time

**Troubleshooting:**

**Issue 1: Paper not announced at scheduled time**
- **Cause:** Moderator hold, policy review, or submission issue
- **Solution:** Check email for moderator requests, check arXiv status page
- **Timeline:** May be delayed 1-2 days for review

**Issue 2: Paper announced but not in expected category**
- **Cause:** Moderator reclassified paper to different primary category
- **Solution:** Accept reclassification or request reconsideration (email arXiv)
- **Common:** Moderators may move papers to more appropriate categories

**Issue 3: Paper placed on hold**
- **Cause:** Policy concern, quality issue, or verification needed
- **Solution:** Respond to moderator email (if any), provide clarification
- **Timeline:** Hold may last 1-5 days, depending on issue

**Pass Criteria:** ✅ Paper announced, publicly accessible, assigned arXiv ID (e.g., arXiv:2501.12345)

---

### 3.3 Indexing and Citation (Immediate after announcement)

**Purpose:** Verify paper indexed correctly and prepare for journal submission

**Timeline:**
- **Indexing:** Immediate (within minutes of announcement)
- **Google Scholar:** 1-2 weeks (automated crawl)
- **Other databases:** 1-4 weeks (varies by database)

**Actions:**
- [ ] Verify arXiv page: https://arxiv.org/abs/2501.XXXXX (replace with actual ID)
- [ ] Check metadata: Title, authors, abstract, categories correct
- [ ] Download PDF: Verify final PDF matches preview
- [ ] Note citation: arXiv:2501.XXXXX v1 (version 1)
- [ ] Update CV/website: Add arXiv link
- [ ] Share with colleagues: Email/social media (if desired)

**Citation Format:**
```
Payopay, A., Claude Sonnet 4.5, Gemini 2.5 Pro, ChatGPT 5, Claude Opus 4.1 (2025).
[Paper Title]. arXiv:2501.XXXXX
```

**BibTeX:**
```bibtex
@misc{payopay2025paperX,
  author = {Payopay, Aldrin and {Claude Sonnet 4.5} and {Gemini 2.5 Pro} and {ChatGPT 5} and {Claude Opus 4.1}},
  title = {[Paper Title]},
  year = {2025},
  eprint = {2501.XXXXX},
  archivePrefix = {arXiv},
  primaryClass = {[category]},
  url = {https://arxiv.org/abs/2501.XXXXX}
}
```

**Next Steps:**
- [ ] Submit to journal: Use arXiv link in cover letter
- [ ] Monitor downloads/citations: Check arXiv stats page
- [ ] Respond to feedback: Monitor email/social media for comments
- [ ] Prepare revisions: (If needed) Upload new version to arXiv

**Pass Criteria:** ✅ Paper publicly accessible, metadata correct, citation noted, shared with relevant communities

---

## PHASE 4: JOURNAL SUBMISSION (PARALLEL OR AFTER ARXIV)

### 4.1 Journal Selection

**Purpose:** Choose appropriate journal for peer review

**Criteria:**
- **Scope:** Journal scope matches paper content
- **Audience:** Target audience matches paper's contribution
- **Impact:** Journal impact factor or reputation
- **Open Access:** Journal OA policy (preferred for public research)
- **Timeline:** Average review time (3-6 months typical)

**Paper-Specific Recommendations:**

**Paper 1: Computational Expense Validation**
- **Primary:** PLOS Computational Biology
  - **Rationale:** Methods paper, open access, computational focus
  - **Timeline:** ~4 months average review
  - **Impact Factor:** 3.8 (2024)
- **Alternative:** Journal of Computational Science
  - **Rationale:** Methods paper, computational validation focus
  - **Timeline:** ~3 months average review

**Paper 2: From Bistability to Collapse**
- **Primary:** PLOS ONE
  - **Rationale:** Broad scope, open access, multidisciplinary
  - **Timeline:** ~3-4 months average review
  - **Impact Factor:** 2.9 (2024)
- **Alternative:** Scientific Reports (Nature)
  - **Rationale:** Similar scope, high visibility
  - **Timeline:** ~2-3 months average review
  - **Impact Factor:** 3.8 (2024)

**Paper 5D: Pattern Mining Framework**
- **Primary:** PLOS ONE
  - **Rationale:** Broad scope, pattern mining applicable across fields
  - **Timeline:** ~3-4 months average review
- **Alternative:** IEEE Transactions on Emerging Topics in Computational Intelligence (TETCI)
  - **Rationale:** Computational intelligence focus, AI applications
  - **Timeline:** ~4-6 months average review

**Paper 3: Mechanism Synergies (Future)**
- **Primary:** Physical Review E (Complexity)
  - **Rationale:** Nonlinear dynamics, statistical mechanics, complexity
  - **Timeline:** ~3-4 months average review
  - **Impact Factor:** 2.2 (2024)
- **Alternative:** Chaos (AIP)
  - **Rationale:** Nonlinear science, interdisciplinary
  - **Timeline:** ~3-4 months average review
  - **Impact Factor:** 2.7 (2024)

**Pass Criteria:** ✅ Journal selected, scope confirmed, submission guidelines reviewed

---

### 4.2 Journal Submission Preparation

**Purpose:** Format manuscript according to journal guidelines

**Steps:**
- [ ] Download journal template: Check journal website for LaTeX template
- [ ] Reformat manuscript: Adapt manuscript.tex to journal format
- [ ] Update references: Use journal citation style (APA, AMA, Vancouver, etc.)
- [ ] Prepare cover letter: Highlight novelty, explain fit with journal
- [ ] Suggest reviewers: (If journal requires) Provide 3-5 reviewer suggestions
- [ ] Declare conflicts: (If any) Disclose conflicts of interest

**Common Formatting Changes:**
- **Line numbers:** Add \usepackage{lineno} and \linenumbers
- **Double spacing:** Add \doublespacing (for some journals)
- **References:** Convert BibTeX to journal style (APA, Vancouver, etc.)
- **Figures:** May need to upload separately (not embedded in PDF)
- **Supplementary materials:** Upload as separate files (not in main manuscript)

**Cover Letter Template:**
```
Dear Editor,

We are pleased to submit our manuscript titled "[Paper Title]" for consideration
for publication in [Journal Name].

This manuscript presents [1-2 sentence summary of key contribution]. Our findings
are significant because [1-2 sentences on novelty and impact].

This work fits the scope of [Journal Name] because [1-2 sentences on journal fit].
We believe it will be of interest to your readers working in [field/subfield].

This manuscript has not been published elsewhere and is not under consideration
by any other journal. All authors have approved the submission.

We have no conflicts of interest to declare. [Or: Declare any conflicts]

We suggest the following researchers as potential reviewers:
- [Reviewer 1 name, affiliation, expertise]
- [Reviewer 2 name, affiliation, expertise]
- [Reviewer 3 name, affiliation, expertise]

Thank you for considering our manuscript.

Sincerely,
[Your name]
[Affiliation]
[Email]
```

**Pass Criteria:** ✅ Manuscript reformatted, cover letter written, reviewer list prepared

---

### 4.3 Online Submission

**Purpose:** Submit manuscript through journal's online system

**Steps:**
- [ ] Create journal account: Register on journal submission portal
- [ ] Start new submission: Select article type (Original Research, Methods, etc.)
- [ ] Enter metadata: Title, authors, abstract, keywords
- [ ] Upload manuscript: PDF or LaTeX source (journal-specific)
- [ ] Upload figures: Separate files (TIFF, EPS, or PDF)
- [ ] Upload supplementary materials: (If any) Code, data, videos
- [ ] Enter cover letter: Paste or upload cover letter
- [ ] Suggest reviewers: (If required) Enter reviewer names and emails
- [ ] Review and submit: Confirm all fields complete, submit

**Common Submission Portals:**
- **PLOS:** Editorial Manager (https://plos.org/publish)
- **Nature journals:** Editorial Manager
- **Physical Review:** PREview (https://publish.aps.org)
- **IEEE:** ScholarOne Manuscripts
- **PNAS:** eJPress

**Troubleshooting:**

**Issue 1: File upload fails**
- **Cause:** File too large or unsupported format
- **Solution:** Compress files, convert to journal-preferred format
- **Check:** Journal submission guidelines for file size limits

**Issue 2: Suggested reviewer email bounces**
- **Cause:** Incorrect email or reviewer left institution
- **Solution:** Verify email on reviewer's current affiliation website
- **Alternative:** Suggest different reviewer from same subfield

**Pass Criteria:** ✅ Submission complete, confirmation email received, manuscript ID assigned

---

## TROUBLESHOOTING COMMON ISSUES

### Issue: LaTeX Compilation Fails on arXiv

**Symptoms:** Error email from arXiv, "Compilation failed" message

**Diagnosis:**
1. Check error log: Review .log file for specific error message
2. Compare local vs arXiv: Test compilation with `pdflatex` locally
3. Identify package issues: Check for packages not in arXiv TeXLive

**Solutions:**
- **Missing package:** Replace with arXiv-compatible alternative or inline definitions
- **Undefined command:** Add `\newcommand` definitions in preamble
- **File not found:** Verify all figures uploaded, filenames match exactly

**Prevention:**
- Test compilation locally with standard TeXLive (not Overleaf or custom setup)
- Use minimal preamble (avoid unnecessary packages)
- Avoid custom .sty files (inline definitions instead)

---

### Issue: Figure Quality Poor in PDF

**Symptoms:** Figures pixelated, blurry, or low resolution

**Diagnosis:**
1. Check figure resolution: `identify figure.png` (should show ≥300 DPI)
2. Check PDF zoom: Zoom to 200%, inspect closely
3. Check figure format: PNG vs JPG vs PDF

**Solutions:**
- **Low resolution:** Regenerate figure at 300+ DPI
- **Wrong format:** Convert JPG to PNG (lossless compression)
- **Over-compression:** Reduce compression level (use `optipng -o2` instead of `-o7`)

**Prevention:**
- Always generate figures at 300 DPI minimum
- Use PNG for plots (lossless), JPG only for photos
- Test PDF zoom before submission (Phase 1.2)

---

### Issue: Abstract Exceeds 1920 Characters

**Symptoms:** arXiv rejects abstract, "Exceeds character limit" error

**Diagnosis:**
1. Count characters: `echo "$abstract" | wc -m` (includes spaces)
2. Identify verbose sections: Look for redundant phrases
3. Prioritize content: Focus on key findings, remove methodology details

**Solutions:**
- **Remove filler:** Phrases like "In this paper" (implied), "Our results show" (use active voice)
- **Condense methods:** Reduce methodology to 1 sentence (details in manuscript)
- **Focus on findings:** Emphasize novel results, minimize background

**Prevention:**
- Write abstract last (after manuscript complete)
- Aim for 1500-1800 characters (buffer for edits)
- Use structured abstract format (Background, Methods, Results, Conclusions)

---

### Issue: Moderator Hold or Delay

**Symptoms:** No announcement after 48 hours, email about hold

**Diagnosis:**
1. Check email: Look for moderator explanation
2. Check arXiv status: Log in, check submission status page
3. Review paper: Look for potential policy issues (plagiarism, inappropriate content)

**Solutions:**
- **Respond to moderator:** If specific issue raised, address in reply email
- **Provide clarification:** Explain unusual content or category choice
- **Wait patiently:** Moderator review can take 1-5 days (normal)

**Common Triggers:**
- First submission to category (requires endorsement)
- Very large files (>20 MB total)
- Unusual category combination (cross-lists)
- Overlapping submissions (same content in multiple papers)

**Prevention:**
- Follow arXiv policies (https://arxiv.org/help/policies)
- Avoid duplicate submissions (don't submit same content twice)
- Use appropriate categories (browse recent papers for guidance)

---

## SUBMISSION TIMELINE SUMMARY

**Pre-Submission (15-20 minutes per paper):**
- Phase 1.1-1.5: Local verification (LaTeX, figures, metadata, files)

**arXiv Submission (10-15 minutes per paper):**
- Phase 2.1-2.7: Account, metadata, upload, preview, submit

**Post-Submission (1-2 days):**
- Phase 3.1: Processing (1-2 hours)
- Phase 3.2: Announcement (1-2 days)
- Phase 3.3: Indexing (immediate after announcement)

**Journal Submission (30-60 minutes per paper):**
- Phase 4.1-4.3: Journal selection, formatting, submission

**Total Timeline:**
- **Immediate:** arXiv submission same day (~25-35 min per paper)
- **Announcement:** 1-2 days (depending on submission time)
- **Journal submission:** Parallel with arXiv or after announcement
- **Peer review:** 3-6 months (journal-dependent)

---

## CHECKLIST SUMMARY

**Before Submission:**
- ☐ LaTeX compiles (3 passes, no errors)
- ☐ Figures render (no "??", resolution ≥300 DPI)
- ☐ Metadata complete (title, authors, abstract ≤1920 chars)
- ☐ Files within limits (<1 MB manuscript, <10 MB per figure, <50 MB total)
- ☐ Ancillary files (if any) properly archived

**During Submission:**
- ☐ Account logged in, submission started
- ☐ Metadata entered (title, authors, abstract, categories)
- ☐ Files uploaded (manuscript.tex, figures, ancillary)
- ☐ Preview PDF verified (matches local compilation)
- ☐ Submission finalized, confirmation email received

**After Submission:**
- ☐ Processing confirmation received (paper ID assigned)
- ☐ Announcement notification received (paper publicly accessible)
- ☐ Citation noted (arXiv:2501.XXXXX)
- ☐ Journal submission prepared (cover letter, reviewer list)
- ☐ Journal submission completed (confirmation email received)

---

**Estimated Time per Paper:**
- **First submission:** 45-60 minutes (including troubleshooting)
- **Subsequent submissions:** 20-30 minutes (familiar with process)

**Key Takeaway:** Systematic pre-flight verification (Phase 1) prevents most submission errors. Invest 15-20 minutes in local checks to avoid delays and re-submissions.

---

**Last Updated:** October 29, 2025 (Cycle 486)
**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive
**License:** GPL-3.0
