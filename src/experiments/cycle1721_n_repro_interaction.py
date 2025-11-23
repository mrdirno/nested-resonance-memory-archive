#!/usr/bin/env python3
"""
CYCLE 1721: N-REPRO INTERACTION
Does optimal N depend on reproduction rate?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1721"
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

def run_interaction_test(seed, n_initial, repro):
    """Test N-repro interaction."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    recharge = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro:
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
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2
    return coexist

def main():
    print(f"CYCLE 1721: N-Repro Interaction | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Does optimal N depend on reproduction rate?")
    print("=" * 70)

    seeds = list(range(1721001, 1721041))  # 40 seeds
    repro_vals = [0.05, 0.075, 0.10, 0.125, 0.15]
    n_vals = list(range(20, 41, 5))  # 20, 25, 30, 35, 40

    # Coexistence matrix
    print("\n" + "=" * 70)
    print("COEXISTENCE MATRIX (N × Repro)")
    print("=" * 70)

    # Header
    header = f"{'N':>4} |"
    for repro in repro_vals:
        header += f" {repro:.3f} |"
    print(header)
    print("-" * (7 + 8 * len(repro_vals)))

    # Find optimal N for each repro
    optimal_n = {}

    for n in n_vals:
        row = f"{n:4d} |"
        for repro in repro_vals:
            results = [run_interaction_test(seed, n, repro) for seed in seeds]
            coexist = sum(results) / len(results) * 100
            row += f" {coexist:5.0f}% |"

            # Track optimal
            if repro not in optimal_n or coexist > optimal_n[repro][1]:
                optimal_n[repro] = (n, coexist)

        print(row)

    # Show optimal N per repro
    print("\n" + "=" * 70)
    print("OPTIMAL N BY REPRO")
    print("=" * 70)
    print(f"\n{'Repro':>6} | {'Optimal N':>10} | {'Coexist':>8}")
    print("-" * 30)
    for repro in repro_vals:
        n, coex = optimal_n[repro]
        print(f"{repro:6.3f} | {n:10d} | {coex:7.0f}%")

    # Test if N*repro is constant
    print("\n" + "=" * 70)
    print("N × REPRO PRODUCT")
    print("=" * 70)
    products = []
    for repro in repro_vals:
        n, _ = optimal_n[repro]
        product = n * repro
        products.append(product)
        print(f"Repro={repro}: N={n}, N×repro={product:.2f}")

    avg_product = np.mean(products)
    std_product = np.std(products)
    print(f"\nMean product: {avg_product:.2f} ± {std_product:.2f}")

if __name__ == "__main__":
    main()
