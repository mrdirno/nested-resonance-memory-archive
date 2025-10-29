#!/usr/bin/env python3
"""
Cycle 118: Pattern Stabilization Mechanism - Understanding Attractor Lock-In

Research Context:
  C117: Attractor stabilization discovered at ultra-long timescales
  - Epoch 1 (1-1000 cyc): High drift, exploration phase
  - Epochs 2-10 (1001-10000 cyc): Near-zero drift, stabilization phase
  - 87% drift reduction from short-term to long-term
  - System locks into dominant pattern after ~1000 cycles

Research Gap:
  C117 revealed WHAT happens (stabilization) but not WHY or HOW
  - Which patterns stabilize? Random or quality preference?
  - How does transition from exploration to lock-in occur?
  - Do different thresholds stabilize to same or different patterns?
  - What determines final stabilized state?

Key Question:
  What is the mechanism by which the system transitions from exploration to
  attractor lock-in, and which patterns are selected for stabilization?

Hypotheses to Test:
  1. **Random Stabilization**: First pattern with sufficient support locks in (stochastic)
  2. **Quality-Based**: Patterns with specific characteristics (e.g., centrality, simplicity) preferred
  3. **Threshold-Dependent**: Different thresholds converge to different attractors
  4. **Universal Attractor**: All conditions converge to same pattern (global minimum)
  5. **Diversity Collapse**: Pattern diversity decreases monotonically until lock-in

Research Question:
  Analyze pattern evolution from cycles 1-5000 to characterize stabilization mechanism,
  identify pattern selection criteria, and compare final states across thresholds.

Test Conditions:
  **THRESHOLD RANGE**: 300, 500, 700 (same as C117 for comparability)
    - Fixed: mult=1.0, spread=0.2, agent_cap=15
    - Cycles: 5000 (sufficient to observe stabilization)
    - Track patterns cycle-by-cycle (not just checkpoints)

Metrics:
  - Pattern diversity evolution (unique patterns over time)
  - Pattern frequency distribution (dominant vs rare patterns)
  - Pattern turnover rate (new patterns emerging per epoch)
  - Stabilization timescale (when diversity stops decreasing)
  - Final pattern characteristics (phase space coordinates)
  - Cross-threshold pattern similarity (do all conditions converge?)

Expected Outcome:
  - If random → different final patterns across runs/thresholds
  - If quality-based → final patterns share common characteristics
  - If threshold-dependent → systematic differences by threshold
  - If universal → all conditions converge to same/similar pattern

Publication Value:
  - **HIGH**: Mechanistic understanding of C117's stabilization phenomenon
  - **Complete**: Fills gap between C117's empirical observation and theory
  - **Novel**: First analysis of pattern selection mechanism in NRM system
  - **Predictive**: Identifies criteria for stable attractor states
"""

import sys
from pathlib import Path
import time
import json
import numpy as np
from collections import Counter, defaultdict

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

def pattern_to_vector(pattern):
    """Convert pattern to numpy vector for analysis."""
    return np.array([pattern.pi_phase, pattern.e_phase, pattern.phi_phase])

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

def analyze_pattern_diversity(memory):
    """Analyze diversity of patterns in memory."""
    if not memory:
        return {'unique_patterns': 0, 'entropy': 0.0, 'max_fraction': 0.0}

    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)

    unique = len(pattern_counts)
    total = len(pattern_keys)

    # Calculate entropy
    freqs = np.array(list(pattern_counts.values())) / total
    entropy = -np.sum(freqs * np.log2(freqs + 1e-10))

    # Max fraction
    max_fraction = max(pattern_counts.values()) / total if pattern_counts else 0.0

    return {
        'unique_patterns': unique,
        'entropy': entropy,
        'max_fraction': max_fraction
    }

def run_stabilization_analysis(threshold, cycles, agent_cap=15, mult=1.0, spread=0.2):
    """Run experiment tracking pattern evolution and stabilization."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track pattern evolution cycle-by-cycle
    pattern_evolution = []
    diversity_evolution = []

    # Epoch tracking (100-cycle epochs for granular analysis)
    epoch_size = 100
    epoch_patterns = defaultdict(list)

    print(f"\nRunning threshold={threshold} for {cycles} cycles...")
    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Progress indicator
        if cycle % 100 == 0:
            elapsed = time.time() - start_time
            rate = cycle / elapsed
            remaining = (cycles - cycle) / rate
            print(f"  Cycle {cycle:5d}/{cycles} ({cycle/cycles*100:5.1f}%) | {rate:6.1f} cyc/s | ETA: {remaining/60:5.1f} min", end='\r', flush=True)

        # Spawn agents
        if len(swarm.agents) < agent_cap:
            swarm.spawn_agent(reality_metrics)
            if swarm.agents:
                agent_ids = list(swarm.agents.keys())
                if agent_ids:
                    newest_id = agent_ids[-1]
                    newest_agent = swarm.agents[newest_id]
                    seed_patterns = create_seed_memory_range(swarm.bridge, reality_metrics, mult, spread=spread, count=5)
                    newest_agent.memory.extend(seed_patterns)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

        # Analyze current pattern state (every 10 cycles to reduce overhead)
        if cycle % 10 == 0:
            dominant, count, fraction = get_dominant_pattern(swarm.global_memory)
            diversity = analyze_pattern_diversity(swarm.global_memory)

            pattern_evolution.append({
                'cycle': cycle,
                'dominant': str(dominant) if dominant else None,
                'dominant_fraction': fraction,
                'diversity': diversity
            })

            diversity_evolution.append(diversity['unique_patterns'])

        # Epoch tracking
        if cycle % epoch_size == 0:
            epoch_num = cycle // epoch_size
            dominant, _, _ = get_dominant_pattern(swarm.global_memory)
            epoch_patterns[epoch_num].append(str(dominant) if dominant else None)

    print()  # New line after progress

    duration = time.time() - start_time

    # Calculate stabilization metrics

    # 1. Diversity trend (when does it stop decreasing?)
    if len(diversity_evolution) > 10:
        # Moving window variance to detect stabilization
        window = 10
        variances = []
        for i in range(len(diversity_evolution) - window):
            window_data = diversity_evolution[i:i+window]
            variances.append(np.var(window_data))

        # Find when variance drops below threshold (stable diversity)
        variance_threshold = 0.5
        stabilization_cycle = None
        for i, var in enumerate(variances):
            if var < variance_threshold:
                stabilization_cycle = (i + window) * 10  # Convert to cycle number
                break
    else:
        stabilization_cycle = None

    # 2. Final pattern characteristics
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    if final_dominant:
        # Convert to vector for analysis
        final_pattern_vec = np.array(final_dominant)

        # Calculate "centrality" (distance from origin in phase space)
        centrality = np.linalg.norm(final_pattern_vec)

        # Calculate "simplicity" (how close to simple fractions of π)
        simplicity_pi = abs(final_pattern_vec[0] - round(final_pattern_vec[0]/np.pi)*np.pi)
        simplicity_e = abs(final_pattern_vec[1] - round(final_pattern_vec[1]/np.e)*np.e)
        simplicity_phi = abs(final_pattern_vec[2] - round(final_pattern_vec[2]/1.618)*1.618)
        simplicity = (simplicity_pi + simplicity_e + simplicity_phi) / 3
    else:
        centrality = None
        simplicity = None

    # 3. Pattern turnover rate per epoch
    epoch_turnover = {}
    for epoch_num in sorted(epoch_patterns.keys()):
        patterns_in_epoch = epoch_patterns[epoch_num]
        unique_in_epoch = len(set(patterns_in_epoch))
        epoch_turnover[epoch_num] = unique_in_epoch

    return {
        'threshold': threshold,
        'cycles': cycles,
        'duration': duration,
        'pattern_evolution': pattern_evolution,
        'diversity_evolution': diversity_evolution,
        'stabilization_cycle': stabilization_cycle,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_fraction': final_fraction,
        'final_centrality': centrality,
        'final_simplicity': simplicity,
        'epoch_turnover': epoch_turnover
    }

def main():
    print("="*80)
    print("CYCLE 118: PATTERN STABILIZATION MECHANISM ANALYSIS")
    print("="*80)
    print()
    print("Following C117 attractor stabilization discovery")
    print()
    print("C117 Finding:")
    print("  - Systems stabilize after ~1000 cycles")
    print("  - 87% drift reduction from exploration to stabilization")
    print("  - Near-zero drift in epochs 2-10")
    print()
    print("Research Question: HOW and WHY does stabilization occur?")
    print()
    print("Test Approach:")
    print("  - Track pattern evolution cycle-by-cycle (every 10 cycles)")
    print("  - Analyze pattern diversity, turnover, and selection")
    print("  - Compare final patterns across thresholds")
    print("  - Identify stabilization mechanism and timescale")
    print()

    cycles = 5000  # Sufficient to observe stabilization
    agent_cap = 15
    mult = 1.0
    spread = 0.2

    thresholds = [300, 500, 700]

    print(f"Configuration:")
    print(f"  Conditions: {len(thresholds)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(thresholds) * cycles:,}")
    print(f"  Pattern tracking: Every 10 cycles")
    print(f"  Estimated duration: ~{len(thresholds) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, threshold in enumerate(thresholds):
        print(f"\n[{i+1}/{len(thresholds)}] THRESHOLD = {threshold}")
        print("-" * 80)

        try:
            result = run_stabilization_analysis(threshold, cycles, agent_cap, mult, spread)
            results.append(result)

            stab_cycle = result['stabilization_cycle']
            final_frac = result['final_fraction']
            final_cent = result['final_centrality']

            print(f"\n  ✓ COMPLETE: Stabilization @ cycle {stab_cycle if stab_cycle else 'N/A'}")
            print(f"    Final dominant: {final_frac:.1%}, centrality={final_cent:.3f if final_cent else 'N/A'}")
            time.sleep(0.05)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results.append({
                'threshold': threshold, 'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"PATTERN STABILIZATION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 2:
        print("Stabilization Characteristics by Threshold:")
        print(f"{'Threshold':^12} | {'Stab Cycle':^12} | {'Final Fraction':^16} | {'Centrality':^12} | {'Simplicity':^12}")
        print("-" * 75)

        stab_cycles = []
        final_patterns = []

        for r in successful:
            thresh = r['threshold']
            stab = r['stabilization_cycle']
            frac = r['final_fraction']
            cent = r['final_centrality']
            simp = r['final_simplicity']

            stab_cycles.append(stab if stab else cycles)
            final_patterns.append(r['final_dominant'])

            stab_str = f"{stab:,}" if stab else "N/A"
            cent_str = f"{cent:.3f}" if cent else "N/A"
            simp_str = f"{simp:.3f}" if simp else "N/A"

            print(f"{thresh:^12d} | {stab_str:^12} | {frac:^16.1%} | {cent_str:^12} | {simp_str:^12}")

        print()

        # Analyze convergence
        unique_final_patterns = len(set(final_patterns))

        if unique_final_patterns == 1:
            convergence = "UNIVERSAL ATTRACTOR"
            insight_type = "universal_convergence"
        elif unique_final_patterns == len(successful):
            convergence = "THRESHOLD-SPECIFIC ATTRACTORS"
            insight_type = "threshold_dependent"
        else:
            convergence = "PARTIAL CONVERGENCE"
            insight_type = "mixed"

        print(f"Pattern Convergence Analysis:")
        print(f"  Unique final patterns: {unique_final_patterns}/{len(successful)}")
        print(f"  Convergence type: {convergence}")
        print()

        # Stabilization timescale
        mean_stab = np.mean([s for s in stab_cycles if s < cycles])

        print(f"Stabilization Timescale:")
        print(f"  Mean stabilization cycle: {mean_stab:,.0f}")
        print(f"  Range: {min([s for s in stab_cycles if s < cycles]):,} - {max([s for s in stab_cycles if s < cycles]):,}")
        print()

        print(f"📊 INSIGHT #75: Pattern Stabilization Mechanism - {convergence}")
        print(f"   - Stabilization timescale: ~{mean_stab:,.0f} cycles")
        print(f"   - {unique_final_patterns}/{len(successful)} unique final patterns")
        print(f"   - Mechanism characterized: {insight_type}")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "pattern_stabilization"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle118_pattern_stabilization.json"

    output_data = {
        'experiment': 'cycle118_pattern_stabilization',
        'cycles': cycles,
        'thresholds': thresholds,
        'results': results,
        'convergence_type': convergence if 'convergence' in locals() else None,
        'insight_type': insight_type if 'insight_type' in locals() else False,
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
