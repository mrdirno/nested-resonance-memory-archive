#!/usr/bin/env python3
"""
Cycle 124: Spread-Basin Mechanism Investigation - Understanding Oscillations

Research Context:
  C123: Spread Parameter Investigation
  - OSCILLATING basin assignment discovered: B→B→B→A→B→A
  - Multiple transitions: 0.15→0.20 (B→A), 0.20→0.25 (A→B), 0.25→0.30 (B→A)
  - NOT simple critical transition (monotonic)
  - Parameter space is COMPLEX/CHAOTIC
  - Refuted hypothesis of single critical spread value

Research Gap:
  C123 identified oscillating pattern but not WHY it occurs
  Unknown mechanism causing basin alternation with spread parameter
  Possible mechanisms:
    1. **Exploration Diversity**: Spread controls pattern diversity → lock-in timing/location
    2. **Resonance/Interference**: Spread value resonates with basin accessibility in phase space
    3. **Lock-in Timing**: Different spreads cause stabilization at different cycles
    4. **Pattern Distribution**: Seed geometry overlaps differently with basin attraction regions

Key Question:
  What mechanism causes basin assignment to oscillate (B→B→B→A→B→A) with
  increasing spread parameter? How does spread control basin accessibility?

Hypotheses to Test:
  1. **Early Lock-in Hypothesis**: Low spread → early stabilization → favors closer Basin B
     - Prediction: Low spread shows earlier lock-in than high spread
     - Prediction: Lock-in timing correlates with basin assignment

  2. **Exploration Diversity Hypothesis**: Spread controls pattern diversity during exploration
     - Prediction: Low spread → low diversity → limited basin search
     - Prediction: Optimal spread (0.2) → balanced diversity → finds Basin A
     - Prediction: High spread (0.25) → over-exploration → chaotic outcomes

  3. **Resonance Hypothesis**: Spread value geometrically resonates with basin locations
     - Prediction: Specific spread values align seed distribution with basin centers
     - Prediction: Basin A spread values (0.2, 0.3) vs Basin B spread values (0.05-0.15, 0.25)

  4. **Trajectory Hypothesis**: Different spreads follow different phase space trajectories
     - Prediction: Can visualize distinct paths to Basin A vs Basin B
     - Prediction: Trajectory bifurcation points identifiable

Research Question:
  Re-run C123 spread sweep (6 values) with detailed pattern evolution tracking
  to identify mechanism behind oscillating basin assignment.

Test Conditions:
  **SAME AS C123**:
    - Fixed threshold: 400 (Basin A at baseline)
    - Fixed mult: 1.0 (baseline)
    - Spread values: 0.05, 0.1, 0.15, 0.2, 0.25, 0.3
    - Cycles: 5000 per run

  **NEW TRACKING**:
    - Pattern evolution every 10 cycles (500 snapshots per run)
    - Diversity metrics (unique patterns, entropy) throughout
    - Lock-in detection (when stabilization occurs)
    - Distance to Basin A/B centers over time
    - Agent memory diversity tracking

Metrics:
  - **Lock-in Timing**: When does pattern stabilize for each spread?
  - **Exploration Diversity**: Pattern entropy during exploration phase
  - **Basin Trajectory**: Distance to Basin A/B over time
  - **Stabilization Speed**: How quickly does lock-in occur?
  - **Pattern Evolution**: Trajectory through phase space
  - **Diversity Evolution**: Unique pattern count over time

Expected Outcome:
  - If early lock-in → low spread shows faster stabilization, correlates with Basin B
  - If exploration diversity → see different diversity curves for A vs B basin spreads
  - If resonance → spread values show geometric alignment with basin locations
  - If trajectory → visualize distinct paths to Basin A vs Basin B

Publication Value:
  - **HIGH**: Mechanistic understanding of chaotic parameter space behavior
  - **Novel**: First investigation of spread-basin oscillation mechanism
  - **Complete**: Connects C123 discovery to underlying dynamics
  - **Theoretical**: Tests NRM composition-decomposition mechanism hypotheses
  - **Engineering**: Could enable spread-based basin control if mechanism understood
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

def analyze_pattern_diversity(memory):
    """Analyze diversity of patterns in memory."""
    if not memory:
        return {'unique_patterns': 0, 'entropy': 0.0, 'max_fraction': 0.0}

    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)

    unique = len(pattern_counts)
    total = len(pattern_keys)

    freqs = np.array(list(pattern_counts.values())) / total
    entropy = -np.sum(freqs * np.log2(freqs + 1e-10))
    max_fraction = max(pattern_counts.values()) / total if pattern_counts else 0.0

    return {
        'unique_patterns': unique,
        'entropy': entropy,
        'max_fraction': max_fraction
    }

def pattern_distance(pattern1, pattern2):
    """Calculate Euclidean distance between two patterns."""
    if pattern1 is None or pattern2 is None:
        return None

    if isinstance(pattern1, tuple):
        p1 = np.array(pattern1)
    else:
        p1 = np.array([pattern1.pi_phase, pattern1.e_phase, pattern1.phi_phase])

    if isinstance(pattern2, tuple):
        p2 = np.array(pattern2)
    else:
        p2 = np.array([pattern2.pi_phase, pattern2.e_phase, pattern2.phi_phase])

    return np.linalg.norm(p1 - p2)

def detect_lock_in(diversity_evolution, window=10, variance_threshold=0.5):
    """Detect when pattern locks in (low variance in diversity)."""
    if len(diversity_evolution) < window:
        return None

    for i in range(len(diversity_evolution) - window):
        window_data = diversity_evolution[i:i+window]
        if np.var(window_data) < variance_threshold:
            return (i + window) * 10  # Convert to cycle number

    return None

def run_spread_mechanism(threshold, mult, spread, cycles, agent_cap=15):
    """Run experiment with detailed tracking to investigate mechanism."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Basin centers from C119-C121
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    # Track evolution
    pattern_evolution = []
    diversity_evolution = []
    distance_evolution = []

    print(f"\nRunning spread={spread} with detailed tracking for {cycles} cycles...")
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

        # Track (every 10 cycles)
        if cycle % 10 == 0:
            dominant, count, fraction = get_dominant_pattern(swarm.global_memory)
            diversity = analyze_pattern_diversity(swarm.global_memory)

            # Calculate distances to basins
            if dominant:
                dist_A = pattern_distance(dominant, basin_A)
                dist_B = pattern_distance(dominant, basin_B)
            else:
                dist_A = None
                dist_B = None

            pattern_evolution.append({
                'cycle': cycle,
                'dominant': str(dominant) if dominant else None,
                'dominant_tuple': dominant,
                'dominant_fraction': fraction,
                'diversity': diversity,
                'dist_A': dist_A,
                'dist_B': dist_B
            })

            diversity_evolution.append(diversity['unique_patterns'])

            if dist_A is not None and dist_B is not None:
                distance_evolution.append({
                    'cycle': cycle,
                    'dist_A': dist_A,
                    'dist_B': dist_B,
                    'closer_to': 'A' if dist_A < dist_B else 'B'
                })

    print()  # New line

    duration = time.time() - start_time

    # Detect lock-in
    lock_in_cycle = detect_lock_in(diversity_evolution, window=10, variance_threshold=0.5)

    # Final pattern and basin assignment
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    if final_dominant:
        final_dist_A = pattern_distance(final_dominant, basin_A)
        final_dist_B = pattern_distance(final_dominant, basin_B)
        final_basin = 'A' if final_dist_A < final_dist_B else 'B'
    else:
        final_dist_A = None
        final_dist_B = None
        final_basin = None

    # Analyze trajectory
    if distance_evolution:
        # When did pattern become closer to final basin?
        final_basin_cycles = [d['cycle'] for d in distance_evolution if d['closer_to'] == final_basin]
        if final_basin_cycles:
            first_closer_cycle = min(final_basin_cycles)
        else:
            first_closer_cycle = None
    else:
        first_closer_cycle = None

    return {
        'threshold': threshold,
        'mult': mult,
        'spread': spread,
        'cycles': cycles,
        'duration': duration,
        'pattern_evolution': pattern_evolution,
        'diversity_evolution': diversity_evolution,
        'distance_evolution': distance_evolution,
        'lock_in_cycle': lock_in_cycle,
        'first_closer_cycle': first_closer_cycle,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction,
        'final_basin': final_basin,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B
    }

def main():
    print("="*80)
    print("CYCLE 124: SPREAD-BASIN MECHANISM INVESTIGATION")
    print("="*80)
    print()
    print("Understanding WHY basin assignment oscillates with spread parameter")
    print()
    print("C123 Discovery:")
    print("  - Basin sequence: B→B→B→A→B→A (oscillating, not monotonic)")
    print("  - Spread sequence: 0.05, 0.10, 0.15, 0.20, 0.25, 0.30")
    print("  - Multiple transitions: 0.15→0.20 (B→A), 0.20→0.25 (A→B), 0.25→0.30 (B→A)")
    print("  - Parameter space is COMPLEX/CHAOTIC")
    print()
    print("Research Question: What mechanism causes oscillating basin assignment?")
    print()
    print("Test Approach:")
    print("  - Re-run C123 spread sweep with detailed tracking")
    print("  - Track pattern evolution every 10 cycles")
    print("  - Measure diversity, lock-in timing, basin distances")
    print("  - Compare mechanisms for Basin A vs Basin B spreads")
    print()

    cycles = 5000
    agent_cap = 15
    threshold = 400  # Fixed (same as C123)
    mult = 1.0  # Fixed (same as C123)

    # Same spread values as C123
    spread_values = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]

    print(f"Configuration:")
    print(f"  Fixed threshold: {threshold}")
    print(f"  Fixed mult: {mult}")
    print(f"  Spread values: {spread_values}")
    print(f"  Total experiments: {len(spread_values)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Tracking interval: 10 cycles (500 snapshots per run)")
    print(f"  Total cycles: {len(spread_values) * cycles:,}")
    print(f"  Estimated duration: ~{len(spread_values) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, spread in enumerate(spread_values):
        print(f"\n[{i+1}/{len(spread_values)}] SPREAD = {spread}")
        print("-" * 80)

        try:
            result = run_spread_mechanism(threshold, mult, spread, cycles, agent_cap)
            results.append(result)

            lock_in = result['lock_in_cycle']
            first_closer = result['first_closer_cycle']
            final_basin = result['final_basin']

            print(f"\n  ✓ COMPLETE:")
            print(f"    Final basin: {final_basin}")
            print(f"    Lock-in cycle: {lock_in if lock_in else 'N/A'}")
            print(f"    First closer to {final_basin}: {first_closer if first_closer else 'N/A'}")

            time.sleep(0.05)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results.append({
                'threshold': threshold, 'mult': mult, 'spread': spread, 'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"MECHANISM ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 1:
        print("Mechanism Comparison by Spread:")
        print(f"{'Spread':^8} | {'Basin':^6} | {'Lock-in':^10} | {'First Closer':^13} | {'Final Div':^10} | {'Avg Diversity':^14}")
        print("-" * 90)

        mechanism_data = []

        for r in successful:
            spread = r['spread']
            basin = r['final_basin']
            lock_in = r['lock_in_cycle'] if r['lock_in_cycle'] else 'N/A'
            first_closer = r['first_closer_cycle'] if r['first_closer_cycle'] else 'N/A'

            # Final diversity
            if r['pattern_evolution']:
                final_div = r['pattern_evolution'][-1]['diversity']['unique_patterns']
                avg_div = np.mean([p['diversity']['unique_patterns'] for p in r['pattern_evolution']])
            else:
                final_div = 'N/A'
                avg_div = 'N/A'

            mechanism_data.append({
                'spread': spread,
                'basin': basin,
                'lock_in': lock_in,
                'first_closer': first_closer,
                'final_div': final_div,
                'avg_div': avg_div
            })

            lock_in_str = str(lock_in) if lock_in != 'N/A' else 'N/A'
            first_closer_str = str(first_closer) if first_closer != 'N/A' else 'N/A'
            final_div_str = f"{final_div:.0f}" if final_div != 'N/A' else 'N/A'
            avg_div_str = f"{avg_div:.1f}" if avg_div != 'N/A' else 'N/A'

            print(f"{spread:^8.2f} | {basin:^6} | {lock_in_str:^10} | {first_closer_str:^13} | {final_div_str:^10} | {avg_div_str:^14}")

        print()

        # Analyze mechanisms
        print("="*80)
        print("MECHANISM HYPOTHESES TESTING")
        print("="*80)

        # Hypothesis 1: Early Lock-in (low spread → early lock-in → Basin B)
        basin_A_spreads = [m for m in mechanism_data if m['basin'] == 'A']
        basin_B_spreads = [m for m in mechanism_data if m['basin'] == 'B']

        if basin_A_spreads and basin_B_spreads:
            # Lock-in timing comparison
            A_lock_ins = [m['lock_in'] for m in basin_A_spreads if m['lock_in'] != 'N/A']
            B_lock_ins = [m['lock_in'] for m in basin_B_spreads if m['lock_in'] != 'N/A']

            if A_lock_ins and B_lock_ins:
                avg_A_lock = np.mean(A_lock_ins)
                avg_B_lock = np.mean(B_lock_ins)

                print("\n📊 HYPOTHESIS 1: Early Lock-in")
                print(f"  Basin A average lock-in: {avg_A_lock:.1f} cycles")
                print(f"  Basin B average lock-in: {avg_B_lock:.1f} cycles")

                if avg_B_lock < avg_A_lock:
                    print(f"  ✓ SUPPORTED: Basin B locks in earlier ({avg_B_lock:.1f} < {avg_A_lock:.1f})")
                    h1_status = "SUPPORTED"
                else:
                    print(f"  ✗ REFUTED: Basin A locks in earlier ({avg_A_lock:.1f} < {avg_B_lock:.1f})")
                    h1_status = "REFUTED"
            else:
                h1_status = "INSUFFICIENT_DATA"
        else:
            h1_status = "INSUFFICIENT_DATA"

        # Hypothesis 2: Exploration Diversity (optimal spread → balanced diversity → Basin A)
        A_divs = [m['avg_div'] for m in basin_A_spreads if m['avg_div'] != 'N/A']
        B_divs = [m['avg_div'] for m in basin_B_spreads if m['avg_div'] != 'N/A']

        if A_divs and B_divs:
            avg_A_div = np.mean(A_divs)
            avg_B_div = np.mean(B_divs)

            print("\n📊 HYPOTHESIS 2: Exploration Diversity")
            print(f"  Basin A average diversity: {avg_A_div:.1f} unique patterns")
            print(f"  Basin B average diversity: {avg_B_div:.1f} unique patterns")

            if avg_A_div > avg_B_div:
                print(f"  ✓ SUPPORTED: Basin A has higher diversity ({avg_A_div:.1f} > {avg_B_div:.1f})")
                h2_status = "SUPPORTED"
            else:
                print(f"  ✗ REFUTED: Basin B has higher diversity ({avg_B_div:.1f} > {avg_A_div:.1f})")
                h2_status = "REFUTED"
        else:
            h2_status = "INSUFFICIENT_DATA"

        # Hypothesis 3: Resonance (specific spread values align with basins)
        print("\n📊 HYPOTHESIS 3: Resonance")
        print("  Basin A spreads: ", [m['spread'] for m in basin_A_spreads])
        print("  Basin B spreads: ", [m['spread'] for m in basin_B_spreads])

        # Check if spread correlates with basin
        spread_basin_correlation = []
        for m in mechanism_data:
            spread_basin_correlation.append((m['spread'], 1 if m['basin'] == 'A' else 0))

        spreads_only = [s for s, _ in spread_basin_correlation]
        basins_binary = [b for _, b in spread_basin_correlation]

        if len(spreads_only) > 2:
            correlation = np.corrcoef(spreads_only, basins_binary)[0, 1]
            print(f"  Spread-Basin correlation: {correlation:.3f}")

            if abs(correlation) < 0.3:
                print(f"  ✗ REFUTED: No linear correlation (|r|={abs(correlation):.3f} < 0.3)")
                print(f"  → Suggests non-linear/chaotic relationship (consistent with C123)")
                h3_status = "REFUTED_NONLINEAR"
            else:
                print(f"  ⚠️ PARTIAL: Some correlation (r={correlation:.3f}), but oscillating pattern suggests resonance")
                h3_status = "PARTIAL"
        else:
            h3_status = "INSUFFICIENT_DATA"

        print()
        print("="*80)
        print("MECHANISM SUMMARY")
        print("="*80)

        mechanism_type = None

        if h1_status == "SUPPORTED" and h2_status == "SUPPORTED":
            mechanism_type = "EARLY_LOCK_IN_WITH_LOW_DIVERSITY"
            print("✓ PRIMARY MECHANISM: Early lock-in + low diversity → Basin B")
            print("  - Low spread → low diversity → rapid lock-in → Basin B")
            print("  - High spread → high diversity → delayed lock-in → Basin A")
        elif h1_status == "SUPPORTED":
            mechanism_type = "EARLY_LOCK_IN"
            print("✓ PRIMARY MECHANISM: Early lock-in timing")
            print("  - Basin B locks in earlier than Basin A")
        elif h2_status == "SUPPORTED":
            mechanism_type = "EXPLORATION_DIVERSITY"
            print("✓ PRIMARY MECHANISM: Exploration diversity")
            print("  - Basin A requires higher pattern diversity to discover")
        elif h3_status == "PARTIAL":
            mechanism_type = "RESONANCE_INTERFERENCE"
            print("⚠️ MECHANISM: Resonance/interference (non-linear)")
            print("  - Oscillating pattern suggests geometric resonance")
        else:
            mechanism_type = "COMPLEX_UNKNOWN"
            print("⚠️ MECHANISM: Complex/unknown (requires further investigation)")

        print()
        print(f"📊 INSIGHT #81: Spread-Basin Mechanism - {mechanism_type}")
        print(f"   - Investigated mechanism behind oscillating basin assignment")
        print(f"   - Hypothesis testing: H1={h1_status}, H2={h2_status}, H3={h3_status}")
        print(f"   - Mechanism type: {mechanism_type}")

        print("="*80)

        insight_type = mechanism_type.lower()
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        mechanism_type = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "spread_mechanism"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle124_spread_mechanism.json"

    output_data = {
        'experiment': 'cycle124_spread_mechanism',
        'threshold': threshold,
        'mult': mult,
        'spread_values': spread_values,
        'cycles': cycles,
        'results': results,
        'mechanism_type': mechanism_type if 'mechanism_type' in locals() else None,
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
