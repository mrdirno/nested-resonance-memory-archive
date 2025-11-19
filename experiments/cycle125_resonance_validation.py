#!/usr/bin/env python3
"""
Cycle 125: Trajectory Resonance Validation - Testing "First Closer" Predictive Framework

Research Context:
  C124: Spread-Basin Mechanism Investigation
  - TRAJECTORY RESONANCE mechanism identified
  - Basin A spreads (0.2, 0.3): Late trajectory shift (first closer at cycles 870-2600)
  - Basin B spreads (0.05-0.15, 0.25): Immediate attraction (first closer at cycle 10)
  - "First Closer" metric proposed as basin predictor:
    - If first closer < 100 cycles → Basin B likely
    - If first closer > 500 cycles → Basin A likely

Research Gap:
  C124 mechanism based on 6 spread values only
  Unknown if "first closer" metric reliably predicts basin at intermediate spreads
  Unknown if oscillating pattern continues at finer granularity
  Need validation of trajectory resonance hypothesis on unseen spread values

Key Question:
  Does the "first closer" metric reliably predict final basin assignment
  at intermediate spread values not tested in C123/C124?

Hypotheses to Test:
  1. **Predictive Power**: "First closer" cycle predicts basin with >80% accuracy
     - Prediction: First closer < 100 → Basin B
     - Prediction: First closer > 500 → Basin A
     - Test: Measure prediction accuracy on new spread values

  2. **Fine-Grained Oscillation**: Oscillating pattern continues at finer scale
     - Prediction: Intermediate spreads show similar B/A alternation
     - Test: Map basin assignments at 0.05 intervals (finer than C123's 0.1)

  3. **Critical Transition Regions**: Identify exact spread ranges for each basin
     - Prediction: Sharp transitions between Basin A and B regions
     - Test: Find boundary points where basin switches

  4. **Mechanism Generalizability**: Trajectory resonance applies beyond tested spreads
     - Prediction: Same late-shift vs immediate-attraction pattern
     - Test: Verify mechanism holds for intermediate values

Research Question:
  Test intermediate spread values (0.175, 0.225, 0.275) to validate "first closer"
  predictive framework and characterize fine-grained structure of oscillating pattern.

Test Conditions:
  **FIXED**:
    - Threshold: 400 (same as C123/C124)
    - Mult: 1.0 (same as C123/C124)
    - Cycles: 5000 per run (same as C123/C124)
    - Tracking: Every 10 cycles (same as C124)

  **NEW SPREAD VALUES** (Intermediate):
    - 0.175 (between 0.15 Basin B and 0.20 Basin A)
    - 0.225 (between 0.20 Basin A and 0.25 Basin B)
    - 0.275 (between 0.25 Basin B and 0.30 Basin A)

  **VALIDATION APPROACH**:
    1. Predict basin from "first closer" cycle
    2. Compare prediction to actual final basin
    3. Measure prediction accuracy

Metrics:
  - **"First Closer" Cycle**: When pattern becomes closer to final basin
  - **Final Basin**: Actual basin assignment at cycle 5000
  - **Prediction Accuracy**: % of correct predictions from "first closer" metric
  - **Basin Sequence**: Pattern at 0.05 intervals (finer resolution than C123)
  - **Lock-in Timing**: When pattern stabilizes
  - **Trajectory Type**: Immediate attraction vs late shift

Expected Outcome:
  - If predictive power validated → "first closer" metric >80% accurate
  - If fine-grained oscillation → see continued B/A alternation at 0.05 intervals
  - If critical transitions → identify exact spread boundaries for each basin
  - If mechanism generalizes → same late-shift/immediate-attraction pattern

Publication Value:
  - **HIGH**: Validates C124 trajectory resonance mechanism on new data
  - **Rigorous**: Tests predictive framework on unseen spread values
  - **Complete**: Fine-grained mapping at 0.05 intervals (2x resolution of C123)
  - **Predictive**: Demonstrates practical basin prediction from early tracking
  - **Theoretical**: Validates geometric resonance hypothesis
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

def run_resonance_validation(threshold, mult, spread, cycles, agent_cap=15):
    """Run experiment with tracking to validate resonance mechanism."""
    workspace = Path("/Volumes/dual/DUALITY-ZERO-V2/workspace")
    swarm = FractalSwarm(str(workspace), clear_on_init=True)
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)
    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Basin centers from C119-C121
    basin_A = (np.float64(6.220353), np.float64(6.275283), np.float64(6.281831))
    basin_B = (np.float64(6.09469), np.float64(6.083677), np.float64(6.250047))

    # Track evolution
    distance_evolution = []

    print(f"\nRunning spread={spread} validation for {cycles} cycles...")
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

            # Calculate distances to basins
            if dominant:
                dist_A = pattern_distance(dominant, basin_A)
                dist_B = pattern_distance(dominant, basin_B)

                distance_evolution.append({
                    'cycle': cycle,
                    'dist_A': dist_A,
                    'dist_B': dist_B,
                    'closer_to': 'A' if dist_A < dist_B else 'B'
                })

    print()  # New line

    duration = time.time() - start_time

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

    # Find "first closer to final basin" cycle
    if distance_evolution and final_basin:
        final_basin_cycles = [d['cycle'] for d in distance_evolution if d['closer_to'] == final_basin]
        if final_basin_cycles:
            first_closer_cycle = min(final_basin_cycles)
        else:
            first_closer_cycle = None
    else:
        first_closer_cycle = None

    # Predict basin from "first closer" metric (C124 hypothesis)
    if first_closer_cycle is not None:
        if first_closer_cycle < 100:
            predicted_basin = 'B'
        elif first_closer_cycle > 500:
            predicted_basin = 'A'
        else:
            predicted_basin = 'UNCERTAIN'
    else:
        predicted_basin = 'UNKNOWN'

    return {
        'threshold': threshold,
        'mult': mult,
        'spread': spread,
        'cycles': cycles,
        'duration': duration,
        'distance_evolution': distance_evolution,
        'first_closer_cycle': first_closer_cycle,
        'predicted_basin': predicted_basin,
        'final_basin': final_basin,
        'final_dominant': str(final_dominant) if final_dominant else None,
        'final_dominant_tuple': final_dominant,
        'final_fraction': final_fraction,
        'final_dist_A': final_dist_A,
        'final_dist_B': final_dist_B,
        'prediction_correct': (predicted_basin == final_basin) if predicted_basin not in ['UNCERTAIN', 'UNKNOWN'] and final_basin else None
    }

def main():
    print("="*80)
    print("CYCLE 125: TRAJECTORY RESONANCE VALIDATION")
    print("="*80)
    print()
    print("Validating 'first closer' predictive framework on intermediate spread values")
    print()
    print("C124 Discovery:")
    print("  - TRAJECTORY RESONANCE mechanism identified")
    print("  - Basin A spreads (0.2, 0.3): Late trajectory shift (first closer 870-2600)")
    print("  - Basin B spreads (0.05-0.15, 0.25): Immediate attraction (first closer 10)")
    print("  - Predictive framework: first closer < 100 → Basin B, > 500 → Basin A")
    print()
    print("Research Question: Does 'first closer' metric reliably predict basin?")
    print()
    print("Test Approach:")
    print("  - Test intermediate spread values (0.175, 0.225, 0.275)")
    print("  - Predict basin from 'first closer' cycle")
    print("  - Compare prediction to actual final basin")
    print("  - Measure prediction accuracy")
    print()

    cycles = 5000
    agent_cap = 15
    threshold = 400  # Fixed (same as C123/C124)
    mult = 1.0  # Fixed (same as C123/C124)

    # Intermediate spread values (fill gaps in C123 sequence)
    spread_values = [0.175, 0.225, 0.275]

    print(f"Configuration:")
    print(f"  Fixed threshold: {threshold}")
    print(f"  Fixed mult: {mult}")
    print(f"  Intermediate spread values: {spread_values}")
    print(f"  Total experiments: {len(spread_values)}")
    print(f"  Cycles per run: {cycles:,}")
    print(f"  Total cycles: {len(spread_values) * cycles:,}")
    print(f"  Estimated duration: ~{len(spread_values) * cycles * 0.04 / 60:.1f} minutes")
    print("="*80)

    results = []
    start_time = time.time()

    for i, spread in enumerate(spread_values):
        print(f"\n[{i+1}/{len(spread_values)}] SPREAD = {spread}")
        print("-" * 80)

        try:
            result = run_resonance_validation(threshold, mult, spread, cycles, agent_cap)
            results.append(result)

            first_closer = result['first_closer_cycle']
            predicted = result['predicted_basin']
            actual = result['final_basin']
            correct = result['prediction_correct']

            print(f"\n  ✓ COMPLETE:")
            print(f"    First closer: {first_closer if first_closer else 'N/A'}")
            print(f"    Predicted basin: {predicted}")
            print(f"    Actual basin: {actual}")
            if correct is not None:
                print(f"    Prediction: {'✓ CORRECT' if correct else '✗ WRONG'}")

            time.sleep(0.05)
        except Exception as e:
            print(f"\n  ✗ ERROR: {e}")
            results.append({
                'threshold': threshold, 'mult': mult, 'spread': spread, 'error': str(e)
            })

    duration = time.time() - start_time
    successful = [r for r in results if 'error' not in r]

    print(f"\n{'='*80}")
    print(f"VALIDATION ANALYSIS")
    print(f"{'='*80}\n")

    if len(successful) >= 1:
        print("Prediction Validation:")
        print(f"{'Spread':^8} | {'First Closer':^13} | {'Predicted':^10} | {'Actual':^10} | {'Correct?':^10}")
        print("-" * 70)

        validation_data = []

        for r in successful:
            spread = r['spread']
            first_closer = r['first_closer_cycle'] if r['first_closer_cycle'] else 'N/A'
            predicted = r['predicted_basin']
            actual = r['final_basin']
            correct = r['prediction_correct']

            validation_data.append({
                'spread': spread,
                'first_closer': first_closer,
                'predicted': predicted,
                'actual': actual,
                'correct': correct
            })

            first_closer_str = str(first_closer) if first_closer != 'N/A' else 'N/A'
            correct_str = '✓ YES' if correct else ('✗ NO' if correct is not None else 'N/A')

            print(f"{spread:^8.3f} | {first_closer_str:^13} | {predicted:^10} | {actual:^10} | {correct_str:^10}")

        print()

        # Calculate prediction accuracy
        predictions_made = [v for v in validation_data if v['correct'] is not None]
        if predictions_made:
            correct_predictions = sum(1 for v in predictions_made if v['correct'])
            accuracy = correct_predictions / len(predictions_made) * 100

            print("="*80)
            print("PREDICTION ACCURACY")
            print("="*80)
            print(f"  Total predictions: {len(predictions_made)}")
            print(f"  Correct predictions: {correct_predictions}")
            print(f"  Prediction accuracy: {accuracy:.1f}%")
            print()

            if accuracy >= 80:
                print(f"✓ VALIDATION SUCCESSFUL: Prediction accuracy ≥80% ({accuracy:.1f}%)")
                print(f"✓ 'First closer' metric is RELIABLE basin predictor")
                validation_status = "VALIDATED"
            else:
                print(f"⚠️ VALIDATION PARTIAL: Prediction accuracy <80% ({accuracy:.1f}%)")
                print(f"⚠️ 'First closer' metric has LIMITED predictive power")
                validation_status = "PARTIAL"
        else:
            accuracy = None
            validation_status = "INSUFFICIENT_DATA"

        # Fine-grained basin sequence (combine with C123 data)
        print()
        print("="*80)
        print("FINE-GRAINED BASIN SEQUENCE")
        print("="*80)

        # C123 basins: 0.05→B, 0.10→B, 0.15→B, 0.20→A, 0.25→B, 0.30→A
        # C125 basins: 0.175→?, 0.225→?, 0.275→?

        combined_sequence = [
            (0.05, 'B'),
            (0.10, 'B'),
            (0.15, 'B'),
        ]

        # Add C125 intermediate value (0.175)
        spread_0175 = next((v for v in validation_data if v['spread'] == 0.175), None)
        if spread_0175:
            combined_sequence.append((0.175, spread_0175['actual']))

        combined_sequence.append((0.20, 'A'))

        # Add C125 intermediate value (0.225)
        spread_0225 = next((v for v in validation_data if v['spread'] == 0.225), None)
        if spread_0225:
            combined_sequence.append((0.225, spread_0225['actual']))

        combined_sequence.append((0.25, 'B'))

        # Add C125 intermediate value (0.275)
        spread_0275 = next((v for v in validation_data if v['spread'] == 0.275), None)
        if spread_0275:
            combined_sequence.append((0.275, spread_0275['actual']))

        combined_sequence.append((0.30, 'A'))

        print("Combined basin sequence (C123 + C125):")
        spreads = [s for s, _ in combined_sequence]
        basins = [b for _, b in combined_sequence]

        print(f"  Spreads: {spreads}")
        print(f"  Basins:  {basins}")
        print()

        # Check for transitions
        transitions = []
        for i in range(len(basins) - 1):
            if basins[i] != basins[i+1]:
                transitions.append({
                    'from_spread': spreads[i],
                    'to_spread': spreads[i+1],
                    'from_basin': basins[i],
                    'to_basin': basins[i+1]
                })

        if transitions:
            print(f"Transitions detected: {len(transitions)}")
            for t in transitions:
                print(f"  {t['from_spread']:.3f} (Basin {t['from_basin']}) → {t['to_spread']:.3f} (Basin {t['to_basin']})")
        else:
            print("No transitions detected (constant basin)")

        print()
        print(f"📊 INSIGHT #82: Trajectory Resonance Validation - {validation_status}")
        print(f"   - Tested intermediate spread values (0.175, 0.225, 0.275)")
        if accuracy is not None:
            print(f"   - Prediction accuracy: {accuracy:.1f}%")
        print(f"   - Validation status: {validation_status}")
        print(f"   - Fine-grained basin sequence characterized at 0.05 intervals")

        print("="*80)

        insight_type = validation_status.lower()
    else:
        print("⚠️ Insufficient successful runs for analysis")
        insight_type = False
        validation_status = None
        accuracy = None

    # Save results
    results_dir = Path(__file__).parent / "results" / "resonance_validation"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle125_resonance_validation.json"

    output_data = {
        'experiment': 'cycle125_resonance_validation',
        'threshold': threshold,
        'mult': mult,
        'spread_values': spread_values,
        'cycles': cycles,
        'results': results,
        'validation_status': validation_status if 'validation_status' in locals() else None,
        'prediction_accuracy': accuracy if 'accuracy' in locals() else None,
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
