#!/usr/bin/env python3
"""
CYCLE 1832: V2 MODEL WITH ATTENUATION
Test improved predictive model with exp(-|k|/2) attenuation.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1832"
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

def predict_v2(n):
    """V2 model with attenuation factor"""
    k = (n - N1) / LAMBDA
    k_frac = k % 1

    # Attenuation at high |k|
    if abs(k) > 1.5:
        return "safe (attenuated)", 0.1

    # Standard prediction with confidence
    if k_frac < 0.15 or k_frac > 0.90:
        return "low (0.05-0.20)", 0.8
    elif 0.30 <= k_frac <= 0.55:
        return "safe or high", 0.7
    elif 0.55 < k_frac <= 0.75:
        return "mid (0.25-0.35)", 0.7
    else:
        return "mid (0.20-0.50)", 0.6

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
    print(f"CYCLE 1832: V2 Model Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing v2 predictive model with attenuation factor")
    print("=" * 80)

    seeds = list(range(1832001, 1832021))  # 20 seeds
    probs = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80]

    # Same validation set as C1831
    validation_n = [17, 20, 25, 37, 40, 52, 65, 72, 80]

    print(f"\n{'N':<4} | {'|k|':<5} | {'Prediction':>22} |", end="")
    for p in probs:
        print(f" {p:<5} |", end="")
    print(" Result")
    print("-" * (38 + len(probs) * 8 + 8))

    v1_correct = 0
    v2_correct = 0
    total = 0

    for n in validation_n:
        k = (n - N1) / LAMBDA
        prediction, conf = predict_v2(n)

        print(f"{n:<4} | {abs(k):>5.2f} | {prediction:>22} |", end="")

        dead_probs = []
        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            marker = "X" if coex < 70 else "."
            print(f" {coex:>3.0f}{marker} |", end="")
            if coex < 70:
                dead_probs.append(prob)

        # Score v2 prediction
        if "attenuated" in prediction and not dead_probs:
            result = "✓ (v2)"
            v2_correct += 1
        elif "safe" in prediction and not dead_probs:
            result = "✓"
            v1_correct += 1
            v2_correct += 1
        elif "low" in prediction and dead_probs and max(dead_probs) <= 0.20:
            result = "✓"
            v1_correct += 1
            v2_correct += 1
        elif "mid" in prediction and dead_probs and 0.20 <= min(dead_probs) <= 0.50:
            result = "✓"
            v1_correct += 1
            v2_correct += 1
        elif "high" in prediction and dead_probs and min(dead_probs) >= 0.50:
            result = "✓"
            v1_correct += 1
            v2_correct += 1
        else:
            result = "✗"

        total += 1
        print(f" {result}")

    print("\n" + "=" * 80)
    print(f"V1 MODEL (no attenuation): {v1_correct}/{total} = {v1_correct/total*100:.0f}%")
    print(f"V2 MODEL (with attenuation): {v2_correct}/{total} = {v2_correct/total*100:.0f}%")
    print(f"IMPROVEMENT: +{(v2_correct-v1_correct)/total*100:.0f}%")
    print("=" * 80)

if __name__ == "__main__":
    main()
