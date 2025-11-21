#!/usr/bin/env python3
"""
CYCLE 1737: PARAMETER SENSITIVITY OF DEAD ZONES
Test if dead zone locations (N = 29 + 14.5k) depend on recharge/repro rates.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1737"
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
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def find_minimum(seeds, n_range, recharge, repro):
    """Find N with minimum coexistence in range"""
    results = []
    for n in n_range:
        outcomes = [run_test(seed, n, recharge, repro) for seed in seeds]
        coexist = sum(outcomes) / len(outcomes) * 100
        results.append((n, coexist))
    min_n, min_c = min(results, key=lambda x: x[1])
    return min_n, min_c

def main():
    print(f"CYCLE 1737: Parameter Sensitivity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Test if dead zone locations depend on recharge/repro rates")
    print("=" * 70)

    seeds = list(range(1737001, 1737031))  # 30 seeds

    # Parameter configurations
    configs = [
        ("Standard", 0.10, 0.10),
        ("Low recharge", 0.05, 0.10),
        ("High recharge", 0.15, 0.10),
        ("Low repro", 0.10, 0.05),
        ("High repro", 0.10, 0.15),
    ]

    # Test zones 1, 3, 5
    zones = [
        ("Zone 1", range(25, 34)),
        ("Zone 3", range(55, 64)),
        ("Zone 5", range(83, 92)),
    ]

    print(f"\n{'Config':<15} | {'Zone 1':>12} | {'Zone 3':>12} | {'Zone 5':>12}")
    print("-" * 60)

    results_table = []
    for config_name, recharge, repro in configs:
        row = [config_name]
        for zone_name, n_range in zones:
            min_n, min_c = find_minimum(seeds, n_range, recharge, repro)
            row.append(f"{min_n} ({min_c:.0f}%)")
        results_table.append(row)
        print(f"{row[0]:<15} | {row[1]:>12} | {row[2]:>12} | {row[3]:>12}")

    # Analysis
    print("\n--- Dead Zone Center Locations ---")
    print(f"{'Config':<15} | Z1 | Z3 | Z5 | Mean Interval")
    print("-" * 55)

    for row in results_table:
        z1 = int(row[1].split()[0])
        z3 = int(row[2].split()[0])
        z5 = int(row[3].split()[0])
        int1 = z3 - z1
        int2 = z5 - z3
        mean_int = (int1 + int2) / 2
        print(f"{row[0]:<15} | {z1} | {z3} | {z5} | {mean_int:.1f}")

    print("\nPredicted: Z1=29, Z3=59, Z5=87 | Mean interval: 29")

if __name__ == "__main__":
    main()
