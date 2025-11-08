# V6 Milestone Tracking Correction

**Author:** Aldrin Payopay <aldrin.gdf@gmail.com>
**Date:** 2025-11-08 (Cycle 1244+)
**Status:** Documentation of tracking error and correction

---

## Issue Summary

During Cycles 1243-1244, V6 milestone tracking used **unreliable process runtime calculations** instead of **GitHub-authoritative commit dates**, leading to incorrect milestone claims.

## Incorrect Claims (Now Retracted)

**Files affected:**
- `generate_v6_90_100_day_milestone_figure.py` (commit 730648a)
  - Claimed milestones up to 100 days
  - Actual last documented: 93 days

**Incorrect milestone data:**
```python
(1243, 2160.00, 90.000, 12.857, "90-DAY EXCEEDED (HISTORIC)"),
(1243, 2184.00, 91.000, 13.000, "91-day exceeded"),
(1243, 2208.00, 92.000, 13.143, "92-day exceeded"),
(1243, 2232.00, 93.000, 13.286, "93-day exceeded"),
(1243, 2256.00, 94.000, 13.429, "94-day exceeded"),  # NOT DOCUMENTED
(1244, 2280.00, 95.000, 13.571, "95-day exceeded"),  # NOT DOCUMENTED
(1244, 2304.00, 96.000, 13.714, "96-day exceeded"),  # NOT DOCUMENTED
(1244, 2328.00, 97.000, 13.857, "97-day exceeded"),  # NOT DOCUMENTED
(1244, 2352.00, 98.000, 14.000, "98-day exceeded"),  # NOT DOCUMENTED
(1245, 2376.00, 99.000, 14.143, "99-day IMMINENT"),  # NOT DOCUMENTED
(1245, 2400.00, 100.000, 14.286, "100-DAY MILESTONE"), # NOT DOCUMENTED
```

**Reality (GitHub-authoritative):**
- **Last documented milestone:** 93-day (Cycle 1243, commit 743b1e7, 2025-11-07 22:44:31 -0800)
- **Current runtime:** 93.18 days (as of 2025-11-08 03:10 PST)
- **Undocumented milestones:** 94, 95, 96, 97, 98, 99, 100 days (not yet reached or documented)

## Root Cause

**Incorrect methodology:**
- Used process CPU time (`ps` output) to calculate runtime
- Process showed ~2510 hours CPU time = ~104 days
- **Error:** CPU time ≠ elapsed time for I/O-bound processes

**Correct methodology (GitHub-authoritative):**
- Use commit dates from GitHub as authoritative source
- Last milestone commit date + elapsed time since = current runtime
- Milestones are OFFICIAL only after documentation + commit

## Corrected Tracking System

**New authoritative tracker:** `milestone_tracker_github_based.py` (commit 3c193b5)

**Methodology:**
1. Extract all milestone commits from `git log`
2. Last documented milestone: 93-day (2025-11-07 22:44:31)
3. Current runtime: 93-day + time_since_commit
4. Next milestone: 94-day (expected ~2025-11-08 18:00 PST)

**Complete milestone history (GitHub-extracted):**
- 50-day through 93-day: All documented with commit dates
- 94-day onwards: Pending future documentation

## Impact Assessment

**Affected artifacts:**
- `generate_v6_90_100_day_milestone_figure.py` (730648a) - contains speculative data
- `v6_90_100_day_milestone_progression.png` (730648a) - visualization based on speculation

**Action required:**
1. Mark 730648a artifacts as SPECULATIVE (not authoritative)
2. Create corrected visualization when actual milestones reached
3. Document 94+ day milestones only after they occur and are committed

## Lessons Learned

1. **Always use GitHub commit dates as authoritative source**
2. **Never trust process runtime metrics** for long-running experiments
3. **Milestone claims require documentation + commit** before being official
4. **Speculation must be clearly labeled** to prevent confusion

## Corrected Current Status

**As of 2025-11-08 03:10 PST:**
- **Last documented:** 93-day (Cycle 1243, commit 743b1e7)
- **Current runtime:** 93.18 days (estimate)
- **Next milestone:** 94-day in ~19.6 hours
- **Claims retracted:** 94, 95, 96, 97, 98, 99, 100 day milestones

---

**Commit:** 3c193b5 (milestone tracking correction)
**License:** GPL-3.0
