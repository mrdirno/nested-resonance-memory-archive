#!/usr/bin/env python3
"""
CYCLE 1843: HARMONIC-CORRECTED MODEL
Adding even-harmonic penalty to improve model accuracy.
Target: coex = B - A × cos²(πk) × exp(-|k|/τ) - H × (1 + cos(2πk))/2
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1843"
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

def model_v1(k, B, A, tau):
    """Original model: B - A × cos²(πk) × exp(-|k|/τ)"""
    return B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)

def model_v2(k, B, A, tau, H):
    """Harmonic model: B - A × cos²(πk) × exp(-|k|/τ) - H × (1+cos(2πk))/2"""
    base = B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)
    even_penalty = H * (1 + math.cos(2 * PI * k)) / 2 * math.exp(-abs(k) / tau)
    return base - even_penalty

def main():
    print(f"CYCLE 1843: Harmonic-Corrected Model | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Developing model with even-harmonic penalty term")
    print("=" * 80)

    seeds = list(range(1843001, 1843021))  # 20 seeds
    prob = 0.10

    # Collect data
    print("\nCollecting data (20 seeds, prob=0.10)...")
    data = []
    for k in np.arange(0, 5.1, 0.5):
        n = int(round(29 + k * LAMBDA))
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds)
        data.append((k, coex))
        print(f"k={k:.1f} N={n} coex={coex*100:.0f}%")

    # Fit V1 model
    print("\n" + "=" * 80)
    print("MODEL V1: Basic Standing Wave")
    print("=" * 80)

    best_v1_err = float('inf')
    best_v1_params = None

    for B in [0.95, 1.0]:
        for A in [0.3, 0.4, 0.5]:
            for tau in [2.0, 3.0, 4.0]:
                err = sum((model_v1(k, B, A, tau) - c) ** 2 for k, c in data)
                if err < best_v1_err:
                    best_v1_err = err
                    best_v1_params = (B, A, tau)

    B1, A1, tau1 = best_v1_params
    rmse1 = math.sqrt(best_v1_err / len(data)) * 100
    print(f"\nV1 parameters: B={B1}, A={A1}, τ={tau1}")
    print(f"V1 RMSE: {rmse1:.1f}%")

    # Fit V2 model with harmonic correction
    print("\n" + "=" * 80)
    print("MODEL V2: Harmonic-Corrected")
    print("=" * 80)

    best_v2_err = float('inf')
    best_v2_params = None

    for B in [0.95, 1.0]:
        for A in [0.2, 0.3, 0.4]:
            for tau in [2.0, 3.0, 4.0]:
                for H in [0.1, 0.15, 0.2, 0.25]:
                    err = sum((model_v2(k, B, A, tau, H) - c) ** 2 for k, c in data)
                    if err < best_v2_err:
                        best_v2_err = err
                        best_v2_params = (B, A, tau, H)

    B2, A2, tau2, H2 = best_v2_params
    rmse2 = math.sqrt(best_v2_err / len(data)) * 100
    print(f"\nV2 parameters: B={B2}, A={A2}, τ={tau2}, H={H2}")
    print(f"V2 RMSE: {rmse2:.1f}%")
    print(f"Improvement: {rmse1 - rmse2:.1f}% reduction in error")

    # Compare models
    print("\n" + "=" * 80)
    print("MODEL COMPARISON")
    print("=" * 80)
    print(f"\n{'k':<6} | {'Actual':>8} | {'V1':>8} | {'V2':>8} | {'V1 err':>8} | {'V2 err':>8}")
    print("-" * 60)

    v1_correct = 0
    v2_correct = 0

    for k, actual in data:
        pred_v1 = model_v1(k, B1, A1, tau1)
        pred_v2 = model_v2(k, B2, A2, tau2, H2)
        err_v1 = abs(pred_v1 - actual)
        err_v2 = abs(pred_v2 - actual)

        # Classification accuracy
        actual_safe = actual >= 0.7
        v1_safe = pred_v1 >= 0.7
        v2_safe = pred_v2 >= 0.7
        if actual_safe == v1_safe:
            v1_correct += 1
        if actual_safe == v2_safe:
            v2_correct += 1

        print(f"{k:<6.1f} | {actual*100:>6.0f}% | {pred_v1*100:>6.0f}% | {pred_v2*100:>6.0f}% | {err_v1*100:>6.1f}% | {err_v2*100:>6.1f}%")

    print("-" * 60)
    print(f"Classification: V1={v1_correct}/{len(data)} ({v1_correct/len(data)*100:.0f}%), V2={v2_correct}/{len(data)} ({v2_correct/len(data)*100:.0f}%)")

    # Final model equations
    print("\n" + "=" * 80)
    print("FINAL MODEL EQUATIONS")
    print("=" * 80)
    print(f"\nV1 (basic):")
    print(f"  Coex = {B1:.2f} - {A1:.2f} × cos²(πk) × exp(-|k|/{tau1:.1f})")
    print(f"\nV2 (harmonic-corrected):")
    print(f"  Coex = {B2:.2f} - {A2:.2f} × cos²(πk) × exp(-|k|/{tau2:.1f})")
    print(f"         - {H2:.2f} × (1+cos(2πk))/2 × exp(-|k|/{tau2:.1f})")

if __name__ == "__main__":
    main()
