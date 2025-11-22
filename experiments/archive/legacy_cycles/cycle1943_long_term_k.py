#!/usr/bin/env python3
"""
CYCLE 1943: LONG-TERM STABILITY WITH LOWER K

C1942 showed K=50 is metastable - works for 500 cycles but drifts to cap at 1000+.
Test lower K values for true long-term equilibrium.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 1000
N_DEPTHS = 5
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# OPTIMAL PARAMETERS
P_BASE = 0.17
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

def run_simulation(seed, K):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    completed = 0
    for cycle in range(CYCLES):
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
        'coex_4': all(final_pops[i] > 0 for i in range(4)),
        'bounded': completed >= CYCLES,
        'total': sum(final_pops)
    }

def main():
    print(f"CYCLE 1943: Long-Term K | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing lower K for true long-term stability (1000 cycles)")
    print("=" * 80)

    seeds = list(range(1943001, 1943031))  # 30 seeds
    K_values = [20, 25, 30, 35, 40, 45]

    print(f"\n{'K':>4} | {'D0-D3 %':>8} | {'Bounded %':>9} | {'Avg Pop':>8}")
    print("-" * 40)

    results = {}
    for K in K_values:
        res = [run_simulation(s, K) for s in seeds]
        coex = np.mean([r['coex_4'] for r in res]) * 100
        bounded = np.mean([r['bounded'] for r in res]) * 100
        avg_pop = np.mean([r['total'] for r in res])
        results[K] = {'coex': coex, 'bounded': bounded, 'avg_pop': avg_pop}
        print(f"{K:>4} | {coex:>7.1f}% | {bounded:>8.1f}% | {avg_pop:>8.0f}")

    # Find optimal K for 1000 cycles
    best_K = max(K_values, key=lambda k: results[k]['coex'] * results[k]['bounded'])

    # Find K range for 90%+ both metrics
    good_K = [k for k in K_values if results[k]['coex'] >= 90 and results[k]['bounded'] >= 90]

    print(f"\n{'=' * 80}")
    print("LONG-TERM STABILITY ANALYSIS")
    print("=" * 80)

    print(f"""
Best K for 1000 cycles: {best_K}
  D0-D3 coexistence: {results[best_K]['coex']:.0f}%
  Bounded: {results[best_K]['bounded']:.0f}%
  Avg population: {results[best_K]['avg_pop']:.0f}

Safe K range (>=90% both at 1000 cycles): {good_K if good_K else 'None found'}

Comparison:
- K=50 at 500 cycles: 100% coex, 100% bounded (C1941)
- K=50 at 1000 cycles: 100% coex, 0% bounded (C1942)
- K={best_K} at 1000 cycles: {results[best_K]['coex']:.0f}% coex, {results[best_K]['bounded']:.0f}% bounded

{'True long-term equilibrium achieved!' if results[best_K]['bounded'] >= 90 and results[best_K]['coex'] >= 90 else 'Need further adjustment for true long-term stability.'}

Session status: 280 cycles completed (C1664-C1943).
""")

if __name__ == "__main__":
    main()
