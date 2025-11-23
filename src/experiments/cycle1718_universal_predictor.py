#!/usr/bin/env python3
"""
CYCLE 1718: UNIVERSAL PREDICTOR
What metric is common to ALL successful configurations?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1718"
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

def run_predictor_search(seed, n_initial, recharge, repro):
    """Collect multiple metrics to find universal predictor."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    d1_created = 0
    d1_decomp = 0
    d2_created = 0
    d1_stable_cycles = 0  # Cycles where D1 population is non-empty
    max_d1 = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        d1_count = len(pops[1])
        if d1_count > 0:
            d1_stable_cycles += 1
        if d1_count > max_d1:
            max_d1 = d1_count

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
                    if d == 0:
                        d1_created += 1
                    elif d == 1:
                        d2_created += 1
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    if d == 1:
                        d1_decomp += 1
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

    # Calculate various metrics
    d1d2_ratio = d2_created / d1_created if d1_created > 0 else 0
    advance_decomp = d2_created / d1_decomp if d1_decomp > 0 else float('inf')
    stability = d1_stable_cycles / CYCLES
    throughput = d2_created / CYCLES

    return {
        "d1d2_ratio": d1d2_ratio,
        "advance_decomp": min(advance_decomp, 10),  # Cap for display
        "stability": stability,
        "throughput": throughput,
        "max_d1": max_d1,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1718: Universal Predictor | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Find metric common to ALL successful configurations")
    print("=" * 70)

    seeds = list(range(1718001, 1718021))  # 20 seeds

    # Test successful vs failed configurations
    test_cases = [
        # (name, n, recharge, repro, expected_success)
        ("Std n=25", 25, 0.1, 0.1, True),
        ("Std n=30", 30, 0.1, 0.1, False),
        ("LowR n=25", 25, 0.05, 0.1, True),
        ("LowR n=35", 35, 0.05, 0.1, True),
        ("LowP n=25", 25, 0.1, 0.05, True),
        ("LowP n=30", 30, 0.1, 0.05, False),
        ("HighP n=35", 35, 0.1, 0.15, True),
    ]

    print(f"\n{'Config':>12} | {'D1D2':>6} | {'A/D':>5} | {'Stab':>5} | {'Thru':>5} | {'MaxD1':>6} | {'Coex':>6}")
    print("-" * 70)

    for name, n, recharge, repro, expected in test_cases:
        results = [run_predictor_search(seed, n, recharge, repro) for seed in seeds]
        avg_d1d2 = np.mean([r["d1d2_ratio"] for r in results])
        avg_ad = np.mean([r["advance_decomp"] for r in results])
        avg_stab = np.mean([r["stability"] for r in results])
        avg_thru = np.mean([r["throughput"] for r in results])
        avg_maxd1 = np.mean([r["max_d1"] for r in results])
        coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100
        marker = "✓" if coexist >= 90 else "✗"
        print(f"{name:>12} | {avg_d1d2:6.2f} | {avg_ad:5.2f} | {avg_stab:5.2f} | {avg_thru:5.2f} | {avg_maxd1:6.1f} | {coexist:5.0f}% {marker}")

if __name__ == "__main__":
    main()
