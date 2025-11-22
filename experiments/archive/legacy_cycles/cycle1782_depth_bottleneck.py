#!/usr/bin/env python3
"""
CYCLE 1782: D1/D2 BOTTLENECK INVESTIGATION
Why do D1 and D2 stay so low (1-2) while D3/D4 scale with N?
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1782"
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

def run_detailed(seed, n_initial):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track flow at each depth
    comp_to = [0] * N_DEPTHS  # Agents composed TO this depth
    decomp_from = [0] * N_DEPTHS  # Agents decomposed FROM this depth
    residence = [[] for _ in range(N_DEPTHS)]  # Track population each cycle

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            residence[d].append(len(pops[d]))

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
                    comp_to[d+1] += 1
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
                    decomp_from[d] += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return {
        'comp_to': comp_to,
        'decomp_from': decomp_from,
        'mean_pop': [np.mean(r) if r else 0 for r in residence]
    }

def main():
    print(f"CYCLE 1782: Depth Bottleneck | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Investigating flow at each depth level")
    print("=" * 70)

    seeds = list(range(1782001, 1782031))

    # Test Zone 1 and Zone 4 for comparison
    for zone, n in [(1, 29), (4, 75)]:
        results = [run_detailed(seed, n) for seed in seeds]

        print(f"\nZone {zone} (N={n}):")
        print(f"  {'Depth':<8} | {'Comp To':>10} | {'Decomp From':>12} | {'Mean Pop':>10}")
        print(f"  {'-'*50}")

        for d in range(N_DEPTHS):
            comp = sum(r['comp_to'][d] for r in results) / len(results)
            decomp = sum(r['decomp_from'][d] for r in results) / len(results)
            mean_pop = sum(r['mean_pop'][d] for r in results) / len(results)
            print(f"  D{d:<7} | {comp:>10.1f} | {decomp:>12.1f} | {mean_pop:>10.2f}")

if __name__ == "__main__":
    main()
