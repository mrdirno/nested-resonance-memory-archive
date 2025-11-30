#!/usr/bin/env python3
"""
Experiment: Cycle 2599 - The Synthesizer
Goal: Automatically generate a summary of Sentinel and Harvester logs.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import statistics

def load_jsonl(file_path):
    data = []
    if not Path(file_path).exists():
        print(f"Warning: File not found {file_path}")
        return data
        
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return data

def analyze_sentinel_logs(logs):
    if not logs:
        return {"status": "No Data"}
    
    total_steps = len(logs)
    alerts = [entry for entry in logs if entry.get("alert")]
    magnitudes = [entry["magnitude"] for entry in logs]
    velocities = [entry["velocity"] for entry in logs]
    
    return {
        "total_monitored_steps": total_steps,
        "alerts_triggered": len(alerts),
        "alert_messages": [a["alert"] for a in alerts],
        "avg_magnitude": statistics.mean(magnitudes) if magnitudes else 0,
        "max_velocity": max(velocities) if velocities else 0,
        "status": "UNSTABLE" if alerts else "STABLE"
    }

def analyze_harvester_logs(logs):
    if not logs:
        return {"status": "No Data"}
        
    total_harvested = len(logs)
    similarities = [entry["similarity"] for entry in logs]
    alignments = [entry["phase_alignment"] for entry in logs]
    
    return {
        "total_harvested_events": total_harvested,
        "avg_similarity": statistics.mean(similarities) if similarities else 0,
        "avg_phase_alignment": statistics.mean(alignments) if alignments else 0,
        "max_similarity": max(similarities) if similarities else 0
    }

def generate_report(sentinel_data, harvester_data):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report = [
        f"# AUTONOMY LAYER REPORT - CYCLE 2599",
        f"**Timestamp:** {timestamp}",
        f"",
        f"## 1. SENTINEL REPORT (Health Monitoring)",
        f"- **Status:** {sentinel_data.get('status', 'UNKNOWN')}",
        f"- **Steps Monitored:** {sentinel_data.get('total_monitored_steps', 0)}",
        f"- **Alerts:** {sentinel_data.get('alerts_triggered', 0)}",
        f"- **Max Phase Velocity:** {sentinel_data.get('max_velocity', 0):.4f}",
    ]
    
    if sentinel_data.get('alerts_triggered', 0) > 0:
        report.append("### Active Alerts:")
        for alert in sentinel_data.get('alert_messages', []):
            report.append(f"- ⚠️ {alert}")
            
    report.extend([
        f"",
        f"## 2. HARVESTER REPORT (Data Collection)",
        f"- **Total Resonance Events:** {harvester_data.get('total_harvested_events', 0)}",
        f"- **Average Similarity:** {harvester_data.get('avg_similarity', 0):.4f}",
        f"- **Max Similarity:** {harvester_data.get('max_similarity', 0):.4f}",
        f"- **Avg Phase Alignment:** {harvester_data.get('avg_phase_alignment', 0):.4f}",
    ])
    
    return "\n".join(report)

def main():
    print("Cycle 2599: The Synthesizer - Initialization")
    
    sentinel_path = "experiments/logs/sentinel_cycle2597.jsonl"
    harvester_path = "experiments/logs/harvester_cycle2598.jsonl"
    
    print("Loading logs...")
    sentinel_logs = load_jsonl(sentinel_path)
    harvester_logs = load_jsonl(harvester_path)
    
    print("Analyzing data...")
    sentinel_analysis = analyze_sentinel_logs(sentinel_logs)
    harvester_analysis = analyze_harvester_logs(harvester_logs)
    
    print("Generating report...")
    report = generate_report(sentinel_analysis, harvester_analysis)
    
    output_path = "experiments/logs/autonomy_report_cycle2599.md"
    with open(output_path, "w") as f:
        f.write(report)
        
    print(f"\nREPORT GENERATED: {output_path}")
    print("-" * 40)
    print(report)
    print("-" * 40)
    
    # Validate that we actually processed data
    if sentinel_analysis.get('total_monitored_steps', 0) == 0:
        print("FAILURE: No Sentinel data processed.")
        sys.exit(1)
        
    if harvester_analysis.get('total_harvested_events', 0) == 0:
        print("FAILURE: No Harvester data processed.")
        sys.exit(1)

    print("SUCCESS: Synthesis complete.")

if __name__ == "__main__":
    main()
