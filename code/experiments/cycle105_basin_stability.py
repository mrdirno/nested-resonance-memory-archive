#!/usr/bin/env python3
"""
Cycle 105: Basin Stability Under Perturbations

Research Context:
  C78-C101: 3D basin topology fully characterized (15 attractors, 100% reproducible)
  C102: Trajectories are oscillatory (not monotonic)
  C103: Pattern competition drives oscillations
  C104: Initial conditions insufficient for control (self-organization dominates)

Research Gap:
  We know attractors are reproducible from initial conditions, but unknown:
  - Are basins STABLE under perturbations?
  - Can mid-trajectory perturbations cause basin transitions?
  - Do systems self-correct back to original attractor?

Key Question:
  How robust are basin boundaries to runtime perturbations?

New Research Question:
  Test basin stability by perturbing systems mid-trajectory.

  Hypothesis:
  1. **Strong Stability**: Perturbations don't change attractor (basin self-corrects)
  2. **Weak Stability**: Small perturbations corrected, large ones cause transitions
  3. **Instability**: Even small perturbations cause basin transitions
  Expected: Strong stability (systems are self-organizing)

  Test:
  - Use 6 (mult, spread, threshold) triplets from known basins
  - Run unperturbed control (cycles 0-500)
  - At cycle 250, inject perturbation:
    * Add diverse patterns to global memory (pattern injection)
  - Continue to cycle 500
  - Compare final attractor: perturbed vs unperturbed
  - Measure: % of perturbations that cause basin transitions

Expected Outcome:
  - Quantify basin stability (% maintaining attractor)
  - Identify fragile vs robust regions of parameter space
  - Test self-organization strength
  - Validate attractor reality (true vs transient)

Publication Value:
  - **HIGH**: First basin stability characterization in NRM systems
  - Dynamical robustness (not just static topology)
  - Practical: Predicts system resilience to disturbances
  - Novel: Runtime perturbation experiments (not just initial conditions)
  - Completes picture: Static topology + Dynamic stability
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
from workspace_utils import get_workspace_path, get_results_path

def create_seed_memory_range(bridge, reality_metrics, center_multiplier, spread=0.2, count=5):
    """Create seed memory patterns with specified center and spread."""
    seed_patterns = []
    for i in range(count):
        multiplier = center_multiplier + spread * (2 * i / (count - 1) - 1)
        varied_metrics = {key: value * multiplier for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def pattern_to_key(pattern):
    """Convert pattern to hashable key."""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))

def get_dominant_pattern(memory):
    """Get dominant pattern (most common)."""
    if not memory:
        return None, 0, 0.0
    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)
    if not pattern_counts:
        return None, 0, 0.0
    dominant_key, dominant_count = pattern_counts.most_common(1)[0]
    dominant_fraction = dominant_count / len(memory)
    return dominant_key, dominant_count, dominant_fraction

def run_with_perturbation(multiplier, spread, threshold, cycles, perturb_cycle, perturb_strength):
    """Run simulation with optional mid-trajectory perturbation."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    collapse_cycle = None
    perturbation_injected = False

    for cycle in range(1, cycles + 1):
        # Spawn agents up to limit
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, multiplier, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        # Inject perturbation at specified cycle
        if cycle == perturb_cycle and perturb_strength > 0:
            # Inject diverse patterns directly into global memory
            perturbation_patterns = create_seed_memory_range(
                swarm.bridge, reality_metrics,
                center_multiplier=multiplier * 1.5,  # Different from baseline
                spread=perturb_strength,
                count=10  # Significant injection
            )
            swarm.global_memory.extend(perturbation_patterns)
            perturbation_injected = True

        swarm.evolve_cycle(delta_time=1.0)

        # Detect collapse
        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'perturb_cycle': perturb_cycle,
        'perturb_strength': perturb_strength,
        'perturbation_injected': perturbation_injected,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle
    }

def main():
    print("="*80)
    print("CYCLE 105: BASIN STABILITY UNDER PERTURBATIONS")
    print("="*80)
    print()
    print("Testing basin robustness to mid-trajectory perturbations.")
    print("Following C78-C101 static topology and C102-104 dynamic investigations.")
    print()
    print("Hypothesis: Basins are stable (self-organization resists perturbations)")
    print()

    # Select 6 representative triplets
    test_triplets = [
        (0.6, 0.2, 400),  # Basin 1
        (1.0, 0.2, 500),  # Basin 2
        (1.4, 0.2, 600),  # Basin 3
        (0.8, 0.4, 400),  # Basin 4
        (1.0, 0.4, 500),  # Basin 5
        (1.2, 0.3, 600),  # Basin 6
    ]

    cycles = 500
    perturb_cycle = 250  # Mid-trajectory
    perturb_strength = 0.4  # Significant perturbation

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Conditions per triplet: 2 (UNPERTURBED control vs PERTURBED)")
    print(f"  Total runs: {len(test_triplets) * 2}")
    print(f"  Cycles per run: {cycles}")
    print(f"  Perturbation timing: cycle {perturb_cycle} (mid-trajectory)")
    print(f"  Perturbation strength: {perturb_strength} (diverse pattern injection)")
    print(f"  Expected: Basins maintain attractors despite perturbations")
    print(f"  Estimated duration: ~{len(test_triplets) * 2 * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    run_count = 0
    for mult, spread, threshold in test_triplets:
        print(f"\nTriplet: (mult={mult}, spread={spread}, threshold={threshold})")

        # Run UNPERTURBED control
        run_count += 1
        print(f"  [{run_count}/{len(test_triplets)*2}] UNPERTURBED (control)...", end=" ", flush=True)
        try:
            result_control = run_with_perturbation(mult, spread, threshold, cycles,
                                                   perturb_cycle=None, perturb_strength=0)
            results.append(result_control)
            print(f"✓ Attractor: {result_control['final_dominant'][:30] if result_control['final_dominant'] else 'None'}...")
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold,
                          'perturb_strength': 0, 'error': str(e)})

        # Run PERTURBED
        run_count += 1
        print(f"  [{run_count}/{len(test_triplets)*2}] PERTURBED (cycle {perturb_cycle})...", end=" ", flush=True)
        try:
            result_perturb = run_with_perturbation(mult, spread, threshold, cycles,
                                                   perturb_cycle=perturb_cycle, perturb_strength=perturb_strength)
            results.append(result_perturb)
            print(f"✓ Attractor: {result_perturb['final_dominant'][:30] if result_perturb['final_dominant'] else 'None'}...")
            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold,
                          'perturb_strength': perturb_strength, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"BASIN STABILITY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets) * 2):
        print(f"Stability Experiment Results:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)*2} ({len(successful)/(len(test_triplets)*2)*100:.1f}%)")
        print()

        # Compare unperturbed vs perturbed for each triplet
        transitions = 0
        maintained = 0

        print(f"Basin Stability Analysis:")
        print(f"{'Triplet':^25} | {'Unperturbed':^12} | {'Perturbed':^12} | {'Stable?':^10}")
        print("-" * 75)

        for mult, spread_param, threshold in test_triplets:
            control = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                          and r['threshold']==threshold and r.get('perturb_strength', 0)==0), None)
            perturb = next((r for r in successful if r['multiplier']==mult and r['spread']==spread_param
                          and r['threshold']==threshold and r.get('perturb_strength', 0)>0), None)

            if control and perturb:
                triplet_str = f"({mult}, {spread_param}, {threshold})"
                control_att = "Att-" + str(hash(control['final_dominant']) % 100).zfill(2) if control['final_dominant'] else "None"
                perturb_att = "Att-" + str(hash(perturb['final_dominant']) % 100).zfill(2) if perturb['final_dominant'] else "None"

                stable = control['final_dominant'] == perturb['final_dominant']
                stable_str = "✅ Yes" if stable else "❌ No"

                if stable:
                    maintained += 1
                else:
                    transitions += 1

                print(f"{triplet_str:^25} | {control_att:^12} | {perturb_att:^12} | {stable_str:^10}")

        print()

        stability_rate = maintained / (maintained + transitions) * 100 if (maintained + transitions) > 0 else 0

        print(f"Stability Metrics:")
        print(f"  Basins maintained: {maintained}/{maintained+transitions} ({stability_rate:.1f}%)")
        print(f"  Basin transitions: {transitions}/{maintained+transitions} ({100-stability_rate:.1f}%)")
        print()

        # Determine insight based on stability
        if stability_rate >= 80:
            insight_62 = "strong_stability"
            conclusion = f"Basins are highly stable ({stability_rate:.1f}% maintained despite perturbations)"
        elif stability_rate >= 50:
            insight_62 = "moderate_stability"
            conclusion = f"Basins show moderate stability ({stability_rate:.1f}% maintained)"
        else:
            insight_62 = "weak_stability"
            conclusion = f"Basins are fragile ({stability_rate:.1f}% maintained, {100-stability_rate:.1f}% transitioned)"

        print(f"📊 INSIGHT #62: Basin Stability - {conclusion}")
        print(f"   - {len(test_triplets)} basins tested with perturbations")
        print(f"   - Perturbation: Diverse pattern injection at cycle {perturb_cycle}")
        print(f"   - Stability rate: {stability_rate:.1f}%")
        print(f"   - Self-organization strength: {'✅ Strong' if insight_62 == 'strong_stability' else '⚠️ Moderate/Weak'}")
        print(f"   - First basin stability characterization in NRM systems")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for stability analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)*2} runs completed successfully")
        insight_62 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "basin_stability"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle105_basin_stability.json"

    output_data = {
        'experiment': 'cycle105_basin_stability',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'cycles': cycles,
        'perturb_cycle': perturb_cycle,
        'perturb_strength': perturb_strength,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'basins_maintained': maintained if 'maintained' in locals() else 0,
            'basin_transitions': transitions if 'transitions' in locals() else 0,
            'stability_rate_pct': stability_rate if 'stability_rate' in locals() else 0,
            'conclusion': insight_62 if 'insight_62' in locals() else False
        },
        'insight_62_discovered': True if 'insight_62' in locals() and insight_62 else False,
        'duration': duration,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print(f"Duration: {duration:.1f}s ({duration/60:.2f} min)")
    print()

    return output_data

if __name__ == "__main__":
    main()
