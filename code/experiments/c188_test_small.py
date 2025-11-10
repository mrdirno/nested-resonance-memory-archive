#!/usr/bin/env python3
"""
C188 Small-Scale Test: 6 experiments (3 topologies × 1 transport × 2 seeds)
Validates C188 implementation before full 300-experiment campaign
"""

import sys
from pathlib import Path

# Modify C188 parameters for quick test
sys.path.insert(0, str(Path(__file__).parent))

# Import and patch C188
import c188_energy_transport as c188

# Override parameters for quick test
c188.CYCLES = 1000  # Reduce from 5000
c188.TRANSPORT_RATES = [0.05]  # Test one non-zero rate
c188.SEEDS = [42, 43]  # Just 2 seeds

print("="*80)
print("C188 SMALL-SCALE TEST")
print("3 topologies × 1 transport rate × 2 seeds = 6 experiments")
print(f"Cycles reduced to {c188.CYCLES} (from 5000)")
print("="*80)
print()

if __name__ == '__main__':
    c188.main()
