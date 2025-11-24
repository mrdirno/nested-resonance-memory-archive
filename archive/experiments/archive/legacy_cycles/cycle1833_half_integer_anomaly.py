#!/usr/bin/env python3
"""
CYCLE 1833: HALF-INTEGER K ANOMALY
Testing if k mod 1 ≈ 0.5 creates resonance even at high |k|.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1833"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI
N1 = 22/PI + 22

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
    print(f"CYCLE 1833: Half-Integer k Anomaly | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing k mod 1 ≈ 0.5 resonance at high |k|")
    print("=" * 80)

    seeds = list(range(1833001, 1833021))  # 20 seeds

    # Find N values with k mod 1 ≈ 0.45-0.55 at different |k|
    # N = N1 + k * LAMBDA, k mod 1 ≈ 0.5 means k ≈ 0.5, 1.5, 2.5, 3.5...
    half_k_values = [0.5, 1.5, 2.5, 3.5, 4.5]

    probs = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80]

    print(f"\n{'N':<4} | {'k':<6} | {'|k|':<5} |", end="")
    for p in probs:
        print(f" {p:<5} |", end="")
    print(" Dead Probs")
    print("-" * (22 + len(probs) * 8 + 15))

    for k_target in half_k_values:
        n = int(round(N1 + k_target * LAMBDA))
        k = (n - N1) / LAMBDA

        print(f"{n:<4} | {k:>5.2f} | {abs(k):>5.2f} |", end="")

        dead_probs = []
        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            marker = "X" if coex < 70 else "."
            print(f" {coex:>3.0f}{marker} |", end="")
            if coex < 70:
                dead_probs.append(prob)

        if dead_probs:
            print(f" {dead_probs}")
        else:
            print(" safe")

    # Also test integer k values at high |k| for comparison
    print("\n" + "=" * 80)
    print("COMPARISON: INTEGER K VALUES AT HIGH |K|")
    print("=" * 80)

    int_k_values = [2, 3, 4, 5]

    print(f"\n{'N':<4} | {'k':<6} | {'|k|':<5} |", end="")
    for p in probs:
        print(f" {p:<5} |", end="")
    print(" Dead Probs")
    print("-" * (22 + len(probs) * 8 + 15))

    for k_target in int_k_values:
        n = int(round(N1 + k_target * LAMBDA))
        k = (n - N1) / LAMBDA

        print(f"{n:<4} | {k:>5.2f} | {abs(k):>5.2f} |", end="")

        dead_probs = []
        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            marker = "X" if coex < 70 else "."
            print(f" {coex:>3.0f}{marker} |", end="")
            if coex < 70:
                dead_probs.append(prob)

        if dead_probs:
            print(f" {dead_probs}")
        else:
            print(" safe")

if __name__ == "__main__":
    main()
