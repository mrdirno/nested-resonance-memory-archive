#!/usr/bin/env python3
"""
Cycle 496: 800-Cycle Anomaly Investigation - High-Resolution Temporal Mapping

RESEARCH QUESTION: Is the 800-cycle F-ratio spike (F=3.32) in C495 a real
oscillatory/recharge phenomenon or a statistical artifact?

EXPERIMENTAL DESIGN:
- Focus on 700-900 cycle window (200-cycle range around anomaly)
- High-resolution sampling: Every 20 cycles (10× finer than C495)
- Statistical power: 8 agents per condition (vs 3 in C495)
- Total: 16 agents × 200 cycles = 3,200 evolution steps
- Expected runtime: ~35 seconds

HYPOTHESES:
H1 (Oscillatory): Reproducible spike with consistent timing (validates oscillation)
H2 (Recharge): Variable spike timing across agents (composition-decomposition bursts)
H3 (Artifact): No spike, F decays monotonically (statistical noise in C495)

SUCCESS CRITERIA:
- H1: Spike appears at 780-820 cycles in ≥50% of runs, amplitude ≥2.5
- H2: Spikes appear with variable timing (σ_t > 30 cycles), amplitude ≥2.0
- H3: F-ratio decreases monotonically, no spikes > 2.0

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-29
License: GPL-3.0
"""

import sys
import json
import time
import numpy as np
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code.bridge.transcendental_bridge import TranscendentalBridge
from code.reality.system_monitor import SystemMonitor
from code.fractal.fractal_agent import FractalAgent

# Configuration
CYCLES_START = 700
CYCLES_END = 900
CYCLES_TOTAL = CYCLES_END - CYCLES_START  # 200 cycles
SAMPLE_INTERVAL = 20  # Every 20 cycles (10× finer than C495)
AGENTS_PER_CONDITION = 8  # 2.67× more than C495 for statistical power
OUTPUT_DIR = Path(__file__).parent.parent.parent / "data" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_phase_reality_correlation(agent, reality_metrics):
    """
    Compute correlation between agent's phase state and current reality.

    Returns:
        float: Normalized distance (0=perfect match, >0=autonomy)
    """
    phase_magnitude = np.linalg.norm([
        agent.phase_state['pi_oscillator'],
        agent.phase_state['e_oscillator'],
        agent.phase_state['phi_oscillator']
    ])

    reality_magnitude = np.linalg.norm([
        reality_metrics.get('cpu_percent', 0),
        reality_metrics.get('memory_percent', 0),
        reality_metrics.get('disk_io_percent', 0)
    ])

    if reality_magnitude == 0:
        return 0.0

    return abs(phase_magnitude - reality_magnitude) / reality_magnitude


def evolve_agent_to_target_cycles(agent, monitor, target_cycles, sample_interval):
    """
    Evolve an agent to target_cycles, recording correlations every sample_interval.

    NOTE: Starts from cycle 0 and evolves to target_cycles. To investigate
    the 800-cycle window, we need to evolve agents for 700-900 cycles total.
    """
    correlations = []

    for cycle in range(0, target_cycles, sample_interval):
        # Get current reality
        reality = monitor.get_snapshot()
        reality_metrics = {
            'cpu_percent': reality['cpu']['percent'],
            'memory_percent': reality['memory']['percent'],
            'disk_io_percent': min(reality['disk']['read_percent'] +
                                 reality['disk']['write_percent'], 100.0)
        }

        # Evolve agent
        agent.evolve(sample_interval, reality_metrics)

        # Compute correlation
        corr = compute_phase_reality_correlation(agent, reality_metrics)
        correlations.append([cycle, corr])

    return correlations


def compute_f_ratio(uniform_slopes, highvar_slopes):
    """Compute F-ratio (variance ratio) between conditions."""
    if len(uniform_slopes) < 2 or len(highvar_slopes) < 2:
        return 0.0

    # Between-group variance
    grand_mean = np.mean(uniform_slopes + highvar_slopes)
    n1, n2 = len(uniform_slopes), len(highvar_slopes)
    between_var = (n1 * (np.mean(uniform_slopes) - grand_mean)**2 +
                   n2 * (np.mean(highvar_slopes) - grand_mean)**2) / 1

    # Within-group variance
    within_var = (np.var(uniform_slopes, ddof=1) + np.var(highvar_slopes, ddof=1)) / 2

    if within_var == 0:
        return 0.0

    return between_var / within_var


def main():
    print("=" * 70)
    print("CYCLE 496: 800-CYCLE ANOMALY INVESTIGATION")
    print("=" * 70)
    print(f"Target window: {CYCLES_START}-{CYCLES_END} cycles")
    print(f"Evolution total: {CYCLES_TOTAL} cycles per agent")
    print(f"Sample interval: {SAMPLE_INTERVAL} cycles")
    print(f"Agents per condition: {AGENTS_PER_CONDITION}")
    print(f"Total evolution steps: {AGENTS_PER_CONDITION * 2 * (CYCLES_TOTAL // SAMPLE_INTERVAL)}")
    print()

    start_time = time.time()

    # Initialize infrastructure
    bridge = TranscendentalBridge()
    monitor = SystemMonitor()

    # Initial reality snapshot for agent initialization
    initial_reality = monitor.get_snapshot()

    # Create agents
    print("Creating agents...")
    agents = []

    # Uniform energy condition
    for i in range(AGENTS_PER_CONDITION):
        agent = FractalAgent(
            agent_id=f"uniform_{i}",
            bridge=bridge,
            initial_reality=initial_reality,
            initial_energy=100.0  # Uniform
        )
        agents.append(('uniform', agent))

    # High-variance condition
    energy_levels = [50.0, 75.0, 100.0, 125.0, 150.0]
    for i in range(AGENTS_PER_CONDITION):
        agent = FractalAgent(
            agent_id=f"highvar_{i}",
            bridge=bridge,
            initial_reality=initial_reality,
            initial_energy=energy_levels[i % len(energy_levels)]
        )
        agents.append(('high_variance', agent))

    print(f"  Created {len(agents)} agents\n")

    # Run experiment
    results = {'uniform': [], 'high_variance': []}

    for condition, agent in agents:
        print(f"  Evolving {agent.agent_id} (E={agent.energy:.1f})...")

        # Evolve to CYCLES_END to capture full 700-900 window
        correlations = evolve_agent_to_target_cycles(
            agent, monitor, CYCLES_END, SAMPLE_INTERVAL
        )

        # Extract 700-900 cycle window only
        window_correlations = [
            [t, c] for t, c in correlations if CYCLES_START <= t <= CYCLES_END
        ]

        # Compute autonomy slope for window
        times = np.array([c[0] for c in window_correlations])
        corrs = np.array([c[1] for c in window_correlations])
        slope = np.polyfit(times, corrs, 1)[0]

        results[condition].append({
            'agent_id': agent.agent_id,
            'energy': agent.energy,
            'correlations': window_correlations,
            'autonomy_slope': float(slope)
        })

        print(f"    Slope: {slope:.6f}")

    # Statistical analysis
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    uniform_slopes = [a['autonomy_slope'] for a in results['uniform']]
    highvar_slopes = [a['autonomy_slope'] for a in results['high_variance']]

    print(f"{'Condition':<20} {'Mean Slope':>15} {'Median':>10} {'Std':>10}")
    print("-" * 70)
    print(f"{'Uniform':<20} {np.mean(uniform_slopes):>15.6f} "
          f"{np.median(uniform_slopes):>10.6f} {np.std(uniform_slopes):>10.6f}")
    print(f"{'High-Variance':<20} {np.mean(highvar_slopes):>15.6f} "
          f"{np.median(highvar_slopes):>10.6f} {np.std(highvar_slopes):>10.6f}")

    f_ratio = compute_f_ratio(uniform_slopes, highvar_slopes)
    mean_diff = abs(np.mean(uniform_slopes) - np.mean(highvar_slopes))

    print(f"\nStatistical Tests:")
    print(f"  F-ratio: {f_ratio:.6f}")
    print(f"  Mean difference: {mean_diff:.6e}")

    # Hypothesis evaluation
    print(f"\nHYPOTHESIS EVALUATION:")
    print(f"  H1 (Oscillatory): Check if F-ratio spike appears at 780-820 cycles")
    print(f"  H2 (Recharge): Check if spikes have variable timing across agents")
    print(f"  H3 (Artifact): Check if F-ratio decreases monotonically")
    print(f"\n  → To evaluate, compute F-ratio at each 20-cycle interval")
    print(f"  → Compare to C495 spike (F=3.32 at 800 cycles)")

    # Save results
    elapsed = time.time() - start_time
    print(f"\nExperiment completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print("=" * 70)

    output = {
        'experiment': 'cycle496_anomaly_investigation',
        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'parameters': {
            'cycles_start': CYCLES_START,
            'cycles_end': CYCLES_END,
            'cycles_total': CYCLES_TOTAL,
            'sample_interval': SAMPLE_INTERVAL,
            'agents_per_condition': AGENTS_PER_CONDITION
        },
        'conditions': [
            {'condition': 'uniform', 'agents': results['uniform']},
            {'condition': 'high_variance', 'agents': results['high_variance']}
        ],
        'statistical_test': {
            'f_ratio': float(f_ratio),
            'mean_difference': float(mean_diff),
            'uniform_slopes': uniform_slopes,
            'highvar_slopes': highvar_slopes
        },
        'runtime_seconds': elapsed
    }

    output_path = OUTPUT_DIR / "cycle496_anomaly_investigation.json"
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
