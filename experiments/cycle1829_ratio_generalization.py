#!/usr/bin/env python3
"""
CYCLE 1829: COMPOSITION RATIO GENERALIZATION
Test if composition depth ratio theory applies to N=24 and N=35.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1829"
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

def run_ratio_test(seed, n_initial, repro_prob):
    """Track composition depth ratio"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    comps = [0] * (N_DEPTHS - 1)

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
                    comps[d] += 1
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
    coex = sum(1 for p in final_pops if len(p) > 0) >= 2
    ratio = comps[0] / comps[1] if comps[1] > 0 else float('inf')

    return coex, ratio, comps

def main():
    print(f"CYCLE 1829: Ratio Generalization | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing composition ratio theory on N=24 and N=35")
    print("=" * 80)

    seeds = list(range(1829001, 1829021))  # 20 seeds
    probs = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60, 0.70, 0.80]

    for n in [24, 35]:
        print(f"\n{'='*80}")
        print(f"N={n} COMPOSITION RATIO ANALYSIS")
        print(f"{'='*80}")
        print(f"\n{'Prob':<6} | {'Coex':>6} | {'Ratio':>8} | {'D0→D1':>8} | {'D1→D2':>8} | {'Status':>10}")
        print("-" * 65)

        for prob in probs:
            results = [run_ratio_test(seed, n, prob) for seed in seeds]
            coex = sum(r[0] for r in results) / len(results) * 100
            ratio = np.mean([r[1] for r in results if r[1] != float('inf')])
            c01 = np.mean([r[2][0] for r in results])
            c12 = np.mean([r[2][1] for r in results])

            # Determine status based on N=29 theory
            if ratio < 0.7:
                status = "D0 depl"
            elif ratio > 1.8:
                status = "Bottlenck"
            else:
                status = "Balanced"

            marker = "X" if coex < 70 else ""
            print(f"{prob:<6} | {coex:>5.0f}%{marker} | {ratio:>8.2f} | {c01:>8.0f} | {c12:>8.0f} | {status:>10}")

    # Summary analysis
    print("\n" + "=" * 80)
    print("THEORY VALIDATION SUMMARY")
    print("=" * 80)
    print("\nN=29 theory: Dead zones when ratio < 0.7 or ratio > 1.8")
    print("Test: Does this apply to N=24 and N=35?")

if __name__ == "__main__":
    main()
