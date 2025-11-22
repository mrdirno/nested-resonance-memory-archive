#!/usr/bin/env python3
"""
CYCLE 1885: ASYMMETRY MECHANISM

Why is β_above > β_below? (Recovery faster above Nc than below)
Hypothesis: Decomposition is more effective above Nc.
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

def run_with_tracking(seed, n_initial, repro_prob):
    """Track compositions and decompositions."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    total_comps = 0
    total_decomps = 0

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

        # Count compositions
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    total_comps += 1
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Count decompositions
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    total_decomps += 1
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
        'compositions': total_comps,
        'decompositions': total_decomps,
        'ratio': total_decomps / total_comps if total_comps > 0 else 0
    }

def main():
    print(f"CYCLE 1885: Asymmetry Mechanism | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why is β_above > β_below?")
    print("=" * 80)

    seeds = list(range(1885001, 1885051))
    prob = 0.10
    n_c = 14

    # Compare below vs above critical
    test_n = list(range(10, 19))

    print(f"\n{'N':>3} | {'Coex':>5} | {'Comps':>6} | {'Decomps':>7} | {'Ratio':>6}")
    print("-" * 45)

    below_ratios = []
    above_ratios = []

    for n in test_n:
        results = [run_with_tracking(s, n, prob) for s in seeds]

        coex = sum(r['coex'] for r in results) / len(seeds) * 100
        comps = np.mean([r['compositions'] for r in results])
        decomps = np.mean([r['decompositions'] for r in results])
        ratio = np.mean([r['ratio'] for r in results])

        if n < n_c:
            below_ratios.append(ratio)
        elif n > n_c:
            above_ratios.append(ratio)

        print(f"{n:>3} | {coex:>4.0f}% | {comps:>6.0f} | {decomps:>7.0f} | {ratio:>6.3f}")

    # Analysis
    print("\n" + "=" * 80)
    print("ASYMMETRY ANALYSIS")
    print("=" * 80)

    avg_below = np.mean(below_ratios)
    avg_above = np.mean(above_ratios)

    print(f"\nDecomp/Comp ratio:")
    print(f"  Below Nc: {avg_below:.3f}")
    print(f"  Above Nc: {avg_above:.3f}")

    if avg_above > avg_below:
        print(f"""
HYPOTHESIS SUPPORTED:

Above Nc, systems have higher decomposition/composition ratio.
This means more D0 replenishment from decomposition.

Mechanism:
1. More agents → more high-depth agents
2. More decompositions → more D0 return
3. D0 return → better coexistence
4. Result: faster recovery above Nc

This explains why β_above > β_below.
""")
    else:
        print("\nHypothesis not supported. Other mechanism at work.")

if __name__ == "__main__":
    main()
