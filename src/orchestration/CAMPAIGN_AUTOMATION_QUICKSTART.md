# Campaign Automation Quick Start Guide

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Date:** 2025-11-05
**Cycle:** 1037+

## Overview

This guide provides a rapid deployment workflow for the complete campaign automation system. All infrastructure is operational and ready for immediate use. This consolidates the entire Validation Campaign Phase 2 automation.

## System Components

The campaign automation system consists of 7 integrated tools (4,317 lines total):

1. **Validation Campaign Orchestrator** (585 lines) - Sequential experiment automation
2. **Campaign Status Dashboard** (352 lines) - Real-time monitoring
3. **Campaign Execution Plan** (453 lines) - Workflow documentation
4. **Paper 4 Integration Guide** (761 lines) - Post-campaign analysis
5. **Campaign Data Validator** (435 lines) - Quality control
6. **Campaign Results Aggregator** (543 lines) - Statistical analysis
7. **Quality Control Guide** (432 lines) - Validation workflows
8. **Session Summaries** (2,340 lines cumulative) - Documentation

## Quick Start (3 Steps)

### Step 1: Launch Campaign (5 minutes)

```bash
# Navigate to orchestration directory
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration

# Launch campaign starting from C186
nohup python3 -u validation_campaign_orchestrator.py --start-from C186 \
  > /tmp/campaign_orchestrator.log 2>&1 &

# Capture process ID
ORCHESTRATOR_PID=$!
echo "Campaign orchestrator launched, PID: $ORCHESTRATOR_PID"

# Verify launch
ps -p $ORCHESTRATOR_PID
```

**What happens:**
- C186 launches immediately (10 experiments, ~5 hours)
- Monitor activates, checks every 60 seconds
- Upon C186 completion → C187 auto-launches
- Upon C187 completion → C188 auto-launches
- Upon C188 completion → C189 auto-launches
- Total campaign: ~28 hours, 180 experiments, **zero manual intervention**

### Step 2: Monitor Campaign (anytime)

```bash
# Quick status check (brief mode)
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_status_dashboard.py --mode brief

# Full status with recommendations
python campaign_status_dashboard.py --mode full

# JSON output for programmatic access
python campaign_status_dashboard.py --mode json > campaign_status.json
```

**Example brief output:**
```
Campaign Status (Brief)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C186: RUNNING [7/10] 3:15:42 ~1.5h remaining 2.4% CPU ⚡
C187: QUEUED (auto-launch after C186, ~5h, 30 exp)
C188: QUEUED (auto-launch after C187, ~6.7h, 40 exp)
C189: QUEUED (auto-launch after C188, ~16.7h, 100 exp)

Timeline: ~22.2h remaining (88% → 100%)
Monitor: PID 44974 ✓ Active
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
→ Continue monitoring
```

### Step 3: Post-Campaign Analysis (after completion)

```bash
# Validate all data (run immediately after C189 completes)
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_data_validator.py --campaign --output validation_report.txt

# If validation passes, aggregate results
python campaign_results_aggregator.py --campaign \
  --output campaign_report.txt \
  --csv campaign_results.csv \
  --json campaign_results.json

# Generate Paper 4 manuscript
cd /Volumes/dual/DUALITY-ZERO-V2/papers/paper4_extension2
python ../paper_generation/generate_paper4_manuscript.py

# Expected timeline: ~10-12 hours from raw data to complete manuscript
```

## Detailed Workflows

### Scenario A: Start Fresh Campaign

**Use case:** Launch complete C186→C187→C188→C189 sequence from scratch

```bash
# Step 1: Launch orchestrator
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
nohup python3 -u validation_campaign_orchestrator.py --start-from C186 \
  > /tmp/campaign_orchestrator.log 2>&1 & echo $!

# Step 2: Verify launch
python campaign_status_dashboard.py --mode brief

# Step 3: Walk away for ~28 hours
# (Optional: Check status periodically)

# Step 4: After completion, run post-campaign workflow (see Step 3 above)
```

**Expected timeline:**
- C186: 0-5 hours (10 exp)
- C187: 5-10 hours (30 exp)
- C188: 10-16.7 hours (40 exp)
- C189: 16.7-33.4 hours (100 exp)
- **Total: ~28-33 hours**

### Scenario B: Resume Mid-Campaign

**Use case:** C186 already running, want to ensure automation continues

```bash
# Check if orchestrator is running
ps aux | grep validation_campaign_orchestrator

# If not running, relaunch from current experiment
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_status_dashboard.py --mode full

# Based on status, launch from appropriate point:
# If C186 complete: --start-from C187
# If C187 complete: --start-from C188
# If C188 complete: --start-from C189

nohup python3 -u validation_campaign_orchestrator.py --start-from C187 \
  > /tmp/campaign_orchestrator.log 2>&1 & echo $!
```

### Scenario C: Individual Experiment Launch

**Use case:** Run single experiment outside automation

```bash
# Launch C186 manually
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
nohup python3 -u cycle186_extended_validation.py > /tmp/c186_output.log 2>&1 &
C186_PID=$!

# Monitor progress
tail -f /tmp/c186_output.log

# Check if complete
python /Volumes/dual/DUALITY-ZERO-V2/code/orchestration/campaign_status_dashboard.py \
  --mode brief

# Validate after completion
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_data_validator.py cycle186 --seeds 10
```

### Scenario D: Data Validation Only

**Use case:** Experiments complete, verify data quality before analysis

```bash
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration

# Validate all campaign experiments
python campaign_data_validator.py --campaign --output validation_report.txt

# Check exit code
echo $?
# 0 = all passed
# 1 = failures detected
# 2 = warnings only

# Review report
cat validation_report.txt

# If issues found, investigate specific experiment
python campaign_data_validator.py cycle186 --seeds 10
```

### Scenario E: Statistical Analysis Only

**Use case:** Data validated, need publication tables and statistics

```bash
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration

# Generate full report
python campaign_results_aggregator.py --campaign --output campaign_report.txt

# Export for statistical software (R, Python, SPSS)
python campaign_results_aggregator.py --campaign --csv campaign_results.csv

# Export for programmatic access
python campaign_results_aggregator.py --campaign --json campaign_results.json

# Use aggregated data in analysis
cd /Volumes/dual/DUALITY-ZERO-V2/papers/paper4_extension2/analysis
python analyze_campaign_results.py --input ../../code/orchestration/campaign_results.csv
```

## Integration Points

### With Paper 4 Workflow

The campaign automation integrates seamlessly with Paper 4 manuscript generation:

```bash
# After campaign completes:

# 1. Validate data
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration
python campaign_data_validator.py --campaign

# 2. Aggregate results
python campaign_results_aggregator.py --campaign --csv campaign_results.csv

# 3. Generate figures (Phase 4 of Integration Guide)
cd /Volumes/dual/DUALITY-ZERO-V2/papers/paper4_extension2
python generate_all_figures.py

# 4. Generate manuscript sections (Phases 5-7 of Integration Guide)
python generate_results_section.py
python generate_discussion_section.py
python generate_abstract.py

# 5. Assemble complete manuscript (Phase 8 of Integration Guide)
python master_manuscript_orchestrator.py

# 6. Verify and refine (Phase 9 of Integration Guide)
python composite_manuscript_scorecard.py
```

See `INTEGRATION_GUIDE.md` for complete 9-phase workflow (~10-12 hours).

### With Monitoring Dashboard

Check campaign status anytime during execution:

```bash
# Quick check
python campaign_status_dashboard.py --mode brief

# Detailed status with recommendations
python campaign_status_dashboard.py --mode full

# Automated monitoring (every 5 minutes)
while true; do
  python campaign_status_dashboard.py --mode brief
  sleep 300
done
```

### With Quality Control

Validate data at any checkpoint:

```bash
# After each experiment completes
python campaign_data_validator.py cycle186 --seeds 10

# After full campaign
python campaign_data_validator.py --campaign

# Integrate with automation
if python campaign_data_validator.py cycle186 --seeds 10; then
  echo "✓ C186 validated, proceeding to C187"
else
  echo "✗ C186 validation failed, investigate before continuing"
  exit 1
fi
```

## Troubleshooting

### Campaign orchestrator not launching

**Symptom:** `python validation_campaign_orchestrator.py` fails

**Solutions:**
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Verify dependencies
pip list | grep -E "psutil|numpy|scipy"

# Check experiment scripts exist
ls /Volumes/dual/DUALITY-ZERO-V2/experiments/cycle{186,187,188,189}_*.py

# Check permissions
chmod +x /Volumes/dual/DUALITY-ZERO-V2/experiments/cycle*.py
```

### Monitor not detecting completion

**Symptom:** C186 completes but C187 doesn't auto-launch

**Solutions:**
```bash
# Check monitor is running
ps aux | grep handoff_monitor

# Check results file exists
ls -lh /Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_results.json

# Manually verify completion
python campaign_status_dashboard.py --mode full

# If needed, manually launch next experiment
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
nohup python3 -u cycle187_network_structure.py > /tmp/c187_output.log 2>&1 &
```

### Validation fails

**Symptom:** `campaign_data_validator.py` reports failures

**Solutions:**
```bash
# Review detailed validation report
python campaign_data_validator.py --campaign --output report.txt
cat report.txt

# Check specific experiment
python campaign_data_validator.py cycle186 --seeds 10

# Common issues:
# - Missing seeds: Experiment crashed partway through
# - JSON errors: Results file corrupted
# - Outliers: Expected variation or genuine anomalies

# Verify experiment logs
tail -100 /tmp/c186_output.log

# If data corruption, may need to re-run experiment
cd /Volumes/dual/DUALITY-ZERO-V2/experiments
python cycle186_extended_validation.py  # Re-run
```

### Results aggregation empty

**Symptom:** `campaign_results_aggregator.py` finds no data

**Solutions:**
```bash
# Verify results files exist
ls -lh /Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle{186,187,188,189}_results.json

# Check file paths in aggregator
python -c "
from pathlib import Path
results_dir = Path('/Volumes/dual/DUALITY-ZERO-V2/experiments/results')
print('Results directory:', results_dir)
print('Exists:', results_dir.exists())
print('Files:', list(results_dir.glob('cycle*.json')))
"

# If path mismatch, specify explicitly
python campaign_results_aggregator.py --campaign \
  --results-dir /Volumes/dual/DUALITY-ZERO-V2/experiments/results
```

## Performance Expectations

### Resource Usage

**Per Experiment:**
- CPU: 2-5% (single core, Python process)
- Memory: ~200-500 MB
- Disk I/O: Minimal (JSON writes only)

**Campaign Total:**
- CPU: Sustained 2-5% for ~28 hours
- Memory: Stable ~200-500 MB
- Disk: ~50 MB results files
- Network: None (all local computation)

### Timing Estimates

Based on historical data:

| Experiment | Seeds | Conditions | Est. Duration | Cumulative |
|------------|-------|------------|---------------|------------|
| C186       | 10    | 10         | ~5.0 hours    | 5.0h       |
| C187       | 10    | 4          | ~5.0 hours    | 10.0h      |
| C188       | 10    | 5          | ~6.7 hours    | 16.7h      |
| C189       | 10    | 6          | ~16.7 hours   | 33.4h      |

**Total campaign: ~28-33 hours** (wall-clock time, single machine)

### Validation/Analysis Timing

**Data Validation:** ~1-2 minutes (all 180 experiments)
**Results Aggregation:** ~30 seconds (statistical summaries)
**Figure Generation:** ~2-3 minutes (6 figures @ 300 DPI)
**Manuscript Generation:** ~10-12 hours (complete workflow)

## File Locations Reference

```
/Volumes/dual/DUALITY-ZERO-V2/
├── code/orchestration/
│   ├── validation_campaign_orchestrator.py    # Main automation
│   ├── campaign_status_dashboard.py           # Monitoring
│   ├── campaign_data_validator.py             # Quality control
│   ├── campaign_results_aggregator.py         # Statistical analysis
│   ├── CAMPAIGN_EXECUTION_PLAN.md             # Workflow docs
│   ├── QUALITY_CONTROL_GUIDE.md               # QC workflows
│   └── CAMPAIGN_AUTOMATION_QUICKSTART.md      # This guide
├── experiments/
│   ├── cycle186_extended_validation.py        # C186 experiment
│   ├── cycle187_network_structure.py          # C187 experiment
│   ├── cycle188_memory_effects.py             # C188 experiment
│   ├── cycle189_burst_clustering.py           # C189 experiment
│   └── results/
│       ├── cycle186_results.json              # C186 data
│       ├── cycle187_results.json              # C187 data
│       ├── cycle188_results.json              # C188 data
│       └── cycle189_results.json              # C189 data
├── papers/paper4_extension2/
│   ├── INTEGRATION_GUIDE.md                   # Post-campaign workflow
│   └── (Paper 4 generation infrastructure)
└── archive/summaries/
    └── SESSION_SUMMARY_CYCLES*.md             # Documentation
```

## Command Cheat Sheet

```bash
# Campaign operations
cd /Volumes/dual/DUALITY-ZERO-V2/code/orchestration

# Launch campaign
nohup python3 -u validation_campaign_orchestrator.py --start-from C186 \
  > /tmp/campaign_orchestrator.log 2>&1 & echo $!

# Quick status
python campaign_status_dashboard.py --mode brief

# Full status
python campaign_status_dashboard.py --mode full

# Validate data
python campaign_data_validator.py --campaign

# Aggregate results
python campaign_results_aggregator.py --campaign --csv campaign_results.csv

# Check experiment logs
tail -f /tmp/c186_output.log
tail -f /tmp/c187_output.log
tail -f /tmp/c188_output.log
tail -f /tmp/c189_output.log

# Check monitor logs
tail -f /tmp/handoff_c187.log
tail -f /tmp/handoff_c188.log
tail -f /tmp/handoff_c189.log

# Kill processes (if needed)
kill <PID>
```

## Next Steps

After campaign completion and validation:

1. **Data Validation** → `campaign_data_validator.py --campaign`
2. **Statistical Analysis** → `campaign_results_aggregator.py --campaign --csv`
3. **Paper 4 Generation** → Follow `INTEGRATION_GUIDE.md` (9 phases)
4. **Manuscript Review** → Use `composite_manuscript_scorecard.py`
5. **Submission** → Format per journal requirements
6. **Continue Research** → Paper 5 series, extended parameter space

## Support

**Documentation:**
- Campaign Execution Plan: `CAMPAIGN_EXECUTION_PLAN.md`
- Paper 4 Integration: `INTEGRATION_GUIDE.md`
- Quality Control: `QUALITY_CONTROL_GUIDE.md`
- Session Summaries: `/archive/summaries/SESSION_SUMMARY_*.md`

**Troubleshooting:**
- Check experiment logs: `/tmp/c{186,187,188,189}_output.log`
- Check monitor logs: `/tmp/handoff_c{187,188,189}.log`
- Check orchestrator log: `/tmp/campaign_orchestrator.log`
- Verify data: `campaign_data_validator.py`

**Source Code:**
- Repository: https://github.com/mrdirno/nested-resonance-memory-archive
- Issue Tracker: https://github.com/mrdirno/nested-resonance-memory-archive/issues

---

**Version:** 1.0
**Last Updated:** 2025-11-05 (Cycle 1037+)
**Total Infrastructure:** 4,317 lines (7 tools + documentation)
**Status:** Operational, ready for deployment
