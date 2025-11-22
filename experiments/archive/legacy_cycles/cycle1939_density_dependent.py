#!/usr/bin/env python3
"""
CYCLE 1939: DENSITY-DEPENDENT REPRODUCTION

Test density-dependent reproduction to achieve bounded dynamics:
p_effective = p_base / (1 + total / K)
where K is carrying capacity parameter.
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

    completed_cycles = 0
    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break
        completed_cycles = cycle + 1

        # Density-dependent reproduction probability
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
        'coex': final_pops[0] > 0 and final_pops[1] > 0,
        'cycles': completed_cycles,
        'total': sum(final_pops),
        'bounded': completed_cycles >= CYCLES
    }

def main():
    print(f"CYCLE 1939: Density-Dependent Reproduction | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing p_effective = p_base / (1 + total / K)")
    print("=" * 80)

    seeds = list(range(1939001, 1939031))  # 30 seeds
    K_values = [50, 100, 200, 500, 1000, 2000]

    print(f"\n{'K':>6} | {'Coex %':>7} | {'Bounded %':>9} | {'Avg Pop':>8}")
    print("-" * 40)

    results = {}
    for K in K_values:
        res = [run_simulation(s, K) for s in seeds]
        coex = np.mean([r['coex'] for r in res]) * 100
        bounded = np.mean([r['bounded'] for r in res]) * 100
        avg_pop = np.mean([r['total'] for r in res])
        results[K] = {
            'coex': coex,
            'bounded': bounded,
            'avg_pop': avg_pop
        }
        print(f"{K:>6} | {coex:>6.1f}% | {bounded:>8.1f}% | {avg_pop:>8.0f}")

    # Analysis
    print(f"\n{'=' * 80}")
    print("DENSITY-DEPENDENT ANALYSIS")
    print("=" * 80)

    # Find sweet spot
    best_K = None
    best_score = 0
    for K in K_values:
        score = results[K]['coex'] * results[K]['bounded'] / 100
        if score > best_score:
            best_score = score
            best_K = K

    # Find K for 90%+ coex AND 50%+ bounded
    balanced_K = None
    for K in K_values:
        if results[K]['coex'] >= 90 and results[K]['bounded'] >= 50:
            balanced_K = K
            break

    print(f"\nBest balanced K: {best_K}")
    print(f"  Coexistence: {results[best_K]['coex']:.0f}%")
    print(f"  Bounded: {results[best_K]['bounded']:.0f}%")
    print(f"  Avg population: {results[best_K]['avg_pop']:.0f}")

    if balanced_K:
        print(f"\nK for >=90% coex AND >=50% bounded: {balanced_K}")

    # Compare to C1938
    print(f"\nImprovement over C1938 (fixed p):")
    print(f"  C1938 best: 77% coex, 23% bounded (p=0.05)")
    print(f"  C1939 best: {results[best_K]['coex']:.0f}% coex, {results[best_K]['bounded']:.0f}% bounded (K={best_K})")

    print(f"""
CONCLUSION:

Density-dependent reproduction {'achieves' if best_score > 23 else 'does not achieve'} better balance:
- Best K = {best_K}
- Coexistence: {results[best_K]['coex']:.0f}%
- Bounded: {results[best_K]['bounded']:.0f}%
- Average population: {results[best_K]['avg_pop']:.0f}

Physical mechanism:
- Low population: p ≈ p_base (high reproduction)
- High population: p → p_base × K / total (low reproduction)
- Creates negative feedback for bounded growth

{'This mechanism successfully combines high coexistence with bounded dynamics.' if best_score > 50 else 'Further tuning needed for optimal balance.'}

Session status: 276 cycles completed (C1664-C1939).
""")

if __name__ == "__main__":
    main()
