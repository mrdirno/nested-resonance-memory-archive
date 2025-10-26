#!/usr/bin/env python3
"""
Generate publication-ready figure data from Cycles 39-40
DUALITY-ZERO-V2 Research Paper Figures

Creates CSV files and plotting scripts for:
- Figure 1: Oscillating attractor time series
- Figure 2: Learning curves comparison
- Figure 3: Reproducibility validation
- Figure 4: Framework validation progression
"""

import json
import csv
from pathlib import Path
from typing import List, Dict, Any

# Paths
RESULTS_DIR = Path(__file__).parent / "results" / "long_term"
OUTPUT_DIR = Path(__file__).parent / "results" / "figures"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_checkpoint_data(experiment_id: str, cycles: List[int]) -> Dict[str, List]:
    """Load agent counts and pattern counts from checkpoint files."""
    agent_counts = []
    pattern_counts = []

    for cycle in cycles:
        checkpoint_file = RESULTS_DIR / f"{experiment_id}_checkpoint_{cycle}.json"

        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                agent_counts.append(data.get('agent_count', 0))
                pattern_counts.append(data.get('emergent_patterns', 0))
        else:
            print(f"Warning: Missing checkpoint {cycle} for {experiment_id}")
            agent_counts.append(None)
            pattern_counts.append(None)

    return {
        'cycles': cycles,
        'agent_counts': agent_counts,
        'pattern_counts': pattern_counts
    }

def generate_figure1_oscillating_attractor():
    """
    Figure 1: Oscillating Attractor Time Series
    Shows agent counts over 100 cycles with phase transitions marked.
    """
    print("Generating Figure 1: Oscillating Attractor...")

    # Load both runs
    cycles = list(range(10, 101, 10))
    run1_data = load_checkpoint_data("longterm_1761111010", cycles)
    run2_data = load_checkpoint_data("longterm_1761111440", cycles)

    # Write CSV
    output_file = OUTPUT_DIR / "figure1_oscillating_attractor.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Cycle', 'Run1_Agents', 'Run2_Agents', 'Match'])

        for i, cycle in enumerate(cycles):
            run1_agents = run1_data['agent_counts'][i]
            run2_agents = run2_data['agent_counts'][i]
            match = 'Yes' if run1_agents == run2_agents else 'No'
            writer.writerow([cycle, run1_agents, run2_agents, match])

    print(f"✅ Figure 1 data saved: {output_file}")
    print(f"   Agent counts: {run1_data['agent_counts']}")
    print(f"   Match rate: 100%" if all(run1_data['agent_counts'][i] == run2_data['agent_counts'][i] for i in range(len(cycles))) else "   Mismatch detected!")

def generate_figure2_learning_curves():
    """
    Figure 2: Learning Curves Comparison
    Shows pattern accumulation over 100 cycles for both runs.
    """
    print("\nGenerating Figure 2: Learning Curves...")

    # Load both runs
    cycles = list(range(10, 101, 10))
    run1_data = load_checkpoint_data("longterm_1761111010", cycles)
    run2_data = load_checkpoint_data("longterm_1761111440", cycles)

    # Calculate learning rates (linear fit)
    def calc_learning_rate(patterns, cycles):
        if not patterns or len(patterns) < 2:
            return 0.0
        # Simple slope calculation
        n = len(patterns)
        sum_x = sum(cycles)
        sum_y = sum(patterns)
        sum_xy = sum(c * p for c, p in zip(cycles, patterns))
        sum_x2 = sum(c * c for c in cycles)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

    run1_rate = calc_learning_rate(run1_data['pattern_counts'], cycles)
    run2_rate = calc_learning_rate(run2_data['pattern_counts'], cycles)

    # Write CSV
    output_file = OUTPUT_DIR / "figure2_learning_curves.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Cycle', 'Run1_Patterns', 'Run2_Patterns', 'Run1_Rate', 'Run2_Rate'])

        for i, cycle in enumerate(cycles):
            writer.writerow([
                cycle,
                run1_data['pattern_counts'][i],
                run2_data['pattern_counts'][i],
                run1_rate,
                run2_rate
            ])

    print(f"✅ Figure 2 data saved: {output_file}")
    print(f"   Run 1 learning rate: {run1_rate:.2f} patterns/cycle")
    print(f"   Run 2 learning rate: {run2_rate:.2f} patterns/cycle")
    print(f"   Variance: {abs((run2_rate - run1_rate) / run1_rate * 100):.1f}%")

def generate_figure3_reproducibility():
    """
    Figure 3: Reproducibility Validation
    Shows stability metrics comparison between runs.
    """
    print("\nGenerating Figure 3: Reproducibility...")

    # Load both runs
    cycles = list(range(10, 101, 10))
    run1_data = load_checkpoint_data("longterm_1761111010", cycles)
    run2_data = load_checkpoint_data("longterm_1761111440", cycles)

    # Calculate statistics
    import statistics

    run1_mean = statistics.mean(run1_data['agent_counts'])
    run1_stdev = statistics.stdev(run1_data['agent_counts'])
    run1_cv = run1_stdev / run1_mean if run1_mean > 0 else 0
    run1_stability = 1.0 / (1.0 + run1_cv)

    run2_mean = statistics.mean(run2_data['agent_counts'])
    run2_stdev = statistics.stdev(run2_data['agent_counts'])
    run2_cv = run2_stdev / run2_mean if run2_mean > 0 else 0
    run2_stability = 1.0 / (1.0 + run2_cv)

    # Write CSV
    output_file = OUTPUT_DIR / "figure3_reproducibility.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Run1', 'Run2', 'Difference', 'Match'])

        metrics = [
            ('Mean Agents', run1_mean, run2_mean),
            ('Std Deviation', run1_stdev, run2_stdev),
            ('CV', run1_cv, run2_cv),
            ('Stability Score', run1_stability, run2_stability)
        ]

        for metric_name, val1, val2 in metrics:
            diff = abs(val2 - val1)
            match = 'Yes' if diff < 0.01 else 'No'  # 1% tolerance
            writer.writerow([metric_name, f"{val1:.4f}", f"{val2:.4f}", f"{diff:.4f}", match])

    print(f"✅ Figure 3 data saved: {output_file}")
    print(f"   Stability Run 1: {run1_stability:.4f}")
    print(f"   Stability Run 2: {run2_stability:.4f}")
    print(f"   Match: {'Yes' if abs(run2_stability - run1_stability) < 0.01 else 'No'}")

def generate_figure4_framework_validation():
    """
    Figure 4: Framework Validation Progression
    Shows progression from Cycle 36 to Cycle 40.
    """
    print("\nGenerating Figure 4: Framework Validation Progression...")

    # Historical data from cycle documentation
    progression_data = [
        {
            'cycle': 36,
            'frameworks': 1,
            'frameworks_names': 'Self-Giving',
            'cycles_run': 20,
            'agents_persisted': 0,
            'patterns_detected': 0,
            'confidence': 0.70,
            'key_achievement': 'First sustained operation'
        },
        {
            'cycle': 37,
            'frameworks': 2,
            'frameworks_names': 'Self-Giving, NRM',
            'cycles_run': 20,
            'agents_persisted': 3,
            'patterns_detected': 0,
            'confidence': 0.76,
            'key_achievement': 'NRM validated via parameter tuning'
        },
        {
            'cycle': 38,
            'frameworks': 3,
            'frameworks_names': 'Self-Giving, NRM, Temporal',
            'cycles_run': 20,
            'agents_persisted': 3,
            'patterns_detected': 34,
            'confidence': 0.76,
            'key_achievement': 'Complete framework validation'
        },
        {
            'cycle': 39,
            'frameworks': 3,
            'frameworks_names': 'All (at scale)',
            'cycles_run': 100,
            'agents_persisted': 2,  # final checkpoint
            'patterns_detected': 173,
            'confidence': 0.76,  # estimated
            'key_achievement': 'Oscillating attractor discovered'
        },
        {
            'cycle': 40,
            'frameworks': 3,
            'frameworks_names': 'All (reproducible)',
            'cycles_run': 100,
            'agents_persisted': 2,
            'patterns_detected': 142,
            'confidence': 0.76,  # estimated
            'key_achievement': 'Reproducibility validated'
        }
    ]

    # Write CSV
    output_file = OUTPUT_DIR / "figure4_framework_progression.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=progression_data[0].keys())
        writer.writeheader()
        writer.writerows(progression_data)

    print(f"✅ Figure 4 data saved: {output_file}")
    print(f"   Progression: 1/3 → 2/3 → 3/3 frameworks")
    print(f"   Scale: 20 → 20 → 20 → 100 → 100 cycles")
    print(f"   Patterns: 0 → 0 → 34 → 173 → 142")

def generate_summary_statistics():
    """Generate summary statistics table."""
    print("\nGenerating Summary Statistics...")

    cycles = list(range(10, 101, 10))
    run1_data = load_checkpoint_data("longterm_1761111010", cycles)
    run2_data = load_checkpoint_data("longterm_1761111440", cycles)

    import statistics

    # Agent statistics
    run1_agents = run1_data['agent_counts']
    run2_agents = run2_data['agent_counts']

    # Pattern statistics
    run1_patterns = run1_data['pattern_counts']
    run2_patterns = run2_data['pattern_counts']

    summary = {
        'Run 1': {
            'Mean Agents': statistics.mean(run1_agents),
            'Std Agents': statistics.stdev(run1_agents),
            'Min Agents': min(run1_agents),
            'Max Agents': max(run1_agents),
            'Final Patterns': run1_patterns[-1],
            'Pattern Rate': run1_patterns[-1] / 100.0  # patterns per cycle
        },
        'Run 2': {
            'Mean Agents': statistics.mean(run2_agents),
            'Std Agents': statistics.stdev(run2_agents),
            'Min Agents': min(run2_agents),
            'Max Agents': max(run2_agents),
            'Final Patterns': run2_patterns[-1],
            'Pattern Rate': run2_patterns[-1] / 100.0
        }
    }

    # Write CSV
    output_file = OUTPUT_DIR / "summary_statistics.csv"
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Run 1', 'Run 2', 'Difference'])

        for metric in summary['Run 1'].keys():
            val1 = summary['Run 1'][metric]
            val2 = summary['Run 2'][metric]
            diff = abs(val2 - val1)
            writer.writerow([metric, f"{val1:.2f}", f"{val2:.2f}", f"{diff:.2f}"])

    print(f"✅ Summary statistics saved: {output_file}")
    print(f"   All data files ready for visualization")

def main():
    """Generate all figure data files."""
    print("="*70)
    print("GENERATING PUBLICATION-READY FIGURE DATA")
    print("="*70)
    print()

    try:
        generate_figure1_oscillating_attractor()
        generate_figure2_learning_curves()
        generate_figure3_reproducibility()
        generate_figure4_framework_validation()
        generate_summary_statistics()

        print()
        print("="*70)
        print("ALL FIGURE DATA GENERATED SUCCESSFULLY")
        print("="*70)
        print(f"Output directory: {OUTPUT_DIR}")
        print()
        print("Files created:")
        for file in OUTPUT_DIR.glob("*.csv"):
            print(f"  - {file.name}")

    except Exception as e:
        print(f"\n❌ Error generating figures: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
