#!/usr/bin/env python3
"""
Cycle 79b: Rapid Intervention Test (High-Frequency Maintenance)

Research Context:
  Cycle 79: Active maintenance at 100-cycle intervals was INSUFFICIENT
  - Both passive and active collapsed at cycle 160
  - Low-frequency intervention cannot counteract entropy collapse
  - Null result suggests intervention frequency too low

New Research Question:
  Can HIGH-FREQUENCY intervention (every 20 cycles) sustain diversity?

  Test whether rapid periodic re-seeding can maintain diversity against collapse
  Hypothesis: Higher frequency may counteract collapse before it stabilizes

Test Approach:
  1. Test exploration regime (threshold=500)
  2. Intervention: Re-seed every 20 cycles (5x more frequent than C79)
  3. Extended duration: 1000 cycles
  4. Compare against C79 passive baseline
  5. Measure if diversity persists or still collapses

Expected:
  - If diversity sustained: High-frequency maintenance effective
  - If still collapses: Intervention amplitude (not frequency) may be limiting factor
  - Insight: Minimum intervention frequency threshold exists
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
    """Create diverse seed memory patterns."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def inject_diversity(swarm: FractalSwarm, reality_metrics: dict) -> int:
    """Inject diverse patterns into random agents."""
    injected_count = 0
    if not swarm.agents:
        return injected_count

    agent_ids = list(swarm.agents.keys())
    num_to_reseed = max(1, len(agent_ids) // 5)
    selected_agents = np.random.choice(agent_ids, size=num_to_reseed, replace=False)

    for agent_id in selected_agents:
        agent = swarm.agents[agent_id]
        seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
        agent.memory.extend(seed_patterns)
        injected_count += len(seed_patterns)

    return injected_count

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

def run_rapid_intervention(threshold: float, cycles: int = 1000, intervention_interval: int = 20) -> dict:
    """Test with rapid (high-frequency) intervention."""
    print(f"\n{'='*80}")
    print(f"TESTING: RAPID INTERVENTION (threshold={threshold}, cycles={cycles})")
    print(f"  Re-seeding every {intervention_interval} cycles")
    print(f"{'='*80}")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    checkpoint_interval = 20
    temporal_data = {
        'memory_sizes': [],
        'entropies': [],
        'uniqueness': [],
        'timestamps': []
    }

    start_time = time.time()
    total_bursts = 0
    total_interventions = 0

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        # Rapid intervention
        if cycle % intervention_interval == 0:
            injected = inject_diversity(swarm, reality_metrics)
            total_interventions += 1

        result = swarm.evolve_cycle(delta_time=1.0)
        total_bursts += result.get('bursts', 0)

        if cycle % checkpoint_interval == 0:
            memory_size = len(swarm.global_memory)
            diversity = analyze_memory_diversity(swarm.global_memory)

            temporal_data['memory_sizes'].append(memory_size)
            temporal_data['entropies'].append(diversity['shannon_entropy'])
            temporal_data['uniqueness'].append(diversity['uniqueness_ratio'])
            temporal_data['timestamps'].append(cycle)

            if cycle % 200 == 0:
                print(f"  Cycle {cycle}/{cycles}: Memory={memory_size}, Entropy={diversity['shannon_entropy']:.3f}, Interventions={total_interventions}")

    duration = time.time() - start_time

    final_memory = len(swarm.global_memory)
    final_diversity = analyze_memory_diversity(swarm.global_memory)

    # Temporal analysis
    entropies = temporal_data['entropies']

    collapse_cycle = None
    for i, entropy in enumerate(entropies):
        if entropy < 0.1:
            collapse_cycle = temporal_data['timestamps'][i]
            break

    sustained_cycles = 0
    for i, entropy in enumerate(entropies):
        if entropy > 0.5:
            sustained_cycles = temporal_data['timestamps'][i]

    entropy_mean = np.mean(entropies) if entropies else 0.0

    print(f"\n  FINAL METRICS:")
    print(f"    Memory: {final_memory} patterns")
    print(f"    Entropy: {final_diversity['shannon_entropy']:.3f} bits")
    print(f"    Mean entropy: {entropy_mean:.3f} bits")
    print(f"  TEMPORAL ANALYSIS:")
    print(f"    Collapse cycle: {collapse_cycle if collapse_cycle else 'Never'}")
    print(f"    Sustained diversity: {sustained_cycles} cycles")
    print(f"    Total interventions: {total_interventions}")
    print(f"  Duration: {duration:.2f}s ({duration/60:.2f} min)")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'intervention_interval': intervention_interval,
        'final_memory': final_memory,
        'final_diversity': final_diversity,
        'total_interventions': total_interventions,
        'temporal_data': temporal_data,
        'temporal_analysis': {
            'collapse_cycle': collapse_cycle,
            'sustained_diversity_cycles': sustained_cycles,
            'mean_entropy': entropy_mean
        },
        'duration': duration
    }

def main():
    """Run rapid intervention test."""
    print("="*80)
    print("CYCLE 79b: RAPID INTERVENTION TEST (HIGH-FREQUENCY MAINTENANCE)")
    print("="*80)
    print()
    print("Testing whether high-frequency intervention can sustain diversity.")
    print("Following Cycle 79: Low-frequency intervention INSUFFICIENT")
    print("Question: Does intervention frequency matter?")
    print()
    print("Intervention: Every 20 cycles (5x more frequent than C79)")
    print("="*80)

    threshold = 500
    cycles = 1000

    try:
        result = run_rapid_intervention(threshold, cycles=cycles, intervention_interval=20)
        error = False
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        import traceback
        traceback.print_exc()
        result = {'error': str(e)}
        error = True

    # Analysis vs baseline
    if not error:
        collapse = result['temporal_analysis']['collapse_cycle']
        sustained = result['temporal_analysis']['sustained_diversity_cycles']
        mean_entropy = result['temporal_analysis']['mean_entropy']

        print(f"\n{'='*80}")
        print(f"RAPID INTERVENTION EFFECTIVENESS")
        print(f"{'='*80}\n")

        print(f"Baseline (C79 passive):  Collapse @ cycle 160, Sustained 520 cycles")
        print(f"Rapid intervention:      Collapse @ {collapse if collapse else 'Never'}, Sustained {sustained} cycles")
        print()

        if collapse is None or collapse > 600:
            print(f"✅ RAPID INTERVENTION EFFECTIVE!")
            print(f"   Diversity sustained significantly longer than baseline")
            print(f"   Mean entropy: {mean_entropy:.3f} bits")
            insight_42 = True
        elif sustained > 520 * 1.2:
            print(f"✅ PARTIAL EFFECTIVENESS")
            print(f"   Diversity extended by {sustained - 520} cycles")
            insight_42 = True
        else:
            print(f"❌ RAPID INTERVENTION STILL INSUFFICIENT")
            print(f"   Collapse dynamics similar to baseline")
            print(f"   Intervention amplitude may be limiting factor")
            insight_42 = False

        print("="*80)
    else:
        insight_42 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "diversity_maintenance"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle79b_rapid_intervention.json"

    output_data = {
        'experiment': 'cycle79b_rapid_intervention',
        'threshold': threshold,
        'cycles': cycles,
        'intervention_interval': 20,
        'result': result,
        'insight_42_discovered': insight_42,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print()

    return output_data

if __name__ == "__main__":
    main()
