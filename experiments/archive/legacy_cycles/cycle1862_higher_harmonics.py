#!/usr/bin/env python3
"""
CYCLE 1862: HIGHER HARMONIC VALIDATION

Standing wave model predicts dead zones at λₖ = k × 14.
Validate λ₄, λ₅, λ₆:
- λ₄ ≈ 56
- λ₅ ≈ 70
- λ₆ ≈ 84
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
    print(f"CYCLE 1862: Higher Harmonic Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Validating λ₄=56, λ₅=70, λ₆=84")
    print("=" * 80)

    seeds = list(range(1862001, 1862031))  # 30 seeds
    prob = 0.10
    lambda1 = 14

    # Scan higher N values
    print("\nHigher harmonic scan (N=50-90):")
    print("-" * 60)

    results = []
    for n in range(50, 91):
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        status = "DEAD" if coex < 70 else "safe"
        results.append((n, coex))

        # Mark harmonics
        harmonic = ""
        for k in [4, 5, 6]:
            if abs(n - k*lambda1) <= 1:
                harmonic = f" ← λ{k}={k*lambda1}"

        if n % 7 == 0 or harmonic:
            print(f"N={n}: {coex:>4.0f}% ({status}){harmonic}")

    # Harmonic validation
    print("\n" + "=" * 80)
    print("HARMONIC VALIDATION")
    print("=" * 80)

    print(f"\nPredicted dead zones (λₖ = k × {lambda1}):")
    print("-" * 50)

    validated = 0
    for k in range(1, 7):
        pred_n = k * lambda1
        found = False
        for n, coex in results:
            if abs(n - pred_n) <= 2:
                status = "VALIDATED" if coex < 75 else "NOT dead"
                print(f"  k={k}: λ{k} = {pred_n} → {coex:.0f}% ({status})")
                if coex < 75:
                    validated += 1
                found = True
                break
        if not found:
            print(f"  k={k}: λ{k} = {pred_n} (outside range)")

    # Anti-node validation
    print("\nPredicted safe zones (N = (k+0.5) × 14):")
    print("-" * 50)

    for k in range(3, 6):
        pred_n = int((k + 0.5) * lambda1)
        for n, coex in results:
            if abs(n - pred_n) <= 1:
                status = "VALIDATED" if coex > 80 else "NOT safe"
                print(f"  k={k}: N = {pred_n} → {coex:.0f}% ({status})")
                break

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    # Find local minima
    minima = []
    for i in range(1, len(results) - 1):
        n, coex = results[i]
        if coex < results[i-1][1] and coex < results[i+1][1] and coex < 80:
            minima.append((n, coex))

    print("\nLocal minima (observed dead zones):")
    for n, coex in minima:
        k = n / lambda1
        print(f"  N={n}: {coex:.0f}% (k = {k:.2f})")

    print(f"\nHarmonic model validation: {validated}/3 higher harmonics confirmed")

if __name__ == "__main__":
    main()
