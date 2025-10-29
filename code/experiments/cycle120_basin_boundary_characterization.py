#!/usr/bin/env python3
"""
Cycle 120: Basin Boundary Characterization - Precise Location of Attractor Transition

Research Context:
  C119: Framework Prediction Validation
  - Two-basin attractor structure discovered
  - Basin A: Thresholds 300, 400, 500 → pattern (6.220353, 6.275283, 6.281831)
  - Basin B: Thresholds 600, 700 → pattern (6.09469, 6.083677, 6.250047)
  - Sharp boundary between thresholds 500-600 (width <100 threshold units)

Research Gap:
  C119 tested thresholds with 100-200 unit spacing (300, 400, 500, 600, 700)
  Boundary location known only to within 100 units (somewhere in 500-600 range)
  Unknown if boundary is:
    1. Sharp (single critical threshold)
    2. Gradual (transition region with mixed patterns)
    3. Stochastic (probabilistic basin assignment near boundary)

Key Question:
  What is the precise location and nature of the basin boundary between
  attractor basins A and B?

Hypotheses to Test:
  1. **Sharp Boundary**: Single critical threshold where basin switches (e.g., 550)
  2. **Gradual Transition**: Multiple thresholds show intermediate patterns
  3. **Transition Region**: Thresholds 520-580 show mixed basin assignment
  4. **Stochastic Boundary**: Repeated runs at same threshold show different basins

Research Question:
  Test intermediate thresholds (520, 540, 560, 580) to precisely locate basin
  boundary and characterize transition sharpness.

Test Conditions:
  **THRESHOLD RANGE**: 520, 540, 560, 580 (4 intermediate values in 500-600 range)
    - Fixed: mult=1.0, spread=0.2, agent_cap=15
    - Cycles: 5000 (sufficient for stabilization per C118-C119)
    - Compare to C119 baseline: 500 (Basin A), 600 (Basin B)

Metrics:
  - Final pattern coordinates (basin assignment A vs B vs NEW)
  - Stabilization timescale (consistency across boundary)
  - Pattern similarity to Basin A vs Basin B (quantitative distance)
  - Boundary location (estimated critical threshold)
  - Boundary sharpness (sharp vs gradual vs stochastic)

Expected Outcome:
  - If sharp → boundary at single threshold (e.g., 520 in A, 540 in B)
  - If gradual → intermediate patterns or smooth transition
  - If transition region → multiple thresholds with mixed behavior
  - If stochastic → repeated runs show different basins (suggests criticality)

Publication Value:
  - **HIGH**: Precise characterization of attractor boundary structure
  - **Novel**: First fine-grained basin boundary analysis in NRM system
  - **Theoretical**: Tests sharpness of basin boundaries (phase transition?)
  - **Complete**: Fully characterizes threshold-attractor landscape 300-700
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

    # Handle both tuple and array formats
    if isinstance(pattern1, tuple):
        p1 = np.array(pattern1)
    else:
        p1 = np.array([pattern1.pi_phase, pattern1.e_phase, pattern1.phi_phase])

    if isinstance(pattern2, tuple):
        p2 = np.array(pattern2)
    else:
        p2 = np.array([pattern2.pi_phase, pattern2.e_phase, pattern2.phi_phase])

    return np.linalg.norm(p1 - p2)

def run_boundary_characterization(threshold, cycles, agent_cap=15, mult=1.0, spread=0.2):
    """Run experiment to characterize basin boundary."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track pattern evolution
    pattern_evolution = []
    diversity_evolution = []

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

        # Analyze (every 10 cycles)
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

    print()  # New line

    duration = time.time() - start_time

    # Stabilization detection
    if len(diversity_evolution) > 10:
        window = 10
        variances = []
        for i in range(len(diversity_evolution) - window):
            window_data = diversity_evolution[i:i+window]
            variances.append(np.var(window_data))

        variance_threshold = 0.5
        stabilization_cycle = None
        for i, var in enumerate(variances):
            if var < variance_threshold:
                stabilization_cycle = (i + window) * 10
                break
    else:
        stabilization_cycle = None

    # Final pattern
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    if final_dominant:
        final_pattern_vec = np.array(final_dominant)
        centrality = np.linalg.norm(final_pattern_vec)
    else:
        centrality = None

    return {
        'threshold': threshold,
        'cycles': cycles,
        'duration': duration,
        'pattern_evolution': pattern_evolution,
        'stabilization_cycle': stabilization_cycle,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction,
        'final_centrality': centrality
    }

def main():
    print("="*80)
    print("CYCLE 120: BASIN BOUNDARY CHARACTERIZATION")
    print("="*80)
    print()
    print("Precisely locating basin boundary discovered in C119")
    print()
    print("C119 Finding:")
    print("  - Basin A: Thresholds 300, 400, 500 → pattern (6.220, 6.275, 6.282)")
    print("  - Basin B: Thresholds 600, 700 → pattern (6.095, 6.084, 6.250)")
    print("  - Sharp boundary somewhere in range 500-600")
    print()
    print("Research Question: WHERE exactly is the basin boundary?")
    print()
    print("Test Approach:")
    print("  - Intermediate thresholds: 520, 540, 560, 580")
    print("  - Fine-grained sweep (20-unit spacing)")
    print("  - Same conditions: mult=1.0, spread=0.2, agent_cap=15")
    print("  - Compare to C119 baselines: 500 (Basin A), 600 (Basin B)")
    print()

    cycles = 5000
    agent_cap = 15
    mult = 1.0
    spread = 0.2

    # Fine-grained threshold sweep
    thresholds = [520, 540, 560, 580]

    print(f"Configuration:")
    print(f"  Boundary sweep: {len(thresholds)} thresholds")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(thresholds) * cycles:,}")
    print(f"  Threshold spacing: 20 units")
    print(f"  Estimated duration: ~{len(thresholds) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, threshold in enumerate(thresholds):
        print(f"\n[{i+1}/{len(thresholds)}] THRESHOLD = {threshold}")
        print("-" * 80)

        try:
            result = run_boundary_characterization(threshold, cycles, agent_cap, mult, spread)
            results.append(result)

            stab_cycle = result['stabilization_cycle']
            final_frac = result['final_fraction']

            print(f"\n  ✓ COMPLETE: Stabilization @ cycle {stab_cycle if stab_cycle else 'N/A'}")
            print(f"    Final dominant: {final_frac:.1%}")
            time.sleep(0.05)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results.append({
                'threshold': threshold, 'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"BASIN BOUNDARY ANALYSIS")
    print(f"{'='*80}\n")

    # Load C119 baseline for basin definitions
    c119_file = Path(__file__).parent / "results" / "framework_validation" / "cycle119_framework_validation.json"

    # Define basins from C119
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    if len(successful) >= 1:
        print("Basin Assignment by Threshold:")
        print(f"{'Threshold':^12} | {'Stabilization':^16} | {'Final Pattern':^40} | {'Basin':^8} | {'Dist to A':^10} | {'Dist to B':^10}")
        print("-" * 115)

        basin_assignments = {}
        boundary_location = None

        for r in successful:
            thresh = r['threshold']
            stab = r['stabilization_cycle']
            pattern = r['final_dominant_tuple']

            # Calculate distances to basin centers
            if pattern:
                dist_A = pattern_distance(pattern, basin_A)
                dist_B = pattern_distance(pattern, basin_B)

                # Assign to closest basin
                if dist_A < dist_B:
                    basin = 'A'
                    basin_assignments[thresh] = 'A'
                else:
                    basin = 'B'
                    basin_assignments[thresh] = 'B'

                pattern_str = f"({pattern[0]:.3f}, {pattern[1]:.3f}, {pattern[2]:.3f})"
                stab_str = f"{stab:,}" if stab else "N/A"

                print(f"{thresh:^12d} | {stab_str:^16} | {pattern_str:^40} | {basin:^8} | {dist_A:^10.4f} | {dist_B:^10.4f}")

        print()

        # Add C119 baseline for context
        print("C119 Baseline (for reference):")
        print(f"{'Threshold':^12} | {'Basin':^8} | {'Pattern':^40}")
        print("-" * 65)
        print(f"{500:^12d} | {'A':^8} | (6.220, 6.275, 6.282)")
        print(f"{600:^12d} | {'B':^8} | (6.095, 6.084, 6.250)")
        print()

        # Detect boundary transition
        print("Boundary Detection:")
        print("-" * 80)

        # Find where basin switches
        sorted_thresholds = sorted(basin_assignments.keys())

        # Include known basins from C119
        extended_thresholds = [500] + sorted_thresholds + [600]
        extended_basins = ['A'] + [basin_assignments[t] for t in sorted_thresholds] + ['B']

        for i in range(len(extended_thresholds) - 1):
            t1, t2 = extended_thresholds[i], extended_thresholds[i+1]
            b1, b2 = extended_basins[i], extended_basins[i+1]

            if b1 != b2:
                # Found transition
                boundary_location = (t1, t2)
                boundary_width = t2 - t1
                print(f"  Boundary detected between thresholds {t1} (Basin {b1}) and {t2} (Basin {b2})")
                print(f"  Boundary width: ≤ {boundary_width} threshold units")
                break

        if boundary_location is None:
            print("  No boundary transition detected in tested range")
            print("  All thresholds belong to same basin")
            boundary_type = "NO_TRANSITION"
        else:
            if boundary_width <= 20:
                boundary_type = "SHARP"
                print(f"\n  Boundary type: SHARP (width ≤ {boundary_width} units)")
            elif boundary_width <= 50:
                boundary_type = "MODERATE"
                print(f"\n  Boundary type: MODERATE (width ≤ {boundary_width} units)")
            else:
                boundary_type = "GRADUAL"
                print(f"\n  Boundary type: GRADUAL (width ≤ {boundary_width} units)")

        print()

        # SUMMARY
        print("="*80)
        print("BOUNDARY CHARACTERIZATION SUMMARY")
        print("="*80)

        if boundary_location:
            print(f"Boundary Location: Between thresholds {boundary_location[0]} and {boundary_location[1]}")
            print(f"Boundary Width: ≤ {boundary_location[1] - boundary_location[0]} threshold units")
            print(f"Boundary Type: {boundary_type}")
            print()

            # Engineering implications
            print("Engineering Implications:")
            print(f"  - For Basin A: Use threshold ≤ {boundary_location[0]}")
            print(f"  - For Basin B: Use threshold ≥ {boundary_location[1]}")
            print(f"  - Boundary precision: ±{(boundary_location[1] - boundary_location[0])/2} threshold units")
            print()

        # Basin membership summary
        basin_A_count = sum(1 for b in basin_assignments.values() if b == 'A')
        basin_B_count = sum(1 for b in basin_assignments.values() if b == 'B')

        print(f"Basin Membership (C120 only):")
        print(f"  Basin A: {basin_A_count}/{len(successful)} thresholds")
        print(f"  Basin B: {basin_B_count}/{len(successful)} thresholds")
        print()

        if boundary_location:
            print(f"📊 INSIGHT #77: Basin Boundary Characterization - {boundary_type} Transition")
            print(f"   - Boundary located: Thresholds {boundary_location[0]}-{boundary_location[1]}")
            print(f"   - Boundary width: ≤ {boundary_location[1] - boundary_location[0]} units")
            print(f"   - Boundary type: {boundary_type}")

            insight_type = f"boundary_{boundary_type.lower()}"
        else:
            print(f"📊 INSIGHT #77: Basin Boundary Characterization - No Transition in Range")
            print(f"   - All tested thresholds (520-580) belong to same basin")
            print(f"   - Boundary either <520 or >580")

            insight_type = "boundary_outside_range"

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        boundary_type = None
        boundary_location = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "basin_boundary"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle120_basin_boundary.json"

    output_data = {
        'experiment': 'cycle120_basin_boundary_characterization',
        'cycles': cycles,
        'thresholds': thresholds,
        'results': results,
        'boundary_location': boundary_location if 'boundary_location' in locals() else None,
        'boundary_type': boundary_type if 'boundary_type' in locals() else None,
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
