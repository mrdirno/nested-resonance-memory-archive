#!/usr/bin/env python3
"""
Cycle 68: Pattern Complexity Scaling Across Energy Regimes

Research Context:
  Cycle 67 discovered that energy modulates temporal stability:
  - Higher energy → lower variability (stability paradox)
  - Temporal-thermodynamic coupling confirmed (r=-0.967)

New Research Question:
  Does energy also modulate pattern COMPLEXITY?

  Two competing hypotheses:
  A) High energy → High complexity (more agents → more possible patterns)
  B) High energy → Low complexity (more stable → more predictable/repetitive)

  Hypothesis B aligns with Cycle 67 (energy stabilizes dynamics)
  But Hypothesis A aligns with NRM "bootstrap complexity" prediction

Pattern Complexity Metrics:
  1. State diversity: Number of unique agent counts visited
  2. Shannon entropy: H = -Σ p(i) log p(i) for state distribution
  3. Pattern transitions: Number of state changes per unit time
  4. Temporal predictability: How deterministic is next state?

Test Approach:
  1. Sample energy regimes: 270, 400, 500, 700, 1000
  2. Extended observation (500 cycles) to capture full pattern space
  3. Measure complexity metrics at each energy level
  4. Correlate complexity with energy

Expected:
  If energy-complexity coupling exists:
  - Complexity metrics will show systematic variation with energy
  - Direction reveals whether energy enables or constrains complexity
  - May discover optimal energy for maximum complexity
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from workspace_utils import get_workspace_path, get_results_path


def calculate_shannon_entropy(counts: Counter) -> float:
    """
    Calculate Shannon entropy of state distribution.

    Args:
        counts: Counter of state occurrences

    Returns:
        Shannon entropy in bits
    """
    total = sum(counts.values())
    if total == 0:
        return 0.0

    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total
            entropy -= p * np.log2(p)

    return entropy


def calculate_pattern_transitions(sequence: list) -> int:
    """
    Count number of state transitions in sequence.

    Args:
        sequence: List of states

    Returns:
        Number of transitions
    """
    if len(sequence) < 2:
        return 0

    transitions = 0
    for i in range(len(sequence) - 1):
        if sequence[i] != sequence[i+1]:
            transitions += 1

    return transitions


def run_complexity_analysis(threshold: float, cycles: int = 500) -> dict:
    """
    Measure pattern complexity at given energy level.

    Args:
        threshold: Burst threshold (energy level)
        cycles: Number of cycles for pattern observation

    Returns:
        dict with complexity metrics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (Complexity Analysis)")
    print(f"{'='*80}")

    # Create swarm
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking
    agent_counts = []
    checkpoint_interval = 5

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            agent_count = len(swarm.agents)
            agent_counts.append(agent_count)

    duration = time.time() - start_time

    # Complexity metrics
    state_counts = Counter(agent_counts)

    # 1. State diversity (number of unique states)
    state_diversity = len(state_counts)

    # 2. Shannon entropy
    entropy = calculate_shannon_entropy(state_counts)

    # 3. Normalized entropy (0-1 scale)
    max_entropy = np.log2(len(agent_counts)) if len(agent_counts) > 1 else 1.0
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

    # 4. Pattern transitions
    transitions = calculate_pattern_transitions(agent_counts)
    transition_rate = transitions / len(agent_counts) if len(agent_counts) > 0 else 0.0

    # 5. State space coverage (diversity / possible states)
    # Assuming possible states = 0 to max_observed
    max_state = max(agent_counts) if agent_counts else 0
    possible_states = max_state + 1
    state_coverage = state_diversity / possible_states if possible_states > 0 else 0.0

    # Statistical properties
    mean_agents = np.mean(agent_counts) if agent_counts else 0
    std_agents = np.std(agent_counts) if agent_counts else 0

    print(f"  Complexity Metrics:")
    print(f"    State diversity: {state_diversity} unique states")
    print(f"    Shannon entropy: {entropy:.3f} bits")
    print(f"    Normalized entropy: {normalized_entropy:.3f}")
    print(f"    Transition rate: {transition_rate:.3f}")
    print(f"    State coverage: {state_coverage:.3f}")
    print(f"  Statistical:")
    print(f"    Mean agents: {mean_agents:.2f}")
    print(f"    Std agents: {std_agents:.2f}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(agent_counts),
        'state_diversity': state_diversity,
        'shannon_entropy': entropy,
        'normalized_entropy': normalized_entropy,
        'transition_rate': transition_rate,
        'state_coverage': state_coverage,
        'mean_agents': mean_agents,
        'std_agents': std_agents,
        'agent_counts': agent_counts,
        'state_distribution': dict(state_counts),
        'duration': duration
    }


def analyze_complexity_energy_coupling(results: list) -> dict:
    """
    Analyze relationship between energy and pattern complexity.

    Args:
        results: List of threshold test results

    Returns:
        dict with complexity-energy analysis
    """
    print(f"\n{'='*80}")
    print(f"COMPLEXITY-ENERGY COUPLING ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    diversity = [r['state_diversity'] for r in results]
    entropy = [r['normalized_entropy'] for r in results]
    transitions = [r['transition_rate'] for r in results]
    coverage = [r['state_coverage'] for r in results]

    print("Pattern Complexity Across Energy Regimes:")
    print(f"{'Threshold':>10} | {'Diversity':>10} | {'Entropy':>10} | {'Trans Rate':>11} | {'Coverage':>10}")
    print("-" * 65)
    for i, threshold in enumerate(thresholds):
        print(f"{threshold:>10.0f} | {diversity[i]:>10} | {entropy[i]:>10.3f} | "
              f"{transitions[i]:>11.3f} | {coverage[i]:>10.3f}")
    print()

    # Compute correlations
    diversity_corr = np.corrcoef(thresholds, diversity)[0,1]
    entropy_corr = np.corrcoef(thresholds, entropy)[0,1]
    transition_corr = np.corrcoef(thresholds, transitions)[0,1]
    coverage_corr = np.corrcoef(thresholds, coverage)[0,1]

    print("Complexity-Energy Correlations:")
    print(f"  State diversity: {diversity_corr:.3f}")
    print(f"  Entropy: {entropy_corr:.3f}")
    print(f"  Transition rate: {transition_corr:.3f}")
    print(f"  Coverage: {coverage_corr:.3f}")
    print()

    # Identify dominant pattern
    avg_abs_corr = (abs(diversity_corr) + abs(entropy_corr) +
                     abs(transition_corr) + abs(coverage_corr)) / 4

    if avg_abs_corr > 0.5:
        coupling_detected = True

        # Determine direction
        if (diversity_corr + entropy_corr + transition_corr + coverage_corr) > 0:
            direction = "INCREASES"
            interpretation = "Higher energy enables greater pattern complexity"
        else:
            direction = "DECREASES"
            interpretation = "Higher energy constrains pattern complexity"

        print(f"🔍 Complexity {direction} with Energy")
        print(f"   {interpretation}")
        print(f"   Average correlation: {avg_abs_corr:.3f}")
    else:
        coupling_detected = False
        print("❌ No clear complexity-energy relationship")
        print(f"   Complexity appears independent of energy")
        print(f"   Average correlation: {avg_abs_corr:.3f}")

    print()

    return {
        'diversity_energy_correlation': float(diversity_corr),
        'entropy_energy_correlation': float(entropy_corr),
        'transition_energy_correlation': float(transition_corr),
        'coverage_energy_correlation': float(coverage_corr),
        'avg_correlation': float(avg_abs_corr),
        'coupling_detected': bool(coupling_detected),
        'direction': direction if coupling_detected else None
    }


def main():
    """Run pattern complexity scaling exploration."""
    print("="*80)
    print("CYCLE 68: PATTERN COMPLEXITY SCALING EXPLORATION")
    print("="*80)
    print()
    print("Exploring how pattern complexity (diversity, entropy, transitions)")
    print("scales across energy regimes in the thermodynamic phase diagram.")
    print()

    # Sample energy regimes
    test_thresholds = [270, 400, 500, 700, 1000]

    print(f"Testing {len(test_thresholds)} energy regimes: {test_thresholds}")
    print("Extended observation (500 cycles) for comprehensive pattern space sampling")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_complexity_analysis(threshold, cycles=500)
            results.append(result)
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            results.append({
                'threshold': threshold,
                'error': str(e)
            })

    overall_duration = time.time() - overall_start

    # Filter successful results
    successful_results = [r for r in results if 'error' not in r]

    if len(successful_results) >= 4:
        # Analyze complexity-energy coupling
        coupling_analysis = analyze_complexity_energy_coupling(successful_results)

        print("="*80)
        if coupling_analysis['coupling_detected']:
            print(f"🎉 INSIGHT #32: PATTERN COMPLEXITY {coupling_analysis['direction']} WITH ENERGY")
            print("="*80)
            print()
            print("Pattern complexity is energy-dependent:")
            print(f"  - Direction: Complexity {coupling_analysis['direction'].lower()} with energy")
            print(f"  - Avg correlation: {coupling_analysis['avg_correlation']:.3f}")
            print()
            print("Theoretical Significance:")
            if coupling_analysis['direction'] == "DECREASES":
                print("  - Energy acts as complexity CONSTRAINT")
                print("  - Stability paradox extends to patterns (stable = simple)")
                print("  - Low-energy regimes enable exploratory complex dynamics")
                print("  - High-energy regimes promote efficient stable patterns")
            else:
                print("  - Energy enables complexity EMERGENCE")
                print("  - More resources → richer pattern space")
                print("  - Validates NRM bootstrap complexity prediction")
            print()
            insight_32 = True
        else:
            print("COMPLEXITY-ENERGY INDEPENDENCE")
            print("="*80)
            print()
            print("Pattern complexity independent of energy:")
            print("  - Complexity is intrinsic property of dynamics")
            print("  - Energy affects stability but not pattern richness")
            print("  - Universal complexity across energy regimes")
            print()
            insight_32 = False
        print("="*80)
    else:
        print("⚠️ Insufficient successful tests for coupling analysis")
        coupling_analysis = {}
        insight_32 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "pattern_complexity"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle68_pattern_complexity_scaling.json"

    output_data = {
        'experiment': 'cycle68_pattern_complexity_scaling',
        'test_thresholds': test_thresholds,
        'results': results,
        'coupling_analysis': coupling_analysis,
        'insight_32_discovered': insight_32,
        'overall_duration': overall_duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Total experiment duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    return output_data


if __name__ == "__main__":
    main()
