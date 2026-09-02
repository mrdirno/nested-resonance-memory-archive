# V6 Timeline Tracking (legacy)

Moved here from `CLAUDE.md` on 2026-09-01, as written except that two absolute workstation paths were made repository-relative. It tracked the 2025 V6 run and no longer steers the repository's agents; it is kept for the record. The tool it names is at `src/analysis/v6_authoritative_timeline.py` in this repository; the correction it cites is at `archive/summaries/MILESTONE_TIMELINE_CORRECTION.md`. The second part below came from the "If V6 Process Restarts" note in the error-correction section of the same file.

---

## V6 TIMELINE TRACKING (CRITICAL - AUTHORITATIVE SOURCE)

**⚠️ CRITICAL: NEVER MANUALLY CALCULATE V6 RUNTIME - ALWAYS USE AUTHORITATIVE TOOL ⚠️**

### Timeline Correction History (2025-11-08)

**MAJOR ERROR CORRECTED:** 69 commits (Nov 5-7, 2025) claimed impossible V6 milestones (50-93 days) that would require the experiment starting **before the repository existed**. This was caused by referencing the original development workspace timeline instead of the current process timeline.

**Complete correction documentation:** See `MILESTONE_TIMELINE_CORRECTION.md`

### Authoritative V6 Timeline (OS-Verified)

**V6 Experiment Start (PID 72904):**
```
Date: November 5, 2025, 3:59:17 PM PST
ISO: 2025-11-05T15:59:17-08:00
Verification: ps -p 72904 -o lstart
Confidence: 100% (OS kernel timestamp)
```

**Repository Timeline:**
```
Created: October 25, 2025, 10:26 PM PST
Age: 13+ days (as of Nov 8, 2025)
```

**V6 and Repository are DIFFERENT timelines:**
- Repository: 13 days old
- V6 process: Started 11 days after repository creation
- V6 runtime: ~2.5 days (as of Nov 8, 2025)

### MANDATORY Runtime Calculation Method

**ALWAYS use this tool for V6 runtime:**
```bash
python3 src/analysis/v6_authoritative_timeline.py
```

**Output example:**
```
V6 EXPERIMENT AUTHORITATIVE TIMELINE
Process ID: 72904
Start Time: 2025-11-05 15:59:17 UTC-08:00
Current Time: 2025-11-08 05:01:20 UTC-08:00

RUNTIME (OS-VERIFIED):
  2.5431 days
  61.03 hours

MILESTONES:
  Last milestone: 2-day
  Next milestone: 3-day (in 11.0h)

VERIFICATION:
  Method: OS process start timestamp (ps -p 72904 -o lstart)
  Confidence: 100% (kernel-level ground truth)
```

### Commit Message Generation

**For milestone documentation, use:**
```bash
python3 src/analysis/v6_authoritative_timeline.py commit-message <milestone_day>
```

This generates a properly formatted commit message with:
- OS-verified runtime
- Exact start timestamp
- Verification method
- Co-Authored-By line

### Prohibited Actions

**❌ NEVER:**
- Calculate V6 runtime manually
- Use process CPU time as runtime (CPU time ≠ elapsed time)
- Reference commit dates to calculate milestones
- Assume milestone claims in previous commits are correct
- Create visualizations with unverified day counts

**✅ ALWAYS:**
- Use `v6_authoritative_timeline.py` for runtime
- Verify runtime against OS process start timestamp
- Cross-check claims against repository age (can't exceed 13 days as of Nov 8)
- Include verification method in documentation
- Question milestone claims that exceed repository age

### Verification Checklist (Before ANY Milestone Claim)

1. ✅ Run `v6_authoritative_timeline.py`
2. ✅ Verify runtime is less than repository age (~13 days)
3. ✅ Check process is still running: `ps -p 72904`
4. ✅ Confirm OS start time matches: `ps -p 72904 -o lstart`
5. ✅ Include verification method in commit/documentation

### Why This Matters

**Without this protocol:**
- ❌ Manual tracking leads to systematic errors
- ❌ Timeline inconsistencies undermine reproducibility
- ❌ Human error propagates across documentation

**With this protocol:**
- ✅ OS-verified ground truth (100% confidence)
- ✅ Automated verification prevents human error
- ✅ Research integrity maintained
- ✅ Reproducible, auditable timeline

---

### If V6 Process Restarts

**If PID 72904 terminates and V6 restarts:**
1. Update `V6_PID` in `v6_authoritative_timeline.py`
2. Update `V6_START` with new process start time
3. Document the restart in repository
4. Reset milestone counter to 0
5. Never claim continuous runtime across restarts
