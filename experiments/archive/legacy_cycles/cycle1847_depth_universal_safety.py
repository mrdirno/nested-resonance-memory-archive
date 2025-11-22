#!/usr/bin/env python3
"""
CYCLE 1847: DEPTH-DEPENDENT UNIVERSAL SAFETY
Does the N ≥ 55 threshold hold across different depth configurations?
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1847"
CYCLES = 500

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

def run_test(seed, n_initial, repro_prob, n_depths):
    reality = RealityInterface(n_populations=n_depths, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(n_depths)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(n_depths):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(n_depths - 1):
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

        for d in range(1, n_depths):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(n_depths):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(n_depths)]
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def main():
    print(f"CYCLE 1847: Depth-Dependent Universal Safety | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing if N ≥ 55 is universally safe across different depths")
    print("=" * 80)

    seeds = list(range(1847001, 1847016))  # 15 seeds
    depths = [4, 5, 6, 7]
    probs = [0.10, 0.30, 0.50]

    # Test key N values: dangerous (29, 43) and safe (55, 75, 90)
    n_values = [29, 43, 55, 75, 90]

    # Build matrix
    print("\nTesting N values across depths and probabilities...")
    print("=" * 80)

    for n in n_values:
        k = (n - 29) / LAMBDA
        print(f"\nN={n} (k={k:.2f})")
        print("-" * 60)

        header = f"{'Depth':<6} |"
        for p in probs:
            header += f" p={p:<5} |"
        header += " Min"
        print(header)
        print("-" * 40)

        for depth in depths:
            row = f"{depth}D     |"
            min_coex = 100

            for prob in probs:
                coex = sum(run_test(seed, n, prob, depth) for seed in seeds) / len(seeds) * 100
                marker = "X" if coex < 70 else " "
                row += f" {coex:>4.0f}{marker} |"
                min_coex = min(min_coex, coex)

            status = "SAFE" if min_coex >= 70 else ""
            row += f" {min_coex:>3.0f}% {status}"
            print(row)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: UNIVERSAL SAFETY BY N VALUE")
    print("=" * 80)

    print(f"\n{'N':<6} | {'4D':<6} | {'5D':<6} | {'6D':<6} | {'7D':<6} | {'Status'}")
    print("-" * 50)

    for n in n_values:
        row = f"{n:<6} |"

        all_safe = True
        for depth in depths:
            min_coex = 100
            for prob in probs:
                coex = sum(run_test(seed, n, prob, depth) for seed in seeds) / len(seeds) * 100
                min_coex = min(min_coex, coex)

            status = "safe" if min_coex >= 70 else "DEAD"
            row += f" {status:<6} |"
            if min_coex < 70:
                all_safe = False

        universal = "UNIVERSAL" if all_safe else ""
        row += f" {universal}"
        print(row)

    # Confirm threshold
    print("\n" + "=" * 80)
    print("THRESHOLD CONFIRMATION")
    print("=" * 80)

    print("\nN ≥ 55 universal safety:")
    for n in [55, 75, 90]:
        k = (n - 29) / LAMBDA
        safe_count = 0
        total = 0
        for depth in depths:
            for prob in probs:
                coex = sum(run_test(seed, n, prob, depth) for seed in seeds) / len(seeds) * 100
                if coex >= 70:
                    safe_count += 1
                total += 1
        print(f"  N={n}: {safe_count}/{total} configurations safe ({safe_count/total*100:.0f}%)")

if __name__ == "__main__":
    main()
