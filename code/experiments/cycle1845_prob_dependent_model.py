#!/usr/bin/env python3
"""
CYCLE 1845: PROBABILITY-DEPENDENT MODEL
Formalizing the cos²/sin² switch based on probability range.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1845"
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

def model_prob_dependent(k, prob, B=0.95, A=0.40, tau=4.0):
    """Probability-dependent standing wave model"""
    if prob <= 0.15:
        # Low prob: cos² pattern (integer k dead)
        return B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)
    elif prob <= 0.35:
        # Mid prob: sin² pattern (half-integer k dead)
        return B - A * (math.sin(PI * k) ** 2) * math.exp(-abs(k) / tau)
    else:
        # High prob: cos² pattern again
        return B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)

def main():
    print(f"CYCLE 1845: Probability-Dependent Model | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing cos²/sin² switch model across probability range")
    print("=" * 80)

    seeds = list(range(1845001, 1845016))  # 15 seeds
    probs = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]
    k_values = [0, 0.5, 1, 1.5, 2, 2.5]

    # Collect data and test model
    print("\nCollecting data and testing model...")
    print("=" * 80)

    total_correct = 0
    total_tests = 0
    errors = []

    for prob in probs:
        correct = 0
        tests = 0

        for k in k_values:
            n = int(round(29 + k * LAMBDA))
            actual = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds)
            predicted = model_prob_dependent(k, prob)

            # Classification
            actual_safe = actual >= 0.70
            pred_safe = predicted >= 0.70
            is_correct = actual_safe == pred_safe

            if is_correct:
                correct += 1
                total_correct += 1
            tests += 1
            total_tests += 1

            errors.append(abs(predicted - actual))

        accuracy = correct / tests * 100
        print(f"prob={prob:.2f}: {correct}/{tests} correct ({accuracy:.0f}%)")

    # Overall results
    print("\n" + "=" * 80)
    print("MODEL PERFORMANCE")
    print("=" * 80)

    overall_accuracy = total_correct / total_tests * 100
    rmse = math.sqrt(sum(e**2 for e in errors) / len(errors)) * 100

    print(f"\nOverall accuracy: {total_correct}/{total_tests} ({overall_accuracy:.0f}%)")
    print(f"RMSE: {rmse:.1f}%")

    # Detailed comparison for key probabilities
    print("\n" + "=" * 80)
    print("DETAILED COMPARISON")
    print("=" * 80)

    key_probs = [0.10, 0.20, 0.30, 0.50]

    for prob in key_probs:
        mode = "cos²" if prob <= 0.15 or prob > 0.35 else "sin²"
        print(f"\nprob={prob} (mode={mode}):")
        print(f"{'k':<6} | {'N':<6} | {'Actual':>8} | {'Pred':>8} | {'Match'}")
        print("-" * 50)

        for k in k_values:
            n = int(round(29 + k * LAMBDA))
            actual = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            predicted = model_prob_dependent(k, prob) * 100
            match = "✓" if (actual >= 70) == (predicted >= 70) else "✗"
            print(f"{k:<6} | {n:<6} | {actual:>6.0f}% | {predicted:>6.0f}% | {match}")

    # Model equation summary
    print("\n" + "=" * 80)
    print("FINAL MODEL")
    print("=" * 80)

    print("\n```python")
    print("def predict_coexistence(k, prob):")
    print("    B, A, tau = 0.95, 0.40, 4.0")
    print("    if prob <= 0.15 or prob > 0.35:")
    print("        return B - A * cos(pi*k)**2 * exp(-abs(k)/tau)")
    print("    else:")
    print("        return B - A * sin(pi*k)**2 * exp(-abs(k)/tau)")
    print("```")

if __name__ == "__main__":
    main()
