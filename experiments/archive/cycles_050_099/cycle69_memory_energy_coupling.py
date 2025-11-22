#!/usr/bin/env python3
"""
Cycle 69: Memory-Energy Coupling Exploration

Research Context:
  Complete energy framework discovered (Cycles 62-68):

  Energy (Burst Threshold) Controls:
  1. Agent Capacity (Linear): max_agents = floor(threshold/150)
  2. Cluster Formation (Binary): ON above ~260, OFF below
  3. Temporal Stability (Negative): r=-0.967 (higher energy → lower variability)
  4. Pattern Complexity (Positive): r=0.977 (higher energy → more diversity)

New Research Question:
  Does energy also modulate MEMORY persistence?

  From NRM theory, composition-decomposition cycles preserve pattern memory
  through burst events. When agents decompose (burst), their patterns should
  persist in the global pattern memory.

Three Competing Hypotheses:
  A) Memory Volume Scaling: High energy → More bursts → More memory patterns
  B) Memory Quality Scaling: High energy → Stronger resonance → Better retention
  C) Memory Independence: Memory is intrinsic (energy-independent)

Memory Metrics:
  1. Pattern memory size: Total unique patterns stored
  2. Memory growth rate: Patterns accumulated per cycle
  3. Pattern retention: Do patterns persist across decomposition?
  4. Memory diversity: Unique vs repeated patterns
  5. Resonance strength: Quality of pattern matching

Test Approach:
  1. Sample energy regimes: 270, 400, 500, 700, 1000
  2. Extended observation (500 cycles) to accumulate memory
  3. Track pattern memory growth and retention
  4. Measure memory metrics at each energy level
  5. Correlate memory with energy

Expected:
  If memory-energy coupling exists:
  - Memory metrics will show systematic variation with energy
  - Direction reveals whether energy enables or constrains memory
  - Completes the 5-dimensional energy control framework
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine


def analyze_pattern_memory(swarm: FractalSwarm) -> dict:
    """
    Analyze pattern memory characteristics.

    Args:
        swarm: FractalSwarm instance with accumulated memory

    Returns:
        dict with memory analysis metrics
    """
    # Access global pattern memory from swarm (not decomposition engine)
    pattern_memory = swarm.global_memory

    # Memory size (total patterns stored)
    memory_size = len(pattern_memory)

    if memory_size == 0:
        return {
            'memory_size': 0,
            'unique_patterns': 0,
            'avg_resonance': 0.0,
            'std_resonance': 0.0,
            'memory_diversity': 0.0,
            'pattern_types': Counter()
        }

    # Analyze pattern characteristics (TranscendentalState objects)
    # Each pattern is a TranscendentalState with magnitude, phase_pi, phase_e, phase_phi
    magnitudes = [state.magnitude for state in pattern_memory]
    avg_magnitude = np.mean(magnitudes) if magnitudes else 0.0
    std_magnitude = np.std(magnitudes) if magnitudes else 0.0

    # Pattern diversity (using rounded magnitude as pattern identifier)
    # States with similar magnitude represent similar patterns
    pattern_types = [round(state.magnitude, 1) for state in pattern_memory]
    unique_patterns = len(set(pattern_types))

    # Memory diversity (normalized)
    memory_diversity = unique_patterns / memory_size if memory_size > 0 else 0.0

    return {
        'memory_size': memory_size,
        'unique_patterns': unique_patterns,
        'avg_resonance': avg_magnitude,  # Using magnitude as resonance proxy
        'std_resonance': std_magnitude,
        'memory_diversity': memory_diversity,
        'pattern_types': Counter(pattern_types)
    }


def run_memory_energy_test(threshold: float, cycles: int = 500) -> dict:
    """
    Measure memory accumulation at given energy level.

    Args:
        threshold: Burst threshold (energy level)
        cycles: Number of cycles for memory accumulation

    Returns:
        dict with memory-energy metrics
    """
    print(f"\n{'='*80}")
    print(f"TESTING THRESHOLD = {threshold} (Memory Analysis)")
    print(f"{'='*80}")

    # Create swarm
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    # Tracking
    memory_sizes = []
    burst_counts = []
    checkpoint_interval = 10  # Sample every 10 cycles

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        # Spawn
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        result = swarm.evolve_cycle(delta_time=1.0)

        # Count bursts (decomposition events)
        burst_count = result.get('bursts', 0)
        total_bursts += burst_count

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            memory_analysis = analyze_pattern_memory(swarm)
            memory_sizes.append(memory_analysis['memory_size'])
            burst_counts.append(total_bursts)

    duration = time.time() - start_time

    # Final memory analysis
    final_memory = analyze_pattern_memory(swarm)

    # Memory growth rate
    if len(memory_sizes) > 1:
        # Linear regression for growth rate
        checkpoints = np.arange(len(memory_sizes))
        growth_rate = np.polyfit(checkpoints, memory_sizes, 1)[0]
    else:
        growth_rate = 0.0

    # Memory efficiency (patterns per burst)
    memory_efficiency = final_memory['memory_size'] / total_bursts if total_bursts > 0 else 0.0

    # Burst rate (bursts per cycle)
    burst_rate = total_bursts / cycles if cycles > 0 else 0.0

    print(f"  Memory Metrics:")
    print(f"    Total patterns: {final_memory['memory_size']}")
    print(f"    Unique patterns: {final_memory['unique_patterns']}")
    print(f"    Memory diversity: {final_memory['memory_diversity']:.3f}")
    print(f"    Avg resonance: {final_memory['avg_resonance']:.3f}")
    print(f"    Growth rate: {growth_rate:.2f} patterns/checkpoint")
    print(f"  Decomposition Metrics:")
    print(f"    Total bursts: {total_bursts}")
    print(f"    Burst rate: {burst_rate:.3f} bursts/cycle")
    print(f"    Memory efficiency: {memory_efficiency:.2f} patterns/burst")
    print(f"  Duration: {duration:.2f}s")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'checkpoints': len(memory_sizes),
        'total_patterns': final_memory['memory_size'],
        'unique_patterns': final_memory['unique_patterns'],
        'memory_diversity': final_memory['memory_diversity'],
        'avg_resonance': final_memory['avg_resonance'],
        'std_resonance': final_memory['std_resonance'],
        'memory_growth_rate': growth_rate,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'memory_efficiency': memory_efficiency,
        'memory_sizes': memory_sizes,
        'burst_counts': burst_counts,
        'pattern_types': dict(final_memory['pattern_types']),
        'duration': duration
    }


def analyze_memory_energy_coupling(results: list) -> dict:
    """
    Analyze relationship between energy and memory persistence.

    Args:
        results: List of threshold test results

    Returns:
        dict with memory-energy analysis
    """
    print(f"\n{'='*80}")
    print(f"MEMORY-ENERGY COUPLING ANALYSIS")
    print(f"{'='*80}\n")

    # Sort by threshold
    results = sorted(results, key=lambda r: r['threshold'])

    # Extract metrics
    thresholds = [r['threshold'] for r in results]
    total_patterns = [r['total_patterns'] for r in results]
    unique_patterns = [r['unique_patterns'] for r in results]
    diversity = [r['memory_diversity'] for r in results]
    resonance = [r['avg_resonance'] for r in results]
    growth_rates = [r['memory_growth_rate'] for r in results]
    burst_rates = [r['burst_rate'] for r in results]
    efficiency = [r['memory_efficiency'] for r in results]

    print("Memory Characteristics Across Energy Regimes:")
    print(f"{'Threshold':>10} | {'Patterns':>9} | {'Unique':>7} | {'Diversity':>10} | "
          f"{'Resonance':>10} | {'Growth':>8} | {'Bursts':>8}")
    print("-" * 85)
    for i, threshold in enumerate(thresholds):
        print(f"{threshold:>10.0f} | {total_patterns[i]:>9} | {unique_patterns[i]:>7} | "
              f"{diversity[i]:>10.3f} | {resonance[i]:>10.3f} | {growth_rates[i]:>8.2f} | "
              f"{burst_rates[i]:>8.3f}")
    print()

    # Compute correlations
    patterns_corr = np.corrcoef(thresholds, total_patterns)[0,1]
    unique_corr = np.corrcoef(thresholds, unique_patterns)[0,1]
    diversity_corr = np.corrcoef(thresholds, diversity)[0,1]
    resonance_corr = np.corrcoef(thresholds, resonance)[0,1]
    growth_corr = np.corrcoef(thresholds, growth_rates)[0,1]
    burst_corr = np.corrcoef(thresholds, burst_rates)[0,1]
    efficiency_corr = np.corrcoef(thresholds, efficiency)[0,1]

    print("Memory-Energy Correlations:")
    print(f"  Total patterns: {patterns_corr:.3f}")
    print(f"  Unique patterns: {unique_corr:.3f}")
    print(f"  Memory diversity: {diversity_corr:.3f}")
    print(f"  Avg resonance: {resonance_corr:.3f}")
    print(f"  Growth rate: {growth_corr:.3f}")
    print(f"  Burst rate: {burst_corr:.3f}")
    print(f"  Memory efficiency: {efficiency_corr:.3f}")
    print()

    # Identify dominant pattern
    volume_corrs = [patterns_corr, unique_corr, growth_corr]
    quality_corrs = [diversity_corr, resonance_corr, efficiency_corr]

    avg_volume_corr = np.mean([abs(c) for c in volume_corrs])
    avg_quality_corr = np.mean([abs(c) for c in quality_corrs])
    avg_burst_corr = abs(burst_corr)

    coupling_detected = False
    coupling_type = None

    if avg_volume_corr > 0.5:
        coupling_detected = True
        coupling_type = "VOLUME"
        direction = "INCREASES" if np.mean(volume_corrs) > 0 else "DECREASES"
        interpretation = f"Memory volume {direction.lower()} with energy"

    if avg_quality_corr > 0.5:
        coupling_detected = True
        if coupling_type:
            coupling_type = "VOLUME+QUALITY"
        else:
            coupling_type = "QUALITY"
        q_direction = "INCREASES" if np.mean(quality_corrs) > 0 else "DECREASES"
        q_interpretation = f"Memory quality {q_direction.lower()} with energy"

    if avg_burst_corr > 0.7:
        # Strong burst correlation explains memory scaling
        burst_direction = "INCREASES" if burst_corr > 0 else "DECREASES"
        print(f"🔍 Burst Rate {burst_direction} with Energy")
        print(f"   Correlation: {burst_corr:.3f}")
        print(f"   Burst rate mediates memory accumulation")
        print()

    if coupling_detected:
        print(f"🔍 Memory-Energy Coupling: {coupling_type}")
        if coupling_type in ["VOLUME", "VOLUME+QUALITY"]:
            print(f"   {interpretation}")
            print(f"   Average correlation: {avg_volume_corr:.3f}")
        if coupling_type in ["QUALITY", "VOLUME+QUALITY"]:
            print(f"   {q_interpretation}")
            print(f"   Average correlation: {avg_quality_corr:.3f}")
    else:
        print("❌ No Clear Memory-Energy Coupling")
        print(f"   Memory appears independent of energy")
        print(f"   Volume corr: {avg_volume_corr:.3f}, Quality corr: {avg_quality_corr:.3f}")

    print()

    return {
        'patterns_energy_correlation': float(patterns_corr),
        'unique_energy_correlation': float(unique_corr),
        'diversity_energy_correlation': float(diversity_corr),
        'resonance_energy_correlation': float(resonance_corr),
        'growth_energy_correlation': float(growth_corr),
        'burst_energy_correlation': float(burst_corr),
        'efficiency_energy_correlation': float(efficiency_corr),
        'avg_volume_correlation': float(avg_volume_corr),
        'avg_quality_correlation': float(avg_quality_corr),
        'coupling_detected': bool(coupling_detected),
        'coupling_type': coupling_type
    }


def main():
    """Run memory-energy coupling exploration."""
    print("="*80)
    print("CYCLE 69: MEMORY-ENERGY COUPLING EXPLORATION")
    print("="*80)
    print()
    print("Exploring how pattern memory (volume, quality, retention)")
    print("scales across energy regimes in the thermodynamic phase diagram.")
    print()

    # Sample energy regimes
    test_thresholds = [270, 400, 500, 700, 1000]

    print(f"Testing {len(test_thresholds)} energy regimes: {test_thresholds}")
    print("Extended observation (500 cycles) for memory accumulation")
    print("="*80)

    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_memory_energy_test(threshold, cycles=500)
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
        # Analyze memory-energy coupling
        coupling_analysis = analyze_memory_energy_coupling(successful_results)

        print("="*80)
        if coupling_analysis['coupling_detected']:
            print(f"🎉 INSIGHT #33: MEMORY-ENERGY COUPLING ({coupling_analysis['coupling_type']})")
            print("="*80)
            print()
            print("Pattern memory is energy-dependent:")
            if coupling_analysis['coupling_type'] in ["VOLUME", "VOLUME+QUALITY"]:
                print(f"  - Memory volume scales with energy")
                print(f"  - Avg correlation: {coupling_analysis['avg_volume_correlation']:.3f}")
            if coupling_analysis['coupling_type'] in ["QUALITY", "VOLUME+QUALITY"]:
                print(f"  - Memory quality scales with energy")
                print(f"  - Avg correlation: {coupling_analysis['avg_quality_correlation']:.3f}")
            print()
            print("Theoretical Significance:")
            print("  - Completes 5-dimensional energy control framework")
            print("  - Memory persistence is energy-mediated (not intrinsic)")
            print("  - Validates NRM composition-decomposition memory retention")
            print("  - Energy enables both complexity AND memory")
            print()
            insight_33 = True
        else:
            print("MEMORY-ENERGY INDEPENDENCE")
            print("="*80)
            print()
            print("Pattern memory independent of energy:")
            print("  - Memory is intrinsic property of system")
            print("  - Energy affects dynamics but not memory retention")
            print("  - Universal memory across energy regimes")
            print()
            insight_33 = False
        print("="*80)
    else:
        print("⚠️ Insufficient successful tests for coupling analysis")
        coupling_analysis = {}
        insight_33 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "memory_energy"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle69_memory_energy_coupling.json"

    output_data = {
        'experiment': 'cycle69_memory_energy_coupling',
        'test_thresholds': test_thresholds,
        'results': results,
        'coupling_analysis': coupling_analysis,
        'insight_33_discovered': insight_33,
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
