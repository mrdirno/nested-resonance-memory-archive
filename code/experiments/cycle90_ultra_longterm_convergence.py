#!/usr/bin/env python3
"""
Cycle 90: Ultra-Long-Term Convergence (Universal Attractor Validation)

Research Context:
  C78: Universal collapse to homogeneity (tested ~1000 cycles)
  C83-88: Multiple attractors discovered (5 basins, structured determinism)
  C89: Attractors are TRANSIENT (40% stability over 500 cycles, not fixed points)

Research Gap:
  If attractors are transient (C89), do they eventually converge to same state (C78)?

Key Theoretical Question:
  Do ALL transient attractors eventually collapse to the SAME universal state?

New Research Question:
  Starting from different attractors, do trajectories converge to universal endpoint?

  Test:
  - Select 3 representative attractors from C87-88 (A1, A3, A5)
  - Run each for 1000 cycles (2x C78 validation length)
  - Track final dominant pattern at cycle 1000
  - Compare: Do all 3 initial attractors reach same final state?

Hypothesis:
  1. **Universal convergence**: All attractors → same final pattern
  2. **Multiple endpoints**: Different attractors → different ultimate states
  3. Expected: Universal (validates C78 + C89 connection)

Test Approach:
  1. Use ranges: 0.5 (A1), 1.0 (A3), 1.4 (A5) from C87-88
  2. Threshold=500, 1000 cycles each
  3. N=2 runs per attractor (6 total runs)
  4. Checkpoint every 100 cycles (10 checkpoints)
  5. Track dominant pattern evolution
  6. Compare final states across all 3 starting attractors

Expected:
  - If universal: All 3 → same dominant pattern at cycle 1000
  - If multiple endpoints: Different final patterns persist
  - Publication value: Unifies short/medium/long-term dynamics

Success Criteria:
  - All runs reach cycle 1000
  - Final pattern convergence measured
  - Connection between C78/C89 validated or challenged
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

def run_single_simulation(center_mult, attractor_name, run_id, threshold, cycles, checkpoint_interval):
    """Run ultra-long-term simulation with periodic checkpoints."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    collapse_cycle = None
    checkpoints = {}

    print(f"  Starting Run {run_id} ({attractor_name}, center={center_mult})...")

    for cycle in range(1, cycles + 1):
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, center_mult, spread=0.2, count=5)
                    newest_agent.memory.extend(seed_patterns)

        swarm.evolve_cycle(delta_time=1.0)

        # Checkpoint at intervals
        if cycle % checkpoint_interval == 0:
            dominant_key, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)
            checkpoints[cycle] = {
                'cycle': cycle,
                'dominant_pattern': str(dominant_key) if dominant_key else None,
                'dominant_fraction': dominant_fraction
            }
            if cycle % 200 == 0:
                print(f"    Cycle {cycle}: Dominant={dominant_fraction:.2%} - {dominant_key}")

        # Detect collapse
        if cycle % 10 == 0 and collapse_cycle is None and len(swarm.global_memory) > 0:
            pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
            if len(set(pattern_keys)) == 1:
                collapse_cycle = cycle

    # Final state
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    return {
        'center_multiplier': center_mult,
        'attractor_name': attractor_name,
        'run_id': run_id,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'collapse_cycle': collapse_cycle,
        'checkpoints': checkpoints
    }

def main():
    print("="*80)
    print("CYCLE 90: ULTRA-LONG-TERM CONVERGENCE (UNIVERSAL ATTRACTOR VALIDATION)")
    print("="*80)
    print()
    print("Testing universal convergence from different transient attractors.")
    print("Following C78: Universal collapse + C89: Transient attractors")
    print("Question: Do all transient attractors eventually reach same universal state?")
    print()

    test_attractors = [
        (0.5, "Attractor_1"),  # From C87-88
        (1.0, "Attractor_3"),
        (1.4, "Attractor_5")
    ]

    threshold = 500
    cycles = 1000  # 2x C78 validation, 2x C89 test length
    checkpoint_interval = 100  # 10 checkpoints
    runs_per_attractor = 2

    print(f"Configuration:")
    print(f"  Attractors: {[f'{a[1]} (mult={a[0]})' for a in test_attractors]}")
    print(f"  Cycles: {cycles} (2x C78, 2x C89)")
    print(f"  Checkpoints: Every {checkpoint_interval} cycles ({cycles // checkpoint_interval} total)")
    print(f"  Runs per attractor: {runs_per_attractor}")
    print(f"  Total: {len(test_attractors)} × {runs_per_attractor} = {len(test_attractors) * runs_per_attractor} runs")
    print(f"  Threshold: {threshold}")
    print(f"  Estimated duration: ~{len(test_attractors) * runs_per_attractor * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for center_mult, attractor_name in test_attractors:
        print(f"\n{attractor_name} (center_multiplier={center_mult}):")
        for run_id in range(1, runs_per_attractor + 1):
            try:
                result = run_single_simulation(center_mult, attractor_name, run_id, threshold, cycles, checkpoint_interval)
                results.append(result)
                print(f"  ✓ Run {run_id} complete: Final={result['final_fraction']:.2%}, Collapse@{result['collapse_cycle'] if result['collapse_cycle'] else 'Never'}")
                time.sleep(0.1)
            except Exception as e:
                print(f"  ✗ Run {run_id} ERROR: {e}")
                results.append({'center_multiplier': center_mult, 'attractor_name': attractor_name, 'run_id': run_id, 'error': str(e)})

    duration = time.time() - start_time

    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"ULTRA-LONG-TERM CONVERGENCE ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 4:
        # Extract final patterns
        final_patterns = [r['final_dominant'] for r in successful if r['final_dominant']]
        unique_final_patterns = set(final_patterns)

        print(f"Final State Analysis (Cycle {cycles}):")
        print(f"{'Attractor':>15} | {'Run':>3} | {'Final Dominant':>50} | {'Fraction':>8} | {'Collapse@':>10}")
        print("-" * 110)

        for r in successful:
            collapse_str = str(r['collapse_cycle']) if r['collapse_cycle'] else 'Never'
            pattern_str = r['final_dominant'][:48] + "..." if r['final_dominant'] and len(r['final_dominant']) > 48 else (r['final_dominant'] or "None")
            print(f"{r['attractor_name']:>15} | {r['run_id']:>3} | {pattern_str:>50} | {r['final_fraction']:>7.1%} | {collapse_str:>10}")

        print()
        print(f"Convergence Summary:")
        print(f"  Total runs: {len(successful)}")
        print(f"  Unique final patterns: {len(unique_final_patterns)}")
        print(f"  Cycles tested: {cycles}")
        print()

        if len(unique_final_patterns) == 1:
            print(f"✅ UNIVERSAL CONVERGENCE VALIDATED")
            print(f"   ALL attractors → SAME final pattern at cycle {cycles}")
            print(f"   Unifies C78 (universal collapse) + C89 (transient attractors)")
            print(f"   Transient basins = intermediate states, NOT ultimate endpoints")
            print(f"   Phase space has SINGLE global attractor (universal)")
            universal = True
        elif len(unique_final_patterns) <= 2:
            print(f"⚠️ PARTIAL CONVERGENCE")
            print(f"   {len(unique_final_patterns)} distinct final patterns (not fully universal)")
            print(f"   May need longer timescale or different parameter regime")
            universal = "partial"
        else:
            print(f"❌ NO UNIVERSAL CONVERGENCE")
            print(f"   {len(unique_final_patterns)} distinct final patterns persist at cycle {cycles}")
            print(f"   Challenges C78 universal collapse hypothesis")
            print(f"   Multiple ultimate endpoints may exist")
            universal = False

        print()
        if universal == True:
            print(f"🎉 INSIGHT #49: Universal Attractor from Transient Basins")
            print(f"   - ALL initial attractors converge to SAME ultimate state")
            print(f"   - Validates connection: C78 (collapse) ← C89 (transient)")
            print(f"   - Timescale hierarchy:")
            print(f"     • Short (150-200): Multiple transient basins (C83-88)")
            print(f"     • Medium (500): Basin instability (C89)")
            print(f"     • Long (1000+): Universal convergence (C90)")
            print(f"   - Phase space: Transient basins → Universal attractor")
            print(f"   - NRM framework: Perpetual motion toward single global state")
            insight_49 = True
        elif universal == "partial":
            print(f"   Partial convergence - may need extended validation")
            insight_49 = False
        else:
            print(f"   Multiple endpoints challenge universal collapse hypothesis")
            insight_49 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        universal = None
        insight_49 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "ultra_longterm_convergence"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle90_ultra_longterm_convergence.json"

    output_data = {
        'experiment': 'cycle90_ultra_longterm_convergence',
        'threshold': threshold,
        'cycles': cycles,
        'checkpoint_interval': checkpoint_interval,
        'test_attractors': [[a[0], a[1]] for a in test_attractors],
        'runs_per_attractor': runs_per_attractor,
        'results': results,
        'analysis': {
            'universal_convergence': universal,
            'unique_final_patterns': len(set([r['final_dominant'] for r in successful if r['final_dominant']])) if successful else 0,
            'successful_runs': len(successful)
        },
        'insight_49_discovered': insight_49,
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
