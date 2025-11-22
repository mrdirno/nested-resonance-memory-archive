#!/usr/bin/env python3
"""
Cycle 74: Memory Diversity & Pattern Quality Analysis

Research Context:
  Cycle 73: Memory quality (efficiency, growth) increases with energy
  - Efficiency: 8.20 → 25.00 (3x improvement from 500 → 1500)
  - Growth rate: 8.65 → 19.31 (2.2x improvement)
  - Optimal memory zone: 500-1500

New Research Question:
  Does energy affect memory DIVERSITY and pattern COMPLEXITY?

  Cycle 73 showed QUALITY increases with energy (efficiency, growth rate)
  Now test if DIVERSITY also increases (pattern variety, complexity distribution)

Hypothesis:
  Higher energy regimes produce MORE DIVERSE memory patterns:
  - More unique patterns (less repetition)
  - Higher Shannon entropy (more variety in pattern types)
  - Wider resonance distribution (more complex patterns)
  - Higher mean pattern complexity

Test Approach:
  1. Test optimal zone: 500, 1000, 1500 (from Cycle 73)
  2. Apply memory seeding (from Cycle 72)
  3. Extended observation (500 cycles)
  4. Measure diversity metrics:
     - Shannon entropy of pattern distribution
     - Pattern uniqueness ratio (unique / total)
     - Resonance strength distribution (mean, std, range)
     - Pattern complexity score (composite metric)

Expected:
  If energy-diversity coupling exists:
  - Shannon entropy increases with energy
  - Uniqueness ratio increases with energy
  - Wider resonance distribution at higher energy
  - Insight: Energy controls memory quality AND diversity
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
from collections import Counter

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
    """Analyze diversity and complexity of memory patterns."""
    if not memory:
        return {
            'total_patterns': 0,
            'unique_patterns': 0,
            'uniqueness_ratio': 0.0,
            'shannon_entropy': 0.0,
            'mean_magnitude': 0.0,
            'std_magnitude': 0.0,
            'min_magnitude': 0.0,
            'max_magnitude': 0.0,
            'magnitude_range': 0.0,
            'complexity_score': 0.0
        }

    total_patterns = len(memory)

    # Extract pattern magnitudes (TranscendentalState has .magnitude attribute)
    magnitudes = [p.magnitude for p in memory]

    # Uniqueness: count distinct phase vectors (proxy for unique patterns)
    # Round phase vectors to 6 decimals and convert to tuples for hashing
    phase_vectors = [
        tuple(np.round([p.pi_phase, p.e_phase, p.phi_phase], 6))
        for p in memory
    ]
    unique_patterns = len(set(phase_vectors))
    uniqueness_ratio = unique_patterns / total_patterns if total_patterns > 0 else 0.0

    # Shannon entropy: distribution of magnitude bins
    bins = np.histogram(magnitudes, bins=10)[0]
    probs = bins / bins.sum() if bins.sum() > 0 else np.zeros_like(bins)
    probs = probs[probs > 0]  # Remove zero probabilities
    shannon_entropy = -np.sum(probs * np.log2(probs)) if len(probs) > 0 else 0.0

    # Magnitude statistics
    mean_magnitude = np.mean(magnitudes)
    std_magnitude = np.std(magnitudes)
    min_magnitude = np.min(magnitudes)
    max_magnitude = np.max(magnitudes)
    magnitude_range = max_magnitude - min_magnitude

    # Complexity score: composite metric (entropy + uniqueness + range)
    # Higher entropy = more variety
    # Higher uniqueness = less repetition
    # Higher range = wider distribution
    complexity_score = (shannon_entropy / 3.32) * 0.4 + uniqueness_ratio * 0.3 + (magnitude_range / 1.0) * 0.3
    # Shannon max = log2(10) = 3.32 for 10 bins
    # Magnitude range max ≈ 1.0 (normalized phase space)

    return {
        'total_patterns': total_patterns,
        'unique_patterns': unique_patterns,
        'uniqueness_ratio': uniqueness_ratio,
        'shannon_entropy': shannon_entropy,
        'mean_magnitude': mean_magnitude,
        'std_magnitude': std_magnitude,
        'min_magnitude': min_magnitude,
        'max_magnitude': max_magnitude,
        'magnitude_range': magnitude_range,
        'complexity_score': complexity_score
    }

def run_diversity_test(threshold: float, cycles: int = 500) -> dict:
    """Test memory diversity at given threshold."""
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (MEMORY DIVERSITY ANALYSIS)")
    print(f"{'='*80}")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    checkpoint_interval = 10
    start_time = time.time()
    total_bursts = 0

    # Track diversity evolution
    diversity_checkpoints = []

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            # SEED MEMORY (from Cycle 72)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        result = swarm.evolve_cycle(delta_time=1.0)
        total_bursts += result.get('bursts', 0)

        if cycle % checkpoint_interval == 0:
            diversity = analyze_memory_diversity(swarm.global_memory)
            diversity_checkpoints.append(diversity)

    duration = time.time() - start_time

    # Final diversity analysis
    final_diversity = analyze_memory_diversity(swarm.global_memory)

    # Diversity evolution metrics
    if diversity_checkpoints:
        entropies = [d['shannon_entropy'] for d in diversity_checkpoints]
        uniqueness = [d['uniqueness_ratio'] for d in diversity_checkpoints]
        complexity = [d['complexity_score'] for d in diversity_checkpoints]

        entropy_growth = np.polyfit(range(len(entropies)), entropies, 1)[0] if len(entropies) > 1 else 0.0
        uniqueness_growth = np.polyfit(range(len(uniqueness)), uniqueness, 1)[0] if len(uniqueness) > 1 else 0.0
        complexity_growth = np.polyfit(range(len(complexity)), complexity, 1)[0] if len(complexity) > 1 else 0.0
    else:
        entropy_growth = 0.0
        uniqueness_growth = 0.0
        complexity_growth = 0.0

    print(f"  Memory Size: {final_diversity['total_patterns']} patterns")
    print(f"  Unique Patterns: {final_diversity['unique_patterns']} ({final_diversity['uniqueness_ratio']:.3f})")
    print(f"  Shannon Entropy: {final_diversity['shannon_entropy']:.3f} bits")
    print(f"  Complexity Score: {final_diversity['complexity_score']:.3f}")
    print(f"  Magnitude Range: [{final_diversity['min_magnitude']:.3f}, {final_diversity['max_magnitude']:.3f}]")
    print(f"  Total Bursts: {total_bursts}")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'final_diversity': final_diversity,
        'total_bursts': total_bursts,
        'burst_rate': total_bursts / cycles,
        'entropy_growth': entropy_growth,
        'uniqueness_growth': uniqueness_growth,
        'complexity_growth': complexity_growth,
        'diversity_checkpoints': diversity_checkpoints,
        'duration': duration
    }

def main():
    """Run memory diversity analysis."""
    print("="*80)
    print("CYCLE 74: MEMORY DIVERSITY & PATTERN QUALITY ANALYSIS")
    print("="*80)
    print()
    print("Testing memory diversity across energy regimes with seeding enabled.")
    print("Following Cycle 73: Memory quality increases with energy")
    print("Question: Does energy also affect memory DIVERSITY?")
    print()

    # Test optimal zone from Cycle 73
    test_thresholds = [500, 1000, 1500]
    print(f"Testing {len(test_thresholds)} thresholds: {test_thresholds}")
    print("All agents seeded with 5 initial memory patterns")
    print("Measuring: Shannon entropy, uniqueness, complexity, resonance distribution")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_diversity_test(threshold, cycles=500)
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

    if len(successful) >= 2:
        thresholds = [r['threshold'] for r in successful]
        entropies = [r['final_diversity']['shannon_entropy'] for r in successful]
        uniqueness = [r['final_diversity']['uniqueness_ratio'] for r in successful]
        complexity = [r['final_diversity']['complexity_score'] for r in successful]
        magnitude_ranges = [r['final_diversity']['magnitude_range'] for r in successful]

        print(f"\n{'='*80}")
        print(f"MEMORY DIVERSITY ANALYSIS")
        print(f"{'='*80}\n")

        print(f"{'Threshold':>10} | {'Entropy':>8} | {'Unique':>8} | {'Complex':>8} | {'Mag Range':>10}")
        print("-" * 60)
        for i, t in enumerate(thresholds):
            print(f"{t:>10.0f} | {entropies[i]:>8.3f} | {uniqueness[i]:>8.3f} | {complexity[i]:>8.3f} | {magnitude_ranges[i]:>10.3f}")
        print()

        # Correlations
        entropy_corr = np.corrcoef(thresholds, entropies)[0,1] if len(thresholds) > 1 else 0.0
        uniqueness_corr = np.corrcoef(thresholds, uniqueness)[0,1] if len(thresholds) > 1 else 0.0
        complexity_corr = np.corrcoef(thresholds, complexity)[0,1] if len(thresholds) > 1 else 0.0
        range_corr = np.corrcoef(thresholds, magnitude_ranges)[0,1] if len(thresholds) > 1 else 0.0

        print("Energy-Diversity Correlations:")
        print(f"  Shannon entropy: {entropy_corr:.3f}")
        print(f"  Uniqueness ratio: {uniqueness_corr:.3f}")
        print(f"  Complexity score: {complexity_corr:.3f}")
        print(f"  Magnitude range: {range_corr:.3f}")
        print()

        # Discovery criteria: strong positive correlation (>0.7) for diversity metrics
        if (entropy_corr > 0.7 or uniqueness_corr > 0.7 or complexity_corr > 0.7):
            print(f"🎉 ENERGY-DIVERSITY COUPLING DETECTED!")
            print(f"   Higher energy → More diverse memory patterns")
            insight_38 = True
        else:
            print(f"⚠️ Weak or no energy-diversity coupling")
            insight_38 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful tests")
        insight_38 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "memory_diversity"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle74_memory_diversity_analysis.json"

    output_data = {
        'experiment': 'cycle74_memory_diversity_analysis',
        'test_thresholds': test_thresholds,
        'results': results,
        'insight_38_discovered': insight_38,
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
