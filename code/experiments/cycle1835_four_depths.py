#!/usr/bin/env python3
"""
CYCLE 1835: FOUR DEPTHS PATTERN
Testing dead zone patterns with N_DEPTHS=4 for trend analysis.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1835"
CYCLES = 500
N_DEPTHS = 4  # Reduced from 5

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

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def main():
    print(f"CYCLE 1835: Four Depths Pattern | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Testing dead zone patterns with N_DEPTHS={N_DEPTHS}")
    print("=" * 80)

    seeds = list(range(1835001, 1835021))

    n_values = [14, 24, 29, 35, 43, 58]
    probs = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.80]

    print(f"\n{'N':<4} |", end="")
    for p in probs:
        print(f" {p:<6} |", end="")
    print(" Pattern")
    print("-" * (8 + len(probs) * 9 + 10))

    results = {}
    for n in n_values:
        print(f"{n:<4} |", end="")

        dead_probs = []
        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            marker = "X" if coex < 70 else "."
            print(f" {coex:>4.0f}{marker} |", end="")
            if coex < 70:
                dead_probs.append(prob)

        if not dead_probs:
            pattern = "safe"
        elif max(dead_probs) <= 0.20:
            pattern = "low prob"
        elif min(dead_probs) >= 0.30:
            pattern = "mid/high"
        else:
            pattern = "mixed"

        results[n] = pattern
        print(f" {pattern}")

    # Trend analysis
    print("\n" + "=" * 80)
    print("DEPTH TREND ANALYSIS")
    print("=" * 80)
    print("\n| N | 4 Depths | 5 Depths | 6 Depths | Trend |")
    print("|---|----------|----------|----------|-------|")

    five_depth = {14: "low prob", 24: "mid prob", 29: "low prob", 35: "mid/high", 43: "mid prob", 58: "safe"}
    six_depth = {14: "low prob", 24: "mid/high", 29: "low prob", 35: "safe", 43: "safe", 58: "low prob"}

    for n in n_values:
        d4 = results[n]
        d5 = five_depth[n]
        d6 = six_depth[n]

        if d4 == d5 == d6:
            trend = "stable"
        elif d4 == "low prob" and d5 == "low prob" and d6 == "low prob":
            trend = "always low"
        else:
            trend = "shifting"

        print(f"| {n} | {d4:>8} | {d5:>8} | {d6:>8} | {trend} |")

if __name__ == "__main__":
    main()
