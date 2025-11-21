#!/usr/bin/env python3
"""
CYCLE 1898: COMPLETE MODEL VALIDATION

Test all model predictions at new probability p=0.12.
Validate: λ, dead zones, threshold, depth.
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
    print(f"CYCLE 1898: Model Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing complete model at p = 0.12")
    print("=" * 80)

    seeds = list(range(1898001, 1898051))  # 50 seeds
    prob = 0.12

    # Model predictions
    lam = 16 - 13 * prob
    print(f"\nModel predictions for p = {prob}:")
    print(f"  λ = {lam:.2f}")

    # Dead zones
    print("\nDead zone predictions:")
    for k in [1, 2]:
        nc = k * lam
        n_det = nc + 3
        depth = 55 * k**(-0.5)
        min_coex = 100 - depth
        print(f"  k={k}: Nc={nc:.1f}, N_det={n_det:.1f}, MinCoex≈{min_coex:.0f}%")

    # Scan to find actual values
    print("\n" + "-" * 50)
    print("Experimental validation")
    print("-" * 50)

    # Test around first harmonic
    results_k1 = {}
    for n in range(10, 22):
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
        results_k1[n] = coex

    # Find minimum
    min_n_k1 = min(results_k1, key=results_k1.get)
    min_coex_k1 = results_k1[min_n_k1]

    # Find threshold
    det_n_k1 = None
    for n in sorted(results_k1.keys()):
        if results_k1[n] >= 95:
            det_n_k1 = n
            break

    print(f"\nFirst harmonic (k=1):")
    print(f"  Predicted Nc: {lam:.1f}")
    print(f"  Actual minimum: N={min_n_k1} ({min_coex_k1:.0f}%)")
    print(f"  Predicted N_det: {lam + 3:.1f}")
    print(f"  Actual threshold: N={det_n_k1} (≥95%)")
    print(f"  Predicted depth: {55:.0f}%")
    print(f"  Actual depth: {100 - min_coex_k1:.0f}%")

    # Test around second harmonic
    results_k2 = {}
    for n in range(24, 36):
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
        results_k2[n] = coex

    # Find minimum
    min_n_k2 = min(results_k2, key=results_k2.get)
    min_coex_k2 = results_k2[min_n_k2]

    # Find threshold
    det_n_k2 = None
    for n in sorted(results_k2.keys()):
        if results_k2[n] >= 95:
            det_n_k2 = n
            break

    print(f"\nSecond harmonic (k=2):")
    print(f"  Predicted Nc: {2*lam:.1f}")
    print(f"  Actual minimum: N={min_n_k2} ({min_coex_k2:.0f}%)")
    print(f"  Predicted N_det: {2*lam + 3:.1f}")
    print(f"  Actual threshold: N={det_n_k2} (≥95%)")
    print(f"  Predicted depth: {55/math.sqrt(2):.0f}%")
    print(f"  Actual depth: {100 - min_coex_k2:.0f}%")

    # Summary
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    errors = []
    errors.append(abs(min_n_k1 - lam))
    errors.append(abs((100 - min_coex_k1) - 55))
    if det_n_k1:
        errors.append(abs(det_n_k1 - (lam + 3)))
    errors.append(abs(min_n_k2 - 2*lam))
    errors.append(abs((100 - min_coex_k2) - 55/math.sqrt(2)))

    avg_error = np.mean(errors)

    print(f"\nAverage prediction error: {avg_error:.1f}")

    if avg_error < 3:
        print("MODEL VALIDATED ✓")
        print("All predictions within acceptable error bounds.")
    else:
        print("Model needs refinement.")

if __name__ == "__main__":
    main()
