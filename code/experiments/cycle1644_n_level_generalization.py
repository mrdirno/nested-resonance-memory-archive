#!/usr/bin/env python3
"""
CYCLE 1644: N-LEVEL GENERALIZATION
Tests if attack ×0.5 principle generalizes to different system sizes.
Compares baseline vs optimal across 3, 5, 7, 9 levels.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1644"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
MAGNITUDE = 0.25

# Test different system sizes
N_LEVELS_LIST = [3, 5, 7, 9]

# Initial populations scaled by level count
def get_initial(n_levels):
    base = [300, 30, 10, 5, 3, 2, 2, 2, 2]
    return base[:n_levels]

# Base attack rates scaled by level
BASE_ATTACKS = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018, 0.020, 0.022, 0.024]

def get_params(n_levels, attack_mult):
    params = [{"f": 0.1, "e_con": 0.2, "e_rech": 0.4}]
    for lvl in range(1, n_levels):
        conv = max(0.5, 3.0 - 0.3 * (lvl - 1)) * MAGNITUDE
        e_gain = 0.3 + 0.2 * lvl
        e_con = 0.2 + 0.1 * lvl
        h = 0.01 + 0.01 * lvl
        params.append({
            "attack": BASE_ATTACKS[lvl - 1] * attack_mult,
            "h": h,
            "e_con": e_con,
            "e_gain": e_gain,
            "conv": conv
        })
    return params

def run_experiment(seed, n_levels, attack_mult):
    params = get_params(n_levels, attack_mult)
    initial = get_initial(n_levels)
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1644_N{n_levels}_atk{attack_mult}_seed{seed}.db", n_populations=n_levels, mode=f"NLEVEL_{n_levels}")
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

        if all(n == 0 for n in ns[:min(3, n_levels)]): break

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else initial[i] for i in range(n_levels)}
    return {"seed": seed, "n_levels": n_levels, "attack_mult": attack_mult, "coexist": all(finals[i] >= 0.5 for i in range(n_levels))}

def main():
    print(f"CYCLE 1644: N-Level Generalization | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing attack ×0.5 principle across system sizes (30 seeds each)")
    print("=" * 70)

    seeds = list(range(150001, 150031))  # 30 seeds per condition
    all_results = []
    rates = {}

    for n_levels in N_LEVELS_LIST:
        rates[n_levels] = {}
        for attack_mult in [1.0, 0.5]:
            condition = f"{n_levels}L_×{attack_mult}"
            print(f"\n{n_levels} levels, attack ×{attack_mult}")

            results = []
            for seed in seeds:
                r = run_experiment(seed, n_levels, attack_mult)
                results.append(r)

            rate = sum(1 for r in results if r["coexist"]) / len(results)
            rates[n_levels][attack_mult] = rate
            print(f"  → {rate*100:.0f}%")
            all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("GENERALIZATION RESULTS")
    print("=" * 70)

    print("\n         │ Baseline │ Optimal │ Improvement")
    print("─────────────────────────────────────────")

    for n_levels in N_LEVELS_LIST:
        baseline = rates[n_levels][1.0]
        optimal = rates[n_levels][0.5]
        improvement = optimal - baseline
        print(f" {n_levels} levels │   {baseline*100:3.0f}%   │   {optimal*100:3.0f}%   │   +{improvement*100:.0f}%")

    # Check generalization
    print("\n" + "=" * 70)
    print("GENERALIZATION ASSESSMENT")
    print("=" * 70)

    all_improved = all(rates[n][0.5] > rates[n][1.0] for n in N_LEVELS_LIST)
    all_high = all(rates[n][0.5] >= 0.9 for n in N_LEVELS_LIST)

    if all_improved and all_high:
        print("\n✅ PRINCIPLE GENERALIZES: attack ×0.5 improves all system sizes")
    elif all_improved:
        print("\n⚠️ Direction generalizes but magnitude varies")
    else:
        print("\n❌ Principle does NOT generalize uniformly")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1644_n_level_generalization_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "magnitude": MAGNITUDE,
            "n_levels_tested": N_LEVELS_LIST,
            "seeds_per_condition": len(seeds),
            "rates": {str(k): {str(m): v for m, v in d.items()} for k, d in rates.items()},
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
