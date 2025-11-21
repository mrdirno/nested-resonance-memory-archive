#!/usr/bin/env python3
"""
CYCLE 1901: FINITE-SIZE SCALING

How do phase transition properties scale with system size?
Test if variance peak height scales with N.
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
    print(f"CYCLE 1901: Finite-Size Scaling | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing how variance peak scales with system size")
    print("=" * 80)

    seeds = list(range(1901001, 1901051))  # 50 seeds
    prob = 0.10
    lam = 16 - 13 * prob

    # Test at harmonics k=1, k=2 to compare scaling
    harmonics = {
        1: int(round(lam)),      # ~15
        2: int(round(2 * lam))   # ~29
    }

    print(f"\nAnalyzing variance at critical points")

    results = {}

    for k, nc in harmonics.items():
        # Scan around critical point
        test_range = range(nc - 3, nc + 4)

        variances = []
        for n in test_range:
            outcomes = [1 if run_test(s, n, prob) else 0 for s in seeds]
            var = np.var(outcomes)
            variances.append((n, var))

        # Find peak
        max_n, max_var = max(variances, key=lambda x: x[1])
        results[k] = {'nc': nc, 'max_n': max_n, 'max_var': max_var}

        print(f"\nHarmonic k={k} (Nc={nc}):")
        for n, var in variances:
            marker = "**" if n == max_n else "  "
            print(f"  N={n}: var={var:.4f}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("FINITE-SIZE SCALING ANALYSIS")
    print("=" * 80)

    print(f"\n{'k':>3} | {'Nc':>4} | {'Peak N':>6} | {'Peak Var':>8}")
    print("-" * 35)

    for k in harmonics:
        r = results[k]
        print(f"{k:>3} | {r['nc']:>4} | {r['max_n']:>6} | {r['max_var']:>8.4f}")

    # Check scaling
    var_1 = results[1]['max_var']
    var_2 = results[2]['max_var']

    ratio = var_1 / var_2 if var_2 > 0 else 0

    print(f"\nVariance ratio k=1/k=2: {ratio:.2f}")

    if ratio > 1.2:
        print(f"""
FINITE-SIZE EFFECT DETECTED:

Peak variance is higher at first harmonic than second.
Ratio: {ratio:.2f}

This suggests:
1. Criticality is stronger at lower N
2. Finite-size effects suppress fluctuations
3. System approaches mean-field at large N

Scaling: χ_peak ~ N^(γ/ν) may apply.
""")
    else:
        print("\nVariance similar across harmonics - no clear finite-size effect.")

if __name__ == "__main__":
    main()
