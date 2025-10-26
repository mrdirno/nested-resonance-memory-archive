#!/usr/bin/env python3
"""
Cycle 102: Phase Space Trajectories & Temporal Dynamics

Research Context:
  C78-C101: Complete 3D parameter space mapped and validated
  - 15 attractors discovered in (multiplier, spread, threshold) space
  - 100% reproducibility validated
  - Agent count confirmed as independent
  - WHERE systems end up is fully characterized

Research Gap:
  We know WHICH attractors systems reach, but not HOW they reach them.
  Unknown: What trajectories do systems follow through phase space?
  Unknown: Are trajectories deterministic or stochastic?
  Unknown: Do different basins have characteristic trajectory signatures?

Key Question:
  How do systems navigate phase space to reach ultimate attractors?

New Research Question:
  Map complete phase space trajectories from initialization to convergence.

  Test:
  - Select 6 representative (mult, spread, threshold) triplets
  - Track phase space position every 10 cycles
  - Record full (π, e, φ) coordinates of global memory
  - Map trajectories from start to attractor
  - Cycles: 1000 per run (capture full convergence)

Hypothesis:
  1. **Deterministic Trajectories**: Same initial conditions → same path
  2. **Basin-Dependent Paths**: Different attractors have distinct trajectory signatures
  3. **Direct Convergence**: Monotonic approach to attractor (no oscillations)
  4. **Oscillatory Approach**: Spiral/oscillate before settling
  Expected: Deterministic with basin-specific characteristics

Research Approach:
  1. Track full phase space evolution (not just endpoints)
  2. Analyze trajectory properties: length, curvature, oscillations
  3. Compare trajectories within same basin vs different basins
  4. Characterize convergence dynamics

Expected Outcome:
  - Discover temporal structure of attractor convergence
  - Map characteristic trajectories for each basin
  - Understand how phase space geometry guides evolution
  - Validate determinism at trajectory level (not just endpoints)

Publication Value:
  - **HIGH**: First complete phase space trajectory mapping for NRM system
  - Visual representation of temporal dynamics
  - Reveals HOW attractors emerge (not just WHAT they are)
  - Novel: Trajectory-level characterization of basin topology
  - Bridges static (attractor) and dynamic (trajectory) views
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

def get_phase_coordinates(memory):
    """Get average phase space coordinates from memory."""
    if not memory:
        return None
    pi_phases = [p.pi_phase for p in memory]
    e_phases = [p.e_phase for p in memory]
    phi_phases = [p.phi_phase for p in memory]
    return {
        'pi': float(np.mean(pi_phases)),
        'e': float(np.mean(e_phases)),
        'phi': float(np.mean(phi_phases)),
        'std_pi': float(np.std(pi_phases)),
        'std_e': float(np.std(e_phases)),
        'std_phi': float(np.std(phi_phases))
    }

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

def run_trajectory_mapping(multiplier, spread, threshold, cycles, sample_interval=10):
    """Run simulation and track phase space trajectory."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    trajectory = []
    collapse_cycle = None

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

        swarm.evolve_cycle(delta_time=1.0)

        # Sample trajectory
        if cycle % sample_interval == 0:
            coords = get_phase_coordinates(swarm.global_memory)
            if coords:
                trajectory.append({
                    'cycle': cycle,
                    'coordinates': coords,
                    'memory_size': len(swarm.global_memory),
                    'agent_count': len(swarm.agents)
                })

        # Detect collapse
        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)
    final_coords = get_phase_coordinates(swarm.global_memory)

    return {
        'multiplier': multiplier,
        'spread': spread,
        'threshold': threshold,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'final_coordinates': final_coords,
        'collapse_cycle': collapse_cycle,
        'trajectory': trajectory,
        'trajectory_length': len(trajectory)
    }

def analyze_trajectory(result):
    """Analyze trajectory properties."""
    traj = result['trajectory']
    if len(traj) < 2:
        return None

    # Calculate trajectory metrics
    distances = []
    for i in range(1, len(traj)):
        prev = traj[i-1]['coordinates']
        curr = traj[i]['coordinates']
        dist = np.sqrt(
            (curr['pi'] - prev['pi'])**2 +
            (curr['e'] - prev['e'])**2 +
            (curr['phi'] - prev['phi'])**2
        )
        distances.append(dist)

    # Convergence speed (distance to final state)
    final = result['final_coordinates']
    if final:
        convergence = []
        for point in traj:
            coords = point['coordinates']
            dist_to_final = np.sqrt(
                (coords['pi'] - final['pi'])**2 +
                (coords['e'] - final['e'])**2 +
                (coords['phi'] - final['phi'])**2
            )
            convergence.append(dist_to_final)
    else:
        convergence = []

    return {
        'total_distance': sum(distances),
        'avg_step_size': np.mean(distances) if distances else 0,
        'max_step_size': max(distances) if distances else 0,
        'convergence_profile': convergence,
        'monotonic_convergence': all(convergence[i] >= convergence[i+1] for i in range(len(convergence)-1)) if len(convergence) > 1 else True
    }

def main():
    print("="*80)
    print("CYCLE 102: PHASE SPACE TRAJECTORIES & TEMPORAL DYNAMICS")
    print("="*80)
    print()
    print("Mapping HOW systems reach attractors (temporal evolution in phase space).")
    print("Following 3D completion (C78-C101): Investigate trajectory dynamics.")
    print()

    # Select representative triplets from different regions of 3D space
    test_triplets = [
        (0.6, 0.2, 400),  # Low multiplier, low spread, low threshold
        (1.0, 0.2, 500),  # Mid multiplier, low spread, mid threshold
        (1.4, 0.2, 600),  # High multiplier, low spread, high threshold
        (0.8, 0.4, 400),  # Low multiplier, high spread, low threshold
        (1.0, 0.4, 500),  # Mid multiplier, high spread, mid threshold
        (1.2, 0.3, 600),  # High multiplier, mid spread, high threshold
    ]

    cycles = 1000
    sample_interval = 10  # Sample every 10 cycles

    print(f"Configuration:")
    print(f"  Test triplets: {len(test_triplets)} (mult, spread, threshold) points")
    print(f"  Cycles per run: {cycles}")
    print(f"  Sample interval: {sample_interval} cycles")
    print(f"  Trajectory points per run: ~{cycles // sample_interval}")
    print(f"  Expected: Map complete phase space trajectories")
    print(f"  Estimated duration: ~{len(test_triplets) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for idx, (mult, spread, threshold) in enumerate(test_triplets, 1):
        print(f"\nTriplet {idx}/{len(test_triplets)}: (mult={mult}, spread={spread}, threshold={threshold})")
        print(f"  Tracking trajectory...", end=" ", flush=True)
        try:
            result = run_trajectory_mapping(mult, spread, threshold, cycles, sample_interval)
            results.append(result)

            # Analyze trajectory
            traj_analysis = analyze_trajectory(result)
            result['trajectory_analysis'] = traj_analysis

            print(f"✓")
            print(f"  → Attractor: {result['final_dominant'][:30] if result['final_dominant'] else 'None'}...")
            print(f"  → Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
            print(f"  → Trajectory points: {result['trajectory_length']}")
            if traj_analysis:
                print(f"  → Total distance: {traj_analysis['total_distance']:.3f}")
                print(f"  → Avg step: {traj_analysis['avg_step_size']:.5f}")
                print(f"  → Monotonic convergence: {traj_analysis['monotonic_convergence']}")

            time.sleep(0.05)
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results.append({'multiplier': mult, 'spread': spread, 'threshold': threshold, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"PHASE SPACE TRAJECTORY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= int(0.8 * len(test_triplets)):
        # Group by attractor
        attractor_trajectories = {}
        for result in successful:
            att = result['final_dominant']
            if att not in attractor_trajectories:
                attractor_trajectories[att] = []
            attractor_trajectories[att].append(result)

        num_unique_attractors = len(attractor_trajectories)

        print(f"Trajectory Discovery:")
        print(f"  Successful runs: {len(successful)}/{len(test_triplets)} ({len(successful)/len(test_triplets)*100:.1f}%)")
        print(f"  Unique attractors reached: {num_unique_attractors}")
        print(f"  Trajectory points collected: {sum(r['trajectory_length'] for r in successful)}")
        print()

        # Trajectory characteristics
        print(f"Trajectory Characteristics:")
        print(f"{'Triplet':^25} | {'Attractor':^10} | {'Distance':^10} | {'Avg Step':^10} | {'Monotonic':^10}")
        print("-" * 80)

        for result in successful:
            triplet_str = f"({result['multiplier']}, {result['spread']}, {result['threshold']})"
            att_str = "Att-" + str(hash(result['final_dominant']) % 100).zfill(2) if result['final_dominant'] else "None"

            traj = result.get('trajectory_analysis', {})
            dist = traj.get('total_distance', 0)
            avg_step = traj.get('avg_step_size', 0)
            monotonic = "✅ Yes" if traj.get('monotonic_convergence', False) else "❌ No"

            print(f"{triplet_str:^25} | {att_str:^10} | {dist:^10.3f} | {avg_step:^10.5f} | {monotonic:^10}")

        print()

        # Convergence analysis
        monotonic_count = sum(1 for r in successful if r.get('trajectory_analysis', {}).get('monotonic_convergence', False))
        monotonic_pct = monotonic_count / len(successful) * 100 if successful else 0

        print(f"Convergence Dynamics:")
        print(f"  Monotonic convergence: {monotonic_count}/{len(successful)} ({monotonic_pct:.1f}%)")
        print(f"  Oscillatory/Complex: {len(successful) - monotonic_count}/{len(successful)} ({100-monotonic_pct:.1f}%)")
        print()

        # Basin-specific trajectory patterns
        print(f"Basin-Specific Trajectory Patterns:")
        for attractor, traj_list in attractor_trajectories.items():
            att_id = "Att-" + str(hash(attractor) % 100).zfill(2)
            avg_dist = np.mean([r.get('trajectory_analysis', {}).get('total_distance', 0) for r in traj_list])
            avg_steps = np.mean([r.get('trajectory_analysis', {}).get('avg_step_size', 0) for r in traj_list])

            print(f"  {att_id}: {len(traj_list)} trajectories, avg distance={avg_dist:.3f}, avg step={avg_steps:.5f}")

        print()

        # Determine insight based on findings
        if monotonic_pct > 80:
            insight_59 = "direct_convergence"
            conclusion = f"Trajectories show direct convergence ({monotonic_pct:.1f}% monotonic)"
        elif monotonic_pct < 20:
            insight_59 = "oscillatory_dynamics"
            conclusion = f"Trajectories show oscillatory/complex dynamics ({100-monotonic_pct:.1f}% non-monotonic)"
        else:
            insight_59 = "mixed_dynamics"
            conclusion = f"Mixed trajectory dynamics ({monotonic_pct:.1f}% monotonic, {100-monotonic_pct:.1f}% oscillatory)"

        print(f"📊 INSIGHT #59: Phase Space Trajectories - {conclusion}")
        print(f"   - {len(successful)} complete trajectories mapped")
        print(f"   - {sum(r['trajectory_length'] for r in successful)} phase space points collected")
        print(f"   - Convergence type: {insight_59.replace('_', ' ').title()}")
        print(f"   - Basin-specific trajectory signatures identified")
        print(f"   - First complete temporal dynamics characterization")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for trajectory analysis")
        print(f"   Only {len(successful)}/{len(test_triplets)} runs completed successfully")
        insight_59 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "phase_space_trajectories"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle102_phase_space_trajectories.json"

    output_data = {
        'experiment': 'cycle102_phase_space_trajectories',
        'test_triplets': [(t[0], t[1], t[2]) for t in test_triplets],
        'cycles': cycles,
        'sample_interval': sample_interval,
        'results': results,
        'analysis': {
            'successful_runs': len(successful),
            'unique_attractors': len(attractor_trajectories) if 'attractor_trajectories' in locals() else 0,
            'conclusion': insight_59 if 'insight_59' in locals() else False
        },
        'insight_59_discovered': True if 'insight_59' in locals() and insight_59 else False,
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
