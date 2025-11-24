#!/usr/bin/env python3
"""
CYCLE 1640: ATTACK RATE × CONVERSION INTERACTION
Maps the 2D parameter space of attack rate and conversion magnitude.
Tests if optimal conversion depends on attack rate.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1640"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]

# 2D grid: attack multiplier × conversion magnitude
ATTACK_MULTIPLIERS = [0.5, 1.0, 1.5]  # Relative to baseline
MAGNITUDES = [0.15, 0.25, 0.35]  # Conversion magnitudes

def get_params(magnitude, attack_mult):
    base_attacks = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018]
    return [
        {"f": 0.1, "e_con": 0.2, "e_rech": 0.4},
        {"attack": base_attacks[0] * attack_mult, "h": 0.02, "e_con": 0.3, "e_gain": 0.5, "conv": 3.0 * magnitude},
        {"attack": base_attacks[1] * attack_mult, "h": 0.03, "e_con": 0.4, "e_gain": 0.6, "conv": 2.5 * magnitude},
        {"attack": base_attacks[2] * attack_mult, "h": 0.04, "e_con": 0.5, "e_gain": 0.8, "conv": 2.0 * magnitude},
        {"attack": base_attacks[3] * attack_mult, "h": 0.05, "e_con": 0.6, "e_gain": 1.0, "conv": 1.5 * magnitude},
        {"attack": base_attacks[4] * attack_mult, "h": 0.06, "e_con": 0.7, "e_gain": 1.2, "conv": 1.2 * magnitude},
        {"attack": base_attacks[5] * attack_mult, "h": 0.07, "e_con": 0.8, "e_gain": 1.4, "conv": 1.0 * magnitude}
    ]

def run_experiment(seed, attack_mult, magnitude):
    params = get_params(magnitude, attack_mult)
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1640_atk{attack_mult}_mag{magnitude}_seed{seed}.db", n_populations=n_levels, mode=f"2D_{attack_mult}_{magnitude}")
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
    return {"seed": seed, "attack_mult": attack_mult, "magnitude": magnitude, "coexist": all(finals[i] >= 0.5 for i in range(n_levels))}

def main():
    print(f"CYCLE 1640: Attack × Conversion 2D Interaction | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Mapping 3×3 parameter grid (20 seeds per cell)")
    print("=" * 70)

    seeds = list(range(110001, 110021))  # 20 seeds per condition
    all_results = []
    grid = {}

    for attack_mult in ATTACK_MULTIPLIERS:
        grid[attack_mult] = {}
        for magnitude in MAGNITUDES:
            print(f"\nAttack ×{attack_mult}, Magnitude {magnitude}")

            cell_results = []
            for seed in seeds:
                r = run_experiment(seed, attack_mult, magnitude)
                cell_results.append(r)

            coexist_rate = sum(1 for r in cell_results if r["coexist"]) / len(cell_results)
            grid[attack_mult][magnitude] = coexist_rate
            print(f"  → {coexist_rate*100:.0f}%")
            all_results.extend(cell_results)

    # Display 2D grid
    print("\n" + "=" * 70)
    print("2D PARAMETER GRID (Coexistence %)")
    print("=" * 70)

    print("\n            │ ", end="")
    for mag in MAGNITUDES:
        print(f" mag={mag} │", end="")
    print("\n" + "─" * 50)

    for attack_mult in ATTACK_MULTIPLIERS:
        print(f" attack ×{attack_mult} │ ", end="")
        for mag in MAGNITUDES:
            rate = grid[attack_mult][mag]
            bar = "█" * int(rate * 5) + "░" * (5 - int(rate * 5))
            print(f"{bar} {rate*100:3.0f}% │", end="")
        print()

    # Find optimal
    best_rate = 0
    best_params = None
    for attack_mult in ATTACK_MULTIPLIERS:
        for mag in MAGNITUDES:
            if grid[attack_mult][mag] > best_rate:
                best_rate = grid[attack_mult][mag]
                best_params = (attack_mult, mag)

    print(f"\nOptimal: attack ×{best_params[0]}, magnitude {best_params[1]} → {best_rate*100:.0f}%")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1640_attack_interaction_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "attack_multipliers": ATTACK_MULTIPLIERS,
            "magnitudes": MAGNITUDES,
            "seeds_per_cell": len(seeds),
            "grid": {str(k): {str(m): v for m, v in d.items()} for k, d in grid.items()},
            "optimal": {"attack_mult": best_params[0], "magnitude": best_params[1], "rate": best_rate},
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
