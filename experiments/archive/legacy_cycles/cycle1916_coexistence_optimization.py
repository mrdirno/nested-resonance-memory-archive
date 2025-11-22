#!/usr/bin/env python3
"""
CYCLE 1916: COEXISTENCE OPTIMIZATION

Push parameters to achieve higher coexistence (target: 80%+).
Focus on comp_threshold and explore more extreme values.
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

def run_optimized(seed, n_initial, repro_prob, decomp, comp, recharge):
    """Run with specified parameters."""
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
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)

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
    print(f"CYCLE 1916: Coexistence Optimization | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Target: 80%+ coexistence")
    print("=" * 80)

    seeds = list(range(1916001, 1916031))
    prob = 0.10
    n = 19  # Showed highest coexistence (53%) in C1915

    # Explore extreme composition thresholds
    print("\n1. VERY HIGH COMPOSITION THRESHOLDS (harder to compose)")
    print(f"{'Comp':>5} | {'Coex%':>6}")
    print("-" * 16)

    for comp in [0.90, 0.95, 0.98, 0.99, 0.999]:
        coex = np.mean([run_optimized(s, n, prob, 1.0, comp, 0.2) for s in seeds]) * 100
        print(f"{comp:>5.3f} | {coex:>5.0f}%")

    # Explore very low decomposition threshold
    print("\n2. VERY LOW DECOMPOSITION THRESHOLDS (easier to decompose)")
    print(f"{'Decomp':>6} | {'Coex%':>6}")
    print("-" * 17)

    for decomp in [0.7, 0.8, 0.9, 1.0, 1.1]:
        coex = np.mean([run_optimized(s, n, prob, decomp, 0.99, 0.2) for s in seeds]) * 100
        print(f"{decomp:>6.1f} | {coex:>5.0f}%")

    # Explore higher recharge
    print("\n3. HIGHER RECHARGE RATES")
    print(f"{'Recharge':>8} | {'Coex%':>6}")
    print("-" * 19)

    for recharge in [0.2, 0.3, 0.4, 0.5]:
        coex = np.mean([run_optimized(s, n, prob, 0.9, 0.99, recharge) for s in seeds]) * 100
        print(f"{recharge:>8.1f} | {coex:>5.0f}%")

    # Best combination search
    print("\n" + "=" * 80)
    print("BEST COMBINATION SEARCH")
    print("=" * 80)

    best = None
    best_coex = 0

    for decomp in [0.8, 0.9, 1.0]:
        for comp in [0.95, 0.98, 0.99]:
            for recharge in [0.2, 0.3, 0.4]:
                coex = np.mean([run_optimized(s, n, prob, decomp, comp, recharge) for s in seeds]) * 100
                if coex > best_coex:
                    best_coex = coex
                    best = (decomp, comp, recharge)

    if best:
        print(f"\nBest for N={n}: decomp={best[0]}, comp={best[1]}, recharge={best[2]}")
        print(f"Coexistence: {best_coex:.0f}%")

    # Test best across N range
    if best:
        print("\n" + "=" * 80)
        print(f"BEST PARAMETERS ACROSS N RANGE")
        print(f"decomp={best[0]}, comp={best[1]}, recharge={best[2]}")
        print("=" * 80)

        print(f"\n{'N':>4} | {'Coex%':>6}")
        print("-" * 14)

        for n in [14, 17, 19, 20, 22]:
            coex = np.mean([run_optimized(s, n, prob, best[0], best[1], best[2]) for s in seeds]) * 100
            print(f"{n:>4} | {coex:>5.0f}%")

if __name__ == "__main__":
    main()
