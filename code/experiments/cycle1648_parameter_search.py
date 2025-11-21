#!/usr/bin/env python3
"""
CYCLE 1648: PARAMETER SEARCH (Bug-Fixed)
Search for parameters that achieve actual coexistence.
Fixes the INITIAL fallback bug - uses 0 instead of INITIAL for collapsed runs.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1648"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]

def get_params(attack_mult, magnitude, energy_mult=1.0):
    """Generate parameters with configurable attack, magnitude, and energy."""
    base_attacks = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018]
    base_energy = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    return [
        {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
        {"attack": base_attacks[0] * attack_mult, "h": 0.02, "e_con": base_energy[0] * energy_mult, "e_gain": 0.5, "conv": 3.0 * magnitude},
        {"attack": base_attacks[1] * attack_mult, "h": 0.03, "e_con": base_energy[1] * energy_mult, "e_gain": 0.6, "conv": 2.5 * magnitude},
        {"attack": base_attacks[2] * attack_mult, "h": 0.04, "e_con": base_energy[2] * energy_mult, "e_gain": 0.8, "conv": 2.0 * magnitude},
        {"attack": base_attacks[3] * attack_mult, "h": 0.05, "e_con": base_energy[3] * energy_mult, "e_gain": 1.0, "conv": 1.5 * magnitude},
        {"attack": base_attacks[4] * attack_mult, "h": 0.06, "e_con": base_energy[4] * energy_mult, "e_gain": 1.2, "conv": 1.2 * magnitude},
        {"attack": base_attacks[5] * attack_mult, "h": 0.07, "e_con": base_energy[5] * energy_mult, "e_gain": 1.4, "conv": 1.0 * magnitude}
    ]

def run_experiment(seed, attack_mult, magnitude, energy_mult=1.0):
    params = get_params(attack_mult, magnitude, energy_mult)
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1648_a{attack_mult}_m{magnitude}_e{energy_mult}_s{seed}.db",
                               n_populations=n_levels, mode="SEARCH")
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

    # BUG FIX: Use 0 instead of INITIAL for collapsed runs
    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else 0 for i in range(n_levels)}
    return {
        "seed": seed,
        "attack_mult": attack_mult,
        "magnitude": magnitude,
        "energy_mult": energy_mult,
        "coexist": all(finals[i] >= 0.5 for i in range(n_levels)),
        "hist_len": len(histories[0]),
        "finals": [round(finals[i], 1) for i in range(n_levels)]
    }

def main():
    print(f"CYCLE 1648: Parameter Search (Bug-Fixed) | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Searching for parameters that achieve actual coexistence")
    print("=" * 70)

    # Test parameter combinations
    seeds = [200001, 200002, 200003]  # Quick test with 3 seeds

    # Parameter grid to test
    configs = [
        (1.0, 0.25, 1.0),    # Baseline
        (0.5, 0.25, 1.0),    # Low attack
        (0.7, 0.25, 1.0),    # Medium-low attack
        (0.8, 0.25, 1.0),    # Medium attack
        (1.0, 0.25, 0.5),    # Reduced energy
        (0.8, 0.35, 1.0),    # Higher conversion
        (0.8, 0.25, 0.5),    # Medium attack + reduced energy
    ]

    all_results = []

    for attack_mult, magnitude, energy_mult in configs:
        label = f"attack={attack_mult}, mag={magnitude}, energy={energy_mult}"
        print(f"\n{label}")

        results = [run_experiment(seed, attack_mult, magnitude, energy_mult) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])

        # Show details
        for r in results:
            status = "✓" if r["coexist"] else "✗"
            print(f"  Seed {r['seed']}: {status} hist={r['hist_len']} finals={r['finals']}")

        print(f"  → {coexist_count}/{len(seeds)} coexist")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("SEARCH RESULTS")
    print("=" * 70)

    # Group by config
    configs_results = {}
    for r in all_results:
        key = (r["attack_mult"], r["magnitude"], r["energy_mult"])
        if key not in configs_results:
            configs_results[key] = []
        configs_results[key].append(r)

    for key, results in configs_results.items():
        rate = sum(1 for r in results if r["coexist"]) / len(results)
        print(f"attack={key[0]}, mag={key[1]}, energy={key[2]}: {rate*100:.0f}%")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1648_parameter_search_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "bug_fix": "Uses 0 instead of INITIAL for collapsed runs",
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
