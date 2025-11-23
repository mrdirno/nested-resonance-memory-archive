#!/usr/bin/env python3
"""
CYCLE 1711: OPTIMAL N PARAMETER SENSITIVITY
How does optimal N shift with different parameters?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1711"
CYCLES = 1000
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

def run_sensitivity(seed, n_initial, recharge, repro, decomp):
    """Run with specified parameters."""
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
                if agent.energy > decomp:
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

def main():
    print(f"CYCLE 1711: Optimal N Sensitivity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: How does optimal N shift with parameters?")
    print("=" * 70)

    seeds = list(range(1711001, 1711016))  # 15 seeds
    population_sizes = [20, 25, 30, 35]

    # Test different parameter combinations
    configs = [
        ("Standard", 0.1, 0.1, 1.3),
        ("Low recharge", 0.05, 0.1, 1.3),
        ("High recharge", 0.15, 0.1, 1.3),
        ("Low repro", 0.1, 0.05, 1.3),
        ("High repro", 0.1, 0.15, 1.3),
        ("Low decomp", 0.1, 0.1, 1.1),
        ("High decomp", 0.1, 0.1, 1.5),
    ]

    results_table = []
    for name, recharge, repro, decomp in configs:
        print(f"\n{name} (r={recharge}, p={repro}, d={decomp})")
        best_n = 0
        best_coex = 0
        row = {"config": name}
        for n_init in population_sizes:
            results = [run_sensitivity(seed, n_init, recharge, repro, decomp) for seed in seeds]
            coexist = sum(results) / len(results) * 100
            row[f"n={n_init}"] = coexist
            if coexist > best_coex:
                best_coex = coexist
                best_n = n_init
        row["optimal"] = best_n
        results_table.append(row)
        print(f"  Optimal: n={best_n} ({best_coex:.0f}%)")

    # Summary table
    print("\n" + "=" * 70)
    print("OPTIMAL N BY PARAMETER CONFIGURATION")
    print("=" * 70)
    print(f"\n{'Config':15} | {'n=20':>5} | {'n=25':>5} | {'n=30':>5} | {'n=35':>5} | {'Opt':>4}")
    print("-" * 60)
    for row in results_table:
        print(f"{row['config']:15} | {row['n=20']:5.0f} | {row['n=25']:5.0f} | {row['n=30']:5.0f} | {row['n=35']:5.0f} | {row['optimal']:4}")

if __name__ == "__main__":
    main()
