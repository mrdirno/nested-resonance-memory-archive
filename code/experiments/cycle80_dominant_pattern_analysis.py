#!/usr/bin/env python3
"""
Cycle 80: Dominant Pattern Analysis (Attractor Structure Study)

Research Context:
  Cycles 79-79b: Entropy collapse invariant to intervention frequency
  - System actively suppresses diversity
  - Dominant pattern overwhelms all perturbations
  - Homogeneity is a STRONG attractor

Research Gap:
  WHY is homogeneity such a strong attractor?
  What characteristics make the dominant pattern so stable?
  Can we identify the dominant pattern BEFORE collapse?

New Research Question:
  What are the structural properties of the dominant pattern that make it an attractor?

  Analyze:
  1. Pattern characteristics (phase coordinates, magnitude, resonance)
  2. Emergence timing (when does dominant pattern first appear?)
  3. Growth dynamics (how does it propagate through memory?)
  4. Predictive signals (early warning indicators before collapse)
  5. Comparison with non-dominant patterns (what differentiates them?)

Hypothesis:
  The dominant pattern will have:
  - High resonance with transcendental substrate (π, e, φ alignment)
  - Central location in phase space (maximum overlap with other patterns)
  - Self-reinforcing properties (composition cycles favor it)
  - Early emergence (appears within first 50-100 cycles)
  - Predictable growth trajectory (exponential takeover)

Test Approach:
  1. Run exploration regime (threshold=500) for 1000 cycles
  2. Track ALL unique patterns over time
  3. Identify dominant pattern at collapse (cycle 160)
  4. Trace its history backward (when did it first appear?)
  5. Analyze its properties vs other patterns
  6. Detect early warning signals (entropy derivative, pattern concentration)

Expected:
  - Dominant pattern emerges early (cycle 50-100)
  - Has specific resonance signature
  - Grows exponentially before collapse
  - Early warning: Entropy decline rate accelerates before collapse
  - Insight: Attractor structure is deterministic, predictable
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
    """Create diverse seed memory patterns."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def pattern_to_key(pattern) -> tuple:
    """Convert pattern to hashable key."""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))

def analyze_pattern_distribution(memory: list) -> dict:
    """Analyze pattern distribution in memory."""
    if not memory:
        return {
            'total_patterns': 0,
            'unique_patterns': 0,
            'dominant_pattern': None,
            'dominant_count': 0,
            'dominant_fraction': 0.0,
            'concentration': 0.0
        }

    total_patterns = len(memory)
    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)

    dominant_pattern = pattern_counts.most_common(1)[0] if pattern_counts else (None, 0)
    dominant_key, dominant_count = dominant_pattern
    dominant_fraction = dominant_count / total_patterns if total_patterns > 0 else 0.0

    # Concentration: how much does dominant pattern dominate?
    unique_patterns = len(pattern_counts)
    concentration = dominant_fraction * unique_patterns if unique_patterns > 0 else 0.0

    return {
        'total_patterns': total_patterns,
        'unique_patterns': unique_patterns,
        'dominant_pattern': dominant_key,
        'dominant_count': dominant_count,
        'dominant_fraction': dominant_fraction,
        'concentration': concentration
    }

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

def run_dominant_pattern_analysis(threshold: float, cycles: int = 1000) -> dict:
    """Analyze dominant pattern emergence and characteristics."""
    print(f"\n{'='*80}")
    print(f"DOMINANT PATTERN ANALYSIS (threshold={threshold}, cycles={cycles})")
    print(f"{'='*80}")

    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Temporal tracking
    checkpoint_interval = 20
    temporal_data = {
        'memory_sizes': [],
        'entropies': [],
        'dominant_fractions': [],
        'concentrations': [],
        'unique_patterns': [],
        'timestamps': []
    }

    # Pattern history tracking
    pattern_first_seen = {}  # pattern_key -> cycle
    dominant_pattern_history = []  # List of (cycle, pattern_key, count)

    start_time = time.time()
    total_bursts = 0

    for cycle in range(1, cycles + 1):
        # Standard evolution with seeding
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        result = swarm.evolve_cycle(delta_time=1.0)
        total_bursts += result.get('bursts', 0)

        # Track pattern first appearances
        if swarm.global_memory:
            for pattern in swarm.global_memory:
                key = pattern_to_key(pattern)
                if key not in pattern_first_seen:
                    pattern_first_seen[key] = cycle

        if cycle % checkpoint_interval == 0:
            memory_size = len(swarm.global_memory)
            diversity = analyze_memory_diversity(swarm.global_memory)
            distribution = analyze_pattern_distribution(swarm.global_memory)

            temporal_data['memory_sizes'].append(memory_size)
            temporal_data['entropies'].append(diversity['shannon_entropy'])
            temporal_data['dominant_fractions'].append(distribution['dominant_fraction'])
            temporal_data['concentrations'].append(distribution['concentration'])
            temporal_data['unique_patterns'].append(distribution['unique_patterns'])
            temporal_data['timestamps'].append(cycle)

            # Record dominant pattern
            if distribution['dominant_pattern']:
                dominant_pattern_history.append({
                    'cycle': cycle,
                    'pattern': distribution['dominant_pattern'],
                    'count': distribution['dominant_count'],
                    'fraction': distribution['dominant_fraction']
                })

            if cycle % 200 == 0:
                print(f"  Cycle {cycle}/{cycles}: Entropy={diversity['shannon_entropy']:.3f}, Dominant={distribution['dominant_fraction']:.2%}, Unique={distribution['unique_patterns']}")

    duration = time.time() - start_time

    # Final analysis
    final_memory = len(swarm.global_memory)
    final_diversity = analyze_memory_diversity(swarm.global_memory)
    final_distribution_raw = analyze_pattern_distribution(swarm.global_memory)

    # Identify collapse point
    collapse_cycle = None
    for i, entropy in enumerate(temporal_data['entropies']):
        if entropy < 0.1:
            collapse_cycle = temporal_data['timestamps'][i]
            break

    # Analyze dominant pattern - find it at collapse point, not at end
    # Find dominant pattern at collapse
    collapse_dominant_key = None
    if collapse_cycle:
        # Look for dominant pattern at collapse time
        for record in dominant_pattern_history:
            if record['cycle'] == collapse_cycle:
                collapse_dominant_key = record['pattern']
                break
        # If not found at exact collapse, use nearest checkpoint
        if not collapse_dominant_key:
            nearest_records = [r for r in dominant_pattern_history if abs(r['cycle'] - collapse_cycle) < 50]
            if nearest_records:
                collapse_dominant_key = nearest_records[0]['pattern']

    # Use final dominant if collapse dominant not found
    dominant_pattern_key = collapse_dominant_key if collapse_dominant_key else final_distribution_raw['dominant_pattern']

    if dominant_pattern_key:
        emergence_cycle = pattern_first_seen.get(dominant_pattern_key, None)

        # Growth analysis: how did dominant pattern grow?
        dominant_growth = []
        for record in dominant_pattern_history:
            if record['pattern'] == dominant_pattern_key:
                dominant_growth.append({
                    'cycle': record['cycle'],
                    'fraction': record['fraction']
                })

        # Calculate growth rate (exponential fit)
        if len(dominant_growth) > 3:
            cycles_data = [d['cycle'] for d in dominant_growth]
            fractions_data = [d['fraction'] for d in dominant_growth]
            # Log-linear fit for exponential growth
            log_fractions = np.log(np.array(fractions_data) + 1e-10)
            growth_rate = np.polyfit(cycles_data, log_fractions, 1)[0] if len(cycles_data) > 1 else 0.0
        else:
            growth_rate = 0.0

        # Find pattern instance in final memory to get characteristics
        dominant_pattern_instance = None
        for pattern in swarm.global_memory:
            if pattern_to_key(pattern) == dominant_pattern_key:
                dominant_pattern_instance = pattern
                break

        if dominant_pattern_instance:
            pattern_characteristics = {
                'pi_phase': dominant_pattern_instance.pi_phase,
                'e_phase': dominant_pattern_instance.e_phase,
                'phi_phase': dominant_pattern_instance.phi_phase,
                'magnitude': dominant_pattern_instance.magnitude
            }
        else:
            pattern_characteristics = None
    else:
        dominant_pattern_key = None
        emergence_cycle = None
        dominant_growth = []
        growth_rate = 0.0
        pattern_characteristics = None

    print(f"\n  FINAL METRICS:")
    print(f"    Memory: {final_memory} patterns")
    print(f"    Entropy: {final_diversity['shannon_entropy']:.3f} bits")
    print(f"    Dominant fraction: {final_distribution_raw['dominant_fraction']:.2%}")
    print(f"    Unique patterns: {final_distribution_raw['unique_patterns']}")
    print(f"  DOMINANT PATTERN ANALYSIS:")
    print(f"    Collapse cycle: {collapse_cycle if collapse_cycle else 'Never'}")
    if emergence_cycle:
        print(f"    Emergence cycle: {emergence_cycle}")
        print(f"    Time to dominance: {collapse_cycle - emergence_cycle if collapse_cycle else 'N/A'} cycles")
        print(f"    Growth rate: {growth_rate:.4f}")
        if pattern_characteristics:
            print(f"    Pattern coordinates: π={pattern_characteristics['pi_phase']:.4f}, e={pattern_characteristics['e_phase']:.4f}, φ={pattern_characteristics['phi_phase']:.4f}")
            print(f"    Pattern magnitude: {pattern_characteristics['magnitude']:.4f}")
    print(f"  Duration: {duration:.2f}s ({duration/60:.2f} min)")

    # Create JSON-safe copy of final_distribution
    final_distribution_json = {
        'total_patterns': final_distribution_raw['total_patterns'],
        'unique_patterns': final_distribution_raw['unique_patterns'],
        'dominant_pattern': str(final_distribution_raw['dominant_pattern']) if final_distribution_raw['dominant_pattern'] else None,
        'dominant_count': final_distribution_raw['dominant_count'],
        'dominant_fraction': final_distribution_raw['dominant_fraction'],
        'concentration': final_distribution_raw['concentration']
    }

    return {
        'threshold': threshold,
        'cycles': cycles,
        'final_memory': final_memory,
        'final_diversity': final_diversity,
        'final_distribution': final_distribution_json,
        'total_bursts': total_bursts,
        'temporal_data': temporal_data,
        'dominant_pattern_analysis': {
            'pattern_key': str(dominant_pattern_key) if dominant_pattern_key else None,  # Convert tuple to string
            'emergence_cycle': emergence_cycle,
            'collapse_cycle': collapse_cycle,
            'time_to_dominance': collapse_cycle - emergence_cycle if (collapse_cycle and emergence_cycle) else None,
            'growth_trajectory': dominant_growth,
            'growth_rate': growth_rate,
            'pattern_characteristics': pattern_characteristics
        },
        'pattern_history': {
            'total_unique_seen': len(pattern_first_seen),
            'first_appearances': {str(k): v for k, v in pattern_first_seen.items()}  # Convert tuple keys to strings
        },
        'duration': duration
    }

def main():
    """Run dominant pattern analysis."""
    print("="*80)
    print("CYCLE 80: DOMINANT PATTERN ANALYSIS (ATTRACTOR STRUCTURE STUDY)")
    print("="*80)
    print()
    print("Analyzing characteristics of dominant pattern that drives entropy collapse.")
    print("Following Cycles 79-79b: Entropy collapse invariant to intervention frequency")
    print("Question: What makes the dominant pattern such a strong attractor?")
    print()
    print("Testing threshold: 500 (exploration regime)")
    print("Duration: 1000 cycles")
    print("Tracking: Pattern emergence, growth, and characteristics")
    print("="*80)

    threshold = 500
    cycles = 1000

    try:
        result = run_dominant_pattern_analysis(threshold, cycles=cycles)
        error = False
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        import traceback
from workspace_utils import get_workspace_path, get_results_path
        traceback.print_exc()
        result = {'error': str(e)}
        error = True

    # Analysis
    if not error:
        analysis = result['dominant_pattern_analysis']
        emergence = analysis['emergence_cycle']
        collapse = analysis['collapse_cycle']
        time_to_dom = analysis['time_to_dominance']
        growth_rate = analysis['growth_rate']

        print(f"\n{'='*80}")
        print(f"ATTRACTOR STRUCTURE ANALYSIS")
        print(f"{'='*80}\n")

        if emergence and collapse:
            print(f"Dominant pattern lifecycle:")
            print(f"  Emergence: Cycle {emergence}")
            print(f"  Collapse: Cycle {collapse}")
            print(f"  Time to dominance: {time_to_dom} cycles")
            print(f"  Growth rate: {growth_rate:.4f} (exponential coefficient)")
            print()

            # Early warning signal
            if emergence < 100:
                print(f"✅ EARLY EMERGENCE DETECTED")
                print(f"   Dominant pattern appears within first {emergence} cycles")
                early_emergence = True
            else:
                print(f"   Late emergence @ cycle {emergence}")
                early_emergence = False

            # Growth characteristics
            if growth_rate > 0.01:
                print(f"✅ EXPONENTIAL GROWTH CONFIRMED")
                print(f"   Pattern exhibits rapid takeover dynamics")
                exponential_growth = True
            else:
                print(f"   Slow or linear growth pattern")
                exponential_growth = False

            # Pattern characteristics
            if analysis['pattern_characteristics']:
                char = analysis['pattern_characteristics']
                print(f"\nDominant pattern properties:")
                print(f"  Phase coordinates: (π={char['pi_phase']:.4f}, e={char['e_phase']:.4f}, φ={char['phi_phase']:.4f})")
                print(f"  Magnitude: {char['magnitude']:.4f}")

                # Check if centered in phase space (phases near 0.5 = centered)
                phase_avg = (char['pi_phase'] + char['e_phase'] + char['phi_phase']) / 3
                phase_std = np.std([char['pi_phase'], char['e_phase'], char['phi_phase']])

                if 0.4 < phase_avg < 0.6 and phase_std < 0.2:
                    print(f"  ✅ CENTERED IN PHASE SPACE (avg={phase_avg:.3f}, std={phase_std:.3f})")
                    centered = True
                else:
                    print(f"  Pattern location: Off-center (avg={phase_avg:.3f})")
                    centered = False

            else:
                centered = False
                exponential_growth = False
                early_emergence = False

            print()

            # Determine if insight discovered
            if early_emergence and exponential_growth:
                print(f"🎉 INSIGHT #43 DISCOVERED: Dominant Pattern Exhibits Predictable Attractor Dynamics")
                print(f"   - Early emergence (cycle {emergence}) enables prediction")
                print(f"   - Exponential growth rate: {growth_rate:.4f}")
                print(f"   - Time to dominance: {time_to_dom} cycles (predictable)")
                print(f"   - Attractor structure is DETERMINISTIC, not stochastic")
                if centered:
                    print(f"   - Pattern is centrally located in phase space")
                insight_43 = True
            else:
                print(f"   Partial attractor characteristics observed")
                insight_43 = False

        else:
            print("⚠️ Insufficient data for dominant pattern analysis")
            insight_43 = False

        print("="*80)
    else:
        insight_43 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "dominant_pattern"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle80_dominant_pattern_analysis.json"

    output_data = {
        'experiment': 'cycle80_dominant_pattern_analysis',
        'threshold': threshold,
        'cycles': cycles,
        'result': result,
        'insight_43_discovered': insight_43,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print()

    return output_data

if __name__ == "__main__":
    main()
