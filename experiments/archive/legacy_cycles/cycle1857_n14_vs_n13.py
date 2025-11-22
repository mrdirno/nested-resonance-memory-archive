#!/usr/bin/env python3
"""
CYCLE 1857: WHY N=14 IS DEAD BUT N=13 IS SAFE

Theory predicts λ ≈ 13, but empirically:
- N=13: 87% (safe)
- N=14: 27% (DEAD)

Investigate the specific difference between these adjacent N values.
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

def run_test_detailed(seed, n_initial, repro_prob):
    """Run test with detailed tracking."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    total_comps_by_depth = [0] * (N_DEPTHS - 1)
    total_decomps_by_depth = [0] * (N_DEPTHS - 1)
    max_pops = [0] * N_DEPTHS
    final_cycle = 0

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        for d in range(N_DEPTHS):
            max_pops[d] = max(max_pops[d], pop_counts[d])

        total = sum(pop_counts)
        if total >= 3000 or total == 0:
            final_cycle = cycle
            break

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
                    total_comps_by_depth[d] += 1
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
                    total_decomps_by_depth[d-1] += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        final_cycle = cycle

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    coex = sum(1 for p in final_pops if p > 0) >= 2

    return {
        'coex': coex,
        'final_cycle': final_cycle,
        'final_pops': final_pops,
        'max_pops': max_pops,
        'comps_by_depth': total_comps_by_depth,
        'decomps_by_depth': total_decomps_by_depth
    }

def main():
    print(f"CYCLE 1857: N=14 vs N=13 Investigation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why is N=14 dead (27%) but N=13 safe (87%)?")
    print("=" * 80)

    seeds = list(range(1857001, 1857031))  # 30 seeds for better statistics
    prob = 0.10

    # Detailed comparison
    for n in [12, 13, 14, 15]:
        print(f"\n{'='*80}")
        print(f"N = {n}")
        print("=" * 80)

        coex_count = 0
        all_comps = [[0] * (N_DEPTHS - 1) for _ in range(len(seeds))]
        all_decomps = [[0] * (N_DEPTHS - 1) for _ in range(len(seeds))]
        all_max_pops = [[0] * N_DEPTHS for _ in range(len(seeds))]

        for i, seed in enumerate(seeds):
            result = run_test_detailed(seed, n, prob)
            if result['coex']:
                coex_count += 1
            all_comps[i] = result['comps_by_depth']
            all_decomps[i] = result['decomps_by_depth']
            all_max_pops[i] = result['max_pops']

        coex_pct = coex_count / len(seeds) * 100

        # Average metrics
        avg_comps = [sum(all_comps[i][d] for i in range(len(seeds))) / len(seeds)
                    for d in range(N_DEPTHS - 1)]
        avg_decomps = [sum(all_decomps[i][d] for i in range(len(seeds))) / len(seeds)
                      for d in range(N_DEPTHS - 1)]
        avg_max_pops = [sum(all_max_pops[i][d] for i in range(len(seeds))) / len(seeds)
                       for d in range(N_DEPTHS)]

        print(f"Coexistence: {coex_pct:.0f}%")
        print(f"\nCompositions by depth (D0→D1, D1→D2, D2→D3, D3→D4):")
        print(f"  {avg_comps[0]:.1f}, {avg_comps[1]:.1f}, {avg_comps[2]:.1f}, {avg_comps[3]:.1f}")
        print(f"\nDecompositions by depth (D1→D0, D2→D1, D3→D2, D4→D3):")
        print(f"  {avg_decomps[0]:.1f}, {avg_decomps[1]:.1f}, {avg_decomps[2]:.1f}, {avg_decomps[3]:.1f}")
        print(f"\nMax populations (D0, D1, D2, D3, D4):")
        print(f"  {avg_max_pops[0]:.1f}, {avg_max_pops[1]:.1f}, {avg_max_pops[2]:.1f}, {avg_max_pops[3]:.1f}, {avg_max_pops[4]:.1f}")

        # Key ratios
        total_comp = sum(avg_comps)
        total_decomp = sum(avg_decomps)
        print(f"\nTotal: {total_comp:.0f} comps, {total_decomp:.0f} decomps, ratio={total_comp/max(total_decomp, 1):.2f}")

    # Number theory analysis
    print("\n" + "=" * 80)
    print("NUMBER THEORY ANALYSIS")
    print("=" * 80)

    for n in [12, 13, 14, 15]:
        # Factors
        factors = [i for i in range(1, n+1) if n % i == 0]
        # Residues mod key numbers
        mod_2 = n % 2
        mod_3 = n % 3
        mod_phi = (n / PHI) % 1

        print(f"\nN={n}:")
        print(f"  Factors: {factors}")
        print(f"  mod 2: {mod_2}, mod 3: {mod_3}")
        print(f"  N/φ = {n/PHI:.3f}, frac = {mod_phi:.3f}")
        print(f"  floor(N/2): {n//2}, N mod 2^3: {n % 8}")

    # The key insight
    print("\n" + "=" * 80)
    print("KEY INSIGHT")
    print("=" * 80)
    print("""
N=13 vs N=14 difference:
- 13 = prime, 14 = 2 × 7
- 13 // 2 = 6 (even number of pairs)
- 14 // 2 = 7 (odd number of pairs)

This affects composition pairing:
- N=13: 6 pairs + 1 leftover → balanced
- N=14: 7 pairs + 0 leftover → all consumed

When all initial agents are consumed by composition,
D0 depletes completely with no "seed" remaining.
""")

if __name__ == "__main__":
    main()
