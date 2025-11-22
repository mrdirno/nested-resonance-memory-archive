#!/usr/bin/env python3
"""
CYCLE 1912: DECOMPOSITION ANALYSIS

Why is D0+D1 coexistence so low?
Track decomposition vs composition rates.
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

def run_with_tracking(seed, n_initial, repro_prob, init_energy):
    """Track composition and decomposition at each depth."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # Track events by depth
    compositions = {d: 0 for d in range(N_DEPTHS - 1)}
    decompositions = {d: 0 for d in range(1, N_DEPTHS)}

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, init_energy, depth=0), 0)

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
                    decompositions[d] += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    coexist = final_pops[0] > 0 and final_pops[1] > 0

    return {
        'coexist': coexist,
        'compositions': compositions,
        'decompositions': decompositions,
        'final': final_pops
    }

def main():
    print(f"CYCLE 1912: Decomposition Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why is D0+D1 coexistence so low?")
    print("=" * 80)

    seeds = list(range(1912001, 1912031))
    prob = 0.10

    # Test at dead zone (N=14) and threshold (N=17)
    for n in [14, 17]:
        print(f"\n{'='*40}")
        print(f"N = {n}")
        print(f"{'='*40}")

        results = [run_with_tracking(s, n, prob, 1.0) for s in seeds]
        coex_rate = np.mean([r['coexist'] for r in results]) * 100

        print(f"\nCoexistence (D0+D1): {coex_rate:.0f}%")

        # Composition totals
        print(f"\nTotal compositions (avg over {len(seeds)} seeds):")
        for d in range(N_DEPTHS - 1):
            total = np.mean([r['compositions'][d] for r in results])
            print(f"  D{d}→D{d+1}: {total:.1f}")

        # Decomposition totals
        print(f"\nTotal decompositions:")
        for d in range(1, N_DEPTHS):
            total = np.mean([r['decompositions'][d] for r in results])
            print(f"  D{d}→D{d-1}: {total:.1f}")

        # Net flow at each level
        print(f"\nNet flow (comp - decomp):")
        for d in range(1, N_DEPTHS - 1):
            comp_in = np.mean([r['compositions'][d-1] for r in results])
            decomp_out = np.mean([r['decompositions'][d] for r in results])
            comp_out = np.mean([r['compositions'][d] for r in results])
            decomp_in = np.mean([r['decompositions'][d+1] for r in results]) if d < N_DEPTHS - 1 else 0

            net = (comp_in + decomp_in) - (decomp_out + comp_out)
            print(f"  D{d}: {net:+.1f}")

        # Final populations
        print(f"\nFinal populations:")
        for d in range(N_DEPTHS):
            pop = np.mean([r['final'][d] for r in results])
            print(f"  D{d}: {pop:.1f}")

    # Analysis
    print("\n" + "=" * 80)
    print("FLOW ANALYSIS")
    print("=" * 80)

    # Compare D1 composition vs decomposition
    results_14 = [run_with_tracking(s, 14, prob, 1.0) for s in seeds]
    results_17 = [run_with_tracking(s, 17, prob, 1.0) for s in seeds]

    d1_comp_14 = np.mean([r['compositions'][1] for r in results_14])
    d1_decomp_14 = np.mean([r['decompositions'][1] for r in results_14])
    d1_comp_17 = np.mean([r['compositions'][1] for r in results_17])
    d1_decomp_17 = np.mean([r['decompositions'][1] for r in results_17])

    print(f"\nD1 dynamics:")
    print(f"  N=14: {d1_comp_14:.1f} compositions, {d1_decomp_14:.1f} decompositions")
    print(f"  N=17: {d1_comp_17:.1f} compositions, {d1_decomp_17:.1f} decompositions")

    ratio_14 = d1_comp_14 / d1_decomp_14 if d1_decomp_14 > 0 else float('inf')
    ratio_17 = d1_comp_17 / d1_decomp_17 if d1_decomp_17 > 0 else float('inf')

    print(f"\nD1 comp/decomp ratio:")
    print(f"  N=14: {ratio_14:.2f}")
    print(f"  N=17: {ratio_17:.2f}")

    print(f"""
HYPOTHESIS:

At N=14 (dead zone):
- D1 composes to D2 faster than it decomposes to D0
- Flow is upward: D0 → D1 → D2 → D3
- D0 population cannot be replenished

At N=17 (threshold):
- More agents → more reproduction at D0
- D1 decomposes back to D0 effectively
- Flow is balanced or downward

The critical difference is the D0 reproduction rate.
If D0 < threshold, reproduction cannot sustain the population.
""")

if __name__ == "__main__":
    main()
