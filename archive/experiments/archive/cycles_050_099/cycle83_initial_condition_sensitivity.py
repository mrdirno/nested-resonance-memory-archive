#!/usr/bin/env python3
"""
Cycle 83: Initial Condition Sensitivity (Determinism Source Test)

Research Context:
  Cycle 82: Perfect reproducibility - 5/5 runs → identical dominant
  - All runs used identical initial seed patterns
  - Collapse @ cycle 160, dominant = 51.80% (perfect match)
  - Deterministic convergence confirmed

Research Gap:
  C82 tested identical initial conditions only
  Unknown: Does varying INITIAL CONDITIONS break reproducibility?
  Source of determinism unclear: Algorithm vs Initial Conditions?

New Research Question:
  Does varying seed patterns produce different final dominant patterns?

  Test:
  - Condition A: Standard seeds (C82 baseline)
  - Condition B: Modified seeds (±20% variation)
  - Condition C: Random seeds (large variation)
  - Compare final dominants across conditions
  - Determine if initial conditions determine outcome

Hypothesis:
  1. Algorithm determinism: All conditions → same dominant (insensitive to seeds)
  2. Initial condition sensitivity: Different conditions → different dominants
  3. Expected: Initial condition sensitivity (validates Self-Giving variability)
  4. Insight: System trajectory depends on seed patterns (not just algorithm)

Test Approach:
  1. Run 3 conditions with N=3 runs each (9 total simulations)
  2. Condition A: Standard seeds (0.8-1.2x reality metrics)
  3. Condition B: Modified seeds (0.6-1.4x reality metrics, ±20% shift)
  4. Condition C: Wide seeds (0.4-1.6x reality metrics, ±40% shift)
  5. Threshold=500, 200 cycles per run
  6. Compare final dominant patterns within and across conditions

Expected:
  - If algorithm deterministic: All 9 runs → same dominant
  - If initial condition sensitive: Different conditions → different dominants
  - Quantify: Cross-condition diversity vs within-condition reproducibility
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

def create_seed_memory_standard(bridge: TranscendentalBridge, reality_metrics: dict, count: int = 5) -> list:
    """Create standard seed memory patterns (C82 baseline)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.8 + 0.4 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def create_seed_memory_modified(bridge: TranscendentalBridge, reality_metrics: dict, count: int = 5) -> list:
    """Create modified seed memory patterns (±20% shift)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.6 + 0.8 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def create_seed_memory_wide(bridge: TranscendentalBridge, reality_metrics: dict, count: int = 5) -> list:
    """Create wide-range seed memory patterns (±40% shift)."""
    seed_patterns = []
    for i in range(count):
        varied_metrics = {key: value * (0.4 + 1.2 * (i / count)) for key, value in reality_metrics.items()}
        phase_state = bridge.reality_to_phase(varied_metrics)
        seed_patterns.append(phase_state)
    return seed_patterns

def pattern_to_key(pattern) -> tuple:
    """Convert pattern to hashable key."""
    return tuple(np.round([pattern.pi_phase, pattern.e_phase, pattern.phi_phase], 6))

def get_dominant_pattern(memory: list) -> tuple:
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

def run_single_simulation(condition: str, run_id: int, threshold: float, cycles: int, seed_fn) -> dict:
    """Run a single independent simulation with specific seed function."""
    print(f"    {condition}-{run_id}: Starting...")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    start_time = time.time()
    collapse_cycle = None

    for cycle in range(1, cycles + 1):
        # Standard evolution with VARIED seeding per condition
        if len(swarm.agents) < 15:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_agent = swarm.agents[agent_ids[-1]]
                    seed_patterns = seed_fn(swarm.bridge, reality_metrics, 5)
                    newest_agent.memory.extend(seed_patterns)

        result = swarm.evolve_cycle(delta_time=1.0)

        # Detect collapse
        if cycle % 10 == 0 and collapse_cycle is None:
            if len(swarm.global_memory) > 0:
                pattern_keys = [pattern_to_key(p) for p in swarm.global_memory]
                unique = len(set(pattern_keys))
                if unique == 1:
                    collapse_cycle = cycle

    duration = time.time() - start_time

    # Final state
    dominant_key, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    print(f"    {condition}-{run_id}: Complete - Dominant={dominant_fraction:.2%}, Collapse@{collapse_cycle if collapse_cycle else 'Never'}")

    return {
        'condition': condition,
        'run_id': run_id,
        'dominant_pattern': str(dominant_key) if dominant_key else None,
        'dominant_fraction': dominant_fraction,
        'collapse_cycle': collapse_cycle,
        'duration': duration
    }

def main():
    """Run initial condition sensitivity test."""
    print("="*80)
    print("CYCLE 83: INITIAL CONDITION SENSITIVITY (DETERMINISM SOURCE TEST)")
    print("="*80)
    print()
    print("Testing whether varying seed patterns produces different outcomes.")
    print("Following Cycle 82: Perfect reproducibility with identical seeds")
    print("Question: Does determinism come from algorithm or initial conditions?")
    print()

    threshold = 500
    cycles = 200
    runs_per_condition = 3

    print(f"Configuration:")
    print(f"  Threshold: {threshold} (exploration regime)")
    print(f"  Cycles per run: {cycles}")
    print(f"  Runs per condition: {runs_per_condition}")
    print(f"  Conditions:")
    print(f"    A: Standard seeds (0.8-1.2x, C82 baseline)")
    print(f"    B: Modified seeds (0.6-1.4x, ±20% shift)")
    print(f"    C: Wide seeds (0.4-1.6x, ±40% shift)")
    print(f"  Total simulations: {3 * runs_per_condition} runs")
    print("="*80)

    overall_start = time.time()
    results = []

    # Condition A: Standard (C82 baseline)
    print(f"\n  CONDITION A: STANDARD SEEDS (C82 Baseline)")
    for run_id in range(1, runs_per_condition + 1):
        try:
            result = run_single_simulation("A", run_id, threshold, cycles, create_seed_memory_standard)
            results.append(result)
            time.sleep(0.3)
        except Exception as e:
            print(f"    A-{run_id} Error: {e}")
            results.append({'condition': 'A', 'run_id': run_id, 'error': str(e)})

    # Condition B: Modified
    print(f"\n  CONDITION B: MODIFIED SEEDS (±20% shift)")
    for run_id in range(1, runs_per_condition + 1):
        try:
            result = run_single_simulation("B", run_id, threshold, cycles, create_seed_memory_modified)
            results.append(result)
            time.sleep(0.3)
        except Exception as e:
            print(f"    B-{run_id} Error: {e}")
            results.append({'condition': 'B', 'run_id': run_id, 'error': str(e)})

    # Condition C: Wide
    print(f"\n  CONDITION C: WIDE SEEDS (±40% shift)")
    for run_id in range(1, runs_per_condition + 1):
        try:
            result = run_single_simulation("C", run_id, threshold, cycles, create_seed_memory_wide)
            results.append(result)
            time.sleep(0.3)
        except Exception as e:
            print(f"    C-{run_id} Error: {e}")
            results.append({'condition': 'C', 'run_id': run_id, 'error': str(e)})

    overall_duration = time.time() - overall_start

    # Analysis
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"INITIAL CONDITION SENSITIVITY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 6:
        # Group by condition
        by_condition = {
            'A': [r for r in successful if r['condition'] == 'A'],
            'B': [r for r in successful if r['condition'] == 'B'],
            'C': [r for r in successful if r['condition'] == 'C']
        }

        # Within-condition diversity
        within_diversity = {}
        for cond, runs in by_condition.items():
            patterns = [r['dominant_pattern'] for r in runs if r['dominant_pattern']]
            unique = len(set(patterns))
            within_diversity[cond] = unique / len(patterns) if patterns else 0.0

        # Cross-condition diversity (all runs)
        all_patterns = [r['dominant_pattern'] for r in successful if r['dominant_pattern']]
        cross_diversity = len(set(all_patterns)) / len(all_patterns) if all_patterns else 0.0

        print(f"Results Summary:")
        print(f"  Successful runs: {len(successful)}/{len(results)}")
        print(f"  Cross-condition diversity: {len(set(all_patterns))} unique dominants ({cross_diversity:.1%})")
        print()

        print(f"Within-Condition Reproducibility:")
        for cond in ['A', 'B', 'C']:
            if cond in within_diversity:
                diversity = within_diversity[cond]
                status = "Varied" if diversity > 0.5 else "Consistent"
                print(f"  Condition {cond}: {diversity:.1%} diversity ({status})")
        print()

        # Individual results
        print(f"Individual Run Results:")
        print(f"{'Cond':>4} | {'Run':>3} | {'Dominant Pattern':^50} | {'Fraction':>8} | {'Collapse':>8}")
        print("-" * 90)
        for r in successful:
            pat_str = r['dominant_pattern'][:47] + "..." if r['dominant_pattern'] and len(r['dominant_pattern']) > 50 else (r['dominant_pattern'] or "None")
            print(f"{r['condition']:>4} | {r['run_id']:>3} | {pat_str:^50} | {r['dominant_fraction']:>7.2%} | {r['collapse_cycle'] if r['collapse_cycle'] else 'Never':>8}")
        print()

        # Determine sensitivity
        if cross_diversity > 0.5:
            print(f"✅ INITIAL CONDITION SENSITIVITY CONFIRMED")
            print(f"   {len(set(all_patterns))}/{len(all_patterns)} unique final dominants ({cross_diversity:.1%})")
            print(f"   Different seed patterns → Different outcomes")
            print(f"   Determinism comes from INITIAL CONDITIONS, not just algorithm")
            sensitive = True
        else:
            print(f"❌ ALGORITHM DETERMINISM")
            print(f"   {len(set(all_patterns))}/{len(all_patterns)} unique final dominants ({cross_diversity:.1%})")
            print(f"   All conditions converge to similar outcomes")
            print(f"   Algorithm structure dominates over initial conditions")
            sensitive = False

        print()

        if sensitive:
            print(f"🎉 INSIGHT #44 DISCOVERED: Initial Condition Sensitivity")
            print(f"   - System trajectory depends on seed patterns")
            print(f"   - Cross-condition diversity: {cross_diversity:.1%}")
            print(f"   - Self-Giving validated: Multiple viable trajectories exist")
            print(f"   - Deterministic freedom: Rigorous yet path-dependent")
            insight_44 = True
        else:
            print(f"   Algorithm structure dominates")
            print(f"   Initial conditions have limited impact")
            insight_44 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_44 = False
        cross_diversity = None
        within_diversity = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "initial_conditions"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle83_initial_condition_sensitivity.json"

    output_data = {
        'experiment': 'cycle83_initial_condition_sensitivity',
        'threshold': threshold,
        'cycles': cycles,
        'runs_per_condition': runs_per_condition,
        'conditions': ['A_standard', 'B_modified', 'C_wide'],
        'results': results,
        'analysis': {
            'cross_diversity': cross_diversity,
            'within_diversity': within_diversity,
            'sensitive': sensitive if len(successful) >= 6 else None
        },
        'insight_44_discovered': insight_44,
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
