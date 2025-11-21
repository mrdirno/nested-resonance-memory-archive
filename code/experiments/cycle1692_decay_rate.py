#!/usr/bin/env python3
"""
CYCLE 1692: DECAY RATE EFFECTS
Does optimal N depend on decay rate (currently DECAY_MULT=0.1)?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1692"
CYCLES = 30000
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

def run_experiment(seed, n_initial=25, decay_mult=0.1):
    """Run with variable decay rate."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Variable decay rate
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * decay_mult
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "n_initial": n_initial,
        "decay_mult": decay_mult,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive
    }

def main():
    print(f"CYCLE 1692: Decay Rate | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Does optimal N depend on decay rate?")
    print("=" * 70)

    seeds = list(range(1692001, 1692051))  # 50 seeds

    decay_mults = [0.05, 0.1, 0.15, 0.2, 0.3]
    population_sizes = [20, 25, 30, 35, 50]

    all_results = []

    for decay in decay_mults:
        print(f"\nDecay Mult = {decay}")
        print("-" * 40)

        for n_init in population_sizes:
            results = [run_experiment(seed, n_init, decay) for seed in seeds]
            coexist_count = sum(1 for r in results if r["coexist"])
            success_rate = coexist_count / len(results)
            print(f"  n={n_init:2d}: {success_rate*100:5.0f}%")
            all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY: OPTIMAL N BY DECAY RATE")
    print("=" * 70)
    print(f"\n{'Decay':>8} | {'Optimal N':>10} | {'Success':>10}")
    print("-" * 35)

    for decay in decay_mults:
        best_n = None
        best_rate = 0
        for n_init in population_sizes:
            subset = [r for r in all_results if r["decay_mult"] == decay and r["n_initial"] == n_init]
            success = sum(1 for r in subset if r["coexist"]) / len(subset)
            if success > best_rate:
                best_rate = success
                best_n = n_init
        print(f"{decay:8.2f} | {best_n:10d} | {best_rate*100:9.0f}%")

if __name__ == "__main__":
    main()
