#!/usr/bin/env python3
"""
CYCLE 1877: RUN LENGTH ANALYSIS

Does 500 cycles capture steady state? Or do longer runs show different behavior?
Test: 500, 1000, 2000 cycles at key N values
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

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

def run_test(seed, n_initial, repro_prob, max_cycles):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(max_cycles):
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
    return sum(1 for p in final_pops if p > 0) >= 2

def main():
    print(f"CYCLE 1877: Run Length Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Is 500 cycles sufficient for steady state?")
    print("=" * 80)

    seeds = list(range(1877001, 1877031))  # 30 seeds
    prob = 0.10

    cycle_lengths = [500, 1000, 2000]
    test_n = [14, 21, 28]  # Dead, safe, dead

    results = []

    for n in test_n:
        zone_type = "DEAD" if n in [14, 28] else "SAFE"
        print(f"\n{'='*60}")
        print(f"N = {n} ({zone_type})")
        print("=" * 60)
        print(f"{'Cycles':>7} | {'Coex %':>7} | {'Change':>7}")
        print("-" * 30)

        prev_coex = None
        for cycles in cycle_lengths:
            coex_count = sum(run_test(s, n, prob, cycles) for s in seeds)
            coex_pct = coex_count / len(seeds) * 100

            if prev_coex is not None:
                change = coex_pct - prev_coex
                change_str = f"{change:+.1f}%"
            else:
                change_str = "-"

            results.append({
                'n': n, 'cycles': cycles, 'coex': coex_pct
            })

            print(f"{cycles:>7} | {coex_pct:>6.0f}% | {change_str:>7}")
            prev_coex = coex_pct

    # Analysis
    print("\n" + "=" * 80)
    print("RUN LENGTH ANALYSIS")
    print("=" * 80)

    # Check stability
    stable = True
    for n in test_n:
        n_results = [r for r in results if r['n'] == n]
        coex_values = [r['coex'] for r in n_results]
        variance = np.var(coex_values)
        if variance > 25:  # >5% change
            stable = False
            print(f"\nN={n}: NOT stable (variance = {variance:.1f})")
        else:
            print(f"\nN={n}: Stable (variance = {variance:.1f})")

    if stable:
        print("""
CONCLUSION: 500 cycles is SUFFICIENT

Results are stable across 500, 1000, 2000 cycles.
Steady state is reached well before 500 cycles.
Current experimental design is valid.
""")
    else:
        print("""
CONCLUSION: 500 cycles may be INSUFFICIENT

Results vary significantly with run length.
Consider increasing default CYCLES for future experiments.
""")

if __name__ == "__main__":
    main()
