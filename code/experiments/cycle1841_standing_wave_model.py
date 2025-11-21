#!/usr/bin/env python3
"""
CYCLE 1841: STANDING WAVE MODEL FIT
Quantifying the cos²(πk) + attenuation model for dead zone prediction.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1841"
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
    print(f"CYCLE 1841: Standing Wave Model Fit | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Fitting coexistence = B - A × cos²(πk) × exp(-k/τ)")
    print("=" * 80)

    seeds = list(range(1841001, 1841021))  # 20 seeds for better stats
    prob = 0.10

    # Collect data points
    data = []
    print(f"\nCollecting coexistence data (prob=0.10, 20 seeds)...")
    print("-" * 60)

    for k_tenth in range(-10, 51):  # k from -1 to 5 in 0.1 steps
        k = k_tenth / 10.0
        n_exact = 29 + k * LAMBDA
        if n_exact < 5:
            continue
        n_int = int(round(n_exact))
        coex = sum(run_test(seed, n_int, prob) for seed in seeds) / len(seeds)
        data.append((k, coex))

        if k_tenth % 5 == 0:  # Print every 0.5
            marker = "*" if k == int(k) else " "
            print(f"k={k:>5.1f}{marker} N={n_int:>3} Coex={coex*100:>5.0f}%")

    # Fit model: coex = B - A × cos²(πk) × exp(-|k|/τ)
    print("\n" + "=" * 80)
    print("MODEL FITTING")
    print("=" * 80)

    # Manual fit by testing parameters
    best_err = float('inf')
    best_params = None

    for B in [0.95, 1.0]:
        for A in [0.4, 0.5, 0.6, 0.7]:
            for tau in [1.5, 2.0, 2.5, 3.0, 4.0]:
                err = 0
                for k, coex in data:
                    pred = B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)
                    err += (pred - coex) ** 2
                err = math.sqrt(err / len(data))
                if err < best_err:
                    best_err = err
                    best_params = (B, A, tau)

    B, A, tau = best_params
    print(f"\nBest fit parameters:")
    print(f"  B (baseline) = {B:.2f}")
    print(f"  A (amplitude) = {A:.2f}")
    print(f"  τ (decay constant) = {tau:.1f}")
    print(f"  RMSE = {best_err*100:.1f}%")

    # Model predictions vs actual
    print(f"\nModel: Coex = {B:.2f} - {A:.2f} × cos²(πk) × exp(-|k|/{tau:.1f})")
    print("-" * 60)
    print(f"{'k':<8} | {'Actual':>8} | {'Predicted':>10} | {'Error':>8}")
    print("-" * 60)

    total_err = 0
    n_correct = 0
    for k in [0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]:
        actual = next((c for (kk, c) in data if abs(kk - k) < 0.01), None)
        if actual is None:
            continue
        pred = B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)
        err = abs(pred - actual)
        total_err += err

        # Check if prediction is correct (both >0.7 or both <0.7)
        actual_safe = actual >= 0.7
        pred_safe = pred >= 0.7
        correct = "✓" if actual_safe == pred_safe else "✗"
        if actual_safe == pred_safe:
            n_correct += 1

        print(f"{k:<8.1f} | {actual*100:>6.0f}% | {pred*100:>8.0f}% | {err*100:>6.1f}% {correct}")

    print("-" * 60)
    print(f"Classification accuracy: {n_correct}/11 = {n_correct/11*100:.0f}%")

    # Predict safe N values
    print("\n" + "=" * 80)
    print("SAFE N VALUES (predicted coex > 70%)")
    print("=" * 80)

    safe_n = []
    for k in np.arange(0, 6.01, 0.25):
        pred = B - A * (math.cos(PI * k) ** 2) * math.exp(-abs(k) / tau)
        if pred >= 0.7:
            n = int(round(29 + k * LAMBDA))
            if n not in safe_n:
                safe_n.append(n)

    print(f"\nSafe N values (k=0 to 6): {safe_n}")
    print(f"Pattern: Every ~7 agents (half-wavelength)")

if __name__ == "__main__":
    main()
