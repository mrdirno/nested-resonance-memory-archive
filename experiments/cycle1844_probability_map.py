#!/usr/bin/env python3
"""
CYCLE 1844: PROBABILITY SPACE MAPPING
How does the standing wave pattern change across probability values?
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1844"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI

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
    print(f"CYCLE 1844: Probability Space Mapping | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("How does the standing wave pattern change across probabilities?")
    print("=" * 80)

    seeds = list(range(1844001, 1844016))  # 15 seeds
    probs = [0.05, 0.10, 0.20, 0.30, 0.50]
    k_values = [0, 0.5, 1, 1.5, 2, 2.5, 3]

    # Build probability × k matrix
    print(f"\nCoexistence (%) by probability and k value")
    print("-" * 80)

    # Header
    header = f"{'k':<6} |"
    for p in probs:
        header += f" {p:<8} |"
    print(header)
    print("-" * 80)

    # Data matrix
    data = {}
    for k in k_values:
        n = int(round(29 + k * LAMBDA))
        row = f"{k:<6} |"
        data[k] = {}

        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            marker = "X" if coex < 70 else " "
            row += f" {coex:>5.0f}{marker}  |"
            data[k][prob] = coex

        print(row)

    print("-" * 80)

    # Analysis: Integer vs half-integer by probability
    print("\n" + "=" * 80)
    print("INTEGER VS HALF-INTEGER BY PROBABILITY")
    print("=" * 80)

    print(f"\n{'Prob':<8} | {'Int avg':<10} | {'Half avg':<10} | {'Diff':>8}")
    print("-" * 45)

    for prob in probs:
        int_avg = np.mean([data[k][prob] for k in [0, 1, 2, 3]])
        half_avg = np.mean([data[k][prob] for k in [0.5, 1.5, 2.5]])
        diff = half_avg - int_avg
        print(f"{prob:<8} | {int_avg:>8.0f}% | {half_avg:>8.0f}% | {diff:>+6.0f}%")

    # Find where resonance pattern is strongest
    print("\n" + "=" * 80)
    print("RESONANCE PATTERN STRENGTH BY PROBABILITY")
    print("=" * 80)

    print("\nResonance = (half-integer avg) - (integer avg)")
    best_prob = None
    best_diff = 0

    for prob in probs:
        int_avg = np.mean([data[k][prob] for k in [0, 1, 2, 3]])
        half_avg = np.mean([data[k][prob] for k in [0.5, 1.5, 2.5]])
        diff = half_avg - int_avg
        if diff > best_diff:
            best_diff = diff
            best_prob = prob

    print(f"\nStrongest resonance at prob={best_prob} (diff={best_diff:.0f}%)")

    # Count dead zones by probability
    print("\n" + "=" * 80)
    print("DEAD ZONE COUNT BY PROBABILITY")
    print("=" * 80)

    print(f"\n{'Prob':<8} | {'Dead zones':<12} | {'Which k'}")
    print("-" * 50)

    for prob in probs:
        dead = [k for k in k_values if data[k][prob] < 70]
        dead_str = ", ".join([str(k) for k in dead]) if dead else "none"
        print(f"{prob:<8} | {len(dead):<12} | {dead_str}")

if __name__ == "__main__":
    main()
