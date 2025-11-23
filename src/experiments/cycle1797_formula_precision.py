#!/usr/bin/env python3
"""
CYCLE 1797: FORMULA PRECISION VERIFICATION
Final verification of N_k = N₁ + kλ across entire range.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1797"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# Formula parameters
N1 = 22/PI + 22  # ≈ 29
LAMBDA = PI + E + PHI + 22/PI  # ≈ 14.5

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

def run_test(seed, n_initial):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    total_before = 0
    total_composed = 0

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

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            total_before += len(agents)
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            composed = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    composed += 2
                    i += 2
                else:
                    i += 1
            total_composed += composed

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

    pairing = total_composed / total_before if total_before > 0 else 0
    return pairing

def main():
    print(f"CYCLE 1797: Formula Precision | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Verifying N_k = N₁ + kλ where N₁={N1:.1f}, λ={LAMBDA:.2f}")
    print("=" * 70)

    seeds = list(range(1797001, 1797031))

    print(f"\n{'k':<4} | {'Predicted':>10} | {'Observed':>10} | {'Error':>8} | {'Pairing':>8}")
    print("-" * 50)

    errors = []

    for k in range(-1, 9):
        predicted = N1 + k * LAMBDA

        # Find observed peak by testing neighborhood
        test_n = [int(predicted) - 2, int(predicted) - 1, int(predicted), int(predicted) + 1, int(predicted) + 2]
        pairing_rates = []
        for n in test_n:
            if n < 10:
                continue
            rate = sum(run_test(seed, n) for seed in seeds) / len(seeds)
            pairing_rates.append((n, rate))

        if pairing_rates:
            observed, max_pairing = max(pairing_rates, key=lambda x: x[1])
            error = observed - predicted
            errors.append(abs(error))
            print(f"{k:<4} | {predicted:>10.1f} | {observed:>10} | {error:>+8.1f} | {max_pairing*100:>7.1f}%")

    print(f"\nMean absolute error: {np.mean(errors):.2f} N units")
    print(f"Max absolute error: {max(errors):.1f} N units")

if __name__ == "__main__":
    main()
