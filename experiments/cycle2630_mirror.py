#!/usr/bin/env python3
"""
Experiment: Cycle 2630 - The Mirror
Goal: System introspection via log analysis.
"""

import json
import statistics
from pathlib import Path
from dataclasses import dataclass

@dataclass
class SelfReport:
    timestamp_start: float
    timestamp_end: float
    total_ticks: int
    avg_agents: float
    target_stability: float # 1.0 = stable target, 0.0 = chaotic

def analyze_logs():
    print("Cycle 2630: The Mirror - Reading System Logs")
    log_path = Path("experiments/logs/system_history.jsonl")
    
    if not log_path.exists():
        print("FAILURE: No logs found.")
        return None

    records = []
    with open(log_path, "r") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except:
                pass
                
    if not records:
        print("FAILURE: Empty logs.")
        return None

    # Calculate Metrics
    timestamps = [r['timestamp'] for r in records]
    agents = [r['agents_active'] for r in records]
    targets = [str(r['target_pos']) for r in records]
    
    # Target stability (how many unique targets / total steps)
    # If unique == 1, stability = 1.0
    unique_targets = len(set(targets))
    stability = 1.0 / unique_targets if unique_targets > 0 else 0.0
    
    report = SelfReport(
        timestamp_start=min(timestamps),
        timestamp_end=max(timestamps),
        total_ticks=len(records),
        avg_agents=statistics.mean(agents),
        target_stability=stability
    )
    
    print("\n--- SELF REPORT ---")
    print(f"Duration: {report.timestamp_end - report.timestamp_start:.2f}s")
    print(f"Ticks Observed: {report.total_ticks}")
    print(f"Avg Active Agents: {report.avg_agents:.1f}")
    print(f"Target Stability: {report.target_stability:.2f}")
    print("-------------------")
    
    return report

if __name__ == "__main__":
    analyze_logs()
