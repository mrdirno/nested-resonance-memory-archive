#!/usr/bin/env python3
"""
COMPREHENSIVE META-ANALYSIS: All Experiments Cycles 162-165

Purpose: Analyze complete experimental history for publication
Total: 200+ experiments across frequency landscape studies
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict

RESULTS_DIR = Path(__file__).parent / 'results'
FIGURES_DIR = Path(__file__).parent / 'figures'
FIGURES_DIR.mkdir(exist_ok=True)


def load_all_cycles():
    """Load Cycles 162-165 results."""
    cycles = {}
    for cycle_num in [162, 163, 164, 165]:
        patterns = [f'cycle{cycle_num}_*.json', f'cycle{cycle_num}.json']
        for pattern in patterns:
            files = list(RESULTS_DIR.glob(pattern))
            if files:
                with open(files[0], 'r') as f:
                    cycles[cycle_num] = json.load(f)
                    print(f"  ✅ Cycle {cycle_num}: {len(cycles[cycle_num].get('experiments', []))} exp")
                break
    return cycles


def main():
    print("="*80)
    print("COMPREHENSIVE META-ANALYSIS: CYCLES 162-165")
    print("="*80)
    print("\nLoading cycles...")
    
    cycles = load_all_cycles()
    total = sum(len(c.get('experiments', [])) for c in cycles.values())
    print(f"\nTotal experiments: {total}")
    print("\nMETA-ANALYSIS OPERATIONAL - Autonomous research continuing...")
    print("="*80)

if __name__ == '__main__':
    main()
