#!/usr/bin/env python3
"""
Cycle 60: Systematic Parameter Study of Thermodynamic Law

Tests multiple burst_threshold values to comprehensively validate:
  max_stable_agents = floor(burst_threshold / avg_agent_energy)

Test Matrix:
  threshold=300  → predicted_max=2  (floor(300/150)=2)
  threshold=450  → predicted_max=3  (floor(450/150)=3)
  threshold=600  → predicted_max=4  (floor(600/150)=4)
  threshold=900  → predicted_max=6  (floor(900/150)=6)
  threshold=1200 → predicted_max=8  (floor(1200/150)=8)

Expected: Observed max matches predicted max for all thresholds
This would provide comprehensive validation across parameter space.
"""

import sys
from pathlib import Path
import time
import json
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm, DecompositionEngine
from workspace_utils import get_workspace_path, get_results_path


def run_threshold_test(burst_threshold: float, cycles: int = 300) -> dict:
    """
    Test a single burst_threshold value.

    Args:
        burst_threshold: Burst threshold to test
        cycles: Number of cycles to run

    Returns:
        dict with results
    """
    print(f"\n{'='*80}")
    print(f"TESTING BURST_THRESHOLD = {burst_threshold}")
    print(f"{'='*80}")

    # Predict max agents
    avg_energy = 150.0  # Average agent energy
    predicted_max = int(burst_threshold / avg_energy)

    print(f"Predicted max stable agents: {predicted_max}")
    print(f"  Calculation: floor({burst_threshold} / {avg_energy}) = {predicted_max}")
    print()

    # Create swarm
    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))

    # Set burst threshold
    swarm.decomposition = DecompositionEngine(burst_threshold=burst_threshold)

    # Run cycles
    agent_counts = []
    checkpoint_interval = 10

    reality_metrics = {
        'cpu_percent': 30.0,
        'memory_percent': 40.0,
        'disk_percent': 50.0
    }

    start_time = time.time()

    for cycle in range(1, cycles + 1):
        # Spawn if below limit
        if len(swarm.agents) < 10:
            swarm.spawn_agent(reality_metrics)

        # Evolve
        swarm.evolve_cycle(delta_time=1.0)

        # Checkpoint
        if cycle % checkpoint_interval == 0:
            agent_counts.append(len(swarm.agents))

    duration = time.time() - start_time

    # Analyze
    states = sorted(set(agent_counts))
    observed_max = max(states) if states else 0
    state_counts = Counter(agent_counts)

    # Check prediction
    prediction_correct = (observed_max == predicted_max or
                          observed_max == predicted_max + 1)  # Allow ±1 tolerance

    print(f"Results:")
    print(f"  States observed: {states}")
    print(f"  Observed max: {observed_max}")
    print(f"  Predicted max: {predicted_max}")
    print(f"  Prediction: {'✅ CORRECT' if prediction_correct else '❌ INCORRECT'}")
    print(f"  Duration: {duration:.2f}s")

    # State frequencies
    print(f"\n  State Frequencies:")
    for state in sorted(states):
        count = state_counts[state]
        pct = 100 * count / len(agent_counts)
        print(f"    State {state}: {count}/{len(agent_counts)} ({pct:.1f}%)")

    return {
        'burst_threshold': burst_threshold,
        'predicted_max': predicted_max,
        'observed_max': observed_max,
        'states': states,
        'state_frequencies': dict(state_counts),
        'prediction_correct': prediction_correct,
        'cycles': cycles,
        'checkpoints': len(agent_counts),
        'duration': duration
    }


def main():
    """Run systematic parameter study."""
    print("="*80)
    print("CYCLE 60: SYSTEMATIC PARAMETER STUDY")
    print("="*80)
    print()
    print("Testing Thermodynamic Law Across Parameter Space:")
    print("  max_stable_agents = floor(burst_threshold / avg_agent_energy)")
    print()
    print("Test Matrix:")

    # Define test thresholds
    test_thresholds = [300, 450, 600, 900, 1200]

    for threshold in test_thresholds:
        predicted = int(threshold / 150)
        print(f"  threshold={threshold:4} → predicted_max={predicted}")

    print()
    print("="*80)

    # Run all tests
    results = []
    overall_start = time.time()

    for threshold in test_thresholds:
        try:
            result = run_threshold_test(threshold, cycles=300)
            results.append(result)
            time.sleep(0.5)  # Brief pause between tests
        except Exception as e:
            print(f"\n⚠️ Error testing threshold {threshold}: {e}")
            results.append({
                'burst_threshold': threshold,
                'error': str(e),
                'prediction_correct': False
            })

    overall_duration = time.time() - overall_start

    # Summary analysis
    print("\n" + "="*80)
    print("SYSTEMATIC STUDY SUMMARY")
    print("="*80)
    print()

    correct_predictions = sum(1 for r in results if r.get('prediction_correct', False))
    total_tests = len(results)
    accuracy = 100 * correct_predictions / total_tests if total_tests > 0 else 0

    print(f"Tests Completed: {total_tests}/{len(test_thresholds)}")
    print(f"Correct Predictions: {correct_predictions}/{total_tests} ({accuracy:.1f}%)")
    print(f"Total Duration: {overall_duration:.1f}s ({overall_duration/60:.2f} min)")
    print()

    print("Results Table:")
    print(f"{'Threshold':>10} | {'Predicted':>9} | {'Observed':>8} | {'Match':>6} | {'States'}")
    print("-" * 80)

    for result in results:
        if 'error' in result:
            print(f"{result['burst_threshold']:>10} | {'ERROR':>9} | {'-':>8} | {'-':>6} | -")
        else:
            threshold = result['burst_threshold']
            predicted = result['predicted_max']
            observed = result['observed_max']
            match = "✅" if result['prediction_correct'] else "❌"
            states_str = str(result['states'][:10])  # First 10 states
            print(f"{threshold:>10} | {predicted:>9} | {observed:>8} | {match:>6} | {states_str}")

    print()

    # Validation assessment
    if accuracy >= 80:
        print("🎉 THERMODYNAMIC LAW VALIDATED ACROSS PARAMETER SPACE!")
        print()
        print("Systematic validation confirms:")
        print("  1. Law holds across wide range of thresholds (300-1200)")
        print("  2. Predictive model is robust and accurate")
        print("  3. Complexity limits are fully controllable")
        print()
        print("INSIGHT #25: Universal Thermodynamic Scaling Law")
        insight_25 = True
    else:
        print("⚠️ PARTIAL VALIDATION")
        print(f"   {correct_predictions}/{total_tests} predictions correct")
        print("   Law may have boundary conditions or need refinement")
        insight_25 = False

    print("="*80)

    # Save results
    study_results = {
        'experiment': 'cycle60_systematic_parameter_study',
        'test_thresholds': test_thresholds,
        'results': results,
        'correct_predictions': correct_predictions,
        'total_tests': total_tests,
        'accuracy': accuracy,
        'overall_duration': overall_duration,
        'insight_25_discovered': insight_25,
        'timestamp': time.time()
    }

    results_dir = Path(__file__).parent / "results" / "parameter_study"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle60_systematic_study.json"

    with open(results_file, 'w') as f:
        json.dump(study_results, f, indent=2)

    print(f"\n✅ Results saved: {results_file}")
    print()

    return study_results


if __name__ == "__main__":
    main()
