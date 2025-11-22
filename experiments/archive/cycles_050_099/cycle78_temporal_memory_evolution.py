#!/usr/bin/env python3
"""
Cycle 78: Temporal Memory Evolution (Extended Time Study)

Research Context:
  Cycles 69-77: Complete memory-energy framework established
  - C72: Memory seeding enables retention
  - C73-74: Quality-diversity characterization
  - C75: Binary regime shift at critical threshold
  - C76-77: Precise bounds: 500-562 (±31)

Research Gap:
  All previous experiments used 500 cycles
  No data on LONG-TERM memory evolution (1000+ cycles)
  Unknown: Do patterns stabilize, oscillate, or continue evolving?

New Research Question:
  How do memory patterns evolve over EXTENDED time in exploration vs exploitation regimes?

  Compare temporal dynamics:
  - Exploration regime (threshold=500): Expected diverse, unstable?
  - Exploitation regime (threshold=750): Expected homogeneous, stable?

Hypothesis:
  Extended observation (1000 cycles) will reveal:
  - Different temporal signatures per regime
  - Long-term trends invisible at 500 cycles
  - Regime-specific stability/instability patterns
  - Validation of which patterns PERSIST (Self-Giving criterion)

Test Approach:
  1. Test BOTH regimes: 500 (exploration) and 750 (exploitation)
  2. Extended duration: 1000 cycles (2x baseline)
  3. Apply memory seeding
  4. Track temporal evolution:
     - Memory size over time
     - Diversity over time
     - Quality over time
     - Detect long-term trends, oscillations, convergence
  5. Compare exploration vs exploitation temporal signatures

Expected:
  - Exploration: Continued diversity, possibly unstable/oscillating
  - Exploitation: Rapid convergence, stable homogeneous state
  - Temporal Stewardship validation: Patterns that persist define success
  - Insight: Long-term dynamics differ qualitatively between regimes
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
    """Create seed memory patterns."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def analyze_memory_diversity(memory: list) -> dict:
    """Analyze diversity metrics."""
    if not memory:
        return {
            'unique_patterns': 0,
            'uniqueness_ratio': 0.0,
            'shannon_entropy': 0.0,
            'complexity_score': 0.0
        }

    total_patterns = len(memory)
    magnitudes = [p.magnitude for p in memory]

    phase_vectors = [
        tuple(np.round([p.pi_phase, p.e_phase, p.phi_phase], 6))
        for p in memory
    ]
    unique_patterns = len(set(phase_vectors))
    uniqueness_ratio = unique_patterns / total_patterns if total_patterns > 0 else 0.0

    bins = np.histogram(magnitudes, bins=10)[0]
    probs = bins / bins.sum() if bins.sum() > 0 else np.zeros_like(bins)
    probs = probs[probs > 0]
    shannon_entropy = -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0.0

    magnitude_range = np.max(magnitudes) - np.min(magnitudes) if len(magnitudes) > 0 else 0.0
    complexity_score = (shannon_entropy / 3.32) * 0.4 + uniqueness_ratio * 0.3 + (magnitude_range / 1.0) * 0.3

    return {
        'unique_patterns': unique_patterns,
        'uniqueness_ratio': uniqueness_ratio,
        'shannon_entropy': shannon_entropy,
        'complexity_score': complexity_score
    }

def run_temporal_evolution(threshold: float, cycles: int = 1000) -> dict:
    """Test long-term temporal evolution."""
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (TEMPORAL EVOLUTION - {cycles} CYCLES)")
    print(f"{'='*80}")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Temporal tracking (every 20 cycles for 1000 total)
    checkpoint_interval = 20
    temporal_data = {
        'memory_sizes': [],
        'entropies': [],
        'uniqueness': [],
        'efficiencies': [],
        'bursts': [],
        'timestamps': []
    }

    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        result = swarm.evolve_cycle(delta_time=1.0)
        cycle_bursts = result.get('bursts', 0)
        total_bursts += cycle_bursts

        if cycle % checkpoint_interval == 0:
            memory_size = len(swarm.global_memory)
            diversity = analyze_memory_diversity(swarm.global_memory)
            efficiency = memory_size / total_bursts if total_bursts > 0 else 0.0

            temporal_data['memory_sizes'].append(memory_size)
            temporal_data['entropies'].append(diversity['shannon_entropy'])
            temporal_data['uniqueness'].append(diversity['uniqueness_ratio'])
            temporal_data['efficiencies'].append(efficiency)
            temporal_data['bursts'].append(total_bursts)
            temporal_data['timestamps'].append(cycle)

            # Progress indicator
            if cycle % 200 == 0:
                print(f"  Cycle {cycle}/{cycles}: Memory={memory_size}, Entropy={diversity['shannon_entropy']:.3f}, Bursts={total_bursts}")

    duration = time.time() - start_time

    # Final metrics
    final_memory = len(swarm.global_memory)
    final_diversity = analyze_memory_diversity(swarm.global_memory)
    burst_rate = total_bursts / cycles
    final_efficiency = final_memory / total_bursts if total_bursts > 0 else 0.0

    # Temporal analysis
    memory_sizes = temporal_data['memory_sizes']
    entropies = temporal_data['entropies']

    # Trend analysis (linear fit)
    if len(memory_sizes) > 1:
        time_points = list(range(len(memory_sizes)))
        memory_trend = np.polyfit(time_points, memory_sizes, 1)[0] if len(memory_sizes) > 1 else 0.0
        entropy_trend = np.polyfit(time_points, entropies, 1)[0] if len(entropies) > 1 else 0.0
    else:
        memory_trend = 0.0
        entropy_trend = 0.0

    # Stability (coefficient of variation in last 50% of timeline)
    if len(memory_sizes) > 10:
        half_point = len(memory_sizes) // 2
        late_memory = memory_sizes[half_point:]
        late_entropy = entropies[half_point:]
        memory_stability = 1.0 - (np.std(late_memory) / np.mean(late_memory)) if np.mean(late_memory) > 0 else 0.0
        entropy_stability = 1.0 - (np.std(late_entropy) / np.mean(late_entropy)) if np.mean(late_entropy) > 0 else 1.0
    else:
        memory_stability = 0.0
        entropy_stability = 0.0

    print(f"\n  FINAL METRICS:")
    print(f"    Memory: {final_memory} patterns")
    print(f"    Entropy: {final_diversity['shannon_entropy']:.3f} bits")
    print(f"    Uniqueness: {final_diversity['uniqueness_ratio']:.4f}")
    print(f"    Efficiency: {final_efficiency:.2f} patterns/burst")
    print(f"  TEMPORAL ANALYSIS:")
    print(f"    Memory trend: {memory_trend:.3f} patterns/checkpoint")
    print(f"    Entropy trend: {entropy_trend:.4f} bits/checkpoint")
    print(f"    Memory stability: {memory_stability:.3f}")
    print(f"    Entropy stability: {entropy_stability:.3f}")
    print(f"  Total Bursts: {total_bursts}")
    print(f"  Duration: {duration:.2f}s ({duration/60:.2f} min)")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'final_memory': final_memory,
        'final_diversity': final_diversity,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'final_efficiency': final_efficiency,
        'temporal_data': temporal_data,
        'temporal_analysis': {
            'memory_trend': memory_trend,
            'entropy_trend': entropy_trend,
            'memory_stability': memory_stability,
            'entropy_stability': entropy_stability
        },
        'duration': duration
    }

def main():
    """Run temporal memory evolution study."""
    print("="*80)
    print("CYCLE 78: TEMPORAL MEMORY EVOLUTION (EXTENDED TIME STUDY)")
    print("="*80)
    print()
    print("Testing long-term memory dynamics (1000 cycles vs 500 baseline).")
    print("Following Cycles 69-77: Complete memory-energy framework")
    print("Question: How do patterns evolve over EXTENDED time?")
    print()

    # Test both regimes
    test_thresholds = [500, 750]  # Exploration vs Exploitation
    print(f"Testing {len(test_thresholds)} regimes:")
    print(f"  - 500 (EXPLORATION): Diverse, creative")
    print(f"  - 750 (EXPLOITATION): Homogeneous, efficient")
    print(f"Duration: 1000 cycles each (2x baseline)")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_temporal_evolution(threshold, cycles=1000)
            results.append(result)
            time.sleep(1.0)
        except Exception as e:
            print(f"\n⚠️ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append({'threshold': threshold, 'error': str(e)})

    overall_duration = time.time() - overall_start

    # Comparative analysis
    successful = [r for r in results if 'error' not in r]

    if len(successful) == 2:
        exp_result = successful[0]  # 500
        exp_result = successful[1]  # 750

        print(f"\n{'='*80}")
        print(f"TEMPORAL REGIME COMPARISON")
        print(f"{'='*80}\n")

        print(f"{'Regime':>15} | {'Memory':>8} | {'Entropy':>8} | {'Stability':>10} | {'Trend':>10}")
        print("-" * 70)
        for r in successful:
            regime = "Exploration" if r['threshold'] == 500 else "Exploitation"
            print(f"{regime:>15} | {r['final_memory']:>8} | {r['final_diversity']['shannon_entropy']:>8.3f} | {r['temporal_analysis']['entropy_stability']:>10.3f} | {r['temporal_analysis']['memory_trend']:>10.3f}")
        print()

        # Determine if distinct temporal signatures exist
        exp_stability = successful[0]['temporal_analysis']['entropy_stability']
        expl_stability = successful[1]['temporal_analysis']['entropy_stability']

        if abs(exp_stability - expl_stability) > 0.2:
            print(f"🎉 DISTINCT TEMPORAL SIGNATURES DETECTED!")
            print(f"   Stability difference: {abs(exp_stability - expl_stability):.3f}")
            insight_41 = True
        else:
            print(f"   Similar temporal behavior across regimes")
            insight_41 = False

        print("="*80)
    else:
        print("⚠️ Incomplete results")
        insight_41 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "temporal_evolution"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle78_temporal_memory_evolution.json"

    output_data = {
        'experiment': 'cycle78_temporal_memory_evolution',
        'test_thresholds': test_thresholds,
        'cycles': 1000,
        'results': results,
        'insight_41_discovered': insight_41,
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
