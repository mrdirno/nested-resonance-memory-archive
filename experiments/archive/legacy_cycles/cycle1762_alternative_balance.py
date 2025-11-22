#!/usr/bin/env python3
"""
CYCLE 1762: ALTERNATIVE BALANCE
Test if other symmetric balances (3:3, 4:4) also produce dead zones.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1762"
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

def run_test(seed, n_initial, comp_size, decomp_size):
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
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Variable composition size
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < comp_size: continue
            np.random.shuffle(agents)
            i = 0
            while i <= len(agents) - comp_size:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    total_e = sum(agents[i+j].energy for j in range(comp_size))
                    new_e = total_e * 0.85
                    for j in range(comp_size):
                        reality.remove_agent(agents[i+j].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += comp_size
                else:
                    i += 1

        # Variable decomposition size
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(decomp_size):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def main():
    print(f"CYCLE 1762: Alternative Balance | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing alternative symmetric balances")
    print("=" * 70)

    seeds = list(range(1762001, 1762021))

    # Test different balances
    configs = [
        (2, 2),  # Standard 2:2
        (3, 3),  # 3:3
        (4, 4),  # 4:4
        (2, 3),  # Unbalanced
        (3, 2),  # Unbalanced
    ]
    zone1_range = range(25, 34)

    print(f"\n{'Comp:Decomp':<12} | {'Zone 1 Min':>15}")
    print("-" * 32)

    for comp, decomp in configs:
        results = []
        for n in zone1_range:
            outcomes = [run_test(seed, n, comp, decomp) for seed in seeds]
            coexist = sum(outcomes) / len(outcomes) * 100
            results.append((n, coexist))
        min_n, min_c = min(results, key=lambda x: x[1])
        print(f"{comp}:{decomp}{'':8} | {min_n} ({min_c:.0f}%)")

if __name__ == "__main__":
    main()
