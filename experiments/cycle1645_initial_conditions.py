#!/usr/bin/env python3
"""
CYCLE 1645: INITIAL CONDITION SENSITIVITY
Tests if optimal parameters (attack ×0.5) hold under varied initial populations.
Tests: standard, sparse, dense, inverted pyramid.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1645"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
MAGNITUDE = 0.25
ATTACK_MULT = 0.5  # Optimal from C1642

# Different initial condition scenarios
INITIAL_CONDITIONS = {
    "standard": [300, 30, 10, 5, 3, 2, 2],      # Original
    "sparse": [150, 15, 5, 3, 2, 1, 1],          # Half population
    "dense": [500, 50, 20, 10, 5, 3, 3],         # Dense population
    "inverted": [100, 50, 30, 20, 15, 10, 8],    # Inverted pyramid
    "uniform": [50, 50, 50, 50, 50, 50, 50]      # Equal across levels
}

def get_params():
    base_attacks = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018]
    return [
        {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
        {"attack": base_attacks[0] * ATTACK_MULT, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 3.0 * MAGNITUDE},
        {"attack": base_attacks[1] * ATTACK_MULT, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 2.5 * MAGNITUDE},
        {"attack": base_attacks[2] * ATTACK_MULT, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 2.0 * MAGNITUDE},
        {"attack": base_attacks[3] * ATTACK_MULT, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 1.5 * MAGNITUDE},
        {"attack": base_attacks[4] * ATTACK_MULT, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 1.2 * MAGNITUDE},
        {"attack": base_attacks[5] * ATTACK_MULT, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 1.0 * MAGNITUDE}
    ]

def run_experiment(seed, condition, initial):
    params = get_params()
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1645_{condition}_seed{seed}.db", n_populations=n_levels, mode=f"INIT_{condition}")
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
    print(f"CYCLE 1645: Initial Condition Sensitivity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Testing optimal params (attack ×{ATTACK_MULT}) under varied ICs (30 seeds)")
    print("=" * 70)

    seeds = list(range(160001, 160031))  # 30 seeds per condition
    all_results = []
    rates = {}

    for condition, initial in INITIAL_CONDITIONS.items():
        print(f"\n{condition}: {initial}")
        results = []
        for seed in seeds:
            r = run_experiment(seed, condition, initial)
            results.append(r)

        rate = sum(1 for r in results if r["coexist"]) / len(results)
        rates[condition] = rate
        print(f"  → {rate*100:.0f}%")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("INITIAL CONDITION SENSITIVITY")
    print("=" * 70)

    for condition in INITIAL_CONDITIONS:
        rate = rates[condition]
        bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))
        print(f"{condition:12s}: {bar} {rate*100:.0f}%")

    # Assessment
    print("\n" + "=" * 70)
    print("ROBUSTNESS ASSESSMENT")
    print("=" * 70)

    all_high = all(r >= 0.9 for r in rates.values())
    min_rate = min(rates.values())
    max_rate = max(rates.values())

    if all_high:
        print(f"\n✅ ROBUST: All conditions ≥90% ({min_rate*100:.0f}%-{max_rate*100:.0f}%)")
    else:
        low = [c for c, r in rates.items() if r < 0.9]
        print(f"\n⚠️ SENSITIVE to: {low}")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1645_initial_conditions_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "attack_mult": ATTACK_MULT,
            "magnitude": MAGNITUDE,
            "initial_conditions": INITIAL_CONDITIONS,
            "seeds_per_condition": len(seeds),
            "rates": rates,
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
