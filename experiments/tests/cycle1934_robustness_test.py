#!/usr/bin/env python3
"""
CYCLE 1934: ROBUSTNESS TEST

Test sensitivity of optimal parameters to perturbations.
How much can each parameter deviate while maintaining >90% coexistence?
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

# OPTIMAL PARAMETERS (baseline)
OPT_P = 0.17
OPT_N = 14
OPT_COMP = 0.99
OPT_DECOMP = 1.7
OPT_RECHARGE = 0.4

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

def run_simulation(seed, p=OPT_P, n=OPT_N, comp=OPT_COMP, decomp=OPT_DECOMP, recharge=OPT_RECHARGE):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(n):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)
    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(pp) for pp in pops)
        if total >= 3000 or total == 0: break
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)
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
                if sim >= comp:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp:
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
    return final_pops[0] > 0 and final_pops[1] > 0

def main():
    print(f"CYCLE 1934: Robustness Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing parameter sensitivity around optimal values")
    print("=" * 80)

    seeds = list(range(1934001, 1934031))  # 30 seeds per test

    # Test each parameter with perturbations
    tests = {
        'p': [0.10, 0.12, 0.14, 0.17, 0.20, 0.22, 0.25],
        'N': [5, 8, 10, 14, 18, 22, 26],
        'comp': [0.90, 0.93, 0.96, 0.99, 0.995, 0.999],
        'decomp': [1.0, 1.2, 1.4, 1.7, 1.8, 1.85],
        'recharge': [0.2, 0.25, 0.3, 0.4, 0.5, 0.6]
    }

    results = {}

    print(f"\nTesting {sum(len(v) for v in tests.values())} parameter variations...")
    print()

    # Test p
    print("p (reproduction probability):")
    for p in tests['p']:
        coex = np.mean([run_simulation(s, p=p) for s in seeds]) * 100
        results[('p', p)] = coex
        marker = '***' if p == OPT_P else ('---' if coex < 90 else '')
        print(f"  {p:.2f}: {coex:.1f}% {marker}")

    # Test N
    print("\nN (initial population):")
    for n in tests['N']:
        coex = np.mean([run_simulation(s, n=n) for s in seeds]) * 100
        results[('N', n)] = coex
        marker = '***' if n == OPT_N else ('---' if coex < 90 else '')
        print(f"  {n:>2}: {coex:.1f}% {marker}")

    # Test comp
    print("\ncomp_thresh (composition threshold):")
    for comp in tests['comp']:
        coex = np.mean([run_simulation(s, comp=comp) for s in seeds]) * 100
        results[('comp', comp)] = coex
        marker = '***' if comp == OPT_COMP else ('---' if coex < 90 else '')
        print(f"  {comp:.3f}: {coex:.1f}% {marker}")

    # Test decomp
    print("\ndecomp_thresh (decomposition threshold):")
    for decomp in tests['decomp']:
        coex = np.mean([run_simulation(s, decomp=decomp) for s in seeds]) * 100
        results[('decomp', decomp)] = coex
        marker = '***' if decomp == OPT_DECOMP else ('---' if coex < 90 else '')
        print(f"  {decomp:.2f}: {coex:.1f}% {marker}")

    # Test recharge
    print("\nrecharge_base (energy recharge):")
    for recharge in tests['recharge']:
        coex = np.mean([run_simulation(s, recharge=recharge) for s in seeds]) * 100
        results[('recharge', recharge)] = coex
        marker = '***' if recharge == OPT_RECHARGE else ('---' if coex < 90 else '')
        print(f"  {recharge:.2f}: {coex:.1f}% {marker}")

    # Analysis
    print(f"\n{'=' * 80}")
    print("ROBUSTNESS ANALYSIS")
    print("=' * 80")

    # Find safe ranges (>90%)
    safe_ranges = {}
    for param in tests:
        values = tests[param]
        safe = [v for v in values if results[(param, v)] >= 90]
        if safe:
            safe_ranges[param] = (min(safe), max(safe))
        else:
            safe_ranges[param] = None

    print("\nSAFE OPERATING RANGES (>90% coexistence):")
    for param in tests:
        if safe_ranges[param]:
            lo, hi = safe_ranges[param]
            print(f"  {param}: [{lo}, {hi}]")
        else:
            print(f"  {param}: NO SAFE RANGE")

    # Identify most sensitive parameter
    sensitivities = {}
    for param in tests:
        values = tests[param]
        coexs = [results[(param, v)] for v in values]
        sensitivities[param] = max(coexs) - min(coexs)

    most_sensitive = max(sensitivities, key=sensitivities.get)
    print(f"\nMost sensitive parameter: {most_sensitive} (range: {sensitivities[most_sensitive]:.1f}%)")

    print(f"""
CONCLUSION:

The optimal parameter set is {'robust' if all(safe_ranges.values()) else 'fragile'}:
{chr(10).join(f"- {p}: safe in [{safe_ranges[p][0]}, {safe_ranges[p][1]}]" if safe_ranges[p] else f"- {p}: sensitive" for p in tests)}

Critical sensitivities:
- {most_sensitive} has largest effect ({sensitivities[most_sensitive]:.1f}% range)
- Parameters ranked by sensitivity: {', '.join(sorted(sensitivities, key=sensitivities.get, reverse=True))}

Session status: 271 cycles completed (C1664-C1934).
""")

if __name__ == "__main__":
    main()
