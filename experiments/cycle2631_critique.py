#!/usr/bin/env python3
"""
Experiment: Cycle 2631 - The Critique
Goal: Evaluate system performance against ideal metrics.
"""

import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2630_mirror import analyze_logs, SelfReport
except ImportError:
    sys.exit(1)

def evaluate_performance(report: SelfReport):
    print("Cycle 2631: The Critique - Scoring Performance")
    
    score = 0.0
    max_score = 3.0
    
    # Metric 1: Uptime (Ticks > 0)
    if report.total_ticks > 0:
        score += 1.0
        print("  [PASS] System has uptime history.")
    
    # Metric 2: Agent Density (Expect 5 agents)
    if 4.0 <= report.avg_agents <= 6.0:
        score += 1.0
        print("  [PASS] Agent count nominal.")
    else:
        print(f"  [WARN] Agent count deviation: {report.avg_agents}")
        
    # Metric 3: Stability (Target shouldn't flicker wildly unless requested)
    if report.target_stability > 0.5:
        score += 1.0
        print("  [PASS] Goal stability nominal.")
        
    final_score = score / max_score
    print(f"\nSystem Health Score: {final_score:.2f} / 1.0")
    
    return final_score

if __name__ == "__main__":
    report = analyze_logs()
    if report:
        evaluate_performance(report)
