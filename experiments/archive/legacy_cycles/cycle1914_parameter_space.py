#!/usr/bin/env python3
"""
CYCLE 1914: PARAMETER SPACE EXPLORATION

Find parameters that allow D0+D1 coexistence.
Test: decomposition threshold, composition threshold, recharge rate.
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

def run_with_params(seed, n_initial, repro_prob, decomp_thresh, comp_thresh, recharge_base):
    """Run with modified parameters."""
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
                agent.recharge_energy(recharge_base / (1 + d * 0.5), cap=2.0)

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
                if sim >= comp_thresh:  # Modified composition threshold
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:  # Modified decomposition threshold
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
    print(f"CYCLE 1914: Parameter Space | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Finding parameters for D0+D1 coexistence")
    print("=" * 80)

    seeds = list(range(1914001, 1914021))  # 20 seeds
    prob = 0.10
    n = 14  # Dead zone

    # Default values
    default_decomp = 1.3
    default_comp = 0.5
    default_recharge = 0.1

    # Test 1: Decomposition threshold
    print("\n1. DECOMPOSITION THRESHOLD (higher = easier decomp)")
    print(f"{'Threshold':>10} | {'Coex%':>6}")
    print("-" * 22)

    for thresh in [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
        coex = np.mean([run_with_params(s, n, prob, thresh, default_comp, default_recharge) for s in seeds]) * 100
        print(f"{thresh:>10.1f} | {coex:>5.0f}%")

    # Test 2: Composition threshold
    print("\n2. COMPOSITION THRESHOLD (higher = harder composition)")
    print(f"{'Threshold':>10} | {'Coex%':>6}")
    print("-" * 22)

    for thresh in [0.3, 0.5, 0.7, 0.8, 0.9]:
        coex = np.mean([run_with_params(s, n, prob, default_decomp, thresh, default_recharge) for s in seeds]) * 100
        print(f"{thresh:>10.1f} | {coex:>5.0f}%")

    # Test 3: Recharge rate
    print("\n3. RECHARGE RATE (higher = faster recharge)")
    print(f"{'Rate':>10} | {'Coex%':>6}")
    print("-" * 22)

    for rate in [0.05, 0.10, 0.15, 0.20, 0.30]:
        coex = np.mean([run_with_params(s, n, prob, default_decomp, default_comp, rate) for s in seeds]) * 100
        print(f"{rate:>10.2f} | {coex:>5.0f}%")

    # Combined parameter search
    print("\n" + "=" * 80)
    print("COMBINED PARAMETER SEARCH")
    print("=" * 80)

    best = None
    best_coex = 0

    # Promising combinations
    for decomp in [1.0, 1.1]:  # Lower = easier decomp
        for comp in [0.7, 0.8, 0.9]:  # Higher = harder comp
            for recharge in [0.15, 0.20]:  # Higher = faster recharge
                coex = np.mean([run_with_params(s, n, prob, decomp, comp, recharge) for s in seeds]) * 100
                if coex > best_coex:
                    best_coex = coex
                    best = (decomp, comp, recharge)
                if coex > 0:
                    print(f"  decomp={decomp}, comp={comp}, recharge={recharge}: {coex:.0f}%")

    if best:
        print(f"\nBest: decomp={best[0]}, comp={best[1]}, recharge={best[2]}: {best_coex:.0f}%")
    else:
        print("\nNo configuration achieved > 0% coexistence")

    print(f"""
CONCLUSION:

The parameter space has been explored for N=14 at p=0.10.
If coexistence > 0% is found, those parameters enable D0+D1 persistence.
If not, the system fundamentally favors upward cascade.
""")

if __name__ == "__main__":
    main()
