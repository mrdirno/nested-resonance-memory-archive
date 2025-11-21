#!/usr/bin/env python3
"""
CYCLE 1769: MEASURE TRANSCENDENTAL MATCH RATE
What effective match rate does the transcendental function produce?
"""
import numpy as np, math
from datetime import datetime

CYCLE_ID = "C1769"

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_phase_resonance(e1, d1, e2, d2):
    """Standard transcendental phase resonance"""
    pi1 = (e1 * PI * 2) % (2 * PI)
    e_1 = (d1 * E / 4) % (2 * PI)
    phi1 = (e1 * PHI) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    e_2 = (d2 * E / 4) % (2 * PI)
    phi2 = (e2 * PHI) % (2 * PI)
    v1 = [pi1, e_1, phi1]
    v2 = [pi2, e_2, phi2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def main():
    print(f"CYCLE 1769: Transcendental Rate | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Measuring effective match rate of transcendental function")
    print("=" * 70)

    np.random.seed(1769)

    # Test with typical energy ranges
    energy_ranges = [
        (0.5, 1.0, "Low"),
        (0.5, 1.5, "Medium"),
        (0.5, 2.0, "High"),
        (1.0, 2.0, "Standard")
    ]

    n_tests = 10000

    print(f"\n{'Range':>12} | {'E1-E2':>12} | {'Rate':>10}")
    print("-" * 40)

    for e_min, e_max, name in energy_ranges:
        matches = 0
        for _ in range(n_tests):
            e1 = np.random.uniform(e_min, e_max)
            e2 = np.random.uniform(e_min, e_max)
            d = 0  # Test at D0
            sim = compute_phase_resonance(e1, d, e2, d)
            if sim >= 0.5:
                matches += 1
        rate = matches / n_tests * 100
        print(f"{name:>12} | {e_min}-{e_max:>5.1f} | {rate:>9.1f}%")

    # Also test at different depths
    print("\n" + "-" * 40)
    print("By depth (E = 0.5-2.0):")
    print("-" * 40)

    for d in range(5):
        matches = 0
        for _ in range(n_tests):
            e1 = np.random.uniform(0.5, 2.0)
            e2 = np.random.uniform(0.5, 2.0)
            sim = compute_phase_resonance(e1, d, e2, d)
            if sim >= 0.5:
                matches += 1
        rate = matches / n_tests * 100
        print(f"D{d}{'':10} | {'0.5-2.0':>12} | {rate:>9.1f}%")

if __name__ == "__main__":
    main()
