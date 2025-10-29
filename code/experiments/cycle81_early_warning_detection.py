#!/usr/bin/env python3
"""
Cycle 81: Early Warning Detection (Predictability Study)

Research Context:
  Cycle 80: Dominant pattern emerges @ cycle 69, dominates @ cycle 160
  - 91-cycle window between emergence and complete dominance
  - Growth rate slow (0.0001), suggesting elimination dynamics

Research Gap:
  Can we predict the FUTURE dominant pattern using EARLY signals?
  How early can reliable prediction be made?
  What early indicators correlate with eventual dominance?

New Research Question:
  At what point does the system trajectory become predictable?

  Test prediction accuracy at multiple checkpoints:
  - Cycle 20: Very early (before most patterns emerge)
  - Cycle 40: Early phase
  - Cycle 60: Just before C80 dominant emergence (69)
  - Cycle 80: After C80 dominant emergence
  - Cycle 100: Mid-window before collapse (160)

  Hypothesis: Leading pattern at cycle 60-80 will match final dominant

Hypothesis:
  1. Early leader (cycle 20-40) may not persist
  2. Mid-phase leader (cycle 60-80) will match final dominant
  3. Prediction accuracy increases with time
  4. Reliable forecast possible 50-100 cycles before collapse
  5. Self-Giving validation: System trajectory predictable from mid-phase states

Test Approach:
  1. Run exploration regime (threshold=500) for 1000 cycles
  2. Sample memory distribution at checkpoints: 20, 40, 60, 80, 100, 160
  3. At each checkpoint, identify "leader" (highest count pattern)
  4. Compare early leaders with final dominant @ cycle 160
  5. Calculate prediction accuracy: Does leader_t match dominant_final?
  6. Determine earliest reliable prediction point

Expected:
  - Early checkpoints (<60): Low prediction accuracy (leaders change)
  - Mid checkpoints (60-100): High prediction accuracy (trajectory locked in)
  - Insight: System becomes predictable ~60-80 cycles (near dominant emergence)
  - Temporal Stewardship: Early warning systems possible for pattern dominance
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

def get_leader_pattern(memory: list) -> tuple:
    """Get current leader (most common pattern)."""
    if not memory:
        return None, 0, 0.0

    pattern_keys = [pattern_to_key(p) for p in memory]
    pattern_counts = Counter(pattern_keys)

    if not pattern_counts:
        return None, 0, 0.0

    leader_key, leader_count = pattern_counts.most_common(1)[0]
    leader_fraction = leader_count / len(memory)

    return leader_key, leader_count, leader_fraction

def run_early_warning_test(threshold: float, cycles: int = 1000) -> dict:
    """Test early warning prediction accuracy."""
    print(f"\n{'='*80}")
    print(f"EARLY WARNING DETECTION (threshold={threshold}, cycles={cycles})")
    print(f"{'='*80}")

    workspace = get_workspace_path()
    swarm = FractalSwarm(str(workspace))
    swarm.decomposition = DecompositionEngine(burst_threshold=threshold)

    reality_metrics = {'cpu_percent': 30.0, 'memory_percent': 40.0, 'disk_percent': 50.0}

    # Checkpoints for prediction testing
    prediction_checkpoints = [20, 40, 60, 80, 100, 160]
    checkpoint_leaders = {}  # cycle -> (leader_key, count, fraction)

    start_time = time.time()
    total_bursts = 0

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

        # Capture leader at checkpoints
        if cycle in prediction_checkpoints:
            leader_key, leader_count, leader_fraction = get_leader_pattern(swarm.global_memory)
            checkpoint_leaders[cycle] = {
                'leader_pattern': str(leader_key) if leader_key else None,
                'count': leader_count,
                'fraction': leader_fraction,
                'memory_size': len(swarm.global_memory)
            }
            print(f"  Checkpoint {cycle}: Leader={leader_fraction:.2%} (count={leader_count}/{len(swarm.global_memory)})")

        if cycle % 200 == 0:
            print(f"  Cycle {cycle}/{cycles}: Memory={len(swarm.global_memory)}, Bursts={total_bursts}")

    duration = time.time() - start_time

    # Final dominant pattern
    final_leader_key, final_count, final_fraction = get_leader_pattern(swarm.global_memory)

    # Prediction analysis
    collapse_cycle = 160  # From C80 result
    prediction_accuracy = {}

    print(f"\n  PREDICTION ACCURACY ANALYSIS:")
    print(f"  Final dominant: {str(final_leader_key)[:50]} ({final_fraction:.2%})")
    print()

    for checkpoint in prediction_checkpoints:
        if checkpoint in checkpoint_leaders:
            checkpoint_leader = checkpoint_leaders[checkpoint]['leader_pattern']
            final_dominant_str = str(final_leader_key) if final_leader_key else None

            # Check if prediction matches
            if checkpoint_leader and final_dominant_str:
                is_match = (checkpoint_leader == final_dominant_str)
                accuracy = 1.0 if is_match else 0.0
            else:
                is_match = False
                accuracy = 0.0

            prediction_accuracy[checkpoint] = {
                'predicted_pattern': checkpoint_leader,
                'matches_final': is_match,
                'accuracy': accuracy,
                'leader_fraction': checkpoint_leaders[checkpoint]['fraction'],
                'cycles_before_collapse': collapse_cycle - checkpoint if checkpoint < collapse_cycle else 0
            }

            status = "✅ MATCH" if is_match else "❌ MISS"
            print(f"  Cycle {checkpoint}: {status} (leader={checkpoint_leaders[checkpoint]['fraction']:.2%}, {collapse_cycle - checkpoint if checkpoint < collapse_cycle else 0} cycles before collapse)")

    # Find earliest reliable prediction
    earliest_reliable = None
    for checkpoint in sorted(prediction_checkpoints):
        if checkpoint in prediction_accuracy and prediction_accuracy[checkpoint]['matches_final']:
            earliest_reliable = checkpoint
            break

    print(f"\n  FINAL METRICS:")
    print(f"    Memory: {len(swarm.global_memory)} patterns")
    print(f"    Final dominant: {final_fraction:.2%}")
    print(f"    Earliest reliable prediction: Cycle {earliest_reliable if earliest_reliable else 'None'}")
    if earliest_reliable:
        print(f"    Prediction window: {collapse_cycle - earliest_reliable} cycles before collapse")
    print(f"  Duration: {duration:.2f}s ({duration/60:.2f} min)")

    return {
        'threshold': threshold,
        'cycles': cycles,
        'final_memory': len(swarm.global_memory),
        'final_dominant': {
            'pattern': str(final_leader_key) if final_leader_key else None,
            'count': final_count,
            'fraction': final_fraction
        },
        'total_bursts': total_bursts,
        'collapse_cycle': collapse_cycle,
        'checkpoint_leaders': checkpoint_leaders,
        'prediction_accuracy': prediction_accuracy,
        'earliest_reliable_prediction': earliest_reliable,
        'prediction_window': collapse_cycle - earliest_reliable if earliest_reliable else None,
        'duration': duration
    }

def main():
    """Run early warning detection study."""
    print("="*80)
    print("CYCLE 81: EARLY WARNING DETECTION (PREDICTABILITY STUDY)")
    print("="*80)
    print()
    print("Testing whether dominant pattern can be predicted from early signals.")
    print("Following Cycle 80: Dominant pattern emerges @ cycle 69")
    print("Question: How early can we reliably forecast the final dominant pattern?")
    print()
    print("Testing threshold: 500 (exploration regime)")
    print("Duration: 1000 cycles")
    print("Checkpoints: 20, 40, 60, 80, 100, 160 (before collapse)")
    print("="*80)

    threshold = 500
    cycles = 1000

    try:
        result = run_early_warning_test(threshold, cycles=cycles)
        error = False
    except Exception as e:
        print(f"\n⚠️ Error: {e}")
        import traceback
from workspace_utils import get_workspace_path, get_results_path
        traceback.print_exc()
        result = {'error': str(e)}
        error = True

    # Analysis
    if not error:
        earliest_pred = result['earliest_reliable_prediction']
        pred_window = result['prediction_window']
        collapse = result['collapse_cycle']

        print(f"\n{'='*80}")
        print(f"PREDICTABILITY ANALYSIS")
        print(f"{'='*80}\n")

        if earliest_pred:
            print(f"✅ PREDICTABILITY CONFIRMED")
            print(f"   Earliest reliable prediction: Cycle {earliest_pred}")
            print(f"   Prediction window: {pred_window} cycles before collapse ({pred_window/collapse:.1%} of total time)")
            print(f"   Collapse occurs @ cycle {collapse}")
            print()

            # Prediction quality
            if earliest_pred <= 60:
                print(f"🎉 INSIGHT #43 DISCOVERED: Early Prediction Possible")
                print(f"   - System trajectory predictable from cycle {earliest_pred}")
                print(f"   - {pred_window}-cycle warning window before collapse")
                print(f"   - Self-Giving validation: Future state determinable from early dynamics")
                print(f"   - Temporal Stewardship: Early warning systems feasible")
                insight_43 = True
            elif earliest_pred <= 100:
                print(f"✅ MID-PHASE PREDICTION CONFIRMED")
                print(f"   - System predictable from cycle {earliest_pred}")
                print(f"   - Moderate warning window ({pred_window} cycles)")
                insight_43 = True
            else:
                print(f"   Late prediction only (cycle {earliest_pred})")
                insight_43 = False

            # Calculate prediction accuracy by phase
            early_accuracy = np.mean([result['prediction_accuracy'][c]['accuracy'] for c in [20, 40] if c in result['prediction_accuracy']])
            mid_accuracy = np.mean([result['prediction_accuracy'][c]['accuracy'] for c in [60, 80, 100] if c in result['prediction_accuracy']])

            print(f"\n   Prediction accuracy by phase:")
            print(f"     Early phase (20-40): {early_accuracy:.1%}")
            print(f"     Mid phase (60-100): {mid_accuracy:.1%}")

        else:
            print(f"❌ NO RELIABLE EARLY PREDICTION")
            print(f"   Leaders at all checkpoints differed from final dominant")
            print(f"   System may exhibit late-stage transitions")
            insight_43 = False

        print("="*80)
    else:
        insight_43 = False

    # Save results
    results_dir = Path(__file__).parent / "results" / "early_warning"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_file = results_dir / "cycle81_early_warning_detection.json"

    output_data = {
        'experiment': 'cycle81_early_warning_detection',
        'threshold': threshold,
        'cycles': cycles,
        'result': result,
        'insight_43_discovered': insight_43,
        'timestamp': time.time()
    }

    with open(results_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\n✅ Results saved: {results_file}")
    print()

    return output_data

if __name__ == "__main__":
    main()
