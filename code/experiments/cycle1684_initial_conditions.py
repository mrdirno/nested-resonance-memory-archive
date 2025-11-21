#!/usr/bin/env python3
"""
CYCLE 1684: INITIAL CONDITIONS ANALYSIS
Why does n=25 achieve success conditions 96% vs n=30 at 42%?
Track the very first cycles (0-50) to understand early dynamics.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1684"
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

def run_experiment(seed, n_initial=100):
    """Track early cycles in detail."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    # Track early dynamics in detail
    first_comp_cycle = -1
    first_d1_cycle = -1
    comps_by_10 = 0
    low_e_by_10 = 0
    d0_energy_at_5 = []  # Energy distribution at cycle 5
    d0_pop_at_10 = 0
    d1_at_10 = 0
    d1_at_50 = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track at specific early cycles
        if cycle == 5:
            d0_energy_at_5 = [a.energy for a in pops[0]]
        if cycle == 10:
            d0_pop_at_10 = len(pops[0])
            d1_at_10 = len(pops[1])
        if cycle == 50:
            d1_at_50 = len(pops[1])

        # Track first D1
        if first_d1_cycle == -1 and len(pops[1]) > 0:
            first_d1_cycle = cycle

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition with early tracking
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
                        if first_comp_cycle == -1:
                            first_comp_cycle = cycle
                        if cycle <= 10:
                            comps_by_10 += 1
                            if new_e < DECOMP_THRESHOLD:
                                low_e_by_10 += 1
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    # Compute energy stats at cycle 5
    if d0_energy_at_5:
        e_mean = np.mean(d0_energy_at_5)
        e_std = np.std(d0_energy_at_5)
        e_cv = e_std / e_mean if e_mean > 0 else 0  # Coefficient of variation
    else:
        e_mean = e_std = e_cv = 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "first_comp_cycle": first_comp_cycle,
        "first_d1_cycle": first_d1_cycle,
        "comps_by_10": comps_by_10,
        "low_e_by_10": low_e_by_10,
        "low_e_ratio_10": low_e_by_10 / comps_by_10 if comps_by_10 > 0 else 0,
        "d0_pop_at_10": d0_pop_at_10,
        "d1_at_10": d1_at_10,
        "d1_at_50": d1_at_50,
        "e_mean_5": float(e_mean),
        "e_std_5": float(e_std),
        "e_cv_5": float(e_cv)
    }

def main():
    print(f"CYCLE 1684: Initial Conditions | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why n=25 achieves success conditions 96% vs n=30 at 42%")
    print("=" * 70)

    seeds = list(range(1684001, 1684101))  # 100 seeds

    initial_sizes = [20, 25, 30, 35]
    all_results = []

    for n_init in initial_sizes:
        print(f"\nn_initial={n_init}")
        results = [run_experiment(seed, n_init) for seed in seeds]
        all_results.extend(results)

        successes = [r for r in results if r["coexist"]]
        failures = [r for r in results if not r["coexist"]]

        print(f"  → {len(successes)}/100 coexist ({len(successes)}%)")

        if successes:
            avg_comps = np.mean([r["comps_by_10"] for r in successes])
            avg_low_e = np.mean([r["low_e_ratio_10"] for r in successes])
            avg_d1_10 = np.mean([r["d1_at_10"] for r in successes])
            avg_cv = np.mean([r["e_cv_5"] for r in successes])
            print(f"  SUCCESS: comps@10={avg_comps:.1f}, low-e={avg_low_e*100:.0f}%, d1@10={avg_d1_10:.1f}, cv={avg_cv:.2f}")

        if failures:
            avg_comps = np.mean([r["comps_by_10"] for r in failures])
            avg_low_e = np.mean([r["low_e_ratio_10"] for r in failures])
            avg_d1_10 = np.mean([r["d1_at_10"] for r in failures])
            avg_cv = np.mean([r["e_cv_5"] for r in failures])
            print(f"  FAILURE: comps@10={avg_comps:.1f}, low-e={avg_low_e*100:.0f}%, d1@10={avg_d1_10:.1f}, cv={avg_cv:.2f}")

    # Key analysis: Energy coefficient of variation
    print("\n" + "=" * 70)
    print("ENERGY DISTRIBUTION ANALYSIS (Coefficient of Variation at cycle 5)")
    print("=" * 70)

    for n_init in initial_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        successes = [r for r in subset if r["coexist"]]
        failures = [r for r in subset if not r["coexist"]]

        if successes:
            s_cv = np.mean([r["e_cv_5"] for r in successes])
        else:
            s_cv = 0

        if failures:
            f_cv = np.mean([r["e_cv_5"] for r in failures])
        else:
            f_cv = 0

        rate = len(successes) / len(subset)
        print(f"n={n_init}: {rate*100:.0f}% success | Success CV={s_cv:.3f}, Failure CV={f_cv:.3f}")

    # Composition in first 10 cycles
    print("\n" + "=" * 70)
    print("COMPOSITIONS IN FIRST 10 CYCLES")
    print("=" * 70)

    for n_init in initial_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_comps = np.mean([r["comps_by_10"] for r in subset])
        avg_low_e = np.mean([r["low_e_ratio_10"] for r in subset])
        avg_d1_10 = np.mean([r["d1_at_10"] for r in subset])

        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        print(f"n={n_init}: {rate*100:.0f}% | comps={avg_comps:.1f}, low-e={avg_low_e*100:.0f}%, D1@10={avg_d1_10:.1f}")

if __name__ == "__main__":
    main()
