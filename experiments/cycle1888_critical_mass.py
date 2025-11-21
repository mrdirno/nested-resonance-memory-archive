#!/usr/bin/env python3
"""
CYCLE 1888: CRITICAL MASS THRESHOLD HYPOTHESIS

Why is β_above > β_below? (Recovery faster above Nc than below)
Hypothesis: Above Nc, systems reach critical mass threshold ensuring stability.

From C1887: Cross-seed variance lower above Nc (more predictable outcomes).
This suggests a threshold effect - once N exceeds some value, success is nearly certain.
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

def run_with_threshold(seed, n_initial, repro_prob):
    """Track when/if system reaches stability threshold."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # Track population at key cycles
    pop_at_10 = 0
    pop_at_50 = 0
    pop_at_100 = 0
    max_d1_plus = 0  # Max agents at depth >= 1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Record populations
        if cycle == 10:
            pop_at_10 = total
        if cycle == 50:
            pop_at_50 = total
        if cycle == 100:
            pop_at_100 = total

        # Track higher depth population
        d1_plus = sum(len(pops[d]) for d in range(1, N_DEPTHS))
        max_d1_plus = max(max_d1_plus, d1_plus)

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
    coex = sum(1 for p in final_pops if p > 0) >= 2

    return {
        'coex': coex,
        'pop_10': pop_at_10,
        'pop_50': pop_at_50,
        'pop_100': pop_at_100,
        'max_d1_plus': max_d1_plus
    }

def main():
    print(f"CYCLE 1888: Critical Mass Threshold | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: Above Nc, early population reaches threshold ensuring success")
    print("=" * 80)

    seeds = list(range(1888001, 1888051))
    prob = 0.10
    n_c = 14

    test_n = list(range(10, 19))

    print(f"\n{'N':>3} | {'Coex':>5} | {'P@10':>5} | {'P@50':>5} | {'P@100':>6} | {'MaxD1+':>6}")
    print("-" * 55)

    # Collect data for threshold analysis
    pop_10_coex = []
    pop_10_fail = []

    for n in test_n:
        results = [run_with_threshold(s, n, prob) for s in seeds]

        coex = sum(r['coex'] for r in results) / len(seeds) * 100
        avg_p10 = np.mean([r['pop_10'] for r in results])
        avg_p50 = np.mean([r['pop_50'] for r in results])
        avg_p100 = np.mean([r['pop_100'] for r in results])
        avg_d1 = np.mean([r['max_d1_plus'] for r in results])

        # Separate by outcome
        for r in results:
            if r['coex']:
                pop_10_coex.append(r['pop_10'])
            else:
                pop_10_fail.append(r['pop_10'])

        marker = "**" if n == n_c else "  "
        print(f"{n:>3} | {coex:>4.0f}% | {avg_p10:>5.1f} | {avg_p50:>5.1f} | {avg_p100:>6.1f} | {avg_d1:>6.1f}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("ASYMMETRY ANALYSIS: Critical Mass Threshold")
    print("=" * 80)

    # Find threshold
    mean_coex = np.mean(pop_10_coex) if pop_10_coex else 0
    mean_fail = np.mean(pop_10_fail) if pop_10_fail else 0

    print(f"\nPopulation at cycle 10 by outcome:")
    print(f"  Coexistence: {mean_coex:.1f}")
    print(f"  Failure: {mean_fail:.1f}")

    if mean_coex > mean_fail and len(pop_10_coex) > 0 and len(pop_10_fail) > 0:
        # Estimate threshold
        threshold = (mean_coex + mean_fail) / 2
        print(f"\nEstimated threshold: ~{threshold:.1f} agents at cycle 10")

        print(f"""
HYPOTHESIS SUPPORTED:

Systems that achieve coexistence have higher early population ({mean_coex:.1f} vs {mean_fail:.1f}).

Mechanism:
1. Initial N determines trajectory
2. Above Nc, more likely to cross critical mass by cycle 10
3. Once crossed, stability is nearly certain
4. Below Nc, fewer systems cross threshold
5. Result: Steeper recovery curve above Nc

The asymmetry (β_above > β_below) reflects this threshold effect:
- Below: Gradual approach to threshold (slow)
- Above: Many systems already above threshold (fast)
""")
    else:
        print("\nNo clear threshold effect detected.")

    # Check predictability relationship
    print("\n" + "-" * 50)
    print("Threshold as predictor of outcome")
    print("-" * 50)

    # Calculate separation
    if len(pop_10_coex) > 0 and len(pop_10_fail) > 0:
        separation = abs(mean_coex - mean_fail) / (np.std(pop_10_coex + pop_10_fail) + 0.001)
        print(f"Separation score: {separation:.2f}")
        if separation > 1:
            print("Strong separation - early population strongly predicts outcome")
        else:
            print("Weak separation - other factors matter")

if __name__ == "__main__":
    main()
