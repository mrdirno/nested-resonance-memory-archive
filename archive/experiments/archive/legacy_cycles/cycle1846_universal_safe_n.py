#!/usr/bin/env python3
"""
CYCLE 1846: UNIVERSAL SAFE N VALUES
Finding N values that are safe across all probability ranges.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1846"
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
    print(f"CYCLE 1846: Universal Safe N Values | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Finding N values safe across all probability ranges")
    print("=" * 80)

    seeds = list(range(1846001, 1846016))  # 15 seeds
    probs = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50]

    # Test candidate N values
    n_values = []
    for k in np.arange(0, 6.01, 0.5):
        n = int(round(29 + k * LAMBDA))
        if n not in n_values and n >= 20:
            n_values.append(n)

    # Add some additional candidates
    n_values = sorted(list(set(n_values + [40, 45, 55, 60, 70, 75, 85, 90, 95, 100])))

    # Collect data
    print("\nTesting N values across probabilities...")
    print("=" * 80)

    results = {}
    for n in n_values:
        results[n] = {}
        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
            results[n][prob] = coex

    # Print matrix
    header = f"{'N':<6} | {'k':<6} |"
    for p in probs:
        header += f" {p:<6} |"
    header += " Min | Status"
    print(header)
    print("-" * 90)

    universal_safe = []
    mostly_safe = []

    for n in n_values:
        k = (n - 29) / LAMBDA
        row = f"{n:<6} | {k:<6.2f} |"

        min_coex = 100
        for prob in probs:
            coex = results[n][prob]
            marker = "X" if coex < 70 else " "
            row += f" {coex:>4.0f}{marker} |"
            min_coex = min(min_coex, coex)

        # Classify N value
        if min_coex >= 70:
            status = "UNIVERSAL SAFE"
            universal_safe.append(n)
        elif min_coex >= 60:
            status = "mostly safe"
            mostly_safe.append(n)
        else:
            status = ""

        row += f" {min_coex:>3.0f} | {status}"
        print(row)

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print(f"\nUniversal safe N (≥70% at all probs): {universal_safe}")
    print(f"Mostly safe N (≥60% at all probs): {mostly_safe}")

    # Analyze universal safe N
    if universal_safe:
        print("\n" + "=" * 80)
        print("UNIVERSAL SAFE N ANALYSIS")
        print("=" * 80)

        for n in universal_safe:
            k = (n - 29) / LAMBDA
            k_type = "integer" if abs(k - round(k)) < 0.1 else "half-int" if abs(k % 1 - 0.5) < 0.1 else "other"
            print(f"N={n}: k={k:.2f} ({k_type})")

    # Design recommendation
    print("\n" + "=" * 80)
    print("DESIGN RECOMMENDATION")
    print("=" * 80)

    if universal_safe:
        print(f"\nFor systems that must work at any probability:")
        print(f"Use N ∈ {{{', '.join(map(str, universal_safe))}}}")
    else:
        print("\nNo truly universal safe N found.")
        print("Use probability-specific selection instead.")

if __name__ == "__main__":
    main()
