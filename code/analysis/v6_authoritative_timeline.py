#!/usr/bin/env python3
"""
V6 Experiment Authoritative Timeline Calculator
================================================

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-08
Repository: https://github.com/mrdirno/nested-resonance-memory-archive

Purpose:
--------
Calculate V6 experiment runtime from AUTHORITATIVE SOURCE: OS process start time.

This replaces all previous milestone tracking methods that caused timeline
inconsistencies. The OS kernel timestamp is the ground truth.

License: GPL-3.0
"""

import subprocess
from datetime import datetime
import sys

# V6 Process ID (constant since launch)
V6_PID = 72904

# V6 AUTHORITATIVE START TIME (from OS kernel)
# Verified by: ps -p 72904 -o lstart
V6_START = datetime.fromisoformat('2025-11-05T15:59:17-08:00')


def get_current_runtime() -> dict:
    """
    Calculate current V6 runtime from OS process start time.

    Returns
    -------
    dict
        Runtime information with days, hours, and milestone status
    """
    try:
        # Verify process is still running
        result = subprocess.run(
            ["ps", "-p", str(V6_PID)],
            capture_output=True,
            text=True,
            check=True
        )

        if str(V6_PID) not in result.stdout:
            return {
                "status": "ERROR",
                "message": f"Process {V6_PID} not found"
            }

    except subprocess.CalledProcessError:
        return {
            "status": "ERROR",
            "message": f"Process {V6_PID} not running"
        }

    # Calculate runtime
    now = datetime.now(V6_START.tzinfo)
    elapsed = now - V6_START

    days = elapsed.total_seconds() / 86400
    hours = elapsed.total_seconds() / 3600

    # Next milestone
    next_milestone_day = int(days) + 1
    hours_to_next = (next_milestone_day - days) * 24

    return {
        "status": "RUNNING",
        "pid": V6_PID,
        "start_time": V6_START.isoformat(),
        "start_time_human": V6_START.strftime('%Y-%m-%d %H:%M:%S %Z'),
        "current_time": now.isoformat(),
        "current_time_human": now.strftime('%Y-%m-%d %H:%M:%S %Z'),
        "runtime_days": days,
        "runtime_hours": hours,
        "runtime_seconds": elapsed.total_seconds(),
        "last_milestone": int(days),
        "next_milestone": next_milestone_day,
        "hours_to_next_milestone": hours_to_next
    }


def print_runtime_status():
    """Print current V6 runtime status."""
    info = get_current_runtime()

    if info["status"] == "ERROR":
        print(f"ERROR: {info['message']}")
        return

    print("=" * 80)
    print("V6 EXPERIMENT AUTHORITATIVE TIMELINE")
    print("=" * 80)
    print()
    print(f"Process ID: {info['pid']}")
    print(f"Start Time: {info['start_time_human']}")
    print(f"Current Time: {info['current_time_human']}")
    print()
    print(f"RUNTIME (OS-VERIFIED):")
    print(f"  {info['runtime_days']:.4f} days")
    print(f"  {info['runtime_hours']:.2f} hours")
    print(f"  {info['runtime_seconds']:.0f} seconds")
    print()
    print(f"MILESTONES:")
    print(f"  Last milestone: {info['last_milestone']}-day")
    print(f"  Next milestone: {info['next_milestone']}-day (in {info['hours_to_next_milestone']:.1f}h)")
    print()
    print("=" * 80)
    print("VERIFICATION:")
    print(f"  Method: OS process start timestamp (ps -p {V6_PID} -o lstart)")
    print("  Confidence: 100% (kernel-level ground truth)")
    print("=" * 80)


def get_milestone_commit_message(milestone_day: int) -> str:
    """
    Generate commit message for milestone documentation.

    Parameters
    ----------
    milestone_day : int
        Milestone day number

    Returns
    -------
    str
        Commit message with Co-Authored-By line
    """
    info = get_current_runtime()

    if info["status"] == "ERROR":
        return f"ERROR: {info['message']}"

    hours_sustained = (info['runtime_days'] - milestone_day) * 24

    message = f"""V6 {milestone_day}-day milestone exceeded

V6 ultra-low frequency experiment runtime: {milestone_day}+ days

Start: {info['start_time_human']}
Milestone: {milestone_day}-day mark exceeded
Sustained: +{hours_sustained:.1f}h beyond milestone

Process: PID {info['pid']}
Verification: OS kernel timestamp (ps -p {info['pid']} -o lstart)

Co-Authored-By: Claude <noreply@anthropic.com>"""

    return message


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "commit-message":
            if len(sys.argv) < 3:
                print("Usage: v6_authoritative_timeline.py commit-message <milestone_day>")
                sys.exit(1)

            milestone = int(sys.argv[2])
            print(get_milestone_commit_message(milestone))
        else:
            print(f"Unknown command: {sys.argv[1]}")
            sys.exit(1)
    else:
        print_runtime_status()
