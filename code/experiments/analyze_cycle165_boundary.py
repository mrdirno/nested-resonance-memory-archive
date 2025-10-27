#!/usr/bin/env python3
"""
CYCLE 165 BOUNDARY ANALYSIS
Upper Frequency Limit Detection

Purpose:
  Analyze Cycle 165 results to determine where Basin A dominance ends

Comparisons:
  - Cycle 164: 80% showed 100% Basin A
  - Cycle 165: 85%, 90%, 95%, 99%, 99.9% tested

Questions:
  1. Does Basin A dominance continue beyond 80%?
  2. Is there a transition zone?
  3. Where is the upper boundary?

Date: 2025-10-25
Researcher: Claude (DUALITY-ZERO-V2)
"""

import json
import numpy as np
from pathlib import Path
from collections import defaultdict

def load_results(filename):
    """Load experiment results from JSON."""
    results_dir = Path(__file__).parent / 'results'
    with open(results_dir / filename, 'r') as f:
        return json.load(f)

def analyze_frequency_basins(experiments):
    """Analyze basin outcomes by frequency."""
    freq_data = defaultdict(list)
    for exp in experiments:
        freq_data[exp['frequency']].append(exp['basin'])

    results = []
    for freq in sorted(freq_data.keys()):
        basins = freq_data[freq]
        n = len(basins)
        a_count = sum(1 for b in basins if b == 'A')
        b_count = n - a_count
        a_pct = (a_count / n * 100) if n > 0 else 0

        # Classification
        if a_pct >= 67:
            classification = 'Harmonic (Basin A)'
        elif a_pct >= 33:
            classification = 'Mixed'
        else:
            classification = 'Anti-harmonic (Basin B)'

        results.append({
            'frequency': freq,
            'n': n,
            'basin_a': a_count,
            'basin_b': b_count,
            'basin_a_pct': a_pct,
            'classification': classification
        })

    return results

def detect_boundary(results):
    """Detect transition boundary from Basin A dominance."""
    # Find where Basin A % first drops below 67%
    for i, r in enumerate(results):
        if r['basin_a_pct'] < 67:
            if i > 0:
                return {
                    'boundary_detected': True,
                    'last_harmonic': results[i-1]['frequency'],
                    'first_non_harmonic': r['frequency'],
                    'transition_type': r['classification']
                }
            else:
                return {
                    'boundary_detected': True,
                    'last_harmonic': None,
                    'first_non_harmonic': r['frequency'],
                    'transition_type': r['classification']
                }

    return {
        'boundary_detected': False,
        'conclusion': 'Universal Basin A attractor extends through all tested frequencies'
    }

def main():
    print("=" * 80)
    print("CYCLE 165 UPPER FREQUENCY BOUNDARY ANALYSIS")
    print("=" * 80)
    print()

    # Load Cycle 165 data
    try:
        c165 = load_results('cycle165_upper_frequency_boundary.json')
    except FileNotFoundError:
        print("❌ ERROR: Cycle 165 results not found")
        print("Waiting for cycle165_upper_frequency_boundary.json...")
        return

    print(f"✅ Loaded Cycle 165: {len(c165['experiments'])} experiments")
    print()

    # Analyze frequencies
    print("FREQUENCY ANALYSIS")
    print("=" * 80)
    results = analyze_frequency_basins(c165['experiments'])

    print(f"{'Freq':>6} | {'N':>3} | {'Basin A':>8} | {'Basin B':>8} | {'A %':>6} | Classification")
    print("-" * 80)
    for r in results:
        print(f"{r['frequency']:5.1f}% | {r['n']:3d} | {r['basin_a']:8d} | {r['basin_b']:8d} | "
              f"{r['basin_a_pct']:5.1f}% | {r['classification']}")

    print()

    # Boundary detection
    print("BOUNDARY DETECTION")
    print("=" * 80)
    boundary = detect_boundary(results)

    if boundary['boundary_detected']:
        if boundary.get('last_harmonic'):
            print(f"✅ BOUNDARY FOUND")
            print(f"   Last harmonic frequency: {boundary['last_harmonic']}%")
            print(f"   First non-harmonic: {boundary['first_non_harmonic']}%")
            print(f"   Transition type: {boundary['transition_type']}")
        else:
            print(f"✅ NO BASIN A DOMINANCE")
            print(f"   All frequencies show: {boundary['transition_type']}")
    else:
        print(f"✅ NO BOUNDARY DETECTED")
        print(f"   {boundary['conclusion']}")

    print()

    # Compare with Cycle 164
    print("CYCLE 164 vs 165 COMPARISON")
    print("=" * 80)

    try:
        c164 = load_results('cycle164_antiharmonic_validation.json')
        c164_results = analyze_frequency_basins(c164['experiments'])

        # Get highest frequency from C164
        c164_max = max(r['frequency'] for r in c164_results)
        c164_max_result = [r for r in c164_results if r['frequency'] == c164_max][0]

        # Get lowest frequency from C165
        c165_min = min(r['frequency'] for r in results)
        c165_min_result = [r for r in results if r['frequency'] == c165_min][0]

        print(f"Cycle 164 highest frequency: {c164_max}% → {c164_max_result['basin_a_pct']:.1f}% Basin A")
        print(f"Cycle 165 lowest frequency: {c165_min}% → {c165_min_result['basin_a_pct']:.1f}% Basin A")
        print()

        if c164_max_result['basin_a_pct'] == 100 and c165_min_result['basin_a_pct'] == 100:
            print("✅ CONTINUITY CONFIRMED: Basin A dominance continues from 80% to 85%")
        else:
            print("⚠️  DISCONTINUITY: Basin A dominance changes between cycles")

    except FileNotFoundError:
        print("Cycle 164 data not available for comparison")

    print()

    # Interpretation
    print("INTERPRETATION")
    print("=" * 80)

    avg_basin_a = np.mean([r['basin_a_pct'] for r in results])

    if avg_basin_a >= 90:
        print("SCENARIO A: UNIVERSAL CONTINUATION")
        print("  Basin A attractor extends to extreme high frequencies")
        print("  No upper boundary detected in tested range")
    elif avg_basin_a >= 50:
        print("SCENARIO B: TRANSITION ZONE")
        print("  Gradual weakening of Basin A dominance at high frequencies")
        print("  Mixed attractor dynamics emerging")
    else:
        print("SCENARIO C: BASIN B EMERGENCE")
        print("  High frequencies show Basin B dominance")
        print("  Clear boundary from Basin A to Basin B")

    print()
    print(f"Average Basin A %: {avg_basin_a:.1f}%")
    print()

    # Save analysis
    output = {
        'frequency_analysis': results,
        'boundary_detection': boundary,
        'avg_basin_a_pct': float(avg_basin_a),
    }

    output_file = Path(__file__).parent / 'results' / 'cycle165_boundary_analysis.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"Analysis saved: {output_file}")
    print()
    print("=" * 80)
    print("CYCLE 165 BOUNDARY ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == '__main__':
    main()
