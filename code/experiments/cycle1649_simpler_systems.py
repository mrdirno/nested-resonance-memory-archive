#!/usr/bin/env python3
"""
CYCLE 1649: SIMPLER TROPHIC SYSTEMS
Test whether 3-level and 5-level systems can achieve stable coexistence.
Hypothesis: 7-level system too deep; simpler systems may be tractable.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1649"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40

def get_initial(n_levels):
    """Generate pyramid initial populations for n levels."""
    if n_levels == 3:
        return [300, 30, 5]
    elif n_levels == 5:
        return [300, 30, 10, 5, 3]
    elif n_levels == 7:
        return [300, 30, 10, 5, 3, 2, 2]
    else:
        raise ValueError(f"Unsupported n_levels: {n_levels}")

def get_params(n_levels, attack_mult=1.0):
    """Generate parameters for n-level system."""
    base_attacks = [0.003, 0.005, 0.008, 0.012, 0.015, 0.018]
    base_energy = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    magnitude = 0.25

    params = [{"f": 0.1, "e_con": 0.2, "e_rech": 0.4}]
    for i in range(1, n_levels):
        idx = min(i - 1, 5)  # Cap at 6 parameter sets
        params.append({
            "attack": base_attacks[idx] * attack_mult,
            "h": 0.02 + i * 0.01,
            "e_con": base_energy[idx],
            "e_gain": 0.5 + i * 0.1,
            "conv": (3.0 - i * 0.3) * magnitude
        })
    return params

def run_experiment(seed, n_levels, attack_mult=1.0):
    initial = get_initial(n_levels)
    params = get_params(n_levels, attack_mult)

    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1649_L{n_levels}_a{attack_mult}_s{seed}.db",
        n_populations=n_levels, mode="SEARCH"
    )
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

        # L0 reproduction
        pops[0] = reality.get_population_agents(0)
        for a in pops[0]:
            f = max(0, params[0]["f"] * (1 - len(pops[0]) / K))
            if np.random.random() < f:
                reality.add_agent(FractalAgent(f"L0_{cycle}_{a.agent_id[-6:]}", 0, 0.5), 0)

        # Predator reproduction
        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                eg = gains[lvl].get(a.agent_id, 0)
                if eg > 0 and np.random.random() < params[lvl]["conv"] * eg:
                    reality.add_agent(FractalAgent(f"L{lvl}_{cycle}_{a.agent_id[-6:]}", lvl, 0.8), lvl)

        # Energy consumption L0
        for a in reality.get_population_agents(0):
            a.energy -= params[0]["e_con"]
            if a.energy <= 0: reality.remove_agent(a.agent_id, 0)
            else: a.energy = min(a.energy + params[0]["e_rech"], 2.0)

        # Energy consumption predators
        for lvl in range(1, n_levels):
            for a in reality.get_population_agents(lvl):
                a.energy += gains[lvl].get(a.agent_id, 0) - params[lvl]["e_con"]
                if a.energy <= 0: reality.remove_agent(a.agent_id, lvl)
                else: a.energy = min(a.energy, 2.0 + lvl)

        # Record history every 100 cycles
        if cycle % 100 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

        # Break if bottom levels collapse
        if all(n == 0 for n in ns[:min(3, n_levels)]): break

    # BUG FIX: Use 0 instead of INITIAL for collapsed runs
    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else 0 for i in range(n_levels)}
    return {
        "seed": seed,
        "n_levels": n_levels,
        "attack_mult": attack_mult,
        "coexist": all(finals[i] >= 0.5 for i in range(n_levels)),
        "hist_len": len(histories[0]),
        "finals": [round(finals[i], 1) for i in range(n_levels)]
    }

def main():
    print(f"CYCLE 1649: Simpler Trophic Systems | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing 3-level and 5-level systems for stable coexistence")
    print("=" * 70)

    seeds = [300001, 300002, 300003, 300004, 300005]

    # Test configurations: (n_levels, attack_mult)
    configs = [
        (3, 1.0),   # 3-level baseline
        (3, 0.5),   # 3-level reduced attack
        (3, 0.7),   # 3-level medium attack
        (5, 1.0),   # 5-level baseline
        (5, 0.5),   # 5-level reduced attack
        (5, 0.7),   # 5-level medium attack
        (7, 0.7),   # 7-level for comparison
    ]

    all_results = []

    for n_levels, attack_mult in configs:
        label = f"{n_levels}-level, attack={attack_mult}"
        print(f"\n{label}")

        results = [run_experiment(seed, n_levels, attack_mult) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])

        for r in results:
            status = "✓" if r["coexist"] else "✗"
            print(f"  Seed {r['seed']}: {status} hist={r['hist_len']} finals={r['finals']}")

        rate = coexist_count / len(seeds)
        print(f"  → {coexist_count}/{len(seeds)} coexist ({rate*100:.0f}%)")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    # Group by config
    configs_results = {}
    for r in all_results:
        key = (r["n_levels"], r["attack_mult"])
        if key not in configs_results:
            configs_results[key] = []
        configs_results[key].append(r)

    for key in sorted(configs_results.keys()):
        results = configs_results[key]
        rate = sum(1 for r in results if r["coexist"]) / len(results)
        print(f"{key[0]}-level attack={key[1]}: {rate*100:.0f}%")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1649_simpler_systems_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "hypothesis": "Simpler systems may achieve coexistence where 7-level fails",
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
