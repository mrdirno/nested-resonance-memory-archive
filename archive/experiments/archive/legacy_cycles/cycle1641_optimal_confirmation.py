#!/usr/bin/env python3
"""
CYCLE 1641: OPTIMAL PARAMETER CONFIRMATION
Confirms C1640 finding (attack ×0.5 → 100%) with larger sample.
Tests combined intervention: attack reduction + energy reduction.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1641"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]
MAGNITUDE = 0.25  # Optimal from C1640

def get_params(attack_mult, energy_mult):
    """attack_mult: 0.5 or 1.0, energy_mult: 0.5 or 1.0 for top levels"""
    base_attacks = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018]
    base_energy = [0.6, 0.7, 0.8]  # L4, L5, L6
    return [
        {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
        {"attack": base_attacks[0] * attack_mult, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 3.0 * MAGNITUDE},
        {"attack": base_attacks[1] * attack_mult, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 2.5 * MAGNITUDE},
        {"attack": base_attacks[2] * attack_mult, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 2.0 * MAGNITUDE},
        {"attack": base_attacks[3] * attack_mult, "h": 0.05, "e_con": base_energy[0] * energy_mult, "e_gain": 1.0, "conv": 1.5 * MAGNITUDE},
        {"attack": base_attacks[4] * attack_mult, "h": 0.06, "e_con": base_energy[1] * energy_mult, "e_gain": 1.2, "conv": 1.2 * MAGNITUDE},
        {"attack": base_attacks[5] * attack_mult, "h": 0.07, "e_con": base_energy[2] * energy_mult, "e_gain": 1.4, "conv": 1.0 * MAGNITUDE}
    ]

CONDITIONS = {
    "baseline": (1.0, 1.0),           # Original parameters
    "attack_only": (0.5, 1.0),        # Just attack reduction (C1640 optimal)
    "energy_only": (1.0, 0.5),        # Just energy reduction (C1638-39)
    "combined": (0.5, 0.5)            # Both interventions
}

def run_experiment(seed, condition, attack_mult, energy_mult):
    params = get_params(attack_mult, energy_mult)
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1641_{condition}_seed{seed}.db", n_populations=n_levels, mode=f"CONFIRM_{condition}")
    np.random.seed(seed)

    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
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

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else INITIAL[i] for i in range(n_levels)}
    return {"seed": seed, "condition": condition, "coexist": all(finals[i] >= 0.5 for i in range(n_levels))}

def main():
    print(f"CYCLE 1641: Optimal Parameter Confirmation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Confirming C1640 and testing combined interventions (50 seeds each)")
    print("=" * 70)

    seeds = list(range(120001, 120051))  # 50 seeds per condition
    all_results = []
    rates = {}

    for condition, (attack_mult, energy_mult) in CONDITIONS.items():
        print(f"\nCondition: {condition.upper()} (attack ×{attack_mult}, energy ×{energy_mult})")
        cond_results = []
        for i, seed in enumerate(seeds, 1):
            r = run_experiment(seed, condition, attack_mult, energy_mult)
            cond_results.append(r)
            if i % 10 == 0:
                current = sum(1 for r in cond_results if r["coexist"])
                print(f"  [{i}/50] {current}/{i} ({current/i*100:.0f}%)")

        rate = sum(1 for r in cond_results if r["coexist"]) / len(cond_results)
        rates[condition] = rate
        print(f"  FINAL: {rate*100:.0f}%")
        all_results.extend(cond_results)

    # Results summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    for condition in CONDITIONS:
        rate = rates[condition]
        bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))
        print(f"{condition:15s}: {bar} {rate*100:.0f}%")

    # Find best
    best = max(rates.items(), key=lambda x: x[1])
    print(f"\nOptimal: {best[0]} → {best[1]*100:.0f}%")

    # Statistical comparisons
    print("\n" + "=" * 70)
    print("STATISTICAL COMPARISONS (vs baseline)")
    print("=" * 70)

    n = len(seeds)
    baseline_rate = rates["baseline"]

    for condition in ["attack_only", "energy_only", "combined"]:
        rate = rates[condition]
        diff = rate - baseline_rate
        p_pooled = (baseline_rate + rate) / 2
        se = np.sqrt(2 * p_pooled * (1 - p_pooled) / n) if p_pooled > 0 and p_pooled < 1 else 0.01
        z = abs(diff) / se if se > 0 else 0
        sig = z > 1.96
        sign = "+" if diff > 0 else ""
        print(f"{condition}: {sign}{diff*100:.0f}% (z={z:.2f}) {'*' if sig else ''}")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1641_optimal_confirmation_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "magnitude": MAGNITUDE,
            "seeds_per_condition": len(seeds),
            "conditions": {k: {"attack_mult": v[0], "energy_mult": v[1]} for k, v in CONDITIONS.items()},
            "rates": rates,
            "optimal": {"condition": best[0], "rate": best[1]},
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
