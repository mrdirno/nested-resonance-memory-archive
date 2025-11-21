#!/usr/bin/env python3
"""
CYCLE 1631: SATURATION BOUNDARY ANALYSIS
Determines at what conversion magnitude spawn probability becomes saturated.
"""
import numpy as np
from datetime import datetime

def analyze_saturation_boundary():
    """Find the magnitude where saturation begins"""

    print(f"CYCLE 1631: Saturation Boundary Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Energy gain values used in experiments
    energy_gains = {
        'L1': 0.5,
        'L2': 0.6,
        'L3': 0.8,
        'L4': 1.0,
        'L5': 1.2,
        'L6': 1.4
    }

    # For spawn: random() < conv * e_gain
    # Saturated when conv * e_gain >= 1
    # Critical conv = 1 / e_gain

    print("\nCritical Conversion Values (where saturation begins):")
    print("-" * 50)
    for level, eg in energy_gains.items():
        critical_conv = 1.0 / eg
        print(f"  {level} (e_gain={eg}): conv >= {critical_conv:.3f}")

    print("\n" + "=" * 70)
    print("MAGNITUDE ANALYSIS")
    print("=" * 70)

    # The experiments use base conversion values like:
    # Level 1: 3.0 × magnitude
    # Level 2: 2.5 × magnitude
    # etc.

    base_convs = [3.0, 2.5, 2.0, 1.5, 1.2, 1.0]

    print("\nFor each magnitude, checking if any level is saturated:")
    print("-" * 70)

    for exp in range(-2, 5):  # 10^-2 to 10^4
        magnitude = 10 ** exp
        saturated_levels = []

        for i, (base, (level, eg)) in enumerate(zip(base_convs, energy_gains.items())):
            conv = base * magnitude
            prob = conv * eg
            if prob >= 1.0:
                saturated_levels.append(level)

        status = "SATURATED" if saturated_levels else "OK"
        if saturated_levels:
            print(f"  10^{exp}: {status} - Levels {', '.join(saturated_levels)}")
        else:
            print(f"  10^{exp}: {status}")

    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    # Calculate exact boundary
    min_eg = min(energy_gains.values())  # 0.5
    max_base = max(base_convs)  # 3.0
    critical_magnitude = 1.0 / (max_base * min_eg)

    print(f"""
Saturation begins when: base_conv × magnitude × e_gain >= 1

With base_conv = 3.0 (highest) and e_gain = 0.5 (lowest):
  Critical magnitude = 1 / (3.0 × 0.5) = {critical_magnitude:.4f}

Therefore:
  - Magnitude >= {critical_magnitude:.4f} causes L1 saturation
  - ALL experiments from 10^0 onward had at least some saturation
  - Magnitude >= 10^0 = ALL levels saturated for highest e_gain

The entire magnitude mapping series (10^86 - 10^94) was testing
parameter space where spawn probability = 100% for all levels.

VALID TESTING RANGE: Magnitude < {critical_magnitude:.4f} (approximately 10^-1)

To test actual conversion dynamics, need magnitude ~ 0.1 or less.
""")

if __name__ == "__main__":
    analyze_saturation_boundary()
