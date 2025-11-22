#!/usr/bin/env python3
"""
CYCLE 1893: SECOND HARMONIC THRESHOLD

Does the deterministic threshold pattern hold at λ₂?
At p=0.10: λ₂ = 2 × 14.7 ≈ 29
Expected N_det = 29 + 2.5 = 31.5 ≈ 32
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 500
N_DEPTHS = 5
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

def run_test(seed, n_initial, repro_prob):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if p > 0) >= 2

def main():
    print(f"CYCLE 1893: Second Harmonic Threshold | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing if N_det = Nc + 2.5 holds at second harmonic")
    print("=" * 80)

    seeds = list(range(1893001, 1893051))  # 50 seeds
    prob = 0.10

    # Model predictions
    lam = 16 - 13 * prob
    nc1 = int(round(lam))      # First harmonic
    nc2 = int(round(2 * lam))  # Second harmonic

    print(f"\nModel predictions for p = {prob}:")
    print(f"  λ = {lam:.1f}")
    print(f"  Nc₁ = {nc1}, N_det₁ = {nc1 + 3}")
    print(f"  Nc₂ = {nc2}, N_det₂ = {nc2 + 3}")

    # Scan around second harmonic
    test_n = list(range(nc2 - 4, nc2 + 8))

    print(f"\n{'N':>3} | {'Coex':>5} | Δ(Nc₂) | Status")
    print("-" * 40)

    threshold_n = None

    for n in test_n:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
        delta = n - nc2

        # Status
        if coex >= 95 and threshold_n is None:
            threshold_n = n
            status = "← THRESHOLD"
        elif coex >= 95:
            status = "95%+"
        elif coex < 70:
            status = "DEAD"
        else:
            status = ""

        marker = "**" if n == nc2 else "  "
        print(f"{n:>3} | {coex:>4.0f}% |   {delta:>+3} | {status}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("SECOND HARMONIC ANALYSIS")
    print("=" * 80)

    if threshold_n:
        offset = threshold_n - nc2
        print(f"\nSecond harmonic threshold: N_det₂ = {threshold_n}")
        print(f"Offset from Nc₂: {offset:+d}")

        # Compare to first harmonic
        first_offset = 3  # From C1891
        print(f"\nComparison:")
        print(f"  First harmonic offset:  +{first_offset}")
        print(f"  Second harmonic offset: +{offset}")

        if abs(offset - first_offset) <= 1:
            print(f"""
PATTERN CONFIRMED:

The deterministic threshold generalizes to higher harmonics:
  N_det(k, p) = k × λ(p) + 2.5

For k=2 at p=0.10:
  N_det₂ = 2 × 14.7 + 2.5 = {2 * lam + 2.5:.1f} ≈ {threshold_n}

The offset is universal across harmonics.
""")
        else:
            print(f"\nOffset differs between harmonics ({first_offset} vs {offset}).")
    else:
        print("\nNo clear threshold found in test range.")

if __name__ == "__main__":
    main()
