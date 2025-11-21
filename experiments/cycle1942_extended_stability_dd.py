#!/usr/bin/env python3
"""
CYCLE 1942: EXTENDED STABILITY UNDER DENSITY-DEPENDENT DYNAMICS

Test long-term stability (500, 1000, 2000 cycles) with K=50 to verify
the 98% coexistence rate holds over extended time scales.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

N_DEPTHS = 5
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# COMPLETE OPTIMAL PARAMETERS
P_BASE = 0.17
K = 50
N_INITIAL = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4

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

def run_simulation(seed, max_cycles):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    completed = 0
    for cycle in range(max_cycles):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break
        completed = cycle + 1

        p_effective = P_BASE / (1 + total / K)

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < p_effective:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= COMP_THRESH:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
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
    return {
        'pops': final_pops,
        'coex_4': all(final_pops[i] > 0 for i in range(4)),
        'bounded': completed >= max_cycles,
        'total': sum(final_pops)
    }

def main():
    print(f"CYCLE 1942: Extended Stability (DD) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing long-term stability under density-dependent dynamics (K=50)")
    print("=" * 80)

    seeds = list(range(1942001, 1942031))  # 30 seeds
    cycle_counts = [500, 1000, 2000]

    print(f"\n{'Cycles':>8} | {'D0-D3 %':>8} | {'Bounded %':>9} | {'Avg Pop':>8}")
    print("-" * 44)

    results = {}
    for max_c in cycle_counts:
        res = [run_simulation(s, max_c) for s in seeds]
        coex = np.mean([r['coex_4'] for r in res]) * 100
        bounded = np.mean([r['bounded'] for r in res]) * 100
        avg_pop = np.mean([r['total'] for r in res])
        results[max_c] = {'coex': coex, 'bounded': bounded, 'avg_pop': avg_pop}
        print(f"{max_c:>8} | {coex:>7.1f}% | {bounded:>8.1f}% | {avg_pop:>8.0f}")

    # Analysis
    print(f"\n{'=' * 80}")
    print("EXTENDED STABILITY ANALYSIS")
    print("=" * 80)

    stable = all(results[c]['coex'] >= 90 and results[c]['bounded'] >= 90 for c in cycle_counts)

    print(f"""
LONG-TERM STABILITY: {'CONFIRMED' if stable else 'NOT CONFIRMED'}

Time scale analysis:
- 500 cycles:  {results[500]['coex']:.0f}% coex, {results[500]['bounded']:.0f}% bounded
- 1000 cycles: {results[1000]['coex']:.0f}% coex, {results[1000]['bounded']:.0f}% bounded
- 2000 cycles: {results[2000]['coex']:.0f}% coex, {results[2000]['bounded']:.0f}% bounded

Population equilibrium:
- Avg at 500:  {results[500]['avg_pop']:.0f}
- Avg at 1000: {results[1000]['avg_pop']:.0f}
- Avg at 2000: {results[2000]['avg_pop']:.0f}

{'The density-dependent mechanism maintains stable four-level hierarchy over extended time scales.' if stable else 'Some instability detected at longer time scales.'}

Session status: 279 cycles completed (C1664-C1942).
""")

if __name__ == "__main__":
    main()
