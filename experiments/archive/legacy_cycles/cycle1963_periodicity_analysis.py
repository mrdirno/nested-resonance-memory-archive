#!/usr/bin/env python3
"""
CYCLE 1963: PERIODICITY ANALYSIS

C1962 showed periodic composition probability structure.
Analyze the period and its relationship to transcendental constants.
"""
import sys, numpy as np, math
from datetime import datetime

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_similarity(e1, e2, d=0):
    """Compute phase resonance similarity."""
    pi1 = (e1 * PI * 2) % (2 * PI)
    e_1 = (d * E / 4) % (2 * PI)
    phi1 = (e1 * PHI) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    e_2 = (d * E / 4) % (2 * PI)
    phi2 = (e2 * PHI) % (2 * PI)
    v1 = [pi1, e_1, phi1]
    v2 = [pi2, e_2, phi2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    return dot / (mag1 * mag2) if mag1 > 0 and mag2 > 0 else 0

def main():
    print(f"CYCLE 1963: Periodicity Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Analyzing periodic structure in phase resonance")
    print("=" * 80)

    # Theoretical periods
    print(f"\nTHEORETICAL PERIOD ANALYSIS:")
    print("-" * 60)
    print(f"  π term period: 2π/(2π) = 1.0 energy units")
    print(f"  φ term period: 2π/φ = {2*PI/PHI:.4f} energy units")
    print(f"  Combined period: LCM approach complex (incommensurate)")

    # Self-similarity along energy axis
    print(f"\nSELF-SIMILARITY (e1 = e2 = e):")
    print("-" * 60)

    energies = np.linspace(0.5, 2.5, 201)
    similarities = [compute_similarity(e, e) for e in energies]

    # All self-similarities should be 1.0
    print(f"  All values = 1.0 (by definition): {np.allclose(similarities, 1.0)}")

    # Find high-similarity regions for near-equal energies
    print(f"\nNEAR-SIMILARITY PERIODICITY (e2 = e1 + δ):")
    print("-" * 60)

    e1 = 1.0
    deltas = np.linspace(0, 1.5, 1501)
    similarities = [compute_similarity(e1, e1 + d) for d in deltas]

    # Find peaks (high similarity)
    threshold = 0.99
    high_sim_deltas = [d for d, s in zip(deltas, similarities) if s >= threshold]

    if len(high_sim_deltas) > 1:
        gaps = np.diff(high_sim_deltas)
        if len(gaps) > 0:
            period = np.median(gaps)
            print(f"  High similarity peaks (≥0.99) at deltas:")
            for d in high_sim_deltas[:6]:
                print(f"    Δ = {d:.4f}")
            print(f"  Estimated period: {period:.4f}")

    # Probability map across energy pairs
    print(f"\nPROBABILITY MAP (random pairs):")
    print("-" * 60)

    n_samples = 50000
    np.random.seed(1963)

    # Sample pairs and bin by average energy
    e_pairs = np.random.uniform(0.5, 2.0, (n_samples, 2))
    avg_energies = np.mean(e_pairs, axis=1)
    sims = [compute_similarity(e[0], e[1]) for e in e_pairs]

    # Bin by average energy
    bins = np.linspace(0.5, 2.0, 16)
    for i in range(len(bins)-1):
        mask = (avg_energies >= bins[i]) & (avg_energies < bins[i+1])
        if np.sum(mask) > 0:
            bin_sims = np.array(sims)[mask]
            prob = np.mean(bin_sims >= 0.99) * 100
            mean_sim = np.mean(bin_sims)
            print(f"  [{bins[i]:.2f}, {bins[i+1]:.2f}): P(≥0.99)={prob:>5.1f}%, mean={mean_sim:.3f}")

    # FFT of similarity along energy axis
    print(f"\nFFT OF SIMILARITY FUNCTION:")
    print("-" * 60)

    e_range = np.linspace(0.5, 3.0, 1000)
    sims_fixed = [compute_similarity(1.0, e) for e in e_range]

    fft = np.fft.fft(sims_fixed)
    freqs = np.fft.fftfreq(len(e_range), e_range[1] - e_range[0])
    power = np.abs(fft)**2

    # Find dominant frequencies
    pos_mask = freqs > 0.1
    top_indices = np.argsort(power[pos_mask])[-3:][::-1]
    top_freqs = freqs[pos_mask][top_indices]
    top_periods = 1 / top_freqs

    print(f"  Dominant periods:")
    for p in top_periods:
        print(f"    T = {p:.4f} energy units")

    print(f"""
{'=' * 80}
PERIODICITY CONCLUSIONS
{'=' * 80}

1. TRANSCENDENTAL PERIODS:
   - π term: period 1.0 energy units
   - φ term: period {2*PI/PHI:.3f} energy units
   - Combined: quasi-periodic (incommensurate)

2. OBSERVED COMPOSITION BANDS (from C1962):
   - High: [0.5,0.75], [1.0,1.5], [1.75,2.0]
   - Low: [0.75,1.0], [1.5,1.75]
   - Period ~0.5-0.75 energy units

3. MECHANISM:
   - Phase angles wrap at 2π
   - Energy determines phase alignment
   - Similar phases → high similarity

4. QUASI-PERIODICITY:
   - Not exactly periodic (π, φ incommensurate)
   - Creates complex beating patterns
   - Bands are approximate, not exact

5. IMPLICATIONS:
   - Energy-selective composition emerges from math
   - Creates natural "affinity bands"
   - Agents cluster in preferred energy ranges

The periodic composition structure is a direct consequence
of the transcendental phase space geometry. The constants
π and φ create quasi-periodic resonance patterns.

Session status: 300 cycles completed (C1664-C1963).
""")

if __name__ == "__main__":
    main()
