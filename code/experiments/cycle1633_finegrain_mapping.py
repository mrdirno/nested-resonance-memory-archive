#!/usr/bin/env python3
"""
CYCLE 1633: FINE-GRAINED CONVERSION MAPPING
Maps the transition zone (0.15-0.35) with higher resolution.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1633"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]

# Fine-grained magnitudes in transition zone
MAGNITUDES = [0.15, 0.20, 0.25, 0.30, 0.35]

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

def run_experiment(seed, magnitude):
    params = get_params(magnitude)
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1633_mag{magnitude}_seed{seed}.db", n_populations=n_levels, mode=f"FINEGRAIN_{magnitude}")
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
    return {"seed": seed, "magnitude": magnitude, "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)}, "coexist": all(finals[i] >= 0.5 for i in range(n_levels))}

def main():
    print(f"CYCLE 1633: Fine-Grained Mapping | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(40011, 40031))  # 20 seeds per magnitude
    all_results = []

    for mag in MAGNITUDES:
        max_prob = 3.0 * mag * 1.4
        print(f"\nMagnitude {mag} (max spawn prob = {max_prob:.2f})")
        print("-" * 50)

        mag_results = []
        for i, seed in enumerate(seeds, 1):
            r = run_experiment(seed, mag)
            mag_results.append(r)
            status = "SURVIVE" if r["coexist"] else "COLLAPSE"
            if i % 5 == 0:
                print(f"  [{i}/{len(seeds)}] Progress...")

        coexist_count = sum(1 for r in mag_results if r["coexist"])
        print(f"  Result: {coexist_count}/{len(mag_results)} ({coexist_count/len(mag_results)*100:.0f}%)")
        all_results.extend(mag_results)

    print("\n" + "=" * 70)
    print("FINE-GRAINED TRANSITION MAP")
    print("=" * 70)

    for mag in MAGNITUDES:
        mag_results = [r for r in all_results if r["magnitude"] == mag]
        rate = sum(1 for r in mag_results if r["coexist"]) / len(mag_results)
        bar = "█" * int(rate * 20) + "░" * (20 - int(rate * 20))
        print(f"  {mag:.2f}: {bar} {rate*100:.0f}%")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1633_finegrain_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "magnitudes": MAGNITUDES, "seeds_per_mag": len(seeds), "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
