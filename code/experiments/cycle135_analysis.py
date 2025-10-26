#!/usr/bin/env python3
"""
CYCLE 135: BOUNDARY MAPPING ANALYSIS

Analyzes transition boundary location and sharpness
"""

import json
import numpy as np
from pathlib import Path
from collections import Counter


def load_results():
    """Load Cycle 135 boundary mapping results"""
    results_path = Path(__file__).parent / 'results' / 'cycle135_boundary_mapping.json'
    if not results_path.exists():
        print(f"❌ Results not found: {results_path}")
        return None

    with open(results_path, 'r') as f:
        data = json.load(f)

    return data


def analyze_boundary(data):
    """Analyze boundary location and sharpness"""
    print("\n" + "="*70)
    print("BOUNDARY LOCATION ANALYSIS")
    print("="*70 + "\n")

    results = data['results']
    thresholds = sorted(set(r['threshold'] for r in results))
    diversities = sorted(set(r['diversity'] for r in results))

    print("Basin Assignments (2D Grid):")
    print("\n           Diversity →")
    print("        ", end="")
    for d in diversities:
        print(f"  {d:.2f}", end="")
    print()
    print("Threshold")

    # Create 2D grid
    grid = {}
    for r in results:
        grid[(r['threshold'], round(r['diversity'], 3))] = r['basin']

    for t in thresholds:
        print(f"  {t:>3}   ", end="")
        for d in diversities:
            basin = grid.get((t, round(d, 3)), '?')
            print(f"   {basin}  ", end="")
        print()

    print("\n" + "-"*70)

    # Find transition points
    print("\nTHRESHOLD TRANSITIONS (at each diversity):")
    for d in diversities:
        basins_at_d = [(t, grid.get((t, round(d, 3)), '?')) for t in thresholds]
        transitions = []
        for i in range(len(basins_at_d) - 1):
            if basins_at_d[i][1] != basins_at_d[i+1][1]:
                transitions.append((basins_at_d[i][0], basins_at_d[i+1][0]))

        if transitions:
            print(f"  diversity={d:.2f}: {transitions}")
        else:
            print(f"  diversity={d:.2f}: No transition (all {basins_at_d[0][1]})")

    print("\nDIVERSITY TRANSITIONS (at each threshold):")
    for t in thresholds:
        basins_at_t = [(d, grid.get((t, round(d, 3)), '?')) for d in diversities]
        transitions = []
        for i in range(len(basins_at_t) - 1):
            if basins_at_t[i][1] != basins_at_t[i+1][1]:
                transitions.append((basins_at_t[i][0], basins_at_t[i+1][0]))

        if transitions:
            print(f"  threshold={t}: {transitions}")
        else:
            print(f"  threshold={t}: No transition (all {basins_at_t[0][1]})")

    # Transition sharpness
    print("\n" + "-"*70)
    print("\nTRANSITION SHARPNESS:")

    total_cells = len(results)
    basin_a_cells = sum(1 for r in results if r['basin'] == 'A')
    basin_b_cells = sum(1 for r in results if r['basin'] == 'B')

    print(f"  Basin A: {basin_a_cells}/{total_cells} cells ({basin_a_cells/total_cells*100:.1f}%)")
    print(f"  Basin B: {basin_b_cells}/{total_cells} cells ({basin_b_cells/total_cells*100:.1f}%)")

    # Estimate boundary width (number of cells on edge)
    edge_cells = 0
    for r in results:
        t, d = r['threshold'], round(r['diversity'], 3)
        basin = r['basin']

        # Check if any neighbors have different basin
        neighbors = [
            (t-25, d), (t+25, d),  # threshold neighbors
            (t, round(d-0.02, 3)), (t, round(d+0.02, 3))  # diversity neighbors
        ]

        for nt, nd in neighbors:
            if (nt, nd) in grid and grid[(nt, nd)] != basin:
                edge_cells += 1
                break

    print(f"  Edge cells (on boundary): {edge_cells}/{total_cells} ({edge_cells/total_cells*100:.1f}%)")

    if edge_cells == 0:
        print(f"  → VERY SHARP: No mixed boundary region (step function)")
    elif edge_cells < total_cells * 0.25:
        print(f"  → SHARP: Narrow transition region")
    else:
        print(f"  → GRADUAL: Wide transition region")

    print()


def main():
    """Run all analyses"""
    print("\n" + "="*70)
    print("CYCLE 135: BOUNDARY MAPPING ANALYSIS")
    print("="*70)

    data = load_results()
    if not data:
        return

    print(f"\n✅ Loaded {len(data['results'])} experiment results")

    analyze_boundary(data)

    print("\n" + "="*70)
    print("ANALYSIS COMPLETE")
    print("="*70 + "\n")


if __name__ == '__main__':
    main()
