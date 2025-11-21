#!/usr/bin/env python3
"""
CYCLE 1651: REPRODUCTION BOOST
Test if higher reproduction/conversion rates achieve coexistence.
Hypothesis: Current rates too low for energy balance.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1651"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40

def get_params(f_mult=1.0, conv_mult=1.0, e_gain_mult=1.0):
    """Generate 3-level parameters with configurable reproduction."""
    return [
        {"f": 0.1 * f_mult, "e_con": 0.2, "e_rech": 0.4},
        {"attack": 0.003, "h": 0.02, "e_con": 0.3, "e_gain": 0.5 * e_gain_mult, "conv": 0.75 * conv_mult},
        {"attack": 0.005, "h": 0.03, "e_con": 0.4, "e_gain": 0.6 * e_gain_mult, "conv": 0.625 * conv_mult}
    ]

def run_experiment(seed, f_mult, conv_mult, e_gain_mult):
    n_levels = 3
    initial = [300, 30, 5]
    params = get_params(f_mult, conv_mult, e_gain_mult)

    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1651_f{f_mult}_c{conv_mult}_g{e_gain_mult}_s{seed}.db",
        n_populations=n_levels, mode="SEARCH"
    )
    np.random.seed(seed)

    for lvl in range(n_levels):
        for i in range(initial[lvl]):
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, 2.0 + lvl * 0.5), lvl)

    histories = {i: [] for i in range(n_levels)}

    for cycle in range(CYCLES):
        K = K_START - (K_START - K_END) * cycle / DECLINE_CYCLES if cycle < DECLINE_CYCLES else K_END
        pops = [reality.get_population_agents(i) for i in range(n_levels)]
        ns = [len(p) for p in pops]
        if sum(ns) >= 4000: break
        gains = [{a.agent_id: 0.0 for a in pops[i]} for i in range(n_levels)]

        # Predation
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

        # Energy consumption
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

        if all(n == 0 for n in ns): break

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else 0 for i in range(n_levels)}
    return {
        "seed": seed,
        "f_mult": f_mult,
        "conv_mult": conv_mult,
        "e_gain_mult": e_gain_mult,
        "coexist": all(finals[i] >= 0.5 for i in range(n_levels)),
        "hist_len": len(histories[0]),
        "finals": [round(float(finals[i]), 1) for i in range(n_levels)]
    }

def main():
    print(f"CYCLE 1651: Reproduction Boost | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing higher reproduction and conversion rates")
    print("=" * 70)

    seeds = [500001, 500002, 500003, 500004, 500005]

    # Test configurations: (f_mult, conv_mult, e_gain_mult)
    configs = [
        # Baseline
        (1.0, 1.0, 1.0),

        # Higher prey reproduction
        (2.0, 1.0, 1.0),
        (3.0, 1.0, 1.0),

        # Higher conversion rate
        (1.0, 2.0, 1.0),
        (1.0, 3.0, 1.0),

        # Higher energy gain
        (1.0, 1.0, 2.0),
        (1.0, 1.0, 3.0),

        # Combined boosts
        (2.0, 2.0, 2.0),
        (3.0, 3.0, 3.0),
    ]

    all_results = []

    for f_mult, conv_mult, e_gain_mult in configs:
        label = f"f={f_mult}x, conv={conv_mult}x, e_gain={e_gain_mult}x"
        print(f"\n{label}")

        results = [run_experiment(seed, f_mult, conv_mult, e_gain_mult) for seed in seeds]
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

    for r in all_results:
        if r["seed"] == 500001:
            status = "✓" if r["coexist"] else "✗"
            print(f"{status} f={r['f_mult']}x, conv={r['conv_mult']}x, gain={r['e_gain_mult']}x")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1651_reproduction_boost_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
