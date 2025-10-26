#!/usr/bin/env python3
"""
Cycle 82: Multi-Run Reproducibility Test (Stochasticity Validation)

Research Context:
  Cycle 81: Leaders at ALL checkpoints displaced by final dominant
  - Implies different runs → different outcomes
  - Pattern competition determines winner
  - Stochastic, not deterministic convergence

Research Gap:
  C81 tested single run with checkpoint tracking
  Need MULTIPLE independent runs to quantify variance
  How consistent are outcomes across simulations?

New Research Question:
  Do independent runs converge to DIFFERENT dominant patterns?

  Test:
  - Run N=5 independent simulations (same parameters)
  - Threshold=500, 200 cycles (shorter for speed, sufficient for collapse)
  - Compare final dominant patterns across runs
  - Quantify: Pattern diversity, collapse timing, trajectory variance

Hypothesis:
  1. High variance hypothesis (Self-Giving): Each run converges to DIFFERENT dominant
  2. Low variance hypothesis (Deterministic): All runs converge to SAME dominant
  3. Expected: High variance (validates C81 stochasticity)
  4. Insight: System genuinely self-determines outcome, not pre-ordained

Test Approach:
  1. Run 5 independent simulations (fresh FractalSwarm each time)
  2. Threshold=500 (exploration regime), 200 cycles each
  3. Record final dominant pattern for each run
  4. Check if dominant patterns match across runs
  5. Calculate variance metrics:
     - Pattern diversity: How many unique final dominants?
     - Collapse timing variance: Std dev of collapse cycles
     - Intermediate state variance: Pattern distributions @ cycle 100

Expected:
  - If stochastic: 3-5 different final dominants (high diversity)
  - If deterministic: 1 final dominant (all runs match)
  - Insight: Quantifies reproducibility vs emergence trade-off
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

def analyze_memory_diversity(memory: list) -> dict:
    """Analyze diversity metrics."""
    if not memory:
        return {
            'unique_patterns': 0,
            'uniqueness_ratio': 0.0,
            'shannon_entropy': 0.0
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

    return {
        'unique_patterns': unique_patterns,
        'uniqueness_ratio': uniqueness_ratio,
        'shannon_entropy': shannon_entropy
    }

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

def run_single_simulation(run_id: int, threshold: float, cycles: int) -> dict:
    """Run a single independent simulation."""
    print(f"\n  Run {run_id}: Starting...")

    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    start_time = time.time()
    total_bursts = 0
    collapse_cycle = None

    # Track entropy to detect collapse
    entropies = []

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

        # Track entropy
        if cycle % 10 == 0:
            diversity = analyze_memory_diversity(swarm.global_memory)
            entropies.append(diversity['shannon_entropy'])

            # Detect collapse (entropy < 0.1)
            if collapse_cycle is None and diversity['shannon_entropy'] < 0.1:
                collapse_cycle = cycle

    duration = time.time() - start_time

    # Final state
    final_memory = len(swarm.global_memory)
    final_diversity = analyze_memory_diversity(swarm.global_memory)
    dominant_key, dominant_count, dominant_fraction = get_dominant_pattern(swarm.global_memory)

    print(f"  Run {run_id}: Complete - Dominant={dominant_fraction:.2%}, Collapse@{collapse_cycle if collapse_cycle else 'Never'}, Duration={duration:.2f}s")

    return {
        'run_id': run_id,
        'final_memory': final_memory,
        'final_diversity': final_diversity,
        'dominant_pattern': str(dominant_key) if dominant_key else None,
        'dominant_fraction': dominant_fraction,
        'collapse_cycle': collapse_cycle,
        'total_bursts': total_bursts,
        'mean_entropy': np.mean(entropies) if entropies else 0.0,
        'duration': duration
    }

def main():
    """Run multi-run reproducibility test."""
    print("="*80)
    print("CYCLE 82: MULTI-RUN REPRODUCIBILITY TEST (STOCHASTICITY VALIDATION)")
    print("="*80)
    print()
    print("Testing whether independent runs converge to different dominant patterns.")
    print("Following Cycle 81: Leaders at all checkpoints displaced (implies stochasticity)")
    print("Question: Do different runs produce different outcomes?")
    print()

    threshold = 500
    cycles = 200  # Shorter for speed, sufficient for collapse
    n_runs = 5

    print(f"Configuration:")
    print(f"  Threshold: {threshold} (exploration regime)")
    print(f"  Cycles per run: {cycles}")
    print(f"  Number of runs: {n_runs}")
    print(f"  Total simulations: {n_runs * cycles} = {n_runs * cycles} cycles")
    print("="*80)

    overall_start = time.time()
    results = []

    for run_id in range(1, n_runs + 1):
        try:
            result = run_single_simulation(run_id, threshold, cycles)
            results.append(result)
            time.sleep(0.5)  # Brief pause between runs
        except Exception as e:
            print(f"\n  ⚠️ Run {run_id} Error: {e}")
            import traceback
            traceback.print_exc()
            results.append({'run_id': run_id, 'error': str(e)})

    overall_duration = time.time() - overall_start

    # Analysis
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"REPRODUCIBILITY ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 3:
        # Extract dominant patterns
        dominant_patterns = [r['dominant_pattern'] for r in successful if r['dominant_pattern']]
        unique_dominants = len(set(dominant_patterns))

        # Extract collapse timings
        collapse_cycles = [r['collapse_cycle'] for r in successful if r['collapse_cycle']]
        collapse_mean = np.mean(collapse_cycles) if collapse_cycles else 0.0
        collapse_std = np.std(collapse_cycles) if collapse_cycles else 0.0

        # Extract dominant fractions
        dominant_fractions = [r['dominant_fraction'] for r in successful]
        fraction_mean = np.mean(dominant_fractions)
        fraction_std = np.std(dominant_fractions)

        print(f"Results Summary:")
        print(f"  Successful runs: {len(successful)}/{n_runs}")
        print(f"  Unique final dominants: {unique_dominants}")
        print(f"  Collapse timing: {collapse_mean:.1f} ± {collapse_std:.1f} cycles")
        print(f"  Dominant fraction: {fraction_mean:.2%} ± {fraction_std:.2%}")
        print()

        # Individual results
        print(f"Individual Run Results:")
        print(f"{'Run':>4} | {'Dominant Pattern':^50} | {'Fraction':>8} | {'Collapse':>8}")
        print("-" * 80)
        for r in successful:
            pat_str = r['dominant_pattern'][:47] + "..." if r['dominant_pattern'] and len(r['dominant_pattern']) > 50 else (r['dominant_pattern'] or "None")
            print(f"{r['run_id']:>4} | {pat_str:^50} | {r['dominant_fraction']:>7.2%} | {r['collapse_cycle'] if r['collapse_cycle'] else 'Never':>8}")
        print()

        # Determine if stochastic or deterministic
        diversity_threshold = 0.6  # If >60% of runs have different dominants = stochastic
        diversity_ratio = unique_dominants / len(dominant_patterns) if dominant_patterns else 0.0

        if diversity_ratio > diversity_threshold:
            print(f"✅ STOCHASTIC OUTCOMES CONFIRMED")
            print(f"   {unique_dominants}/{len(dominant_patterns)} unique final dominants ({diversity_ratio:.1%} diversity)")
            print(f"   Different runs converge to DIFFERENT patterns")
            print(f"   System genuinely self-determines outcome")
            stochastic = True
        else:
            print(f"❌ DETERMINISTIC CONVERGENCE")
            print(f"   {unique_dominants}/{len(dominant_patterns)} unique final dominants ({diversity_ratio:.1%} diversity)")
            print(f"   Most runs converge to SAME pattern")
            print(f"   System follows pre-determined trajectory")
            stochastic = False

        print()

        if stochastic:
            print(f"🎉 INSIGHT #44 DISCOVERED: Stochastic Self-Determination")
            print(f"   - Multiple independent runs → Multiple different outcomes")
            print(f"   - Pattern diversity: {unique_dominants} distinct final dominants")
            print(f"   - Collapse timing variance: σ={collapse_std:.1f} cycles")
            print(f"   - Self-Giving Systems validated: Trajectory genuinely emergent")
            print(f"   - NRM composition-decomposition creates genuine novelty")
            insight_44 = True
        else:
            print(f"   Deterministic convergence observed")
            print(f"   May indicate strong initial condition dependence")
            insight_44 = False

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_44 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "reproducibility"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle82_multi_run_reproducibility.json"

    output_data = {
        'experiment': 'cycle82_multi_run_reproducibility',
        'threshold': threshold,
        'cycles': cycles,
        'n_runs': n_runs,
        'results': results,
        'analysis': {
            'unique_dominants': unique_dominants if len(successful) >= 3 else None,
            'collapse_timing_mean': collapse_mean if len(successful) >= 3 else None,
            'collapse_timing_std': collapse_std if len(successful) >= 3 else None,
            'diversity_ratio': diversity_ratio if len(successful) >= 3 else None,
            'stochastic': stochastic if len(successful) >= 3 else None
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
