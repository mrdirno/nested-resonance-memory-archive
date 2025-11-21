#!/usr/bin/env python3
"""
CYCLE 1938: BOUNDED POPULATION DYNAMICS

Find reproduction rate p that achieves stable bounded population
while maintaining high coexistence. C1937 showed p=0.17 causes
population explosion (~61 cycles to cap).
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

# OPTIMAL PARAMETERS (except p)
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

def run_simulation(seed, p):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    completed_cycles = 0
    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(pp) for pp in pops)
        if total >= 3000 or total == 0: break
        completed_cycles = cycle + 1

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < p:
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
        'coex': final_pops[0] > 0 and final_pops[1] > 0,
        'cycles': completed_cycles,
        'total': sum(final_pops),
        'bounded': completed_cycles >= CYCLES
    }

def main():
    print(f"CYCLE 1938: Bounded Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Finding p for stable bounded population with high coexistence")
    print("=" * 80)

    seeds = list(range(1938001, 1938031))  # 30 seeds
    p_values = [0.05, 0.08, 0.10, 0.12, 0.14, 0.17]

    print(f"\n{'p':>6} | {'Coex %':>7} | {'Bounded %':>9} | {'Avg Cycles':>10}")
    print("-" * 44)

    results = {}
    for p in p_values:
        res = [run_simulation(s, p) for s in seeds]
        coex = np.mean([r['coex'] for r in res]) * 100
        bounded = np.mean([r['bounded'] for r in res]) * 100
        avg_cycles = np.mean([r['cycles'] for r in res])
        results[p] = {
            'coex': coex,
            'bounded': bounded,
            'avg_cycles': avg_cycles
        }
        print(f"{p:>6.2f} | {coex:>6.1f}% | {bounded:>8.1f}% | {avg_cycles:>10.0f}")

    # Analysis
    print(f"\n{'=' * 80}")
    print("BOUNDED DYNAMICS ANALYSIS")
    print("=' * 80")

    # Find sweet spot: high coex AND high bounded
    best_p = None
    best_score = 0
    for p in p_values:
        score = results[p]['coex'] * results[p]['bounded'] / 100
        if score > best_score:
            best_score = score
            best_p = p

    # Find minimum p for 90% coex
    min_p_90 = None
    for p in sorted(p_values):
        if results[p]['coex'] >= 90:
            min_p_90 = p
            break

    print(f"\nOptimal for bounded + coexistence: p = {best_p}")
    print(f"  Coexistence: {results[best_p]['coex']:.0f}%")
    print(f"  Bounded: {results[best_p]['bounded']:.0f}%")
    print(f"  Score: {best_score:.0f}")

    print(f"\nMinimum p for 90%+ coexistence: {min_p_90}")

    # Characterize trade-off
    print(f"\nTrade-off analysis:")
    print(f"  p=0.17 (optimal): {results[0.17]['coex']:.0f}% coex, {results[0.17]['bounded']:.0f}% bounded")
    if min_p_90:
        print(f"  p={min_p_90} (bounded): {results[min_p_90]['coex']:.0f}% coex, {results[min_p_90]['bounded']:.0f}% bounded")

    print(f"""
CONCLUSION:

Best balanced parameters for bounded dynamics:
  p = {best_p}
  → {results[best_p]['coex']:.0f}% coexistence
  → {results[best_p]['bounded']:.0f}% runs complete 500 cycles

Trade-off:
- Higher p → more coexistence, faster explosion
- Lower p → bounded population, less coexistence

Recommended configurations:
1. Maximum coexistence: p = 0.17 (100% coex, unbounded)
2. Balanced: p = {best_p} ({results[best_p]['coex']:.0f}% coex, {results[best_p]['bounded']:.0f}% bounded)
3. Maximum stability: p = 0.05 ({results[0.05]['coex']:.0f}% coex, {results[0.05]['bounded']:.0f}% bounded)

Session status: 275 cycles completed (C1664-C1938).
""")

if __name__ == "__main__":
    main()
