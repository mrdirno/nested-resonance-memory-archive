#!/usr/bin/env python3
"""
CYCLE 1736: ATTENUATION MECHANISM ANALYSIS
Why does the dead zone pattern weaken at N>150?

Hypotheses:
1. Population cap (3000) effects
2. Statistical smoothing at scale
3. Energy distribution changes
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1736"
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

def run_detailed_test(seed, n_initial, pop_cap=3000):
    """Run test and collect diagnostic data"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    recharge = 0.1
    repro = 0.1

    cap_hits = 0
    max_pop = 0

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        max_pop = max(max_pop, total)

        if total >= pop_cap:
            cap_hits += 1
        if total == 0: break

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

    return {
        'coexist': coexist,
        'cap_hits': cap_hits,
        'max_pop': max_pop
    }

def main():
    print(f"CYCLE 1736: Attenuation Mechanism | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Understand why dead zone pattern attenuates at N>150")
    print("=" * 70)

    seeds = list(range(1736001, 1736031))  # 30 seeds

    # Test key N values: dead zones vs safe zones
    test_cases = [
        ("Zone 1", 29),
        ("Safe", 35),
        ("Zone 5", 87),
        ("Safe", 95),
        ("Zone 9", 147),
        ("Safe", 155),
        ("Expected Zone 10", 160),
        ("High N", 175),
    ]

    print("\n--- Standard Pop Cap (3000) ---")
    print(f"{'Case':<20} | {'N':>4} | {'Coexist':>8} | {'Cap Hits':>10} | {'Max Pop':>8}")
    print("-" * 65)

    for name, n in test_cases:
        results = [run_detailed_test(seed, n, pop_cap=3000) for seed in seeds]
        coexist = sum(r['coexist'] for r in results) / len(results) * 100
        avg_cap = sum(r['cap_hits'] for r in results) / len(results)
        avg_max = sum(r['max_pop'] for r in results) / len(results)
        print(f"{name:<20} | {n:4d} | {coexist:7.0f}% | {avg_cap:10.1f} | {avg_max:8.0f}")

    # Test with higher pop cap to see if that's the issue
    print("\n--- Higher Pop Cap (10000) ---")
    print(f"{'Case':<20} | {'N':>4} | {'Coexist':>8} | {'Cap Hits':>10} | {'Max Pop':>8}")
    print("-" * 65)

    high_n_cases = [
        ("Zone 9", 147),
        ("Expected Zone 10", 160),
        ("High N", 175),
    ]

    for name, n in high_n_cases:
        results = [run_detailed_test(seed, n, pop_cap=10000) for seed in seeds]
        coexist = sum(r['coexist'] for r in results) / len(results) * 100
        avg_cap = sum(r['cap_hits'] for r in results) / len(results)
        avg_max = sum(r['max_pop'] for r in results) / len(results)
        print(f"{name:<20} | {n:4d} | {coexist:7.0f}% | {avg_cap:10.1f} | {avg_max:8.0f}")

if __name__ == "__main__":
    main()
