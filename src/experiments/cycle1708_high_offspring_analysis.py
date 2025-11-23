#!/usr/bin/env python3
"""
CYCLE 1708: WHY IS HIGH OFFSPRING RATIO DETRIMENTAL?
Investigate why >65% offspring ratio leads to lower coexistence.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1708"
CYCLES = 1000
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
DECOMP_THRESHOLD = 1.3
RESONANCE_THRESHOLD = 0.5

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

def run_detailed_analysis(seed, n_initial):
    """Track detailed dynamics including D1→D2 compositions."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    original_ids = set()
    for i in range(n_initial):
        agent_id = f"D0_{i}"
        reality.add_agent(FractalAgent(agent_id, 0, 1.0, depth=0), 0)
        original_ids.add(agent_id)

    # Track metrics
    d0_to_d1 = 0
    d1_to_d2 = 0
    d1_decomps = 0
    d1_deaths = 0
    both_offspring = 0
    one_original = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                offspring_id = f"D0_{cycle}_{agent.agent_id[-6:]}"
                reality.add_agent(FractalAgent(offspring_id, 0, 0.5, depth=0), 0)
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

                    if d == 0:
                        d0_to_d1 += 1
                        a1_orig = agents[i].agent_id in original_ids
                        a2_orig = agents[i+1].agent_id in original_ids
                        if not a1_orig and not a2_orig:
                            both_offspring += 1
                        elif a1_orig or a2_orig:
                            one_original += 1
                    elif d == 1:
                        d1_to_d2 += 1

                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Track D1 decompositions
        for agent in list(reality.get_population_agents(1)):
            if agent.energy > DECOMP_THRESHOLD:
                d1_decomps += 1
                ce = agent.energy * 0.45
                for j in range(2):
                    reality.add_agent(FractalAgent(f"D0_{cycle}_{j}", 0, ce, depth=0), 0)
                reality.remove_agent(agent.agent_id, 1)

        for d in range(2, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Track D1 deaths
        for agent in list(reality.get_population_agents(1)):
            decay = 0.02 * (1 + 1 * 0.1) * DECAY_MULT
            if not agent.consume_energy(decay):
                d1_deaths += 1
                reality.remove_agent(agent.agent_id, 1)

        for d in [0] + list(range(2, N_DEPTHS)):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2

    total_comps = d0_to_d1
    offspring_ratio = (one_original + 2*both_offspring) / (2*total_comps) if total_comps > 0 else 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "d0_to_d1": d0_to_d1,
        "d1_to_d2": d1_to_d2,
        "d1_decomps": d1_decomps,
        "d1_deaths": d1_deaths,
        "offspring_ratio": offspring_ratio,
        "d1_survival": (d1_to_d2 / d0_to_d1) if d0_to_d1 > 0 else 0,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1708: High Offspring Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why is high offspring ratio (>65%) detrimental?")
    print("=" * 70)

    seeds = list(range(1708001, 1708031))  # 30 seeds
    population_sizes = [20, 25, 30, 35]

    all_results = []
    for n_init in population_sizes:
        results = [run_detailed_analysis(seed, n_init) for seed in seeds]
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("D1 DYNAMICS BY POPULATION SIZE")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Off%':>6} | {'D0→D1':>7} | {'D1→D2':>7} | {'Decomp':>7} | {'Death':>6} | {'Coexist':>8}")
    print("-" * 65)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_off = np.mean([r["offspring_ratio"] for r in subset])
        avg_d0d1 = np.mean([r["d0_to_d1"] for r in subset])
        avg_d1d2 = np.mean([r["d1_to_d2"] for r in subset])
        avg_dec = np.mean([r["d1_decomps"] for r in subset])
        avg_death = np.mean([r["d1_deaths"] for r in subset])
        coexist = sum(1 for r in subset if r["coexist"]) / len(subset) * 100
        print(f"{n_init:4d} | {avg_off:5.1%} | {avg_d0d1:7.1f} | {avg_d1d2:7.1f} | {avg_dec:7.1f} | {avg_death:6.1f} | {coexist:7.0f}%")

    # D1 survival rate
    print("\n" + "=" * 70)
    print("D1 SURVIVAL ANALYSIS")
    print("=" * 70)
    print(f"\n{'N':>4} | {'D1 Survival':>12} | {'Off%':>6} | {'Coexist':>8}")
    print("-" * 40)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_surv = np.mean([r["d1_survival"] for r in subset])
        avg_off = np.mean([r["offspring_ratio"] for r in subset])
        coexist = sum(1 for r in subset if r["coexist"]) / len(subset) * 100
        print(f"{n_init:4d} | {avg_surv:11.1%} | {avg_off:5.1%} | {coexist:7.0f}%")

if __name__ == "__main__":
    main()
