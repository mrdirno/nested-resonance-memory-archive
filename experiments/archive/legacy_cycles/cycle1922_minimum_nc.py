#!/usr/bin/env python3
"""
CYCLE 1922: MINIMUM Nc BOUNDARY TEST

C1921 showed Nc = 3.0 for all depths (100% coexistence at N=3).
Test N = 1, 2 to find true minimum coexistence threshold.
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
DECOMP_THRESH = 0.8
COMP_THRESH = 0.99
RECHARGE_BASE = 0.2
REPRO_PROB = 0.17  # Optimal from C1918-C1920

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

def run_optimal(seed, n_initial):
    """Run with optimal parameters."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
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
    return final_pops[0] > 0 and final_pops[1] > 0

def main():
    print(f"CYCLE 1922: Minimum Nc Boundary | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Testing N = 1, 2, 3 at optimal p = {REPRO_PROB}")
    print("=" * 80)

    seeds = list(range(1922001, 1922051))  # 50 seeds

    # Test low N values
    n_values = [1, 2, 3]

    print(f"\n{'N':>4} | {'Coex %':>8} | {'Status':>12}")
    print("-" * 32)

    results = {}
    for n in n_values:
        coex = np.mean([run_optimal(s, n) for s in seeds]) * 100
        results[n] = coex

        if coex >= 50:
            status = "VIABLE"
        else:
            status = "SUB-THRESHOLD"

        print(f"{n:>4} | {coex:>7.1f}% | {status:>12}")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)

    # Find 50% threshold
    if results[1] >= 50:
        nc = 1.0
        print(f"\nMinimum Nc = 1 (100% coexistence even with single agent)")
    elif results[2] >= 50:
        if results[1] < 50:
            nc = 1 + (50 - results[1]) / (results[2] - results[1])
        else:
            nc = 1.0
        print(f"\nNc ≈ {nc:.2f} (interpolated)")
    elif results[3] >= 50:
        nc = 2 + (50 - results[2]) / (results[3] - results[2])
        print(f"\nNc ≈ {nc:.2f} (interpolated)")
    else:
        nc = 3.0  # Above range
        print(f"\nNc > 3 (unexpected given C1921 results)")

    # Interpretation
    print(f"""
CONCLUSION:

Minimum Nc boundary analysis:

1. N=1: {results[1]:.1f}% coexistence
2. N=2: {results[2]:.1f}% coexistence
3. N=3: {results[3]:.1f}% coexistence

True Nc = {nc:.2f}

Physical interpretation:
- N=1: {'Can reproduce and create D1 via decomposition' if results[1] > 0 else 'Cannot create D1'}
- N=2: {'Composition possible, D1 emerges' if results[2] > 50 else 'Insufficient for composition'}
- N=3: {'Robust coexistence' if results[3] >= 50 else 'Still marginal'}

Key insight: At optimal p = {REPRO_PROB}:
- Reproduction can bootstrap from minimal population
- The true minimum is {'surprisingly low' if nc <= 2 else 'at N=' + str(int(np.ceil(nc)))}

Session status: 259 cycles completed (C1664-C1922).
""")

if __name__ == "__main__":
    main()
