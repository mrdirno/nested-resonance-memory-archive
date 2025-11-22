#!/usr/bin/env python3
"""
CYCLE 1853: LAMBDA INVARIANCE TEST
Is λ = 14 invariant across different reproduction probabilities?
Testing if the first dead zone shifts with probability.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1853"
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

def run_test(seed, n_initial, repro_prob):
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

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def find_dead_zones(seeds, prob):
    """Find N values with <70% coexistence"""
    dead = []
    for n in range(10, 61, 2):
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        if coex < 70:
            dead.append(n)
    return dead

def main():
    print(f"CYCLE 1853: Lambda Invariance Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Is λ = 14 invariant across reproduction probabilities?")
    print("=" * 80)

    seeds = list(range(1853001, 1853011))  # 10 seeds for speed
    probs = [0.05, 0.10, 0.20, 0.30]

    # Find dead zones at each probability
    print("\nFinding dead zones at different probabilities...")
    print("=" * 80)

    all_dead = {}
    for prob in probs:
        dead = find_dead_zones(seeds, prob)
        all_dead[prob] = dead
        print(f"prob={prob}: Dead zones at N = {dead}")

    # Calculate first dead zone and spacing
    print("\n" + "=" * 80)
    print("FIRST DEAD ZONE AND SPACING")
    print("=" * 80)

    print(f"\n{'Prob':<8} | {'First N':<10} | {'Dead zones'}")
    print("-" * 50)

    for prob in probs:
        dead = all_dead[prob]
        first = dead[0] if dead else None
        print(f"{prob:<8} | {first:<10} | {dead}")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: LAMBDA INVARIANCE")
    print("=" * 80)

    first_zones = [all_dead[p][0] for p in probs if all_dead[p]]
    if first_zones:
        avg_first = np.mean(first_zones)
        std_first = np.std(first_zones)
        print(f"\nFirst dead zone: {avg_first:.1f} ± {std_first:.1f}")
        print(f"Range: {min(first_zones)} to {max(first_zones)}")

        if std_first < 3:
            print("\n** λ = 14 CONFIRMED INVARIANT **")
        else:
            print("\n** λ VARIES WITH PROBABILITY **")

if __name__ == "__main__":
    main()
