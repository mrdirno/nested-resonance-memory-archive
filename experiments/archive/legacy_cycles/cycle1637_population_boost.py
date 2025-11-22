#!/usr/bin/env python3
"""
CYCLE 1637: POPULATION BOOST TEST
Tests if increasing initial populations at top levels reduces failure rate.
Compares baseline (3,2,2) vs boosted (5,4,3) for L4,L5,L6.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1637"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
MAGNITUDE = 0.25

# Test conditions
CONDITIONS = {
    "baseline": [300, 30, 10, 5, 3, 2, 2],  # Original
    "boosted":  [300, 30, 10, 5, 5, 4, 3],  # Increased top levels
}

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

def run_experiment(seed, condition, initial):
    params = get_params(MAGNITUDE)
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1637_{condition}_seed{seed}.db", n_populations=n_levels, mode=f"BOOST_{condition}")
    np.random.seed(seed)

    for lvl in range(n_levels):
        for i in range(initial[lvl]):
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, 1.0 + lvl * 0.5), lvl)

    histories = {i: [] for i in range(n_levels)}

    for cycle in range(CYCLES):
        K = K_START - (K_START - K_END) * cycle / DECLINE_CYCLES if cycle < DECLINE_CYCLES else K_END
        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]
        if sum(ns) >= 4000: break
        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_levels)]

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

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else initial[i] for i in range(n_levels)}
    return {"seed": seed, "condition": condition, "coexist": all(finals[i] >= 0.5 for i in range(n_levels))}

def main():
    print(f"CYCLE 1637: Population Boost Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing if increased initial populations reduce failure rate")
    print("Baseline: L4=3, L5=2, L6=2 | Boosted: L4=5, L5=4, L6=3")
    print("=" * 70)

    seeds = list(range(80001, 80051))  # 50 seeds per condition
    all_results = []

    for condition, initial in CONDITIONS.items():
        print(f"\nCondition: {condition.upper()}")
        print(f"Initial populations: {initial}")
        print("-" * 50)

        cond_results = []
        for i, seed in enumerate(seeds, 1):
            r = run_experiment(seed, condition, initial)
            cond_results.append(r)
            if i % 10 == 0:
                current = sum(1 for r in cond_results if r["coexist"])
                print(f"  [{i}/50] {current}/{i} survive ({current/i*100:.0f}%)")

        coexist_count = sum(1 for r in cond_results if r["coexist"])
        print(f"  FINAL: {coexist_count}/50 ({coexist_count/50*100:.0f}%)")
        all_results.extend(cond_results)

    # Analysis
    print("\n" + "=" * 70)
    print("COMPARISON")
    print("=" * 70)

    baseline_results = [r for r in all_results if r["condition"] == "baseline"]
    boosted_results = [r for r in all_results if r["condition"] == "boosted"]

    baseline_rate = sum(1 for r in baseline_results if r["coexist"]) / len(baseline_results)
    boosted_rate = sum(1 for r in boosted_results if r["coexist"]) / len(boosted_results)

    baseline_bar = "█" * int(baseline_rate * 20) + "░" * (20 - int(baseline_rate * 20))
    boosted_bar = "█" * int(boosted_rate * 20) + "░" * (20 - int(boosted_rate * 20))

    print(f"\nBaseline (3,2,2): {baseline_bar} {baseline_rate*100:.0f}%")
    print(f"Boosted  (5,4,3): {boosted_bar} {boosted_rate*100:.0f}%")

    improvement = boosted_rate - baseline_rate
    if improvement > 0:
        print(f"\n✅ IMPROVEMENT: +{improvement*100:.0f}% with boosted populations")
    elif improvement < 0:
        print(f"\n❌ DEGRADATION: {improvement*100:.0f}% with boosted populations")
    else:
        print(f"\n➖ NO CHANGE: Same performance")

    # Statistical significance (simple z-test for proportions)
    n = len(baseline_results)
    p_pooled = (baseline_rate * n + boosted_rate * n) / (2 * n)
    se = np.sqrt(2 * p_pooled * (1 - p_pooled) / n)
    z = abs(boosted_rate - baseline_rate) / se if se > 0 else 0
    significant = z > 1.96

    print(f"\nStatistical test: z = {z:.2f} {'(p < 0.05, SIGNIFICANT)' if significant else '(not significant)'}")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1637_population_boost_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "magnitude": MAGNITUDE,
            "seeds_per_condition": len(seeds),
            "conditions": {k: v for k, v in CONDITIONS.items()},
            "baseline_rate": baseline_rate,
            "boosted_rate": boosted_rate,
            "improvement": improvement,
            "z_score": z,
            "significant": bool(significant),
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
