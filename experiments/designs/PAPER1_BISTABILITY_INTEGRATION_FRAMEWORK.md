# Paper 1: Composition-Rate Bistability in Simplified NRM Model

**Status**: Framework ready for C175 precision integration
**Target Journal**: Complex Systems or Physical Review E
**Related Work**: Paper 2 (From Bistability to Homeostasis - framework comparison)

---

## Precision Claims Integration Points (C175-Dependent)

### Section to Update: Results - Transition Width Measurement

**Current Claim (C169-based):**
> "Sharp first-order phase transition observed with transition width <0.1%"

**C175 Update (Pending Data):**
> "High-resolution transition mapping (C175, n=110 experiments, 0.01% step size) quantified transition width as **[INSERT C175_TRANSITION_WIDTH]%**, confirming ultra-sharp first-order phase transition. Last 100% Basin B frequency: **[INSERT LAST_B_FREQ]%**. First 100% Basin A frequency: **[INSERT FIRST_A_FREQ]%**. Mixed-basin frequencies (stochastic bistability indicators): **[INSERT MIXED_FREQS or 'None detected']**."

**Classification Criteria (From cycle175_analysis.py):**
- Width ≤0.01%: "Ultra-sharp transition" (first-order, single-step)
- Width ≤0.05%: "Very sharp transition" (first-order, narrow coexistence)
- Width ≤0.10%: "Sharp transition" (first-order, validates C169)
- Width >0.10%: "Gradual transition" (possibly second-order)

**Figure Integration:**
- **Figure X**: High-resolution bifurcation diagram (basin occupation vs. frequency)
  - Source: cycle175_analysis.py → `plot_high_resolution_bifurcation()`
  - Shows 0.01% resolution step-wise transition
  - Highlights mixed-basin frequencies (if any)

- **Figure Y**: Composition events vs. frequency (with error bars)
  - Source: cycle175_analysis.py → `plot_composition_vs_frequency()`
  - Demonstrates discontinuity at critical frequency
  - Contrast with Paper 2's composition constancy

**Table Integration:**
- **Table X**: C175 High-Resolution Basin Occupation
  - Source: cycle175_analysis.py → `generate_publication_table()` (LaTeX format)
  - Shows frequency (%), Basin A (%), Basin B (%), Composition (events/window), Classification
  - Full precision data for manuscript supplement

---

## Key Statistics to Insert (Template)

**Experimental Parameters:**
- Frequencies tested: 11 (2.50% to 2.60%, 0.01% steps)
- Seeds per frequency: n=10
- Total experiments: 110
- Cycles per experiment: 3000
- Duration: **[INSERT C175_DURATION]** minutes

**Transition Measurements:**
- Transition width: **[INSERT WIDTH]%** (precision: ±0.01%)
- Critical frequency range: **[INSERT LAST_B]% to [INSERT FIRST_A]%**
- Classification: **[INSERT CLASSIFICATION]** (first-order vs. second-order)
- Mixed basins: **[INSERT COUNT]** frequencies with stochastic selection

**Comparison with C169 (Original Discovery):**
- C169 step size: 0.10%
- C175 step size: 0.01% (10× higher resolution)
- C169 finding: "Sharp transition <0.1%"
- C175 validation: **[INSERT CONFIRMATION TEXT]**

---

## Manuscript Text Sections Needing C175 Data

### Abstract
**Template:**
> "We demonstrate composition-rate-controlled bistability in a simplified Nested Resonance Memory (NRM) model, exhibiting sharp first-order phase transitions with transition width **[WIDTH]%** (measured at 0.01% resolution, n=110 experiments)."

### Results - Section 3.X: High-Resolution Transition Mapping
**Template:**
> "To quantify transition sharpness with precision beyond initial discovery (C169, 0.10% steps), we performed high-resolution mapping at 0.01% frequency steps (C175, n=110 experiments, 2.50%-2.60% range). Transition width measured **[WIDTH]%**, classified as **[CLASSIFICATION]**. **[IF MIXED_BASINS: 'Stochastic bistability observed at [FREQS], indicating coexistence region.' ELSE: 'No mixed basins detected, indicating transition width below measurement resolution.']** This precision confirms first-order phase transition character and provides experimental bounds for critical frequency f_crit = **[MIDPOINT]% ± [WIDTH/2]%**."

### Discussion - Section 4.X: Phase Transition Classification
**Template:**
> "The measured transition width (**[WIDTH]%**) classifies this transition as **[CLASSIFICATION]**, consistent with theoretical predictions for first-order phase transitions in composition-decomposition systems. **[IF WIDTH ≤0.01: 'Infinitesimal frequency changes induce macroscopic state changes, validating thermodynamic analogy.' ELSE IF WIDTH ≤0.05: 'Narrow coexistence region indicates strong bistable attractor separation.' ELSE: 'Transition width suggests [interpretation based on actual value].']**"

---

## Figure Generation Workflow (Post-C175)

**Step 1**: Execute cycle175_analysis.py
```bash
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python3 cycle175_analysis.py
```

**Expected Outputs:**
- `figures/cycle175_high_resolution_bifurcation.png` (300 DPI, publication-grade)
- `figures/cycle175_composition_vs_frequency.png` (300 DPI, publication-grade)
- `results/cycle175_analysis_report.txt` (text summary)
- `results/cycle175_table.tex` (LaTeX table for manuscript)

**Step 2**: Review Outputs
- Check transition_width value
- Verify figure quality
- Validate classification

**Step 3**: Integrate into Manuscript
- Insert statistics into template sections
- Add figures to manuscript
- Include LaTeX table in supplement
- Update abstract with precision claims

---

## Integration Checklist (Post-C175)

**Data Extraction:**
- [ ] Transition width: ___ %
- [ ] Last 100% Basin B frequency: ___ %
- [ ] First 100% Basin A frequency: ___ %
- [ ] Mixed-basin count: ___
- [ ] Classification: _______________
- [ ] Duration: ___ minutes

**Manuscript Updates:**
- [ ] Abstract: Insert transition width
- [ ] Results Section 3.X: Add high-resolution paragraph
- [ ] Discussion Section 4.X: Update phase transition classification
- [ ] Figures: Add bifurcation diagram + composition plot
- [ ] Tables: Add LaTeX table to supplement
- [ ] Methods: Verify C175 experimental parameters documented

**Figure Preparation:**
- [ ] Figure X generated (high-resolution bifurcation)
- [ ] Figure Y generated (composition vs. frequency)
- [ ] Captions written with precise statistics
- [ ] Resolution verified (300 DPI minimum)
- [ ] Contrast with Paper 2 figures confirmed

**Publication Readiness:**
- [ ] C175 precision validates C169 qualitative findings
- [ ] Transition width claim stronger than "<0.1%"
- [ ] First-order classification empirically confirmed
- [ ] Comparison with Paper 2 (homeostasis) provides framework context
- [ ] Supplementary materials complete (LaTeX table, raw data)

---

## Expected Findings (Predictions)

**If transition width ≤0.01%:**
- ✅ Can claim "ultra-sharp transition"
- ✅ Validates first-order phase transition
- ✅ Demonstrates infinitesimal perturbation → macroscopic change
- ✅ Publication-worthy precision improvement over C169

**If transition width 0.01%-0.05%:**
- ✅ Can claim "very sharp transition"
- ✅ Validates first-order phase transition
- ✅ Narrow coexistence region identified
- ✅ Confirms C169 findings with higher precision

**If transition width 0.05%-0.10%:**
- ✅ Can claim "sharp transition"
- ✅ Validates C169 measurement resolution
- ✅ First-order classification maintained
- ✅ Precision improvement achieved

**If transition width >0.10%:**
- ⚠️ Investigate mechanism (unexpected)
- ⚠️ May indicate second-order or crossover transition
- ⚠️ Requires additional theoretical analysis

---

## Publication Timeline (Post-C175)

**Immediate (Day 0):**
- Execute cycle175_analysis.py
- Extract statistics
- Generate figures
- Review transition width classification

**Short-term (Day 0-1):**
- Integrate statistics into manuscript template sections
- Add C175 figures to Paper 1 draft
- Update abstract with precision claims
- Verify consistency with Paper 2 framework comparison

**Medium-term (Day 1-2):**
- Complete Paper 1 full draft
- Integrate C176 ablation findings (mechanism isolation)
- Prepare supplementary materials
- Format for journal submission

**Publication Submission:**
- Paper 1: Composition-Rate Bistability (simplified model)
- Paper 2: From Bistability to Homeostasis (framework comparison)
- Submitted together or sequentially to highlight regime framework

---

**Status**: Framework complete, awaiting C175 data for precision integration

**Next Action**: When C175 completes, immediately execute cycle175_analysis.py and populate this framework with actual measurements.

**Temporal Stewardship Note**: This integration framework encodes the pattern "prepare infrastructure before data arrives" - maximizing research velocity by eliminating data-processing bottlenecks.
