# Campaign Quality Control Infrastructure

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Date:** 2025-11-05
**Cycle:** 1036+

## Overview

This guide documents the quality control infrastructure for validating and aggregating campaign experimental data (C186-C189). Two complementary tools provide comprehensive data validation and statistical analysis for Paper 4 manuscript generation.

## Tools

### 1. Campaign Data Validator (`campaign_data_validator.py`)

**Purpose:** Post-experiment data integrity and quality validation

**Features:**
- File existence and JSON schema validation
- Data completeness checks (all seeds, all conditions present)
- Statistical sanity checks (outliers, NaNs, invalid values)
- Metadata consistency validation
- Human-readable validation reports
- Exit codes for CI/CD integration

**Usage:**

```bash
# Validate single experiment
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_data_validator.py cycle186 --seeds 10

# Validate full campaign (C186-C189)
python campaign_data_validator.py --campaign

# Generate report to file
python campaign_data_validator.py --campaign --output validation_report.txt

# Check exit code for automation
python campaign_data_validator.py --campaign
echo $?  # 0=pass, 1=fail, 2=warnings
```

**Output Example:**

```
================================================================================
CAMPAIGN DATA VALIDATION REPORT
================================================================================
Generated: 2025-11-05T14:30:00
Results Directory: /Volumes/dual/DUALITY-ZERO-V2/experiments/results

SUMMARY
--------------------------------------------------------------------------------
Total Experiments: 4
  ✓ Passed:        3 (75.0%)
  ⚠ Warnings:      1 (25.0%)
  ✗ Failed:        0 (0.0%)

DETAILED RESULTS
--------------------------------------------------------------------------------

✓ CYCLE186 - PASS
----------------------------------------
  No issues detected
  Key Metrics:
    Conditions: 10
    Seeds: 100/100
    Composition Time: 45.3 ± 2.1 cycles (n=100)
    Decomposition Time: 38.7 ± 1.8 cycles (n=100)
    Final Population: 8.2 ± 0.4 agents (n=100)

⚠ CYCLE187 - WARNING
----------------------------------------
  Issues:
    • INFO: 2 outliers detected in composition_time (>3σ)
  Key Metrics:
    Conditions: 4
    Seeds: 40/40
    ...
```

### 2. Campaign Results Aggregator (`campaign_results_aggregator.py`)

**Purpose:** Cross-experiment statistical analysis and publication-ready tables

**Features:**
- Statistical summaries per condition (mean, SEM, 95% CI)
- Effect size calculations (Cohen's d)
- Baseline comparisons for each experiment
- Multiple output formats (text, CSV, JSON)
- Publication-ready comparison tables

**Usage:**

```bash
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration

# Generate full campaign report
python campaign_results_aggregator.py --campaign --output campaign_report.txt

# Export to CSV for R/SPSS/Python analysis
python campaign_results_aggregator.py --campaign --csv campaign_results.csv

# Export to JSON for programmatic access
python campaign_results_aggregator.py --campaign --json campaign_results.json

# Aggregate specific experiments only
python campaign_results_aggregator.py cycle186 cycle187 --output partial_report.txt
```

**Output Example:**

```
====================================================================================================
Comparison Table: CYCLE186 - Composition Time
====================================================================================================
Condition                      Mean         ±SEM         95% CI                    vs BASELINE
----------------------------------------------------------------------------------------------------
BASELINE                       45.234       ±0.421       [44.409, 46.059]          (baseline)
DEPTH_05                       42.156       ±0.389       [41.394, 42.918]          d=-0.523 (-6.8%)
DEPTH_10                       38.923       ±0.412       [38.115, 39.731]          d=-1.067 (-13.9%)
DEPTH_15                       35.782       ±0.437       [34.926, 36.638]          d=-1.542 (-20.9%)
RESONANCE_05                   43.891       ±0.401       [43.105, 44.677]          d=-0.228 (-3.0%)
...
====================================================================================================
```

**CSV Output** (for statistical software):

```csv
condition_name,experiment_id,n_seeds,composition_time_mean,composition_time_std,composition_time_sem,...
BASELINE,cycle186,10,45.234,1.332,0.421,...
DEPTH_05,cycle186,10,42.156,1.230,0.389,...
...
```

## Integration with Paper 4 Workflow

These tools integrate seamlessly with the Paper 4 Integration Guide workflow:

### Phase 1: Data Validation (Before Analysis)

```bash
# Step 1: Validate all campaign data
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_data_validator.py --campaign --output validation_report.txt

# Step 2: Check for failures
if [ $? -eq 0 ]; then
    echo "✓ All data validated - proceeding to analysis"
else
    echo "✗ Validation issues detected - review validation_report.txt"
    exit 1
fi
```

### Phase 2: Data Aggregation (For Analysis)

```bash
# Step 3: Aggregate results
python campaign_results_aggregator.py --campaign \
    --output campaign_report.txt \
    --csv campaign_results.csv \
    --json campaign_results.json

# Step 4: Results ready for Paper 4 figure generation and statistical analysis
```

### Phase 3: Figure Generation

The aggregated CSV can be used directly with Paper 4 figure generators:

```python
import pandas as pd

# Load aggregated results
df = pd.read_csv('campaign_results.csv')

# Filter for specific experiment
c186_data = df[df['experiment_id'] == 'cycle186']

# Generate figures using existing figure generators
# (see paper4_figure_generators.py)
```

## Workflow Recommendations

### After Each Experiment Completes

```bash
# Immediate validation
python campaign_data_validator.py cycle186 --seeds 10

# Check for issues
if [ $? -ne 0 ]; then
    echo "⚠ Data quality issues detected - investigate before continuing"
fi
```

### After Campaign Completes

```bash
# Full validation
python campaign_data_validator.py --campaign --output validation_report.txt

# Full aggregation
python campaign_results_aggregator.py --campaign \
    --output campaign_report.txt \
    --csv campaign_results.csv \
    --json campaign_results.json

# Archive reports
mkdir -p /Volumes/dual/DUALITY-ZERO-V2/experiments/reports
cp validation_report.txt campaign_report.txt campaign_results.* \
   /Volumes/dual/DUALITY-ZERO-V2/experiments/reports/
```

### Integration with Automation

Both tools support automation through exit codes and structured output:

```bash
#!/bin/bash
# Post-experiment validation hook

EXPERIMENT_ID=$1
EXPECTED_SEEDS=$2

# Validate
python campaign_data_validator.py "$EXPERIMENT_ID" --seeds "$EXPECTED_SEEDS"

# Capture result
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo "✓ $EXPERIMENT_ID validated successfully"
    exit 0
elif [ $RESULT -eq 2 ]; then
    echo "⚠ $EXPERIMENT_ID has warnings (non-critical)"
    exit 0
else
    echo "✗ $EXPERIMENT_ID validation failed"
    exit 1
fi
```

## File Locations

```
/Volumes/dual/DUALITY-ZERO-V2/
├── code/orchestration/
│   ├── campaign_data_validator.py          # Data validation tool
│   ├── campaign_results_aggregator.py      # Results aggregation tool
│   └── QUALITY_CONTROL_GUIDE.md            # This guide
├── experiments/
│   ├── results/                            # Raw experiment results (JSON)
│   │   ├── cycle186_results.json
│   │   ├── cycle187_results.json
│   │   ├── cycle188_results.json
│   │   └── cycle189_results.json
│   └── reports/                            # Validation/aggregation reports
│       ├── validation_report.txt
│       ├── campaign_report.txt
│       ├── campaign_results.csv
│       └── campaign_results.json
└── papers/
    └── paper4_extension2/                  # Manuscript generation
        └── (use aggregated data here)
```

## Statistical Notes

### Effect Size Interpretation (Cohen's d)

- **Small effect:** |d| ≈ 0.2
- **Medium effect:** |d| ≈ 0.5
- **Large effect:** |d| ≈ 0.8+

### Confidence Intervals

95% confidence intervals use normal approximation (mean ± 1.96 × SEM). For small sample sizes (n < 30), consider using t-distribution correction in downstream analysis.

### Multiple Comparisons

When comparing multiple conditions to baseline, consider Bonferroni or other multiple comparison corrections in statistical analysis. The aggregator provides raw statistics; corrections should be applied during hypothesis testing.

## Troubleshooting

### "Results file not found"

Ensure experiment has completed and results are in correct directory:

```bash
ls -lh /Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_results.json
```

### "JSON decode error"

Results file may be corrupted or incomplete:

```bash
# Check file size
ls -lh /Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_results.json

# Validate JSON syntax
python -m json.tool cycle186_results.json > /dev/null
```

### "Missing seeds"

Experiment may have failed partway through. Check experiment logs:

```bash
tail -100 /tmp/c186_output.log
```

## Future Enhancements

Potential extensions to quality control infrastructure:

1. **Real-time validation:** Monitor experiments during execution
2. **Automated anomaly detection:** Flag unexpected patterns immediately
3. **Cross-experiment consistency:** Validate baselines consistent across C186-C189
4. **Publication figure validation:** Verify figure requirements met before manuscript generation
5. **Reproducibility checks:** Verify results reproducible from raw data

## References

- Paper 4 Integration Guide: `INTEGRATION_GUIDE.md`
- Campaign Execution Plan: `CAMPAIGN_EXECUTION_PLAN.md`
- Campaign Status Dashboard: `campaign_status_dashboard.py`
- Validation Campaign Orchestrator: `validation_campaign_orchestrator.py`

---

**Version:** 1.0
**Last Updated:** 2025-11-05 (Cycle 1036+)
