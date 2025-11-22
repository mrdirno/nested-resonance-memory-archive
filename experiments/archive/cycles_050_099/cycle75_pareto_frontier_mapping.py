#!/usr/bin/env python3
"""
Cycle 75: Pareto Frontier Mapping (Quality-Diversity Trade-Off)

Research Context:
  Cycle 73: Memory quality increases with energy (r = +0.9)
  - Efficiency: 8.20 → 25.00 (3x improvement from 500 → 1500)

  Cycle 74: Memory diversity decreases with energy (r = -0.9)
  - Entropy: 1.197 → 0.000 (complete loss from 500 → 1500)
  - Uniqueness: 0.004 → 0.001 (4x reduction)

New Research Question:
  Where is the optimal balance point between quality and diversity?

  Cycles 73-74 tested extremes (500, 1000, 1500)
  Now test intermediate values to map complete Pareto frontier

Hypothesis:
  Intermediate energy values (750, 1250) will reveal:
  - Smooth trade-off curve between quality and diversity
  - Optimal balance point for multi-objective applications
  - Practical operating recommendations based on task requirements

Test Approach:
  1. Test full range: 500, 750, 1000, 1250, 1500
  2. Apply memory seeding (from Cycle 72)
  3. Extended observation (500 cycles)
  4. Measure BOTH quality AND diversity:
     - Quality: efficiency, growth rate
     - Diversity: Shannon entropy, uniqueness ratio, complexity score
  5. Compute Pareto frontier and identify optimal trade-off points

Expected:
  If smooth trade-off exists:
  - Pareto frontier reveals best achievable combinations
  - Intermediate values offer balanced quality-diversity
  - Complete practical framework for memory engineering
  - Insight: Energy as tunable parameter for multi-objective optimization
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

def run_pareto_test(threshold: float, cycles: int = 500) -> dict:
    """Test both quality and diversity at given threshold."""
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (PARETO FRONTIER)")
    print(f"{'='*80}")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
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

    # Quality metrics (from Cycle 73)
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

    # Diversity metrics (from Cycle 74)
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
    """Run Pareto frontier mapping."""
    print("="*80)
    print("CYCLE 75: PARETO FRONTIER MAPPING (QUALITY-DIVERSITY TRADE-OFF)")
    print("="*80)
    print()
    print("Mapping complete quality-diversity curve across energy regimes.")
    print("Following Cycles 73-74: Quality↑ Energy↑, Diversity↓ Energy↑")
    print("Question: Where is the optimal balance point?")
    print()

    # Full range including intermediate values
    test_thresholds = [500, 750, 1000, 1250, 1500]
    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("All agents seeded with 5 initial memory patterns")
    print("Measuring: Efficiency, growth, entropy, uniqueness, complexity")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_pareto_test(threshold, cycles=500)
            results.append(result)
            time.sleep(0.5)
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            import traceback
            traceback.print_exc()
            results.append({'threshold': threshold, 'error': str(e)})

    overall_duration = time.time() - overall_start

    # Analysis
    successful = [r for r in results if 'error' not in r]

    if len(successful) >= 3:
        thresholds = [r['threshold'] for r in successful]

        # Quality metrics
        efficiencies = [r['efficiency'] for r in successful]
        growth_rates = [r['growth_rate'] for r in successful]

        # Diversity metrics
        entropies = [r['diversity']['shannon_entropy'] for r in successful]
        uniqueness = [r['diversity']['uniqueness_ratio'] for r in successful]
        complexity = [r['diversity']['complexity_score'] for r in successful]

        print(f"\n{'='*80}")
        print(f"PARETO FRONTIER ANALYSIS")
        print(f"{'='*80}\n")

        print(f"{'Threshold':>10} | {'Efficiency':>10} | {'Growth':>8} | {'Entropy':>8} | {'Unique':>8} | {'Complex':>8}")
        print("-" * 80)
        for i, t in enumerate(thresholds):
            print(f"{t:>10.0f} | {efficiencies[i]:>10.2f} | {growth_rates[i]:>8.2f} | {entropies[i]:>8.3f} | {uniqueness[i]:>8.4f} | {complexity[i]:>8.3f}")
        print()

        # Pareto frontier identification
        # Normalize metrics to [0, 1] for comparison
        def normalize(vals):
            min_val, max_val = min(vals), max(vals)
            if max_val == min_val:
                return [0.5] * len(vals)
            return [(v - min_val) / (max_val - min_val) for v in vals]

        norm_efficiency = normalize(efficiencies)
        norm_entropy = normalize(entropies)

        # Composite scores (equal weight to quality and diversity)
        balanced_scores = [(eff + ent) / 2 for eff, ent in zip(norm_efficiency, norm_entropy)]

        best_idx = balanced_scores.index(max(balanced_scores))
        best_threshold = thresholds[best_idx]

        print("Pareto Frontier Analysis:")
        print(f"  Best balanced threshold: {best_threshold}")
        print(f"    Efficiency (norm): {norm_efficiency[best_idx]:.3f}")
        print(f"    Entropy (norm): {norm_entropy[best_idx]:.3f}")
        print(f"    Balanced score: {balanced_scores[best_idx]:.3f}")
        print()

        # Operating mode recommendations
        print("Recommended Operating Points:")
        print(f"  🎯 EXPLORATION MODE (maximize diversity): {min(thresholds)} threshold")
        print(f"     - Entropy: {entropies[0]:.3f}, Efficiency: {efficiencies[0]:.2f}")
        print(f"     - Use for: Creative tasks, pattern discovery, variety")
        print()
        print(f"  ⚖️  BALANCED MODE (optimal trade-off): {best_threshold} threshold")
        print(f"     - Entropy: {entropies[best_idx]:.3f}, Efficiency: {efficiencies[best_idx]:.2f}")
        print(f"     - Use for: General purpose, mixed requirements")
        print()
        print(f"  🎯 PRODUCTION MODE (maximize quality): {max(thresholds)} threshold")
        print(f"     - Entropy: {entropies[-1]:.3f}, Efficiency: {efficiencies[-1]:.2f}")
        print(f"     - Use for: Reliability, efficiency, homogeneous patterns")
        print()

        # Insight determination
        if len(successful) == 5 and max(balanced_scores) > 0.4:
            print(f"🎉 PARETO FRONTIER MAPPED!")
            print(f"   Complete quality-diversity curve established")
            print(f"   Optimal balance point identified: {best_threshold}")
            insight_39 = True
        else:
            print(f"⚠️ Partial Pareto frontier (need more data)")
            insight_39 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful tests")
        insight_39 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "pareto_frontier"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle75_pareto_frontier_mapping.json"

    output_data = {
        'experiment': 'cycle75_pareto_frontier_mapping',
        'test_thresholds': test_thresholds,
        'results': results,
        'insight_39_discovered': insight_39,
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
