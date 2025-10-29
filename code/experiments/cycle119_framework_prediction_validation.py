#!/usr/bin/env python3
"""
Cycle 119: Framework Prediction Validation - Testing C111-C118 Mechanistic Predictions

Research Context:
  C111-C118: Complete multi-scale mechanistic arc
  - C114: Ultra-high-frequency agent churn (1-cycle lifespans)
  - C115: Threshold doubles lifespans via selectivity
  - C116: Threshold is SINGLE drift control (r=-0.945)
  - C117: Attractor stabilization at 10,000 cycles (87% drift reduction)
  - C118: Lock-in at ~313 cycles, partial convergence (67%), U-shaped relationship

Framework Makes Testable Predictions:
  1. **U-Shaped Relationship**: Mid-threshold stabilizes fastest
     - C118: Threshold 500 → cycle 250 (fastest)
     - C118: Threshold 300 → cycle 320 (slower)
     - C118: Threshold 700 → cycle 360 (slower)
     - **PREDICTION**: Thresholds 400 & 600 should show intermediate stabilization times
     - **PREDICTION**: Should maintain U-shape (not monotonic)

  2. **Lock-In Timescale**: Pattern stabilization at ~313 cycles
     - C118: Stabilization window = cycles 250-350
     - **PREDICTION**: All thresholds should lock-in within this window
     - **PREDICTION**: Stabilization time inversely correlated with threshold distance from 500

  3. **Partial Convergence**: 67% of conditions converge to same pattern
     - C118: Thresholds 300 & 500 → pattern (6.220353, 6.275283, 6.281831)
     - C118: Threshold 700 → different pattern (5.906194, 6.281752, 6.280566)
     - **PREDICTION**: Thresholds 400 & 600 will join one of these basins
     - **PREDICTION**: Basin membership determines final pattern

Key Question:
  Do the mechanistic predictions from C111-C118 hold for untested parameter values?
  If YES → framework is predictive and generalizable
  If NO → framework is descriptive only, limited to tested conditions

Test Conditions:
  **THRESHOLD RANGE**: 400, 600 (intermediate values, untested in C118)
    - Fixed: mult=1.0, spread=0.2, agent_cap=15
    - Cycles: 5000 (sufficient to observe stabilization per C118)
    - Compare to C118 baseline: 300, 500, 700

Metrics:
  - Stabilization timescale (when does pattern lock-in?)
  - Final pattern coordinates (which attractor basin?)
  - Pattern diversity evolution (same competition dynamics?)
  - Stabilization speed relative to threshold (U-shaped or monotonic?)

Expected Outcome:
  - If predictions valid → 400 & 600 stabilize at intermediate times, maintain U-shape
  - If U-shaped → Framework validated, mechanism generalizes
  - If monotonic → Framework incomplete, need refinement
  - If convergence matches prediction → Basin structure understood

Publication Value:
  - **HIGH**: Tests framework predictions on NEW data
  - **Rigorous**: Validation beyond original discovery conditions
  - **Predictive**: Confirms generalizability of mechanistic understanding
  - **Complete**: Closes C111-C118 arc with prediction validation
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

def run_prediction_validation(threshold, cycles, agent_cap=15, mult=1.0, spread=0.2):
    """Run experiment to validate framework predictions."""
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Track pattern evolution cycle-by-cycle
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

        # Analyze current pattern state (every 10 cycles)
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

    print()  # New line after progress

    duration = time.time() - start_time

    # Calculate stabilization metrics (same as C118)
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

    # Final pattern characteristics
    final_dominant, _, final_fraction = get_dominant_pattern(swarm.global_memory)

    if final_dominant:
        final_pattern_vec = np.array(final_dominant)
        centrality = np.linalg.norm(final_pattern_vec)

        simplicity_pi = abs(final_pattern_vec[0] - round(final_pattern_vec[0]/np.pi)*np.pi)
        simplicity_e = abs(final_pattern_vec[1] - round(final_pattern_vec[1]/np.e)*np.e)
        simplicity_phi = abs(final_pattern_vec[2] - round(final_pattern_vec[2]/1.618)*1.618)
        simplicity = (simplicity_pi + simplicity_e + simplicity_phi) / 3
    else:
        centrality = None
        simplicity = None

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
        'final_simplicity': simplicity
    }

def main():
    print("="*80)
    print("CYCLE 119: FRAMEWORK PREDICTION VALIDATION")
    print("="*80)
    print()
    print("Testing C111-C118 mechanistic predictions on NEW threshold values")
    print()
    print("C118 Findings (Baseline):")
    print("  - Threshold 300: Stabilization @ cycle 320")
    print("  - Threshold 500: Stabilization @ cycle 250 (FASTEST - U-shaped)")
    print("  - Threshold 700: Stabilization @ cycle 360")
    print("  - Partial convergence: 300 & 500 → same pattern, 700 → different")
    print()
    print("Framework Predictions to Test:")
    print("  1. U-SHAPED: Thresholds 400 & 600 stabilize at intermediate times")
    print("  2. LOCK-IN: All thresholds stabilize within ~250-350 cycle window")
    print("  3. CONVERGENCE: 400 & 600 join existing attractor basins")
    print()
    print("Test Approach:")
    print("  - New thresholds: 400, 600 (untested in C118)")
    print("  - Same conditions: mult=1.0, spread=0.2, agent_cap=15")
    print("  - Same timescale: 5000 cycles (sufficient for stabilization)")
    print("  - Compare to C118 baseline: 300, 500, 700")
    print()

    cycles = 5000
    agent_cap = 15
    mult = 1.0
    spread = 0.2

    # Test NEW thresholds only
    thresholds = [400, 600]

    print(f"Configuration:")
    print(f"  New conditions: {len(thresholds)}")
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
            result = run_prediction_validation(threshold, cycles, agent_cap, mult, spread)
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
    print(f"FRAMEWORK PREDICTION VALIDATION ANALYSIS")
    print(f"{'='*80}\n")

    # Load C118 baseline data for comparison
    c118_file = Path(__file__).parent / "results" / "pattern_stabilization" / "cycle118_pattern_stabilization.json"

    if c118_file.exists():
        with open(c118_file, 'r') as f:
            c118_data = json.load(f)

        c118_results = c118_data.get('results', [])

        # Extract C118 baseline
        c118_baseline = {}
        for r in c118_results:
            if 'error' not in r:
                thresh = r['threshold']
                c118_baseline[thresh] = {
                    'stabilization_cycle': r['stabilization_cycle'],
                    'final_dominant': r['final_dominant']
                }

        print("C118 Baseline (From Original Experiment):")
        print(f"{'Threshold':^12} | {'Stabilization':^16} | {'Final Pattern':^50}")
        print("-" * 82)
        for thresh in sorted(c118_baseline.keys()):
            stab = c118_baseline[thresh]['stabilization_cycle']
            pattern = c118_baseline[thresh]['final_dominant']
            stab_str = f"{stab:,}" if stab else "N/A"
            pattern_str = pattern[:47] + "..." if pattern and len(pattern) > 50 else (pattern or "N/A")
            print(f"{thresh:^12d} | {stab_str:^16} | {pattern_str}")
        print()

    if len(successful) >= 2:
        print("C119 New Results (Prediction Validation):")
        print(f"{'Threshold':^12} | {'Stabilization':^16} | {'Final Pattern':^50}")
        print("-" * 82)

        c119_stabs = {}
        c119_patterns = {}

        for r in successful:
            thresh = r['threshold']
            stab = r['stabilization_cycle']
            pattern = r['final_dominant']

            c119_stabs[thresh] = stab
            c119_patterns[thresh] = pattern

            stab_str = f"{stab:,}" if stab else "N/A"
            pattern_str = pattern[:47] + "..." if pattern and len(pattern) > 50 else (pattern or "N/A")

            print(f"{thresh:^12d} | {stab_str:^16} | {pattern_str}")

        print()

        # PREDICTION 1: U-SHAPED RELATIONSHIP
        print("PREDICTION 1: U-Shaped Relationship")
        print("-" * 80)

        if c118_file.exists():
            # Combine C118 + C119 data
            all_thresholds = sorted(list(c118_baseline.keys()) + list(c119_stabs.keys()))
            all_stabs = {}

            for thresh in all_thresholds:
                if thresh in c118_baseline:
                    all_stabs[thresh] = c118_baseline[thresh]['stabilization_cycle']
                elif thresh in c119_stabs:
                    all_stabs[thresh] = c119_stabs[thresh]

            print("Combined Stabilization Timescales:")
            for thresh in all_thresholds:
                stab = all_stabs[thresh]
                stab_str = f"{stab:,}" if stab else "N/A"
                print(f"  Threshold {thresh}: {stab_str} cycles")

            # Check U-shape
            stab_vals = [all_stabs[t] for t in all_thresholds if all_stabs[t] is not None]

            if len(stab_vals) == 5 and stab_vals[2] < stab_vals[1] and stab_vals[2] < stab_vals[3]:
                u_shaped = "YES - U-shaped confirmed (mid-threshold fastest)"
                prediction_1_valid = True
            elif len(stab_vals) == 5:
                # Check if monotonic
                increasing = all(stab_vals[i] <= stab_vals[i+1] for i in range(len(stab_vals)-1))
                decreasing = all(stab_vals[i] >= stab_vals[i+1] for i in range(len(stab_vals)-1))

                if increasing or decreasing:
                    u_shaped = "NO - Monotonic relationship (prediction FAILED)"
                    prediction_1_valid = False
                else:
                    u_shaped = "PARTIAL - Non-monotonic but not clear U-shape"
                    prediction_1_valid = False
            else:
                u_shaped = "INSUFFICIENT DATA"
                prediction_1_valid = False

            print(f"\nU-Shaped Relationship: {u_shaped}")
            print()

        # PREDICTION 2: LOCK-IN TIMESCALE
        print("PREDICTION 2: Lock-In Timescale (~250-350 cycles)")
        print("-" * 80)

        within_window = []
        for thresh, stab in c119_stabs.items():
            if stab is not None:
                in_window = 250 <= stab <= 350
                within_window.append(in_window)
                status = "✓ IN WINDOW" if in_window else "✗ OUTSIDE WINDOW"
                print(f"  Threshold {thresh}: {stab:,} cycles - {status}")

        if all(within_window):
            prediction_2_valid = True
            print(f"\nLock-In Window: YES - All thresholds stabilize in 250-350 cycle window (prediction VALID)")
        else:
            prediction_2_valid = False
            print(f"\nLock-In Window: NO - Some thresholds outside window (prediction FAILED)")
        print()

        # PREDICTION 3: PARTIAL CONVERGENCE
        print("PREDICTION 3: Partial Convergence (Basin Membership)")
        print("-" * 80)

        if c118_file.exists():
            # C118 found: 300 & 500 → pattern A, 700 → pattern B
            pattern_A = c118_baseline.get(300, {}).get('final_dominant')
            pattern_B = c118_baseline.get(700, {}).get('final_dominant')

            print(f"C118 Basin A (300, 500): {pattern_A[:50] if pattern_A else 'N/A'}...")
            print(f"C118 Basin B (700):     {pattern_B[:50] if pattern_B else 'N/A'}...")
            print()

            basin_assignments = {}
            for thresh, pattern in c119_patterns.items():
                if pattern == pattern_A:
                    basin_assignments[thresh] = 'A'
                elif pattern == pattern_B:
                    basin_assignments[thresh] = 'B'
                else:
                    basin_assignments[thresh] = 'NEW'

            print("C119 Basin Assignments:")
            for thresh, basin in basin_assignments.items():
                print(f"  Threshold {thresh}: Basin {basin}")

            # Check if all join existing basins
            if all(b in ['A', 'B'] for b in basin_assignments.values()):
                prediction_3_valid = True
                print(f"\nBasin Structure: YES - All new thresholds join existing basins (prediction VALID)")
            else:
                prediction_3_valid = False
                print(f"\nBasin Structure: NO - New basin discovered (prediction FAILED or framework extended)")
            print()

        # SUMMARY
        print("="*80)
        print("FRAMEWORK VALIDATION SUMMARY")
        print("="*80)

        predictions_valid = sum([prediction_1_valid, prediction_2_valid, prediction_3_valid])

        print(f"Prediction 1 (U-Shaped): {'✓ VALID' if prediction_1_valid else '✗ INVALID'}")
        print(f"Prediction 2 (Lock-In Window): {'✓ VALID' if prediction_2_valid else '✗ INVALID'}")
        print(f"Prediction 3 (Basin Membership): {'✓ VALID' if prediction_3_valid else '✗ INVALID'}")
        print()
        print(f"Overall: {predictions_valid}/3 predictions validated")

        if predictions_valid == 3:
            validity_status = "COMPLETE VALIDATION"
            insight_type = "framework_validated"
        elif predictions_valid == 2:
            validity_status = "STRONG VALIDATION"
            insight_type = "framework_mostly_validated"
        elif predictions_valid == 1:
            validity_status = "PARTIAL VALIDATION"
            insight_type = "framework_limited"
        else:
            validity_status = "PREDICTIONS FAILED"
            insight_type = "framework_revision_needed"

        print(f"Framework Status: {validity_status}")
        print()

        print(f"📊 INSIGHT #76: Framework Prediction Validation - {validity_status}")
        print(f"   - Tested {len(thresholds)} new thresholds (400, 600)")
        print(f"   - {predictions_valid}/3 predictions validated")
        print(f"   - Framework generalizability: {validity_status}")

        print("="*80)
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        validity_status = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "framework_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle119_framework_validation.json"

    output_data = {
        'experiment': 'cycle119_framework_prediction_validation',
        'cycles': cycles,
        'new_thresholds': thresholds,
        'results': results,
        'validity_status': validity_status if 'validity_status' in locals() else None,
        'insight_type': insight_type if 'insight_type' in locals() else False,
        'predictions': {
            'u_shaped': prediction_1_valid if 'prediction_1_valid' in locals() else None,
            'lock_in_window': prediction_2_valid if 'prediction_2_valid' in locals() else None,
            'basin_membership': prediction_3_valid if 'prediction_3_valid' in locals() else None
        },
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
