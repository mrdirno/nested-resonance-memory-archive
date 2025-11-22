#!/usr/bin/env python3
"""
CYCLE 1884: MODEL PREDICTION TEST

Test λ(p) = 16 - 13p at new probability value p=0.18.
Predicted: λ = 13.66 → dead zone at N ≈ 14
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

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if p > 0) >= 2

def main():
    print(f"CYCLE 1884: Model Prediction Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing λ(p) = 16 - 13p at p = 0.18")
    print("=" * 80)

    seeds = list(range(1884001, 1884051))
    prob = 0.18

    # Model prediction
    pred_lambda = 16 - 13 * prob
    pred_dead = [int(k * pred_lambda) for k in [1, 2, 3]]
    pred_safe = [int((k + 0.5) * pred_lambda) for k in [1, 2]]

    print(f"\nModel predictions for p = {prob}:")
    print(f"  λ = {pred_lambda:.2f}")
    print(f"  Dead zones: N = {pred_dead}")
    print(f"  Safe zones: N = {pred_safe}")

    # Test range
    test_n = list(range(10, 35))

    print(f"\n{'N':>3} | {'Coex':>5} | {'Predicted':>9}")
    print("-" * 30)

    correct = 0
    total_tests = 0

    for n in test_n:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100

        # Prediction
        if n in pred_dead or abs(n - pred_dead[0]) <= 1 or abs(n - pred_dead[1]) <= 1:
            predicted = "DEAD"
        else:
            predicted = "safe"

        actual = "DEAD" if coex < 70 else "safe"
        match = "✓" if predicted == actual else "✗"

        # Count correct predictions
        if n in pred_dead + pred_safe or (n > 16 and n < 25):
            total_tests += 1
            if predicted == actual:
                correct += 1

        if n in pred_dead or n in pred_safe or coex < 70:
            print(f"{n:>3} | {coex:>4.0f}% | {predicted:>9} {match}")

    # Summary
    print("\n" + "=" * 80)
    print("PREDICTION ACCURACY")
    print("=" * 80)

    # Find actual dead zone minimum
    min_coex = 100
    min_n = 0
    for n in test_n:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
        if coex < min_coex:
            min_coex = coex
            min_n = n

    print(f"\nPredicted dead zone: N = {pred_dead[0]}")
    print(f"Actual minimum coex: N = {min_n} ({min_coex:.0f}%)")
    print(f"Error: {abs(pred_dead[0] - min_n)} positions")

    if abs(pred_dead[0] - min_n) <= 1:
        print("\nModel prediction VALIDATED ✓")
    else:
        print("\nModel prediction needs refinement")

if __name__ == "__main__":
    main()
