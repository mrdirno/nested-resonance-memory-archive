#!/usr/bin/env python3
"""
CYCLE 1738: DEPTH DYNAMICS IN DEAD ZONES VS SAFE ZONES
Compare depth structure evolution between N=29 (dead) and N=35 (safe).
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1738"
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

def run_detailed_test(seed, n_initial):
    """Run test and track depth dynamics"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    recharge = 0.1
    repro = 0.1

    # Tracking
    compositions = [0] * (N_DEPTHS - 1)
    decompositions = [0] * (N_DEPTHS - 1)
    depth_history = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)

        # Record depth distribution every 50 cycles
        if cycle % 50 == 0:
            depth_dist = [len(p) for p in pops]
            depth_history.append(depth_dist)

        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro:
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
                    compositions[d] += 1
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
                    decompositions[d-1] += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2
    final_dist = [len(p) for p in final_pops]

    return {
        'coexist': coexist,
        'final_dist': final_dist,
        'compositions': compositions,
        'decompositions': decompositions,
        'depth_history': depth_history
    }

def main():
    print(f"CYCLE 1738: Depth Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Compare depth structure between dead zones and safe zones")
    print("=" * 70)

    seeds = list(range(1738001, 1738021))  # 20 seeds

    test_cases = [
        ("Dead Zone 1", 29),
        ("Safe 1", 35),
        ("Dead Zone 5", 87),
        ("Safe 5", 95),
    ]

    for name, n in test_cases:
        print(f"\n--- {name} (N={n}) ---")

        all_results = [run_detailed_test(seed, n) for seed in seeds]
        coexist = sum(r['coexist'] for r in all_results) / len(all_results) * 100

        # Average compositions
        avg_comp = [sum(r['compositions'][d] for r in all_results) / len(all_results) for d in range(N_DEPTHS-1)]
        avg_decomp = [sum(r['decompositions'][d] for r in all_results) / len(all_results) for d in range(N_DEPTHS-1)]

        # Average final distribution
        avg_final = [sum(r['final_dist'][d] for r in all_results) / len(all_results) for d in range(N_DEPTHS)]

        print(f"Coexistence: {coexist:.0f}%")
        print(f"\nCompositions (D0→D1, D1→D2, D2→D3, D3→D4):")
        print(f"  {avg_comp}")
        print(f"\nDecompositions (D1→D0, D2→D1, D3→D2, D4→D3):")
        print(f"  {avg_decomp}")
        print(f"\nFinal distribution [D0, D1, D2, D3, D4]:")
        print(f"  {avg_final}")

        # Key ratio: D1 decomp / D0→D1 comp
        if avg_comp[0] > 0:
            d1_trap_ratio = avg_decomp[0] / avg_comp[0]
            print(f"\nD1 trap ratio (D1 decomp / D0→D1 comp): {d1_trap_ratio:.2f}")

if __name__ == "__main__":
    main()
