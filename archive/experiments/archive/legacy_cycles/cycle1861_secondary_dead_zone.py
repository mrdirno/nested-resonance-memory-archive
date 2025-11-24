#!/usr/bin/env python3
"""
CYCLE 1861: SECONDARY DEAD ZONE AT N≈30

We observed N=30 has lower survival (67%) than neighbors.
Is there a second transition zone at N≈30?

If yes: λ₂ = 2λ₁ (harmonic)?
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
    print(f"CYCLE 1861: Secondary Dead Zone | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Is there a second transition zone at N≈30?")
    print("=" * 80)

    seeds = list(range(1861001, 1861031))  # 30 seeds
    prob = 0.10

    # Detailed scan around N=30
    print("\nDetailed scan N=20 to N=45:")
    print("-" * 60)

    results = []
    for n in range(20, 46):
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        status = "DEAD" if coex < 70 else "safe"

        # Check if local minimum
        marker = ""
        results.append((n, coex))

        print(f"N={n:>2}: {coex:>5.0f}% ({status}){marker}")

    # Find local minima
    print("\n" + "=" * 80)
    print("LOCAL MINIMA ANALYSIS")
    print("=" * 80)

    minima = []
    for i in range(1, len(results) - 1):
        n, coex = results[i]
        prev_coex = results[i-1][1]
        next_coex = results[i+1][1]
        if coex < prev_coex and coex < next_coex:
            minima.append((n, coex))

    print("\nLocal minima (potential dead zones):")
    for n, coex in minima:
        print(f"  N={n}: {coex:.0f}%")

    # Check for harmonic relationship
    lambda1 = 14
    print(f"\nHarmonic analysis (λ₁ = {lambda1}):")
    print("-" * 40)

    for k in range(1, 5):
        harmonic_n = lambda1 * k
        print(f"  k={k}: N = {harmonic_n}", end="")

        # Find closest result
        for n, coex in results:
            if abs(n - harmonic_n) <= 1:
                status = "DEAD" if coex < 70 else "safe"
                print(f" → {coex:.0f}% ({status})")
                break
        else:
            print(" (outside range)")

    # Check Fibonacci multiples
    print("\nFibonacci analysis:")
    print("-" * 40)
    fibs = [8, 13, 21, 34]
    for f in fibs:
        for n, coex in results:
            if n == f:
                status = "DEAD" if coex < 70 else "safe"
                print(f"  F={f}: {coex:.0f}% ({status})")
                break

    # Summary
    print("\n" + "=" * 80)
    print("SECONDARY DEAD ZONE ANALYSIS")
    print("=" * 80)

    # Check if N=28-30 is dead
    n28_30 = [(n, c) for n, c in results if 28 <= n <= 30]
    avg_28_30 = np.mean([c for _, c in n28_30])

    print(f"\nN=28-30 average: {avg_28_30:.0f}%")

    if avg_28_30 < 75:
        print("SECONDARY DEAD ZONE CONFIRMED at N≈28-30")
        print(f"Ratio: 28/14 = 2.0 (harmonic)")
    else:
        print("No clear secondary dead zone")

if __name__ == "__main__":
    main()
