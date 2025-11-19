#!/usr/bin/env python3
"""
Cycle 79: Active Diversity Maintenance (Intervention Study)

Research Context:
  Cycle 78: MAJOR DISCOVERY - Universal entropy collapse
  - All regimes converge to homogeneity over extended time
  - Energy controls RATE of convergence, not whether diversity persists
  - Diversity is transient in passive systems

Research Gap:
  Cycle 78 tested PASSIVE evolution (no intervention after initial seeding)
  Unknown: Can ACTIVE maintenance sustain diversity against natural collapse?

New Research Question:
  Can periodic diversity injection counteract universal entropy collapse?

  Compare:
  - PASSIVE: No intervention (Cycle 78 baseline)
  - ACTIVE: Periodic re-seeding every N cycles

  Measure:
  - Does diversity persist longer with intervention?
  - What is the maintenance cost (re-seed frequency)?
  - Is there a stability-diversity trade-off?

Hypothesis:
  Active diversity maintenance will:
  1. Extend diversity lifespan beyond passive baseline
  2. Require increasing intervention frequency as system scales
  3. Trade stability for variety (oscillating diversity)
  4. Validate whether diversity CAN persist with external perturbation

Test Approach:
  1. Test exploration regime (threshold=500) with interventions
  2. Baseline: Passive evolution (no re-seeding after spawn)
  3. Active: Re-seed every 100 cycles with diverse patterns
  4. Extended duration: 1000 cycles to observe long-term effects
  5. Compare temporal entropy dynamics (passive vs active)
  6. Measure intervention effectiveness and costs

Expected:
  - Passive: Entropy collapses to zero (~400-600 cycles, C78 result)
  - Active: Entropy oscillates but remains above zero
  - Intervention cost: Must re-seed more frequently over time
  - Insight: Diversity requires continuous energy input to persist
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
        # Create varied patterns across full range
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def inject_diversity(swarm: FractalSwarm, reality_metrics: dict) -> int:
    """Inject diverse patterns into random agents."""
    injected_count = 0
    if not swarm.agents:
        return injected_count

    # Select 20% of agents for re-seeding
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

def run_maintenance_test(threshold: float, cycles: int = 1000, intervention_interval: int = None) -> dict:
    """Test with or without active diversity maintenance."""
    mode = "ACTIVE MAINTENANCE" if intervention_interval else "PASSIVE BASELINE"
    print(f"\n{'='*80}")
    print(f"TESTING: {mode} (threshold={threshold}, cycles={cycles})")
    if intervention_interval:
        print(f"  Re-seeding every {intervention_interval} cycles")
    print(f"{'='*80}")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Temporal tracking
    checkpoint_interval = 20
    temporal_data = {
        'memory_sizes': [],
        'entropies': [],
        'uniqueness': [],
        'efficiencies': [],
        'bursts': [],
        'interventions': [],
        'timestamps': []
    }

    start_time = time.time()
    total_bursts = 0
    total_interventions = 0

    for cycle in range(1, cycles + 1):
        # Standard spawn with initial seeding
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        # Active maintenance: periodic re-seeding
        if intervention_interval and cycle % intervention_interval == 0:
            injected = inject_diversity(swarm, reality_metrics)
            total_interventions += 1
            if cycle % 200 == 0:
                print(f"  Cycle {cycle}: Intervention #{total_interventions} - injected {injected} patterns")

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
            temporal_data['interventions'].append(total_interventions)
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
    entropies = temporal_data['entropies']

    # Find collapse point (first time entropy drops below 0.1)
    collapse_cycle = None
    for i, entropy in enumerate(entropies):
        if entropy < 0.1:
            collapse_cycle = temporal_data['timestamps'][i]
            break

    # Sustained diversity metric (how long entropy > 0.5)
    sustained_cycles = 0
    for i, entropy in enumerate(entropies):
        if entropy > 0.5:
            sustained_cycles = temporal_data['timestamps'][i]

    # Oscillation detection (std of entropy in late phase)
    if len(entropies) > 10:
        half_point = len(entropies) // 2
        late_entropy = entropies[half_point:]
        entropy_oscillation = np.std(late_entropy)
    else:
        entropy_oscillation = 0.0

    print(f"\n  FINAL METRICS:")
    print(f"    Memory: {final_memory} patterns")
    print(f"    Entropy: {final_diversity['shannon_entropy']:.3f} bits")
    print(f"    Uniqueness: {final_diversity['uniqueness_ratio']:.4f}")
    print(f"    Efficiency: {final_efficiency:.2f} patterns/burst")
    print(f"  TEMPORAL ANALYSIS:")
    print(f"    Collapse cycle: {collapse_cycle if collapse_cycle else 'Never'}")
    print(f"    Sustained diversity: {sustained_cycles} cycles")
    print(f"    Entropy oscillation: {entropy_oscillation:.3f}")
    if intervention_interval:
        print(f"    Total interventions: {total_interventions}")
        print(f"    Intervention rate: {total_interventions/cycles:.3f} per cycle")
    print(f"  Duration: {duration:.2f}s ({duration/60:.2f} min)")

    return {
        'mode': mode,
        'threshold': threshold,
        'cycles': cycles,
        'intervention_interval': intervention_interval,
        'final_memory': final_memory,
        'final_diversity': final_diversity,
        'total_bursts': total_bursts,
        'burst_rate': burst_rate,
        'final_efficiency': final_efficiency,
        'total_interventions': total_interventions,
        'temporal_data': temporal_data,
        'temporal_analysis': {
            'collapse_cycle': collapse_cycle,
            'sustained_diversity_cycles': sustained_cycles,
            'entropy_oscillation': entropy_oscillation
        },
        'duration': duration
    }

def main():
    """Run active diversity maintenance study."""
    print("="*80)
    print("CYCLE 79: ACTIVE DIVERSITY MAINTENANCE (INTERVENTION STUDY)")
    print("="*80)
    print()
    print("Testing whether periodic diversity injection can counteract entropy collapse.")
    print("Following Cycle 78: Universal entropy collapse discovered")
    print("Question: Can active maintenance sustain diversity?")
    print()

    # Test exploration regime (500) with two conditions
    threshold = 500
    cycles = 1000

    print(f"Testing threshold: {threshold} (exploration regime)")
    print(f"Duration: {cycles} cycles")
    print()
    print("CONDITIONS:")
    print("  1. PASSIVE: No intervention (C78 baseline)")
    print("  2. ACTIVE: Re-seed every 100 cycles")
    print("="*80)

    results = []
    overall_start = time.time()

    # Condition 1: Passive baseline
    try:
        print("\n" + "="*80)
        print("CONDITION 1: PASSIVE BASELINE")
        print("="*80)
        result_passive = run_maintenance_test(threshold, cycles=cycles, intervention_interval=None)
        results.append(result_passive)
        time.sleep(1.0)
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        import traceback
        traceback.print_exc()
        results.append({'mode': 'PASSIVE', 'error': str(e)})

    # Condition 2: Active maintenance
    try:
        print("\n" + "="*80)
        print("CONDITION 2: ACTIVE MAINTENANCE")
        print("="*80)
        result_active = run_maintenance_test(threshold, cycles=cycles, intervention_interval=100)
        results.append(result_active)
        time.sleep(1.0)
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        import traceback
        traceback.print_exc()
        results.append({'mode': 'ACTIVE', 'error': str(e)})

    overall_duration = time.time() - overall_start

    # Comparative analysis
    successful = [r for r in results if 'error' not in r]

    if len(successful) == 2:
        passive = successful[0]
        active = successful[1]

        print(f"\n{'='*80}")
        print(f"MAINTENANCE EFFECTIVENESS ANALYSIS")
        print(f"{'='*80}\n")

        print(f"{'Condition':>15} | {'Collapse':>10} | {'Sustained':>10} | {'Final Entropy':>13} | {'Oscillation':>11}")
        print("-" * 80)

        passive_collapse = passive['temporal_analysis']['collapse_cycle'] if passive['temporal_analysis']['collapse_cycle'] else "Never"
        active_collapse = active['temporal_analysis']['collapse_cycle'] if active['temporal_analysis']['collapse_cycle'] else "Never"

        print(f"{'PASSIVE':>15} | {str(passive_collapse):>10} | {passive['temporal_analysis']['sustained_diversity_cycles']:>10} | {passive['final_diversity']['shannon_entropy']:>13.3f} | {passive['temporal_analysis']['entropy_oscillation']:>11.3f}")
        print(f"{'ACTIVE':>15} | {str(active_collapse):>10} | {active['temporal_analysis']['sustained_diversity_cycles']:>10} | {active['final_diversity']['shannon_entropy']:>13.3f} | {active['temporal_analysis']['entropy_oscillation']:>11.3f}")
        print()

        # Determine if maintenance worked
        passive_sustained = passive['temporal_analysis']['sustained_diversity_cycles']
        active_sustained = active['temporal_analysis']['sustained_diversity_cycles']

        if active_sustained > passive_sustained * 1.5:
            print(f"✅ ACTIVE MAINTENANCE EFFECTIVE!")
            print(f"   Diversity sustained {active_sustained - passive_sustained} cycles longer")
            print(f"   Intervention cost: {active['total_interventions']} re-seedings")
            maintenance_effective = True
        elif active['final_diversity']['shannon_entropy'] > 0.5:
            print(f"✅ ACTIVE MAINTENANCE SUSTAINED DIVERSITY!")
            print(f"   Final entropy: {active['final_diversity']['shannon_entropy']:.3f} bits (vs {passive['final_diversity']['shannon_entropy']:.3f})")
            print(f"   Intervention cost: {active['total_interventions']} re-seedings")
            maintenance_effective = True
        else:
            print(f"❌ ACTIVE MAINTENANCE INSUFFICIENT")
            print(f"   Diversity still collapsed despite intervention")
            print(f"   May require higher intervention frequency")
            maintenance_effective = False

        print()

        if maintenance_effective:
            print(f"🎉 INSIGHT #42 DISCOVERED: Active Diversity Maintenance Can Extend Lifespan")
            print(f"   - Periodic intervention counteracts natural entropy collapse")
            print(f"   - Diversity requires continuous energy input to persist")
            print(f"   - Trade-off: Stability vs variety (intervention cost)")
            insight_42 = True
        else:
            print(f"   Insight: Intervention frequency may need adjustment")
            insight_42 = False

        print("="*80)
    else:
        print("⚠️ Incomplete results")
        insight_42 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "diversity_maintenance"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle79_active_diversity_maintenance.json"

    output_data = {
        'experiment': 'cycle79_active_diversity_maintenance',
        'threshold': threshold,
        'cycles': cycles,
        'conditions': ['passive', 'active_100cycles'],
        'results': results,
        'insight_42_discovered': insight_42,
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
