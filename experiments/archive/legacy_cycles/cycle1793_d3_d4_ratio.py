#!/usr/bin/env python3
"""
CYCLE 1793: D3/D4 RATIO ANALYSIS
The D3/D4 ratio determines coexistence quality.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1793"
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

def run_test(seed, n_initial):
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
            if agent.energy > 1.0 and np.random.random() < 0.1:
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
    coexist = sum(1 for p in final_pops if p > 0) >= 2
    d3 = final_pops[3]
    d4 = final_pops[4]
    ratio = d3 / d4 if d4 > 0 else float('inf')

    return {'coexist': coexist, 'd3': d3, 'd4': d4, 'ratio': ratio}

def main():
    print(f"CYCLE 1793: D3/D4 Ratio | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Analyzing D3/D4 ratio across N values")
    print("=" * 70)

    seeds = list(range(1793001, 1793031))

    print(f"\n{'N':<6} | {'Coexist':>8} | {'D3':>6} | {'D4':>6} | {'Ratio':>8}")
    print("-" * 45)

    for n in range(25, 81, 5):
        results = [run_test(seed, n) for seed in seeds]
        coexist = sum(r['coexist'] for r in results) / len(results) * 100
        avg_d3 = sum(r['d3'] for r in results) / len(results)
        avg_d4 = sum(r['d4'] for r in results) / len(results)

        # Calculate ratio from averages
        ratio = avg_d3 / avg_d4 if avg_d4 > 0.1 else float('inf')

        marker = " ***" if ratio > 5 else ""
        if ratio == float('inf'):
            print(f"{n:<6} | {coexist:>7.0f}% | {avg_d3:>6.1f} | {avg_d4:>6.1f} | {'inf':>8}{marker}")
        else:
            print(f"{n:<6} | {coexist:>7.0f}% | {avg_d3:>6.1f} | {avg_d4:>6.1f} | {ratio:>8.1f}{marker}")

if __name__ == "__main__":
    main()
