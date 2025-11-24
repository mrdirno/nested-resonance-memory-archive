#!/usr/bin/env python3
"""
CYCLE 1857C: PHASE TRANSITION VARIANCE TEST

If N=14-15 are phase transitions, they should show:
1. Maximum variance in outcomes
2. Bimodal distribution (some runs in each regime)
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

    d3_to_d4_count = 0

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
                    if d == 3:
                        d3_to_d4_count += 1
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
        'd3_d4': d3_to_d4_count
    }

def main():
    print(f"CYCLE 1857C: Transition Variance Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Phase transitions should show maximum variance")
    print("=" * 80)

    seeds = list(range(1857001, 1857051))  # 50 seeds for variance
    prob = 0.10

    print("\nVariance Analysis:")
    print("-" * 70)
    print(f"{'N':>3} | {'Coex%':>5} | {'Var(D3D4)':>10} | {'StdDev':>8} | Analysis")
    print("-" * 70)

    for n in range(8, 25):
        d3d4_values = []
        coex_count = 0

        for seed in seeds:
            m = run_test(seed, n, prob)
            d3d4_values.append(m['d3_d4'])
            if m['coex']:
                coex_count += 1

        coex_pct = coex_count / len(seeds) * 100
        variance = np.var(d3d4_values)
        std = np.std(d3d4_values)

        analysis = ""
        if n in [14, 15]:
            analysis = " ← TRANSITION"
        elif variance > 1000:
            analysis = " high var"

        print(f"{n:>3} | {coex_pct:>4.0f}% | {variance:>10.1f} | {std:>8.1f} | {analysis}")

    # Summary
    print("\n" + "=" * 80)
    print("VARIANCE INTERPRETATION")
    print("=" * 80)
    print("""
Phase transition signatures:
- Maximum variance at transition points
- Bimodal outcome distribution
- High sensitivity to initial conditions

If N=14-15 are true phase transitions, they should show
higher variance than adjacent N values.
""")

if __name__ == "__main__":
    main()
