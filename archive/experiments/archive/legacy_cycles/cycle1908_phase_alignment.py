#!/usr/bin/env python3
"""
CYCLE 1908: PHASE ALIGNMENT ANALYSIS

Directly measure phase similarity to understand the energy effect.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_phase_resonance(e1, d1, e2, d2):
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
    print(f"CYCLE 1908: Phase Alignment | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Direct measurement of phase similarity")
    print("=" * 80)

    # Test phase resonance for different energy pairs
    energies = [0.5, 0.7, 1.0, 1.3, 1.5]
    depth = 0  # D0 agents

    print("\nPhase resonance between agents with different energies:")
    print(f"\n{'E1':>5} | {'E2':>5} | {'Resonance':>10}")
    print("-" * 30)

    # Same energy
    print("\nSame energy (perfect alignment):")
    for e in energies:
        res = compute_phase_resonance(e, depth, e, depth)
        print(f"{e:>5.1f} | {e:>5.1f} | {res:>10.4f}")

    # Different energies
    print("\nDifferent energies (varied alignment):")
    for e1 in [0.5, 1.0]:
        for e2 in [0.5, 1.0]:
            if e1 != e2:
                res = compute_phase_resonance(e1, depth, e2, depth)
                print(f"{e1:>5.1f} | {e2:>5.1f} | {res:>10.4f}")

    # Analysis for N agents with same energy
    print("\n" + "=" * 80)
    print("N AGENT PHASE ALIGNMENT")
    print("=" * 80)

    for e in [0.5, 1.0, 1.5]:
        res = compute_phase_resonance(e, 0, e, 0)
        exceeds = "≥ 0.5" if res >= 0.5 else "< 0.5"
        print(f"\nE={e:.1f}: resonance = {res:.4f} ({exceeds})")
        if res >= 0.5:
            print(f"  → All pairs will compose immediately!")
        else:
            print(f"  → Pairs won't compose until energy changes")

    # Check composition threshold
    print("\n" + "=" * 80)
    print("COMPOSITION THRESHOLD ANALYSIS")
    print("=" * 80)

    # Find energy where resonance crosses 0.5
    threshold_found = False
    for e in np.arange(0.1, 2.0, 0.1):
        res = compute_phase_resonance(e, 0, e, 0)
        if res >= 0.5 and not threshold_found:
            print(f"\nComposition threshold: E ≈ {e:.1f}")
            print(f"At this energy, same-energy pairs will compose.")
            threshold_found = True

    print(f"""
MECHANISM EXPLANATION:

The phase resonance of two D0 agents with same energy E:
- E=0.5: resonance = {compute_phase_resonance(0.5, 0, 0.5, 0):.4f}
- E=1.0: resonance = {compute_phase_resonance(1.0, 0, 1.0, 0):.4f}
- E=1.5: resonance = {compute_phase_resonance(1.5, 0, 1.5, 0):.4f}

WHY E=0.5 CAUSES IMMEDIATE COMPOSITION:
All agents start with same energy → same phase → high resonance
If resonance ≥ 0.5, pairs compose immediately

WHY THIS HELPS AT N=13-14 BUT HURTS AT N=15-16:
- N=13-14: Immediate composition creates D1 quickly
  D1 decomposes back to D0, maintaining cycling
- N=15-16: Immediate composition depletes D0
  Not enough D0 remains for sustainable cycling
  System collapses

The critical N separates "sustainable immediate composition"
from "fatal immediate composition".
""")

if __name__ == "__main__":
    main()
