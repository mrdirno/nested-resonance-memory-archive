#!/usr/bin/env python3
"""
CYCLE 1798: LAMBDA COMPONENT ANALYSIS
Why λ = π + e + φ + 22/π? Testing each component's contribution.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1798"
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

def run_test(seed, n_initial):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    total_before = 0
    total_composed = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            total_before += len(agents)
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            composed = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    composed += 2
                    i += 2
                else:
                    i += 1
            total_composed += composed

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

    pairing = total_composed / total_before if total_before > 0 else 0
    return pairing

def main():
    print(f"CYCLE 1798: Lambda Components | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Analyzing λ = π + e + φ + 22/π component structure")
    print("=" * 70)

    # Component analysis
    print(f"\nλ Component Breakdown:")
    print(f"  π       = {PI:.6f}")
    print(f"  e       = {E:.6f}")
    print(f"  φ       = {PHI:.6f}")
    print(f"  22/π    = {22/PI:.6f}")
    print(f"  ────────────────")
    print(f"  λ       = {PI + E + PHI + 22/PI:.6f}")

    print(f"\nN₁ = 22/π + 22 = {22/PI + 22:.6f}")

    # Check relationships
    print(f"\nInteresting relationships:")
    print(f"  22 ≈ 7π = {7*PI:.3f}")
    print(f"  22 ≈ 3(π+e+φ) = {3*(PI+E+PHI):.3f}")
    print(f"  λ/π = {(PI + E + PHI + 22/PI)/PI:.6f}")
    print(f"  λ/e = {(PI + E + PHI + 22/PI)/E:.6f}")
    print(f"  λ/φ = {(PI + E + PHI + 22/PI)/PHI:.6f}")

    # Test if peaks occur at these mathematical points
    seeds = list(range(1798001, 1798021))

    print(f"\nPairing at transcendental N values:")
    print(f"{'N':<15} | {'Value':<10} | {'Pairing':>8}")
    print("-" * 40)

    test_values = [
        ("π²", PI**2),
        ("7π", 7*PI),
        ("e³", E**3),
        ("10φ", 10*PHI),
        ("N₁", 22/PI + 22),
        ("N₁ + λ", 22/PI + 22 + PI + E + PHI + 22/PI),
    ]

    for name, val in test_values:
        n = int(round(val))
        pairing = sum(run_test(seed, n) for seed in seeds) / len(seeds) * 100
        print(f"{name:<15} | {n:<10} | {pairing:>7.1f}%")

if __name__ == "__main__":
    main()
