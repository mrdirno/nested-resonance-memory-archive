#!/usr/bin/env python3
"""
CYCLE 1632: SUB-SATURATION CONVERSION MAPPING
Tests conversion dynamics in valid parameter space (magnitude < 0.67)
where spawn probability < 1.0 for meaningful variation.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1632"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]

# Test magnitudes in valid range (< 0.67)
MAGNITUDES = [0.1, 0.2, 0.3, 0.4, 0.5]

def get_params(magnitude, attack_mult=1.0):
    """Get params with specified magnitude and attack multiplier"""
    base_attack = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018]
    return [
        {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
        {"attack": base_attack[0] * attack_mult, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 3.0 * magnitude},
        {"attack": base_attack[1] * attack_mult, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 2.5 * magnitude},
        {"attack": base_attack[2] * attack_mult, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 2.0 * magnitude},
        {"attack": base_attack[3] * attack_mult, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 1.5 * magnitude},
        {"attack": base_attack[4] * attack_mult, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 1.2 * magnitude},
        {"attack": base_attack[5] * attack_mult, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 1.0 * magnitude}
    ]

def run_experiment(seed, magnitude):
    """Run single experiment with given magnitude"""
    params = get_params(magnitude)
    n_levels = 7

    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1632_mag{magnitude}_seed{seed}.db",
        n_populations=n_levels,
        mode=f"SUBSATURATION_MAG{magnitude}"
    )

    np.random.seed(seed)

    # Initialize populations
    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, 1.0 + lvl * 0.5), lvl)

    histories = {i: [] for i in range(n_levels)}

    for cycle in range(CYCLES):
        K = K_START - (K_START - K_END) * cycle / DECLINE_CYCLES if cycle < DECLINE_CYCLES else K_END
        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]

        if sum(ns) >= 4000:
            break

        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_levels)]

        # Predation (top-down)
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

        # Base reproduction
        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, params[0]["f"] * (1 - len(pops[0]) / K))
            if np.random.random() < f:
                reality.add_agent(FractalAgent(f"L0_{cycle}_{a.agent_id[-6:]}", 0, 0.5), 0)

        # Predator reproduction (sub-saturation - probability < 1)
        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                spawn_prob = params[lvl]["conv"] * eg
                if eg > 0 and np.random.random() < spawn_prob:
                    reality.add_agent(FractalAgent(f"L{lvl}_{cycle}_{a.agent_id[-6:]}", lvl, 0.8), lvl)

        # Energy dynamics
        for a in reality.get_population_agents(0):
            a.energy -= params[0]["e_con"]
            if a.energy <= 0:
                reality.remove_agent(a.agent_id, 0)
            else:
                a.energy = min(a.energy + params[0]["e_rech"], 2.0)

        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - params[lvl]["e_con"]
                if a.energy <= 0:
                    reality.remove_agent(a.agent_id, lvl)
                else:
                    a.energy = min(a.energy, 2.0 + lvl)

        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

        if all(n == 0 for n in ns[:3]):
            break

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else INITIAL[i] for i in range(n_levels)}
    return {
        "seed": seed,
        "magnitude": magnitude,
        "finals": {f"L{i}": float(finals[i]) for i in range(n_levels)},
        "coexist": all(finals[i] >= 0.5 for i in range(n_levels))
    }

def main():
    print(f"CYCLE 1632: Sub-Saturation Mapping | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing conversion dynamics in valid parameter space (mag < 0.67)")
    print("=" * 70)

    seeds = list(range(40001, 40011))  # 10 seeds per magnitude
    all_results = []

    for mag in MAGNITUDES:
        # Calculate max spawn probability to verify sub-saturation
        max_prob = 3.0 * mag * 1.4  # highest conv × highest e_gain
        print(f"\nMagnitude {mag} (max spawn prob = {max_prob:.2f})")
        print("-" * 50)

        mag_results = []
        for i, seed in enumerate(seeds, 1):
            r = run_experiment(seed, mag)
            mag_results.append(r)
            print(f"  [{i}/{len(seeds)}] seed={seed} → {'SURVIVE' if r['coexist'] else 'COLLAPSE'}")

        coexist_count = sum(1 for r in mag_results if r["coexist"])
        print(f"  Coexistence: {coexist_count}/{len(mag_results)} ({coexist_count/len(mag_results)*100:.0f}%)")
        all_results.extend(mag_results)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for mag in MAGNITUDES:
        mag_results = [r for r in all_results if r["magnitude"] == mag]
        rate = sum(1 for r in mag_results if r["coexist"]) / len(mag_results)
        print(f"  Magnitude {mag}: {rate*100:.0f}% coexistence")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1632_subsaturation_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "magnitudes": MAGNITUDES,
            "seeds_per_mag": len(seeds),
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
