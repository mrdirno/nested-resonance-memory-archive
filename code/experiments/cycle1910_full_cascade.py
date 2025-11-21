#!/usr/bin/env python3
"""
CYCLE 1910: FULL CASCADE TRACKING

Track ALL depth levels to understand the population cascade.
Also use 500 cycles and 30 seeds to match earlier experiments.
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

def run_full_tracking(seed, n_initial, repro_prob, init_energy):
    """Track all depth populations over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # Track all depths
    history = {d: [] for d in range(N_DEPTHS)}

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, init_energy, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            history[d].append(len(pops[d]))

        # Recharge
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
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

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    # Final state
    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    coexist = 1 if final_pops[0] > 0 and final_pops[1] > 0 else 0

    return {
        'history': history,
        'coexist': coexist,
        'final': final_pops,
        'cycles_run': len(history[0])
    }

def main():
    print(f"CYCLE 1910: Full Cascade | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Track ALL depths with 500 cycles, 30 seeds")
    print("=" * 80)

    seeds = list(range(1910001, 1910031))  # 30 seeds
    prob = 0.10

    # Test configurations
    configs = [
        (13, 0.5), (13, 1.0),
        (14, 0.5), (14, 1.0),
        (15, 0.5), (15, 1.0),
        (16, 0.5), (16, 1.0),
    ]

    print(f"\n{'N':>3} | {'E':>4} | {'Coex%':>6} | {'D0':>6} | {'D1':>6} | {'D2':>6} | {'D3':>6}")
    print("-" * 55)

    results_table = {}
    for n, e in configs:
        results = [run_full_tracking(s, n, prob, e) for s in seeds]
        coex_rate = np.mean([r['coexist'] for r in results]) * 100
        avg_d0 = np.mean([r['final'][0] for r in results])
        avg_d1 = np.mean([r['final'][1] for r in results])
        avg_d2 = np.mean([r['final'][2] for r in results])
        avg_d3 = np.mean([r['final'][3] for r in results])

        print(f"{n:>3} | {e:>4.1f} | {coex_rate:>5.0f}% | {avg_d0:>6.1f} | {avg_d1:>6.1f} | {avg_d2:>6.1f} | {avg_d3:>6.1f}")
        results_table[(n, e)] = {'coex': coex_rate, 'results': results}

    # Analysis: Energy effect
    print("\n" + "=" * 80)
    print("ENERGY EFFECT ANALYSIS")
    print("=" * 80)

    for n in [13, 14, 15, 16]:
        coex_05 = results_table[(n, 0.5)]['coex']
        coex_10 = results_table[(n, 1.0)]['coex']
        diff = coex_05 - coex_10
        effect = "HELPS" if diff > 0 else "HURTS" if diff < 0 else "NEUTRAL"
        print(f"N={n}: E=0.5 {effect} ({coex_05:.0f}% vs {coex_10:.0f}%, diff={diff:+.0f}%)")

    # Detailed cascade analysis for N=14 vs N=15
    print("\n" + "=" * 80)
    print("CASCADE ANALYSIS: N=14 vs N=15 with E=0.5")
    print("=" * 80)

    for n in [14, 15]:
        results = results_table[(n, 0.5)]['results']

        # First 10 cycles population dynamics
        print(f"\nN={n} first 10 cycles (averaged):")
        print(f"{'Cycle':>5} | {'D0':>6} | {'D1':>6} | {'D2':>6} | {'D3':>6}")
        print("-" * 40)

        for c in range(min(10, len(results[0]['history'][0]))):
            d0 = np.mean([r['history'][0][c] if c < len(r['history'][0]) else 0 for r in results])
            d1 = np.mean([r['history'][1][c] if c < len(r['history'][1]) else 0 for r in results])
            d2 = np.mean([r['history'][2][c] if c < len(r['history'][2]) else 0 for r in results])
            d3 = np.mean([r['history'][3][c] if c < len(r['history'][3]) else 0 for r in results])
            print(f"{c:>5} | {d0:>6.1f} | {d1:>6.1f} | {d2:>6.1f} | {d3:>6.1f}")

    print(f"""
FINDINGS:

The energy effect with E=0.5 depends on the interplay between:
1. Immediate composition (depletes D0 → D1)
2. Composition cascade (D1 → D2 → D3...)
3. Decomposition return (D1 → D0, D2 → D1...)
4. Decay at each depth

The critical N is where the upward cascade exceeds
the system's ability to maintain D0 population.
""")

if __name__ == "__main__":
    main()
