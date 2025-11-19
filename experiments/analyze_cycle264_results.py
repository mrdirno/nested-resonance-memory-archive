import json
import sys
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Paths
RESULTS_FILE = Path(__file__).parent / "results" / "cycle264_parameter_sensitivity_h1h2_results.json"
SUMMARY_FILE = Path(__file__).parent.parent / "archive" / "summaries" / "CYCLE264_RESULTS_ANALYSIS.md"

def load_results() -> Dict[str, Any]:
    if not RESULTS_FILE.exists():
        print(f"Error: Results file not found at {RESULTS_FILE}")
        sys.exit(1)
    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)

def calculate_synergy(baseline: float, h1: float, h2: float, combined: float) -> float:
    """
    Calculate Synergy Coefficient (S).
    S = Combined - (H1 + H2 - Baseline)
    
    If S > 0: Synergistic (Whole > Sum of Parts)
    If S < 0: Antagonistic (Whole < Sum of Parts)
    If S ~ 0: Additive (Independent)
    """
    expected = (h1 - baseline) + (h2 - baseline) + baseline
    return combined - expected

def analyze_results(data: Dict[str, Any]):
    print("Analyzing C264 Results...")
    
    # Organize data by parameter combination
    # Structure: {(pooling, sources): {'OFF-OFF': val, 'ON-OFF': val, 'OFF-ON': val, 'ON-ON': val}}
    analysis_grid = {}
    
    for key, result in data.items():
        p = result['pooling_rate']
        s = result['sources_rate']
        pop = result['mean_population']
        
        grid_key = (p, s)
        if grid_key not in analysis_grid:
            analysis_grid[grid_key] = {}
            
        if not result['h1_enabled'] and not result['h2_enabled']:
            mode = 'OFF-OFF'
        elif result['h1_enabled'] and not result['h2_enabled']:
            mode = 'ON-OFF'
        elif not result['h1_enabled'] and result['h2_enabled']:
            mode = 'OFF-ON'
        else:
            mode = 'ON-ON'
            
        analysis_grid[grid_key][mode] = pop

    # Generate Report
    report_lines = []
    report_lines.append("# Cycle 264 Analysis: H1×H2 Parameter Sensitivity")
    report_lines.append(f"**Date:** {datetime.now().isoformat()}")
    report_lines.append("**Metric:** Mean Population (3000 cycles)")
    report_lines.append("")
    report_lines.append("## Synergy Landscape")
    report_lines.append("| Pooling (H1) | Sources (H2) | Baseline | H1 Only | H2 Only | Combined | Expected | Synergy (S) | Regime |")
    report_lines.append("|---|---|---|---|---|---|---|---|---|")

    synergy_scores = []

    for (p, s), modes in sorted(analysis_grid.items()):
        # Ensure we have all 4 modes (handle missing data gracefully)
        if len(modes) < 4:
            continue
            
        base = modes.get('OFF-OFF', 0)
        h1 = modes.get('ON-OFF', 0)
        h2 = modes.get('OFF-ON', 0)
        comb = modes.get('ON-ON', 0)
        
        expected = (h1 - base) + (h2 - base) + base
        synergy = comb - expected
        synergy_scores.append(synergy)
        
        if synergy > 5.0:
            regime = "**SYNERGISTIC** 🚀"
        elif synergy < -5.0:
            regime = "**ANTAGONISTIC** ⚔️"
        else:
            regime = "ADDITIVE ➕"
            
        report_lines.append(f"| {p:.2f} | {s:.4f} | {base:.1f} | {h1:.1f} | {h2:.1f} | {comb:.1f} | {expected:.1f} | {synergy:.2f} | {regime} |")

    report_lines.append("")
    report_lines.append("## Summary Statistics")
    if synergy_scores:
        report_lines.append(f"- **Mean Synergy:** {np.mean(synergy_scores):.2f}")
        report_lines.append(f"- **Max Synergy:** {np.max(synergy_scores):.2f}")
        report_lines.append(f"- **Min Synergy:** {np.min(synergy_scores):.2f}")
    else:
        report_lines.append("- No complete data sets available yet.")

    # Write Report
    SUMMARY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, 'w') as f:
        f.write("\n".join(report_lines))
    
    print(f"Analysis complete. Report generated at {SUMMARY_FILE}")
    print("\n".join(report_lines))

if __name__ == "__main__":
    data = load_results()
    analyze_results(data)
