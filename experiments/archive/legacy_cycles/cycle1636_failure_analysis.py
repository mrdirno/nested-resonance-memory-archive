#!/usr/bin/env python3
"""
CYCLE 1636: FAILURE MECHANISM ANALYSIS
Investigates why ~33% of experiments fail even in optimal parameter range.
Tracks which levels fail and at what time.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1636"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]
MAGNITUDE = 0.25  # Optimal range

def get_params(magnitude):
    return [
        {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
        {"attack": 0.003, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 3.0 * magnitude},
        {"attack": 0.005, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 2.5 * magnitude},
        {"attack": 0.008, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 2.0 * magnitude},
        {"attack": 0.012, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 1.5 * magnitude},
        {"attack": 0.015, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 1.2 * magnitude},
        {"attack": 0.018, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 1.0 * magnitude}
    ]

def run_experiment(seed):
    params = get_params(MAGNITUDE)
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1636_seed{seed}.db", n_populations=n_levels, mode="FAILURE_ANALYSIS")
    np.random.seed(seed)

    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, 1.0 + lvl * 0.5), lvl)

    histories = {i: [] for i in range(n_levels)}
    extinction_times = {i: None for i in range(n_levels)}  # Track when each level goes extinct
    first_extinction = None

    for cycle in range(CYCLES):
        K = K_START - (K_START - K_END) * cycle / DECLINE_CYCLES if cycle < DECLINE_CYCLES else K_END
        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]
        if sum(ns) >= 4000: break
        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_levels)]

        # Track extinctions
        for lvl in range(n_levels):
            if extinction_times[lvl] is None and ns[lvl] == 0:
                extinction_times[lvl] = cycle
                if first_extinction is None:
                    first_extinction = (lvl, cycle)

        for lvl in range(n_levels - 1, 0, -1):
            prey_lvl = lvl - 1
            pops[prey_lvl] = reality.get_population_agents(prey_lvl)
            ns[prey_lvl] = len(pops[prey_lvl])
            if ns[prey_lvl] > 0:
                ids = [a.agent_id for a in pops[prey_lvl]]
                consumed = []
                p = params[lvl]
                for pred in pops[lvl]:
                    avail = ns[prey_lvl] - len(consumed)
                    if avail > 0:
                        rate = (p["attack"] * avail) / (1 + p["attack"] * p["h"] * avail)
                        for _ in range(min(np.random.poisson(rate), avail)):
                            remain = [i for i in ids if i not in consumed]
                            if remain:
                                v = np.random.choice(remain)
                                consumed.append(v)
                                gains[lvl][pred.agent_id] += p["e_gain"]
                for v in consumed:
                    reality.remove_agent(v, prey_lvl)

        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, params[0]["f"] * (1 - len(pops[0]) / K))
            if np.random.random() < f:
                reality.add_agent(FractalAgent(f"L0_{cycle}_{a.agent_id[-6:]}", 0, 0.5), 0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < params[lvl]["conv"] * eg:
                    reality.add_agent(FractalAgent(f"L{lvl}_{cycle}_{a.agent_id[-6:]}", lvl, 0.8), lvl)

        for a in reality.get_population_agents(0):
            a.energy -= params[0]["e_con"]
            if a.energy <= 0: reality.remove_agent(a.agent_id, 0)
            else: a.energy = min(a.energy + params[0]["e_rech"], 2.0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - params[lvl]["e_con"]
                if a.energy <= 0: reality.remove_agent(a.agent_id, lvl)
                else: a.energy = min(a.energy, 2.0 + lvl)

        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

        if all(n == 0 for n in ns[:3]): break

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else INITIAL[i] for i in range(n_levels)}
    coexist = all(finals[i] >= 0.5 for i in range(n_levels))

    # Determine which levels failed
    failed_levels = [i for i in range(n_levels) if finals[i] < 0.5]

    return {
        "seed": seed,
        "coexist": coexist,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)},
        "failed_levels": failed_levels,
        "extinction_times": {f"L{i}": extinction_times[i] for i in range(n_levels)},
        "first_extinction": first_extinction
    }

def main():
    print(f"CYCLE 1636: Failure Mechanism Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Magnitude: {MAGNITUDE} | 100 seeds")
    print("=" * 70)

    seeds = list(range(70001, 70101))  # 100 seeds
    all_results = []

    failures_by_level = {i: 0 for i in range(7)}
    first_extinction_by_level = {i: 0 for i in range(7)}
    extinction_times_by_level = {i: [] for i in range(7)}

    for i, seed in enumerate(seeds, 1):
        r = run_experiment(seed)
        all_results.append(r)

        # Count failures
        if not r["coexist"]:
            for lvl in r["failed_levels"]:
                failures_by_level[lvl] += 1
            if r["first_extinction"]:
                first_extinction_by_level[r["first_extinction"][0]] += 1

        # Track extinction times
        for lvl in range(7):
            if r["extinction_times"][f"L{lvl}"] is not None:
                extinction_times_by_level[lvl].append(r["extinction_times"][f"L{lvl}"])

        if i % 20 == 0:
            current = sum(1 for r in all_results if r["coexist"])
            print(f"  [{i}/100] {current}/{i} survive ({current/i*100:.0f}%)")

    # Analysis
    print("\n" + "=" * 70)
    print("FAILURE ANALYSIS")
    print("=" * 70)

    total_failures = sum(1 for r in all_results if not r["coexist"])
    total_successes = sum(1 for r in all_results if r["coexist"])

    print(f"\nOverall: {total_successes}/100 coexist ({total_successes}%)")
    print(f"Failures: {total_failures}")

    print("\n--- Failures by Level ---")
    for lvl in range(7):
        pct = failures_by_level[lvl] / total_failures * 100 if total_failures > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  L{lvl}: {bar} {failures_by_level[lvl]:3d} ({pct:.0f}%)")

    print("\n--- First Extinction (Which level dies first) ---")
    for lvl in range(7):
        pct = first_extinction_by_level[lvl] / total_failures * 100 if total_failures > 0 else 0
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"  L{lvl}: {bar} {first_extinction_by_level[lvl]:3d} ({pct:.0f}%)")

    print("\n--- Mean Extinction Time (when present) ---")
    for lvl in range(7):
        if extinction_times_by_level[lvl]:
            mean_time = np.mean(extinction_times_by_level[lvl])
            std_time = np.std(extinction_times_by_level[lvl])
            print(f"  L{lvl}: {mean_time:.0f} ± {std_time:.0f} cycles (n={len(extinction_times_by_level[lvl])})")
        else:
            print(f"  L{lvl}: No extinctions")

    # Identify pattern
    print("\n" + "=" * 70)
    print("MECHANISM HYPOTHESIS")
    print("=" * 70)

    # Find most common first extinction
    max_first = max(first_extinction_by_level.values())
    primary_failure = [lvl for lvl, count in first_extinction_by_level.items() if count == max_first][0]

    if primary_failure >= 5:
        print(f"  Primary failure point: TOP PREDATORS (L{primary_failure})")
        print("  Mechanism: Stochastic extinction of small populations")
        print("  Solution: Increase initial population or reduce energy costs")
    elif primary_failure == 0:
        print(f"  Primary failure point: BASE LAYER (L0)")
        print("  Mechanism: Carrying capacity collapse")
        print("  Solution: Adjust K decline parameters")
    else:
        print(f"  Primary failure point: MID-TIER (L{primary_failure})")
        print("  Mechanism: Trophic cascade or energy flow disruption")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1636_failure_analysis_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "magnitude": MAGNITUDE,
            "n_seeds": len(seeds),
            "coexistence_rate": total_successes / len(seeds),
            "failures_by_level": failures_by_level,
            "first_extinction_by_level": first_extinction_by_level,
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
