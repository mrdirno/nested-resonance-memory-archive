#!/usr/bin/env python3
"""
CYCLE 1729: WAVELENGTH ANALYSIS
Is λ≈15 fundamental or parameter-dependent?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1729"
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

def run_test(seed, n_initial, recharge, repro):
    """Test coexistence."""
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
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro:
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

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2
    return coexist

def find_dead_zone_center(seeds, n_range, recharge, repro):
    """Find the minimum coexistence N in a range."""
    results = []
    for n in n_range:
        outcomes = [run_test(seed, n, recharge, repro) for seed in seeds]
        coexist = sum(outcomes) / len(outcomes) * 100
        results.append((n, coexist))
    min_n, min_c = min(results, key=lambda x: x[1])
    return min_n, min_c

def main():
    print(f"CYCLE 1729: Wavelength Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Is λ≈15 fundamental or parameter-dependent?")
    print("=" * 70)

    seeds = list(range(1729001, 1729031))  # 30 seeds

    # Test at different parameter values
    configs = [
        ("Standard", 0.1, 0.1),
        ("Low recharge", 0.05, 0.1),
        ("High recharge", 0.15, 0.1),
    ]

    print("\n" + "=" * 70)
    print("DEAD ZONE CENTERS BY PARAMETERS")
    print("=" * 70)

    for name, recharge, repro in configs:
        print(f"\n--- {name} (rech={recharge}, repr={repro}) ---")

        # Find zone 1 center (around N=29)
        z1_n, z1_c = find_dead_zone_center(seeds, range(26, 34), recharge, repro)

        # Find zone 2 center (around N=43)
        z2_n, z2_c = find_dead_zone_center(seeds, range(40, 48), recharge, repro)

        # Find zone 3 center (around N=59)
        z3_n, z3_c = find_dead_zone_center(seeds, range(56, 64), recharge, repro)

        print(f"Zone 1: N={z1_n} ({z1_c:.0f}%)")
        print(f"Zone 2: N={z2_n} ({z2_c:.0f}%)")
        print(f"Zone 3: N={z3_n} ({z3_c:.0f}%)")

        interval1 = z2_n - z1_n
        interval2 = z3_n - z2_n
        mean_interval = (interval1 + interval2) / 2

        print(f"Intervals: {interval1}, {interval2}")
        print(f"Mean wavelength: {mean_interval:.1f}")

    # Mathematical analysis
    print("\n" + "=" * 70)
    print("MATHEMATICAL RELATIONSHIPS")
    print("=" * 70)
    print(f"\nTranscendental constants:")
    print(f"  π = {PI:.6f}")
    print(f"  e = {E:.6f}")
    print(f"  φ = {PHI:.6f}")
    print(f"\nPossible wavelength formulas:")
    print(f"  π × e = {PI * E:.2f}")
    print(f"  π × φ = {PI * PHI:.2f}")
    print(f"  e × φ = {E * PHI:.2f}")
    print(f"  π + e + φ = {PI + E + PHI:.2f}")
    print(f"  2π + e = {2*PI + E:.2f}")
    print(f"  3e + π = {3*E + PI:.2f}")
    print(f"  5φ² = {5 * PHI**2:.2f}")

if __name__ == "__main__":
    main()
