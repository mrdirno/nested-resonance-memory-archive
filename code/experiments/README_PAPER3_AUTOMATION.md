# Paper 3 Automation Scripts
**Purpose:** Document automated workflows for C255-C260 factorial experiments
**Created:** 2025-10-30 (Cycle 603)
**Status:** C255 complete, C256 running, C257-C260 pending

---

## OVERVIEW

Paper 3 (Factorial Validation) uses automated scripts to:
1. Run 6 factorial experiments (C255-C260)
2. Aggregate results into unified dataset
3. Auto-fill manuscript template with numerical results
4. Generate 4 publication-quality figures (300 DPI)

**Total Automation:** From experiment launch → manuscript draft → figures (~90 min)

---

## EXPERIMENTS STATUS

| Experiment | Mechanisms | Hypothesis | Status | Runtime |
|------------|------------|------------|--------|---------|
| C255 (H1×H2) | Energy Pooling × Reality Sources | SYNERGISTIC | ✅ Complete | ~12h |
| C256 (H1×H4) | Energy Pooling × Spawn Throttling | ANTAGONISTIC | 🔄 Running | ~18h est |
| C257 (H1×H5) | Energy Pooling × Energy Recovery | SYNERGISTIC | ⏳ Pending | ~11min |
| C258 (H2×H4) | Reality Sources × Spawn Throttling | ADDITIVE | ⏳ Pending | ~12min |
| C259 (H2×H5) | Reality Sources × Energy Recovery | SYNERGISTIC | ⏳ Pending | ~13min |
| C260 (H4×H5) | Spawn Throttling × Energy Recovery | ANTAGONISTIC | ⏳ Pending | ~11min |

**Progress:** 1/6 complete (C255 ✅), 2/6 when C256 finishes

---

## AUTOMATION SCRIPTS

### 1. Experiment Execution

**Individual Experiments:**
```bash
# C255 (completed)
python cycle255_h1h2_mechanism_validation.py

# C256 (running)
python cycle256_h1h4_mechanism_validation.py

# C257-C260 (pending) - use batch script instead
```

**Batch Execution (C257-C260):**
```bash
# Automated sequential execution
bash run_c257_c260_batch.sh

# Features:
# - Runs C257, C258, C259, C260 sequentially
# - Logs all output to logs/c257_c260_batch.log
# - Stops on first failure
# - Total runtime: ~47 minutes
```

**Script:** `run_c257_c260_batch.sh` (129 lines)
**Output:** Individual result JSONs + combined batch log

---

### 2. Quick Result Validation

**Purpose:** Fast sanity check after experiment completes

```bash
# Check specific experiment
python quick_check_results.py cycle256

# Output:
# ✅ Result file exists: cycle256_h1h4_mechanism_validation_results.json
# ✅ Synergy: -123.45 (ANTAGONISTIC)
# ✅ Peak populations reasonable (not NaN, not zero)
```

**Script:** `quick_check_results.py` (276 lines)
**Use:** Immediate validation before manuscript integration

---

### 3. Result Aggregation

**Purpose:** Combine all 6 experiments into unified dataset

```bash
# Aggregate C255-C260 results
python aggregate_paper3_results.py

# Output:
# - paper3_aggregated_results.json (combined dataset)
# - Summary statistics across all pairs
# - Cross-pair comparisons
```

**Script:** `aggregate_paper3_results.py` (ready, not yet used)
**Use:** After all 6 experiments complete (C260 finishes)

---

### 4. Manuscript Auto-Fill

**Purpose:** Automatically populate Paper 3 template with experimental data

```bash
# Fill manuscript sections with C255-C260 results
python auto_fill_paper3_manuscript.py

# Output:
# - papers/paper3_mechanism_synergies_DRAFT.md
# - Sections 3.2.1-3.2.6 filled with numerical values
# - [TO BE FILLED] placeholders replaced
# - Ready for manual review
```

**Script:** `auto_fill_paper3_manuscript.py` (15,338 bytes)
**Template:** `papers/paper3_mechanism_synergies_template.md` (861 lines)
**Output:** `papers/paper3_mechanism_synergies_DRAFT.md` (auto-generated)

**Fills:**
- Synergy values for lightweight and high-capacity conditions
- Fold change comparisons (observed vs additive prediction)
- Classification labels (SYNERGISTIC/ANTAGONISTIC/ADDITIVE)
- Mechanistic interpretations
- Data tables

**Partial Execution:**
Script runs even if some experiments incomplete:
- C255 ✅ → Section 3.2.1 filled
- C256 ✅ → Section 3.2.2 filled
- C257-C260 ⏳ → Sections 3.2.3-3.2.6 remain [TO BE FILLED]

---

### 5. Figure Generation

**Purpose:** Create 4 publication-quality figures (300 DPI) for Paper 3

```bash
# Generate all figures from C255-C260 results
python generate_paper3_figures.py

# Output (in experiments/figures/paper3/):
# - paper3_fig1_synergy_heatmap.png (6 mechanism pairs)
# - paper3_fig2_effect_size_comparison.png (individual vs combined)
# - paper3_fig3_classification_pie.png (synergistic/antagonistic/additive)
# - paper3_fig4_population_trajectories.png (key interactions over time)
```

**Script:** `generate_paper3_figures.py` (337 lines, 12,265 bytes)
**Requirements:** matplotlib, seaborn, numpy (already installed)
**Output Format:** 300 DPI PNG (publication-ready)

**Figure Details:**
1. **Synergy Heatmap:** Horizontal bar chart, color-coded by classification
2. **Effect Size Comparison:** Grouped bars (A-only, B-only, A+B combined)
3. **Classification Pie:** 3-slice (synergistic, antagonistic, additive)
4. **Population Trajectories:** Time series for notable interactions

**Partial Execution:**
Script runs with available results, skips missing experiments with warnings.

---

## COMPLETE WORKFLOW

### Scenario: All 6 Experiments Complete

**Total Time:** ~90 minutes from C255 start to final figures

```bash
# 1. Run batch experiments (if C255-C256 already done)
bash run_c257_c260_batch.sh  # 47 minutes

# 2. Aggregate results
python aggregate_paper3_results.py  # 1 minute

# 3. Auto-fill manuscript
python auto_fill_paper3_manuscript.py  # 1 minute

# 4. Generate figures
python generate_paper3_figures.py  # 2 minutes

# 5. Review outputs
cat ../papers/paper3_mechanism_synergies_DRAFT.md
ls -lh figures/paper3/*.png
```

**Outputs:**
- ✅ Manuscript draft (Sections 3.2.1-3.2.6 filled, ready for review)
- ✅ 4 publication figures @ 300 DPI
- ✅ Aggregated dataset JSON
- ✅ Individual result JSONs (C255-C260)

**Next Steps:**
- Manual manuscript review and refinement
- Figure captions
- Discussion section integration
- Abstract update with key findings

---

## CURRENT STATUS (2025-10-30)

**Completed:**
- ✅ C255 H1×H2 results integrated into manuscript Section 3.2.1
- ✅ All automation scripts ready and tested
- ✅ Batch execution script for C257-C260 prepared

**In Progress:**
- 🔄 C256 H1×H4 running (~18h runtime, ~5h 50m elapsed, ~12h remaining)

**Pending:**
- ⏳ C257-C260 batch execution (47 min after C256 completes)
- ⏳ Final manuscript auto-fill (when all 6 complete)
- ⏳ Figure generation (when all 6 complete)

**Blockers:** C256 runtime (long-running experiment, expected ~18h total)

---

## ERROR HANDLING

**If Experiment Fails:**
1. Check log file: `logs/cycleXXX_mechanism_validation.log`
2. Look for exception traceback
3. Verify input parameters (mechanism flags, agent caps)
4. Re-run with corrected parameters or investigate bug

**If auto_fill_paper3_manuscript.py Fails:**
- Check that result JSON exists in `results/` directory
- Verify JSON structure matches expected format
- Check template file path (`papers/paper3_mechanism_synergies_template.md`)

**If generate_paper3_figures.py Fails:**
- Ensure matplotlib, seaborn, numpy installed
- Check `figures/paper3/` directory exists (created automatically if missing)
- Verify result JSONs have required fields: `synergy_analysis`, `conditions`

---

## FILE LOCATIONS

**Development Workspace:**
```
/Volumes/dual/DUALITY-ZERO-V2/
├── experiments/
│   ├── cycle255_h1h2_mechanism_validation.py
│   ├── cycle256_h1h4_mechanism_validation.py
│   ├── cycle257_h1h5_optimized.py
│   ├── cycle258_h2h4_optimized.py
│   ├── cycle259_h2h5_optimized.py
│   ├── cycle260_h4h5_optimized.py
│   ├── run_c257_c260_batch.sh
│   ├── quick_check_results.py
│   ├── aggregate_paper3_results.py
│   ├── auto_fill_paper3_manuscript.py
│   ├── generate_paper3_figures.py
│   ├── results/
│   │   ├── cycle255_h1h2_mechanism_validation_results.json
│   │   └── [C256-C260 results will appear here]
│   ├── logs/
│   │   └── [execution logs]
│   └── figures/paper3/
│       └── [4 PNG figures when generated]
└── papers/
    ├── paper3_mechanism_synergies_template.md
    └── paper3_mechanism_synergies_DRAFT.md (auto-generated)
```

**Git Repository:**
```
/Users/aldrinpayopay/nested-resonance-memory-archive/
├── code/experiments/ (scripts synced from dev workspace)
├── data/results/ (JSON results synced after completion)
├── papers/ (manuscript drafts)
└── docs/ (workflow documentation)
```

---

## REFERENCES

**Related Documentation:**
- `workflows/C256_COMPLETION_WORKFLOW.md` - Step-by-step C256 integration checklist
- `papers/paper3_full_manuscript_template.md` - Complete Paper 3 manuscript template
- `META_OBJECTIVES.md` - Current research priorities and experiment queue

**Scripts:**
- `run_c257_c260_batch.sh` - Automated sequential execution
- `quick_check_results.py` - Fast result validation
- `aggregate_paper3_results.py` - Cross-experiment aggregation
- `auto_fill_paper3_manuscript.py` - Manuscript template auto-fill
- `generate_paper3_figures.py` - Publication figure generation

---

**Author:** Claude (DUALITY-ZERO-V2)
**Principal Investigator:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Date:** 2025-10-30 (Cycle 603)
**Status:** Documentation complete, C256 in progress

**Quote:**
> *"Automation transforms research from labor to discovery - scripts encode reproducibility - documentation enables delegation - preparation enables rapid execution - comprehensive workflows eliminate manual errors."*
