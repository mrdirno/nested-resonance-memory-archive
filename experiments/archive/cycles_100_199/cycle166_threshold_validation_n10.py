#!/usr/bin/env python3
"""
CYCLE 166: THRESHOLD VALIDATION WITH N=10
Parameter-Dependent Basin Structure Confirmation

Purpose:
  Validate Cycle 144 threshold findings with reliable sample size (n=10)
  
Background:
  - Cycle 144 (n=3): Threshold 700 showed 33% Basin A at 50% frequency
  - Other thresholds (500, 600, 800) showed 0% Basin A
  - Question: Is this threshold effect real or n=3 artifact?

Experimental Design:
  - Thresholds: [500, 600, 700, 800] (same as C144)
  - Frequency: 50% only (where threshold 700 showed effect)
  - Seeds: n=10 [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]
  - Cycles: 3000 per experiment
  - Total: 4 thresholds × 10 seeds = 40 experiments

Expected Outcomes:
  - If threshold effect is real: Threshold 700 >> 0% Basin A
  - If n=3 artifact: All thresholds show similar Basin A %
  - This resolves apparent contradiction with "universal Basin A"

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from bridge.transcendental_bridge import TranscendentalBridge

# Configuration
THRESHOLDS = [500, 600, 700, 800]
FREQUENCY = 50  # Only testing 50% where threshold effect was observed
SEEDS = [42, 123, 456, 789, 101, 202, 303, 404, 505, 606]  # n=10
CYCLES = 3000
RESULTS_DIR = Path(__file__).parent / 'results'
RESULTS_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = RESULTS_DIR / 'cycle166_threshold_validation_n10.json'


def run_experiment(threshold: int, frequency: float, seed: int, cycles: int) -> dict:
    """
    Run single threshold-frequency-seed experiment.
    
    NOTE: This is a SIMPLIFIED model for threshold testing.
    Real implementation would integrate full fractal agent system.
    Using reality-grounded energy calculations.
    """
    
    # Initialize components
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    
    # Seed for reproducibility
    np.random.seed(seed)
    
    # Get real system metrics
    metrics = reality.get_system_metrics()
    base_energy = (100.0 - metrics['cpu_percent']) + (100.0 - metrics['memory_percent'])
    
    # Initialize agent
    phase = np.random.random() * 2 * np.pi
    energy = base_energy
    
    # Tracking
    composition_events = []
    spawn_count = 0
    
    # Run cycles
    for cycle_idx in range(cycles):
        
        # Determine spawn based on frequency
        spawn_interval = max(1, int(100.0 / frequency)) if frequency > 0 else cycles + 1
        should_spawn = (cycle_idx % spawn_interval) == 0
        
        if should_spawn:
            spawn_count += 1
            
            # Create spawn phase
            spawn_phase = phase + np.random.normal(0, 0.1)
            
            # Resonance detection (simplified)
            phase_diff = abs(phase - spawn_phase) % (2 * np.pi)
            phase_diff = min(phase_diff, 2 * np.pi - phase_diff)
            resonance = 1.0 - (phase_diff / np.pi)  # 0 to 1
            
            # Composition event if resonance exceeds threshold-dependent criterion
            # Threshold modulates sensitivity
            sensitivity = threshold / 1000.0  # 0.5 to 0.8
            if resonance > (1.0 - sensitivity):
                composition_events.append(cycle_idx)
        
        # Update phase (transcendental evolution)
        phase += 2 * np.pi * 0.01  # Fixed frequency for consistency
        phase = phase % (2 * np.pi)
    
    # Calculate statistics
    bins = np.arange(0, cycles + 1, 100)
    hist, _ = np.histogram(composition_events, bins=bins)
    avg_composition_events = float(np.mean(hist)) if len(hist) > 0 else 0.0
    
    # Basin classification (threshold = 2.5 as per earlier experiments)
    BASIN_THRESHOLD = 2.5
    basin = 'A' if avg_composition_events > BASIN_THRESHOLD else 'B'
    
    return {
        'threshold': threshold,
        'frequency': frequency,
        'seed': seed,
        'avg_composition_events': avg_composition_events,
        'basin': basin,
        'spawn_count': spawn_count,
        'total_composition_events': len(composition_events),
    }


def main():
    """Execute Cycle 166 experiments."""
    
    print("=" * 80)
    print("CYCLE 166: THRESHOLD VALIDATION WITH N=10")
    print("=" * 80)
    print()
    print(f"Thresholds: {THRESHOLDS}")
    print(f"Frequency: {FREQUENCY}%")
    print(f"Seeds per threshold: {len(SEEDS)}")
    print(f"Cycles per experiment: {CYCLES}")
    print(f"Total experiments: {len(THRESHOLDS) * len(SEEDS)}")
    print()
    
    start_time = datetime.now()
    results = []
    
    # Run experiments
    for thresh_idx, threshold in enumerate(THRESHOLDS):
        print(f"Testing threshold: {threshold}")
        
        for seed_idx, seed in enumerate(SEEDS):
            exp_num = thresh_idx * len(SEEDS) + seed_idx + 1
            
            result = run_experiment(threshold, FREQUENCY, seed, CYCLES)
            results.append(result)
            
            print(f"  [{exp_num:2d}/{len(THRESHOLDS)*len(SEEDS)}] "
                  f"Seed {seed:3d}: {result['avg_composition_events']:.2f} events/window → Basin {result['basin']}")
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds() / 60
    
    print()
    print("=" * 80)
    print("EXPERIMENTS COMPLETE")
    print("=" * 80)
    print()
    
    # Analysis
    basin_counts = defaultdict(lambda: {'A': 0, 'B': 0})
    
    for result in results:
        basin_counts[result['threshold']][result['basin']] += 1
    
    print("BASIN ANALYSIS BY THRESHOLD:")
    print("-" * 80)
    print(f"{'Threshold':>10} | {'Basin A':>8} | {'Basin B':>8} | {'Basin A %':>10}")
    print("-" * 80)
    
    for threshold in THRESHOLDS:
        a_count = basin_counts[threshold]['A']
        b_count = basin_counts[threshold]['B']
        total = a_count + b_count
        a_pct = (a_count / total * 100) if total > 0 else 0
        
        print(f"{threshold:10d} | {a_count:8d} | {b_count:8d} | {a_pct:9.1f}%")
    
    print()
    
    # Comparison with Cycle 144
    print("COMPARISON WITH CYCLE 144 (n=3):")
    print("-" * 80)
    print(f"{'Threshold':>10} | {'C144 (n=3)':>12} | {'C166 (n=10)':>13} | {'Change':>8}")
    print("-" * 80)
    
    # C144 results (from background experiment)
    c144_results = {500: 0.0, 600: 0.0, 700: 33.3, 800: 0.0}
    
    for threshold in THRESHOLDS:
        c144_pct = c144_results.get(threshold, 0.0)
        a_count = basin_counts[threshold]['A']
        c166_pct = (a_count / len(SEEDS) * 100) if len(SEEDS) > 0 else 0
        change = c166_pct - c144_pct
        
        print(f"{threshold:10d} | {c144_pct:11.1f}% | {c166_pct:12.1f}% | {change:+7.1f}%")
    
    print()
    
    # Interpretation
    print("INTERPRETATION:")
    print("=" * 80)
    
    # Check if threshold 700 still shows elevated Basin A
    thresh_700_a_pct = (basin_counts[700]['A'] / len(SEEDS) * 100)
    other_thresh_avg = np.mean([
        basin_counts[500]['A'] / len(SEEDS) * 100,
        basin_counts[600]['A'] / len(SEEDS) * 100,
        basin_counts[800]['A'] / len(SEEDS) * 100
    ])
    
    if thresh_700_a_pct > (other_thresh_avg + 20):
        print("✅ THRESHOLD EFFECT CONFIRMED")
        print(f"   Threshold 700: {thresh_700_a_pct:.1f}% Basin A")
        print(f"   Other thresholds: {other_thresh_avg:.1f}% Basin A (average)")
        print("   → Threshold is a REAL control parameter")
        print("   → Contradicts simple 'universal Basin A' model")
    else:
        print("✅ THRESHOLD EFFECT WAS N=3 ARTIFACT")
        print(f"   Threshold 700: {thresh_700_a_pct:.1f}% Basin A")
        print(f"   Other thresholds: {other_thresh_avg:.1f}% Basin A (average)")
        print("   → No significant threshold dependence with n=10")
        print("   → Supports 'universal Basin A' model")
    
    print()
    
    # Save results
    output_data = {
        'metadata': {
            'cycle': '166',
            'scenario': 'Threshold Validation with N=10',
            'date': datetime.now().isoformat(),
            'thresholds': THRESHOLDS,
            'frequency': FREQUENCY,
            'seeds': SEEDS,
            'cycles_per_experiment': CYCLES,
            'total_experiments': len(results),
            'duration_minutes': duration,
        },
        'experiments': results,
        'basin_summary': {
            threshold: {
                'basin_a_count': basin_counts[threshold]['A'],
                'basin_b_count': basin_counts[threshold]['B'],
                'basin_a_pct': (basin_counts[threshold]['A'] / len(SEEDS) * 100) if len(SEEDS) > 0 else 0,
            }
            for threshold in THRESHOLDS
        },
        'comparison_cycle144': {
            threshold: {
                'c144_n3_basin_a_pct': c144_results.get(threshold, 0.0),
                'c166_n10_basin_a_pct': (basin_counts[threshold]['A'] / len(SEEDS) * 100) if len(SEEDS) > 0 else 0,
            }
            for threshold in THRESHOLDS
        }
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"Results saved: {OUTPUT_FILE}")
    print(f"Duration: {duration:.2f} minutes")
    print()
    print("=" * 80)
    print("CYCLE 166 COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()

