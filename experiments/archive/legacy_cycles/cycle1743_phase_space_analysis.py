#!/usr/bin/env python3
"""
CYCLE 1743: PHASE SPACE STRUCTURE ANALYSIS
Analyze the resonance pattern to understand wavelength λ ≈ 14.5.
"""
import sys, numpy as np, math
from datetime import datetime

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_phase_resonance(e1, d1, e2, d2):
    """Compute resonance between two agents"""
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

def analyze_population_resonance(n_agents):
    """Compute mean pairwise resonance for n agents at D0"""
    # Agents start with energy 1.0
    energies = [1.0] * n_agents
    d = 0  # D0

    resonances = []
    for i in range(n_agents):
        for j in range(i+1, n_agents):
            res = compute_phase_resonance(energies[i], d, energies[j], d)
            resonances.append(res)

    return np.mean(resonances) if resonances else 0.0

def analyze_energy_spread(n_agents):
    """Analyze resonance with energy spread (after some recharge cycles)"""
    # Simulate energy spread from recharge
    base_energy = 1.0
    energies = [base_energy + 0.1 * (i / n_agents) for i in range(n_agents)]
    d = 0

    resonances = []
    for i in range(n_agents):
        for j in range(i+1, n_agents):
            res = compute_phase_resonance(energies[i], d, energies[j], d)
            resonances.append(res)

    return np.mean(resonances) if resonances else 0.0

def analyze_phi_pattern(n_range):
    """Check if dead zones relate to φ patterns"""
    print("\nPhi-related analysis:")
    print(f"φ = {PHI:.6f}")
    print(f"φ² = {PHI**2:.6f}")
    print(f"1/φ = {1/PHI:.6f}")

    # Check if 29 relates to φ
    print(f"\n29 / φ = {29/PHI:.2f}")
    print(f"29 / φ² = {29/PHI**2:.2f}")
    print(f"29 * φ / 10 = {29*PHI/10:.2f}")

    # Check wavelength relation
    print(f"\n14.5 / φ = {14.5/PHI:.2f}")
    print(f"14.5 / (φ²) = {14.5/PHI**2:.2f}")
    print(f"14.5 / π = {14.5/PI:.2f}")
    print(f"14.5 / e = {14.5/E:.2f}")

def analyze_modular_patterns(n_range):
    """Check for modular arithmetic patterns"""
    print("\nModular patterns at dead zones:")
    dead_zones = [29, 43, 59, 73, 87, 102, 116, 132, 147]

    for n in dead_zones:
        pi_mod = (n * PI) % (2 * PI)
        e_mod = (n * E) % (2 * PI)
        phi_mod = (n * PHI) % (2 * PI)
        print(f"N={n:3d}: π-mod={pi_mod:.2f}, e-mod={e_mod:.2f}, φ-mod={phi_mod:.2f}")

def main():
    print(f"CYCLE 1743: Phase Space Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Understand wavelength λ ≈ 14.5 from phase space geometry")
    print("=" * 70)

    # Analysis 1: Mean resonance vs N
    print("\n--- Mean Pairwise Resonance vs N ---")
    print(f"{'N':>4} | {'Mean Res':>10} | {'Status'}")
    print("-" * 30)

    dead_zones = [29, 43, 59, 73, 87, 102, 116]
    for n in range(25, 80, 5):
        mean_res = analyze_population_resonance(n)
        status = "✗ DEAD" if n in dead_zones else ""
        print(f"{n:4d} | {mean_res:10.4f} | {status}")

    # Analysis 2: With energy spread
    print("\n--- With Energy Spread ---")
    print(f"{'N':>4} | {'Spread Res':>10} | {'Status'}")
    print("-" * 30)

    for n in range(25, 80, 5):
        spread_res = analyze_energy_spread(n)
        status = "✗ DEAD" if n in dead_zones else ""
        print(f"{n:4d} | {spread_res:10.4f} | {status}")

    # Analysis 3: Mathematical relationships
    analyze_phi_pattern(range(25, 150))

    # Analysis 4: Modular patterns
    analyze_modular_patterns(range(25, 150))

    # Analysis 5: Wavelength hypothesis
    print("\n--- Wavelength Candidates ---")
    candidates = [
        ("4π + 2", 4*PI + 2),
        ("5φ", 5*PHI),
        ("3π + 5", 3*PI + 5),
        ("φ⁴", PHI**4),
        ("3e + 6", 3*E + 6),
        ("π + e + φ + 7", PI + E + PHI + 7),
    ]

    for name, value in candidates:
        error = abs(value - 14.5)
        print(f"{name:20} = {value:.3f} | error: {error:.3f}")

if __name__ == "__main__":
    main()
