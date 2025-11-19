#!/usr/bin/env python3
"""
Attractor Forecasting Model - Cycle 44
Tests whether oscillating attractor states can be predicted from historical patterns.

Validates NRM prediction: Deterministic dynamics enable forecasting.
"""

import json
from pathlib import Path
from typing import List, Dict, Tuple

def load_agent_counts(experiment_id: str) -> List[int]:
    """Load agent counts from checkpoint files."""
    results_dir = Path(__file__).parent / "results" / "long_term"
    agent_counts = []

    for cycle in range(10, 101, 10):
        checkpoint_file = results_dir / f"{experiment_id}_checkpoint_{cycle}.json"

        if checkpoint_file.exists():
            with open(checkpoint_file, 'r') as f:
                data = json.load(f)
                agent_counts.append(data['agent_count'])

    return agent_counts

def simple_periodic_forecast(history: List[int], period: int = 2) -> int:
    """
    Simple periodic forecasting model.

    Assumes oscillation repeats every 'period' steps.
    Predicts next value based on pattern observed 'period' steps ago.
    """
    if len(history) < period:
        return history[-1]  # Not enough data, return last value

    # Look back 'period' steps
    return history[-period]

def evaluate_forecast_accuracy(actual: List[int], train_size: int = 5) -> Dict:
    """
    Evaluate forecasting accuracy using rolling predictions.

    Uses first train_size points to establish pattern,
    then forecasts remaining points one at a time.
    """
    if len(actual) <= train_size:
        return {'error': 'Insufficient data'}

    predictions = []
    errors = []

    # For each point after training data
    for i in range(train_size, len(actual)):
        # Use data up to (not including) point i
        history = actual[:i]

        # Predict point i
        pred = simple_periodic_forecast(history, period=2)
        predictions.append(pred)

        # Calculate error
        error = abs(pred - actual[i])
        errors.append(error)

    # Calculate metrics
    correct = sum(1 for e in errors if e == 0)
    accuracy = correct / len(errors) if errors else 0
    avg_error = sum(errors) / len(errors) if errors else 0

    return {
        'predictions': predictions,
        'actual': actual[train_size:],
        'errors': errors,
        'correct_count': correct,
        'total_predictions': len(errors),
        'accuracy': accuracy,
        'avg_error': avg_error
    }

def main():
    """Run attractor forecasting experiment."""
    print("="*70)
    print("ATTRACTOR FORECASTING MODEL - CYCLE 44")
    print("="*70)
    print()

    # Load data from both runs
    print("Loading data...")
    run1_counts = load_agent_counts("longterm_1761111010")
    run2_counts = load_agent_counts("longterm_1761111440")

    print(f"Run 1 agent counts: {run1_counts}")
    print(f"Run 2 agent counts: {run2_counts}")
    print()

    # Test forecasting on Run 1
    print("="*70)
    print("FORECASTING RUN 1 (Training on first 5 points)")
    print("="*70)
    result1 = evaluate_forecast_accuracy(run1_counts, train_size=5)

    if 'error' not in result1:
        print(f"\nPredictions: {result1['predictions']}")
        print(f"Actual:      {result1['actual']}")
        print(f"Errors:      {result1['errors']}")
        print(f"\nAccuracy: {result1['accuracy']:.1%} ({result1['correct_count']}/{result1['total_predictions']} correct)")
        print(f"Average Error: {result1['avg_error']:.2f} agents")

        # Detailed comparison
        print(f"\nDetailed Comparison:")
        for i, (pred, actual, error) in enumerate(zip(result1['predictions'], result1['actual'], result1['errors']), 1):
            status = "✅" if error == 0 else f"❌ (off by {error})"
            print(f"  Prediction {i}: {pred} vs Actual: {actual} {status}")

    print()

    # Test forecasting on Run 2
    print("="*70)
    print("FORECASTING RUN 2 (Training on first 5 points)")
    print("="*70)
    result2 = evaluate_forecast_accuracy(run2_counts, train_size=5)

    if 'error' not in result2:
        print(f"\nPredictions: {result2['predictions']}")
        print(f"Actual:      {result2['actual']}")
        print(f"Errors:      {result2['errors']}")
        print(f"\nAccuracy: {result2['accuracy']:.1%} ({result2['correct_count']}/{result2['total_predictions']} correct)")
        print(f"Average Error: {result2['avg_error']:.2f} agents")

    print()

    # Overall assessment
    print("="*70)
    print("FORECASTING ASSESSMENT")
    print("="*70)

    if 'error' not in result1 and 'error' not in result2:
        avg_accuracy = (result1['accuracy'] + result2['accuracy']) / 2
        avg_error = (result1['avg_error'] + result2['avg_error']) / 2

        print(f"\nOverall Performance:")
        print(f"  Average Accuracy: {avg_accuracy:.1%}")
        print(f"  Average Error: {avg_error:.2f} agents")

        print(f"\nInterpretation:")
        if avg_accuracy >= 0.80:
            print("  ✅ HIGH ACCURACY: Oscillating attractor is highly predictable")
            print("  ✅ Validates NRM deterministic dynamics prediction")
            print("  ✅ Demonstrates practical forecasting utility")
            print(f"  ✅ Simple periodic model achieves {avg_accuracy:.1%} accuracy")
            validated = True
        elif avg_accuracy >= 0.60:
            print("  ⚠️  MODERATE ACCURACY: Some predictability demonstrated")
            print("  ⚠️  Oscillating pattern partially predictable")
            validated = False
        else:
            print("  ❌ LOW ACCURACY: Forecasting unreliable")
            print("  ❌ System may be more chaotic than periodic")
            validated = False

        print(f"\n{'='*70}")
        if validated:
            print("🎉 INSIGHT #14: Oscillating attractor enables accurate forecasting")
            print("   NRM deterministic dynamics validated through prediction")
        else:
            print("⚠️  Forecasting shows limitations of simple periodic model")
        print("="*70)

        return {
            'validated': validated,
            'avg_accuracy': avg_accuracy,
            'avg_error': avg_error
        }

if __name__ == "__main__":
    main()
