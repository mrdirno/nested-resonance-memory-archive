#!/usr/bin/env python3
"""
CYCLE 1857B: D4 DEAD-END HYPOTHESIS

Hypothesis: N=14 is dead because it pushes agents to D4, where:
1. No higher depth to compose to
2. High decay rate
3. Decomposition returns to D3 (not back to D0)

Test: Compare D4 activity at N=12-15 and correlation with coexistence.
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

def run_test_d4_focus(seed, n_initial, repro_prob):
    """Track D4 specific metrics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    d4_cycles = 0  # How many cycles have D4 population
    d4_total = 0   # Total D4 agent-cycles
    d3_to_d4 = 0   # Compositions into D4

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        d4_count = len(pops[4])

        if d4_count > 0:
            d4_cycles += 1
            d4_total += d4_count

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
                    if d == 3:  # D3→D4
                        d3_to_d4 += 1
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
    coex = sum(1 for p in final_pops if p > 0) >= 2

    return {
        'coex': coex,
        'd4_cycles': d4_cycles,
        'd4_total': d4_total,
        'd3_to_d4': d3_to_d4
    }

def main():
    print(f"CYCLE 1857B: D4 Dead-End Hypothesis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing: Does D4 accumulation explain N=14 failure?")
    print("=" * 80)

    seeds = list(range(1857001, 1857031))
    prob = 0.10

    print("\nD4 Activity Analysis:")
    print("-" * 70)
    print(f"{'N':>3} | {'Coex':>5} | {'D4_cyc':>7} | {'D4_tot':>7} | {'D3→D4':>6} | Analysis")
    print("-" * 70)

    results = []
    for n in range(8, 25):
        d4_cycles_total = 0
        d4_total_total = 0
        d3_to_d4_total = 0
        coex_count = 0

        for seed in seeds:
            m = run_test_d4_focus(seed, n, prob)
            d4_cycles_total += m['d4_cycles']
            d4_total_total += m['d4_total']
            d3_to_d4_total += m['d3_to_d4']
            if m['coex']:
                coex_count += 1

        avg_d4_cyc = d4_cycles_total / len(seeds)
        avg_d4_tot = d4_total_total / len(seeds)
        avg_d3_d4 = d3_to_d4_total / len(seeds)
        coex_pct = coex_count / len(seeds) * 100

        analysis = ""
        if avg_d3_d4 > 40:
            analysis = "HIGH D4!"
        elif coex_pct < 70:
            analysis = "dead"

        marker = " ← λ" if n == 14 else ""
        print(f"{n:>3} | {coex_pct:>4.0f}% | {avg_d4_cyc:>7.0f} | {avg_d4_tot:>7.0f} | {avg_d3_d4:>6.1f} | {analysis}{marker}")

        results.append({'n': n, 'coex': coex_pct, 'd3_d4': avg_d3_d4})

    # Correlation analysis
    print("\n" + "=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80)

    # Check if high D3→D4 correlates with dead zones
    coex_vals = [r['coex'] for r in results]
    d3d4_vals = [r['d3_d4'] for r in results]

    corr = np.corrcoef(coex_vals, d3d4_vals)[0, 1]
    print(f"\nCorrelation(Coex, D3→D4): {corr:.3f}")

    if corr < -0.3:
        print("NEGATIVE correlation: More D4 activity → Lower survival")
    elif corr > 0.3:
        print("POSITIVE correlation: More D4 activity → Higher survival")
    else:
        print("WEAK correlation: D4 activity doesn't explain pattern")

    # Threshold analysis
    dead_zones = [r for r in results if r['coex'] < 70]
    safe_zones = [r for r in results if r['coex'] >= 70]

    avg_d4_dead = np.mean([r['d3_d4'] for r in dead_zones]) if dead_zones else 0
    avg_d4_safe = np.mean([r['d3_d4'] for r in safe_zones]) if safe_zones else 0

    print(f"\nDead zones average D3→D4: {avg_d4_dead:.1f}")
    print(f"Safe zones average D3→D4: {avg_d4_safe:.1f}")

if __name__ == "__main__":
    main()
