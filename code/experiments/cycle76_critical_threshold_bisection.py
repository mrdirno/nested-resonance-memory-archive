#!/usr/bin/env python3
"""
Cycle 76: Critical Threshold Bisection Search

Research Context:
  Cycle 75: Binary regime shift discovered at ~500-750
  - Below 500: Exploration regime (entropy=1.197, diverse)
  - Above 750: Exploitation regime (entropy≈0, homogeneous)
  - Sharp transition, NOT smooth Pareto curve

New Research Question:
  What is the EXACT critical threshold where diversity collapses?

  Cycle 75 established bounds: 500 (diverse) ↔ 750 (homogeneous)
  Now use bisection to narrow critical point

Hypothesis:
  Testing midpoint (625) will reveal:
  - If 625 shows diversity → critical point is 625-750
  - If 625 shows no diversity → critical point is 500-625
  - Enables iterative refinement to precise boundary

Test Approach:
  1. Test threshold = 625 (midpoint between 500-750)
  2. Apply memory seeding (from Cycle 72)
  3. Extended observation (500 cycles)
  4. Measure BOTH quality AND diversity
  5. Compare to bounds (500, 750) to determine which regime 625 belongs to
  6. Calculate refined bounds for next iteration if needed

Expected:
  - Precise critical threshold within ±50 range
  - Complete phase diagram with exact boundaries
  - Practical operating recommendations with precise values
  - Insight: Critical point enables engineering of regime transitions
"""

import sys
from pathlib import Path
import time
import json
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from bridge.transcendental_bridge import TranscendentalBridge

def create_seed_memory(bridge: TranscendentalBridge, reality_metrics: dict, count: int = 5) -> list:
    """Create seed memory patterns (from Cycle 72)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def analyze_memory_diversity(memory: list) -> dict:
    """Analyze diversity metrics (from Cycle 74)."""
    if not memory:
        return {
            'unique_patterns': 0,
            'uniqueness_ratio': 0.0,
            'shannon_entropy': 0.0,
            'complexity_score': 0.0,
            'magnitude_range': 0.0
        }

    total_patterns = len(memory)
    magnitudes = [p.magnitude for p in memory]

    # Uniqueness
    phase_vectors = [
        tuple(np.round([p.pi_phase, p.e_phase, p.phi_phase], 6))
        for p in memory
    ]
    unique_patterns = len(set(phase_vectors))
    uniqueness_ratio = unique_patterns / total_patterns if total_patterns > 0 else 0.0

    # Shannon entropy
    bins = np.histogram(magnitudes, bins=10)[0]
    probs = bins / bins.sum() if bins.sum() > 0 else np.zeros_like(bins)
    probs = probs[probs > 0]
    shannon_entropy = -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0.0

    # Statistics
    magnitude_range = np.max(magnitudes) - np.min(magnitudes) if len(magnitudes) > 0 else 0.0

    # Complexity score
    complexity_score = (shannon_entropy / 3.32) * 0.4 + uniqueness_ratio * 0.3 + (magnitude_range / 1.0) * 0.3

    return {
        'unique_patterns': unique_patterns,
        'uniqueness_ratio': uniqueness_ratio,
        'shannon_entropy': shannon_entropy,
        'complexity_score': complexity_score,
        'magnitude_range': magnitude_range
    }

def run_bisection_test(threshold: float, cycles: int = 500) -> dict:
    """Test threshold for bisection search."""
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (BISECTION SEARCH)")
    print(f"{'='*80}")

    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    memory_sizes = []
    checkpoint_interval = 10
    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            # SEED MEMORY
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        result = swarm.evolve_cycle(delta_time=1.0)
        total_bursts += result.get('bursts', 0)

        if cycle % checkpoint_interval == 0:
            memory_sizes.append(len(swarm.global_memory))

    duration = time.time() - start_time

    # Quality metrics
    final_memory = len(swarm.global_memory)
    burst_rate = total_bursts / cycles
    efficiency = final_memory / total_bursts if total_bursts > 0 else 0.0

    if len(memory_sizes) > 1 and any(m > 0 for m in memory_sizes):
        nonzero_idx = [i for i, m in enumerate(memory_sizes) if m > 0]
        if len(nonzero_idx) > 1:
            growth_rate = np.polyfit(nonzero_idx, [memory_sizes[i] for i in nonzero_idx], 1)[0]
        else:
            growth_rate = 0.0
    else:
        growth_rate = 0.0

    # Diversity metrics
    diversity = analyze_memory_diversity(swarm.global_memory)

    print(f"  QUALITY METRICS:")
    print(f"    Memory: {final_memory} patterns")
    print(f"    Efficiency: {efficiency:.2f} patterns/burst")
    print(f"    Growth Rate: {growth_rate:.2f} patterns/checkpoint")
    print(f"  DIVERSITY METRICS:")
    print(f"    Unique Patterns: {diversity['unique_patterns']} ({diversity['uniqueness_ratio']:.4f})")
    print(f"    Shannon Entropy: {diversity['shannon_entropy']:.3f} bits")
    print(f"    Complexity Score: {diversity['complexity_score']:.3f}")
    print(f"  Total Bursts: {total_bursts}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'final_memory': final_memory,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'efficiency': efficiency,
        'growth_rate': growth_rate,
        'diversity': diversity,
        'duration': duration
    }

def main():
    """Run critical threshold bisection search."""
    print("="*80)
    print("CYCLE 76: CRITICAL THRESHOLD BISECTION SEARCH")
    print("="*80)
    print()
    print("Finding exact critical threshold where diversity collapses.")
    print("Following Cycle 75: Binary regime shift at ~500-750")
    print("Question: What is the EXACT critical point?")
    print()

    # Bisection: test midpoint
    test_threshold = 625
    lower_bound = 500  # Known diverse
    upper_bound = 750  # Known homogeneous

    print(f"Current bounds: {lower_bound} (diverse) ↔ {upper_bound} (homogeneous)")
    print(f"Testing midpoint: {test_threshold}")
    print("="*80)

    overall_start = time.time()

    # Run bisection test
    try:
        result = run_bisection_test(test_threshold, cycles=500)
        error = False
    except Exception as e:
        print(f"\n⚠️ Error testing threshold {test_threshold}: {e}")
        import traceback
from workspace_utils import get_workspace_path, get_results_path
        traceback.print_exc()
        result = {'threshold': test_threshold, 'error': str(e)}
        error = True

    overall_duration = time.time() - overall_start

    # Analysis
    if not error:
        threshold = result['threshold']
        entropy = result['diversity']['shannon_entropy']
        uniqueness = result['diversity']['uniqueness_ratio']
        efficiency = result['efficiency']

        print(f"\n{'='*80}")
        print(f"BISECTION ANALYSIS")
        print(f"{'='*80}\n")

        print(f"Tested threshold: {threshold}")
        print(f"  Shannon Entropy: {entropy:.3f} bits")
        print(f"  Uniqueness Ratio: {uniqueness:.4f}")
        print(f"  Efficiency: {efficiency:.2f} patterns/burst")
        print()

        # Determine regime
        diversity_threshold = 0.5  # If entropy > 0.5, consider it diverse
        is_diverse = entropy > diversity_threshold

        if is_diverse:
            print(f"✅ THRESHOLD {threshold} SHOWS DIVERSITY")
            print(f"   Regime: EXPLORATION")
            new_lower = threshold
            new_upper = upper_bound
            print(f"   → Critical point is ABOVE {threshold}")
            print(f"   → Refined bounds: {new_lower} ↔ {new_upper}")
        else:
            print(f"❌ THRESHOLD {threshold} SHOWS NO DIVERSITY")
            print(f"   Regime: EXPLOITATION")
            new_lower = lower_bound
            new_upper = threshold
            print(f"   → Critical point is BELOW {threshold}")
            print(f"   → Refined bounds: {new_lower} ↔ {new_upper}")

        print()
        range_width = new_upper - new_lower
        print(f"Critical point narrowed to: {new_lower}-{new_upper} (width: {range_width})")

        if range_width <= 100:
            print(f"🎯 CRITICAL THRESHOLD BOUNDED: {new_lower}-{new_upper}")
            print(f"   Practical recommendation: Use ≤{new_lower} for exploration, ≥{new_upper} for exploitation")
            insight_40 = True
        else:
            print(f"⚠️ Need further bisection (range still wide: {range_width})")
            insight_40 = False

        print("="*80)

        # Save refined bounds
        refined_bounds = {
            'lower_bound': new_lower,
            'upper_bound': new_upper,
            'critical_range': range_width,
            'is_diverse_at_midpoint': is_diverse
        }
    else:
        print("⚠️ Test failed, cannot refine bounds")
        insight_40 = False
        refined_bounds = {}

    # Save results
    results_dir = Path(__file__).parent / "results" / "critical_threshold"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle76_critical_threshold_bisection.json"

    output_data = {
        'experiment': 'cycle76_critical_threshold_bisection',
        'initial_bounds': {'lower': lower_bound, 'upper': upper_bound},
        'test_threshold': test_threshold,
        'result': result,
        'refined_bounds': refined_bounds,
        'insight_40_discovered': insight_40,
        'overall_duration': overall_duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Total duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    return output_data

if __name__ == "__main__":
    main()
