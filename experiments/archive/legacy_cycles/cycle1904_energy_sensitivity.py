#!/usr/bin/env python3
"""
CYCLE 1904: INITIAL ENERGY SENSITIVITY

How does the system respond to different initial energy levels?
This reveals phase space basin structure.
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

def run_with_energy(seed, n_initial, repro_prob, init_energy):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, init_energy, depth=0), 0)

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
    print(f"CYCLE 1904: Energy Sensitivity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing initial energy effect on coexistence")
    print("=" * 80)

    seeds = list(range(1904001, 1904041))  # 40 seeds
    prob = 0.10

    # Test at dead zone and safe zone
    test_n = [14, 17]  # Dead zone and threshold
    energies = [0.5, 0.7, 1.0, 1.3, 1.5]

    for n in test_n:
        print(f"\nN = {n}:")
        print(f"{'Energy':>7} | {'Coex':>5}")
        print("-" * 20)

        for e in energies:
            coex = sum(run_with_energy(s, n, prob, e) for s in seeds) / len(seeds) * 100
            print(f"{e:>7.1f} | {coex:>4.0f}%")

    # Summary
    print("\n" + "=" * 80)
    print("ENERGY SENSITIVITY ANALYSIS")
    print("=" * 80)

    # Compare at dead zone
    coex_low = sum(run_with_energy(s, 14, prob, 0.5) for s in seeds) / len(seeds) * 100
    coex_med = sum(run_with_energy(s, 14, prob, 1.0) for s in seeds) / len(seeds) * 100
    coex_high = sum(run_with_energy(s, 14, prob, 1.5) for s in seeds) / len(seeds) * 100

    print(f"\nDead zone (N=14) sensitivity:")
    print(f"  Low energy (0.5): {coex_low:.0f}%")
    print(f"  Medium energy (1.0): {coex_med:.0f}%")
    print(f"  High energy (1.5): {coex_high:.0f}%")

    spread = max(coex_low, coex_med, coex_high) - min(coex_low, coex_med, coex_high)
    print(f"  Spread: {spread:.0f}%")

    if spread > 30:
        print("\nHIGH ENERGY SENSITIVITY at dead zone.")
        print("Initial conditions strongly affect outcome.")
    else:
        print("\nMODERATE ENERGY SENSITIVITY at dead zone.")

if __name__ == "__main__":
    main()
