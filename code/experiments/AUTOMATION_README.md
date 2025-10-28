<!--
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
-->

# Experiment Automation Tools

**Purpose:** Automated monitoring and pipeline execution tools for efficient research workflows

**Created:** 2025-10-27 (Cycle 421)
**Status:** Production-ready

---

## Tools Overview

### 1. C255 Completion Monitor & Pipeline Auto-Launcher

**File:** `monitor_c255_and_launch_pipeline.py`

**Purpose:** Automatically detect C255 experiment completion and optionally launch the complete Paper 3 pipeline (C256-C260 → aggregation → visualization).

**Design Philosophy:**
- **Proactive Automation:** Eliminates latency upon C255 completion
- **Reality Grounding:** File system monitoring, process checks, JSON validation
- **Audit Trail:** Comprehensive logging for reproducibility
- **Perpetual Research:** Enables continuous autonomous operation
- **Publication Value:** Demonstrates automation methodology for empirical research

**Usage Modes:**

```bash
# 1. Monitor only (check every 60 seconds, no auto-launch)
python3 monitor_c255_and_launch_pipeline.py --monitor-only

# 2. Auto-launch pipeline when C255 completes (recommended for unattended operation)
python3 monitor_c255_and_launch_pipeline.py --auto-launch

# 3. One-time check (no loop, useful for manual scripts)
python3 monitor_c255_and_launch_pipeline.py --check-once

# 4. Custom check interval (e.g., every 2 minutes)
python3 monitor_c255_and_launch_pipeline.py --monitor-only --check-interval 120
```

**Pipeline Execution Steps:**

When auto-launch is enabled and C255 completes, the tool automatically executes:

1. **C256-C260 Factorial Experiments** (~67 minutes total)
   - C256: H1×H4 pairwise validation
   - C257: H1×H5 pairwise validation
   - C258: H2×H4 pairwise validation
   - C259: H2×H5 pairwise validation
   - C260: H4×H5 pairwise validation

2. **Result Aggregation** (~5 minutes)
   - Executes `aggregate_paper3_results.py`
   - Combines all 6 factorial experiments (C255-C260)
   - Generates unified JSON with synergy calculations

3. **Visualization Generation** (~5 minutes)
   - Executes `visualize_factorial_synergy.py`
   - Generates publication-quality figures (300 DPI)
   - Creates synergy heatmaps, interaction plots

**Total Timeline:** ~102 minutes from C255 completion to Paper 3 submission-ready

**Monitoring Logic:**

The tool verifies C255 completion through multiple checks:
- ✅ Output file existence (`cycle255_h1h2_mechanism_validation_results.json`)
- ✅ JSON validity (parseable, non-empty)
- ✅ Required keys present (`experiment_name`, `conditions`, `metadata`)
- ✅ File recency (modified within last hour)
- ✅ Process status check (confirms process terminated)

**Audit Logging:**

All actions logged to `paper3_pipeline_execution.log`:
- Timestamped status checks
- Experiment execution start/completion
- Error messages with context
- Total execution time

**Example Log Output:**

```
[2025-10-27 21:25:00] Starting C255 monitoring (check interval: 60s)
[2025-10-27 21:25:00] Auto-launch: ENABLED
[2025-10-27 21:25:00] ✅ All pipeline scripts verified present
[2025-10-27 21:26:00] Status check #1: C255 still running, output not detected
[2025-10-27 21:27:00] Status check #2: C255 still running, output not detected
...
[2025-10-27 22:15:00] ✅ C255 completion verified: cycle255_h1h2_mechanism_validation_results.json
[2025-10-27 22:15:00] 🎉 C255 COMPLETION DETECTED (iteration 50)
[2025-10-27 22:15:00] Auto-launch enabled, starting Paper 3 pipeline...
[2025-10-27 22:15:00] ============================================================
[2025-10-27 22:15:00] PAPER 3 PIPELINE EXECUTION STARTING
[2025-10-27 22:15:00] ============================================================
[2025-10-27 22:15:00] STEP 1: Executing C256-C260 factorial experiments
[2025-10-27 22:15:00] Executing: cycle256_h1h4_mechanism_validation.py
[2025-10-27 22:28:15] ✅ cycle256_h1h4_mechanism_validation.py completed successfully
[2025-10-27 22:28:15] Executing: cycle257_h1h5_mechanism_validation.py
...
[2025-10-27 23:57:00] ✅ PAPER 3 PIPELINE COMPLETED SUCCESSFULLY
[2025-10-27 23:57:00] Total execution time: 102.0 minutes
```

**Error Handling:**

Robust error handling for common failure modes:
- **Timeout Protection:** 20 min per experiment, 5 min per analysis
- **Script Validation:** Pre-flight checks for all required files
- **JSON Validation:** Ensures output files are well-formed
- **Process Monitoring:** Detects unexpected terminations
- **Graceful Failures:** Exits with appropriate codes (0=success, 1=failure)

**Integration with Research Workflow:**

This tool embodies the "eliminate latency" principle from Cycle 419:
> "When experimental work is blocked, prepare all downstream infrastructure to eliminate latency upon completion."

**Timeline Context:**

- **Cycle 407:** Papers 1 & 5D arXiv packages created
- **Cycle 418:** Complete submission materials prepared (1,421 lines)
- **Cycle 419:** Root README updated, repository maintenance
- **Cycle 420:** Workspace verification, pipeline scripts confirmed ready
- **Cycle 421:** Automated monitoring tool created ← YOU ARE HERE
- **Upon C255 completion:** Tool auto-launches Paper 3 pipeline (~102 min to submission)

**Publication Value:**

This automation demonstrates:
- **Reproducible Research:** Automated pipelines ensure consistent execution
- **Methodological Rigor:** Multi-step validation before pipeline execution
- **Scalability:** Same pattern applicable to Papers 4, 5A-5F pipelines
- **Transparency:** Complete audit trail for peer review

**Future Extensions:**

Potential enhancements for subsequent papers:
- Email/Slack notifications upon completion
- Parallel execution of independent experiments
- Resource usage monitoring and throttling
- Automatic git commit and push upon success
- Integration with Paper 4 (C262-C263) and Paper 5 series

---

## Design Patterns

### Pattern 1: Proactive Pipeline Preparation

**Context:** Long-running experiments (C255 ~80+ hours) block downstream work

**Solution:** Prepare all downstream automation during blocked period

**Benefits:**
- Zero latency from C255 completion to Paper 3 submission
- Reproducible execution via automation
- Audit trail for publication

**Implementation:** `monitor_c255_and_launch_pipeline.py`

### Pattern 2: Multi-Stage Validation

**Context:** Pipeline execution involves multiple dependent steps

**Solution:** Validate each stage before proceeding to next

**Validation Stages:**
1. Pre-flight: Verify all scripts present
2. Per-experiment: Check exit codes and output files
3. Aggregation: Verify JSON structure
4. Visualization: Check figure generation

**Benefits:** Early failure detection, clear error messages

### Pattern 3: Reality-Grounded Monitoring

**Context:** Need to detect experiment completion reliably

**Solution:** Multiple independent checks (file, process, validation)

**Checks:**
- File existence
- JSON parsability
- Required keys present
- File recency
- Process status

**Benefits:** Robust detection, avoids false positives

---

## Usage Recommendations

### For Unattended Operation (Recommended)

```bash
# Run in background with auto-launch
nohup python3 monitor_c255_and_launch_pipeline.py --auto-launch > monitor.log 2>&1 &

# Check status
tail -f monitor.log

# Or check dedicated pipeline log
tail -f /Volumes/dual/DUALITY-ZERO-V2/paper3_pipeline_execution.log
```

### For Manual Control

```bash
# Monitor only, get notification when ready
python3 monitor_c255_and_launch_pipeline.py --monitor-only

# When notified, manually launch pipeline steps
python3 cycle256_h1h4_mechanism_validation.py
python3 cycle257_h1h5_mechanism_validation.py
# ... etc
```

### For Integration into Other Scripts

```bash
# Check completion status in shell script
if python3 monitor_c255_and_launch_pipeline.py --check-once; then
    echo "C255 complete, ready for pipeline"
    # ... your code here
else
    echo "C255 still running"
fi
```

---

## Maintenance Notes

**Script Location (Development):** `/Volumes/dual/DUALITY-ZERO-V2/experiments/monitor_c255_and_launch_pipeline.py`

**Script Location (Git Repo):** `/Users/aldrinpayopay/nested-resonance-memory-archive/code/experiments/monitor_c255_and_launch_pipeline.py`

**Dependencies:**
- Python 3.13
- Standard library only (subprocess, json, pathlib, time, argparse)
- No external packages required

**Testing:**
```bash
# Verify script syntax
python3 -m py_compile monitor_c255_and_launch_pipeline.py

# Test check-once mode (should exit with code 1 while C255 running)
python3 monitor_c255_and_launch_pipeline.py --check-once
echo $?  # Should show 1 if still running, 0 if complete
```

---

## Attribution

**Author:** Aldrin Payopay (aldrin.gdf@gmail.com)
**Co-Author:** Claude (DUALITY-ZERO-V2)
**License:** GPL-3.0
**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive

---

## Changelog

### Version 1.0 (2025-10-27, Cycle 421)
- Initial release
- C255 completion monitoring
- Auto-launch Paper 3 pipeline (C256-C260 → aggregate → visualize)
- Comprehensive logging and error handling
- Multiple validation checks
- Tested in check-once mode

---

**Last Updated:** 2025-10-27 (Cycle 421)
