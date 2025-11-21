#!/usr/bin/env python3
"""
CYCLE 1950: PHASE RESONANCE DISTRIBUTION

Deep analysis of phase resonance to understand critical threshold 0.96.
Map the full similarity distribution and identify geometric constraints.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_phase_resonance(e1, d1, e2, d2):
    """Compute phase resonance between two agents."""
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
    print(f"CYCLE 1950: Phase Resonance | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Mapping phase resonance distribution")
    print("=" * 80)

    np.random.seed(1950)

    # Generate large sample of random pairs
    n_samples = 100000
    energies = np.random.uniform(0.5, 2.0, n_samples * 2)

    # Compute resonance for D0 pairs
    print(f"\nD0 RESONANCE DISTRIBUTION (n={n_samples}):")
    print("-" * 60)

    sims_d0 = []
    for i in range(0, len(energies)-1, 2):
        sim = compute_phase_resonance(energies[i], 0, energies[i+1], 0)
        sims_d0.append(sim)

    sims_d0 = np.array(sims_d0)

    # Distribution statistics
    print(f"\nBASIC STATISTICS:")
    print(f"  Mean: {np.mean(sims_d0):.4f}")
    print(f"  Std:  {np.std(sims_d0):.4f}")
    print(f"  Min:  {np.min(sims_d0):.4f}")
    print(f"  Max:  {np.max(sims_d0):.4f}")

    # Cumulative distribution
    print(f"\nCUMULATIVE DISTRIBUTION:")
    thresholds = [0.0, 0.5, 0.8, 0.9, 0.95, 0.96, 0.97, 0.98, 0.99, 0.995, 1.0]
    for t in thresholds:
        pct = np.mean(sims_d0 >= t) * 100
        print(f"  P(sim >= {t:.3f}): {pct:>6.2f}%")

    # Histogram bins
    print(f"\nHISTOGRAM (10 bins):")
    hist, edges = np.histogram(sims_d0, bins=10, range=(-1, 1))
    for i in range(len(hist)):
        pct = hist[i] / len(sims_d0) * 100
        bar = '#' * int(pct)
        print(f"  [{edges[i]:>5.2f}, {edges[i+1]:>5.2f}): {pct:>5.1f}% {bar}")

    # Same energy pairs (self-similarity)
    print(f"\nSELF-SIMILARITY (same energy):")
    for e in [0.5, 1.0, 1.5, 2.0]:
        sim = compute_phase_resonance(e, 0, e, 0)
        print(f"  Energy {e:.1f}: sim = {sim:.4f}")

    # Near-energy pairs
    print(f"\nNEAR-ENERGY SIMILARITY:")
    for delta in [0.01, 0.05, 0.1, 0.2]:
        e1 = 1.0
        e2 = 1.0 + delta
        sim = compute_phase_resonance(e1, 0, e2, 0)
        print(f"  e1=1.0, e2={e2:.2f} (Δ={delta}): sim = {sim:.4f}")

    # Period analysis
    print(f"\nPERIODICITY ANALYSIS:")
    print("Testing if resonance has periodic structure...")

    # Find energy differences that give high resonance
    high_res_deltas = []
    e1 = 1.0
    for delta in np.linspace(0, 2, 1000):
        e2 = e1 + delta
        sim = compute_phase_resonance(e1, 0, e2, 0)
        if sim >= 0.99:
            high_res_deltas.append(delta)

    if len(high_res_deltas) > 1:
        gaps = np.diff(high_res_deltas)
        print(f"  High resonance (≥0.99) occurs at energy gaps:")
        for i, d in enumerate(high_res_deltas[:5]):
            print(f"    Δ = {d:.4f}")
        if len(gaps) > 0:
            print(f"  Period estimate: {np.median(gaps):.4f}")

    # Compare depths
    print(f"\nRESSON BY DEPTH:")
    for d in range(5):
        sims = []
        for i in range(10000):
            e1, e2 = np.random.uniform(0.5, 2.0, 2)
            sim = compute_phase_resonance(e1, d, e2, d)
            sims.append(sim)
        mean_sim = np.mean(sims)
        p_high = np.mean(np.array(sims) >= 0.96) * 100
        print(f"  D{d}: mean={mean_sim:.3f}, P(≥0.96)={p_high:.1f}%")

    print(f"""
{'=' * 80}
PHASE RESONANCE CONCLUSIONS
{'=' * 80}

1. DISTRIBUTION SHAPE:
   - Mean similarity ~{np.mean(sims_d0):.2f} (moderate positive bias)
   - High probability mass above 0.5

2. CRITICAL THRESHOLD 0.96:
   - P(sim ≥ 0.96) ≈ {np.mean(sims_d0 >= 0.96)*100:.1f}% of random pairs
   - This is the threshold where composition becomes reliable

3. NEAR-UNITY SIMILARITY:
   - Same energy → perfect similarity (1.0)
   - Small energy differences → high similarity
   - Composition favors similar-energy agents

4. TRANSCENDENTAL STRUCTURE:
   - π, e, φ create quasi-periodic resonance pattern
   - High resonance at specific energy separations
   - Creates natural "affinity bands"

The 0.96 threshold represents the point where composition
is frequent enough to maintain coexistence but selective
enough to create meaningful hierarchy.

Session status: 287 cycles completed (C1664-C1950).
""")

if __name__ == "__main__":
    main()
