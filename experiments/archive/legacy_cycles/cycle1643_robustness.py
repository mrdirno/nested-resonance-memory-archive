#!/usr/bin/env python3
"""
CYCLE 1643: ROBUSTNESS TEST
Tests optimal parameters (attack ×0.5, magnitude 0.25) with large sample.
Validates 100% coexistence finding with high confidence.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1643"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
INITIAL = [300, 30, 10, 5, 3, 2, 2]

# Optimal parameters from C1642
ATTACK_MULT = 0.5
MAGNITUDE = 0.25

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

def run_experiment(seed):
    params = get_params()
    n_levels = 7
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1643_seed{seed}.db", n_populations=n_levels, mode="ROBUST")
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

    finals = {i: np.mean(histories[i][-10:]) if len(histories[i]) > 10 else 0.0 for i in range(n_levels)}
    return {"seed": seed, "coexist": all(finals[i] >= 0.5 for i in range(n_levels)), "finals": finals}

def main():
    print(f"CYCLE 1643: Robustness Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Testing optimal parameters (attack ×{ATTACK_MULT}, mag {MAGNITUDE})")
    print("n=100 for high confidence")
    print("=" * 70)

    seeds = list(range(140001, 140101))  # 100 seeds
    results = []

    for i, seed in enumerate(seeds, 1):
        r = run_experiment(seed)
        if i == 1:
            print(f"DEBUG: Seed {seed} Result: {r}")
            # We can't easily access internal vars here, so we'll rely on the return value.
            # But wait, run_experiment returns a dict. I should modify run_experiment to print debug info.
        results.append(r)
        if i % 20 == 0:
            current = sum(1 for r in results if r["coexist"])
            print(f"  [{i}/100] {current}/{i} ({current/i*100:.0f}%)")

    # Final results
    coexist = sum(1 for r in results if r["coexist"])
    rate = coexist / len(results)

    print("\n" + "=" * 70)
    print("ROBUSTNESS TEST RESULTS")
    print("=" * 70)

    bar = "█" * int(rate * 50) + "░" * (50 - int(rate * 50))
    print(f"\n{bar}")
    print(f"\nCoexistence: {coexist}/100 ({rate*100:.0f}%)")

    # 95% confidence interval (Wilson score)
    from scipy.stats import norm
    z = 1.96
    n = len(results)
    p = rate
    denom = 1 + z**2 / n
    center = (p + z**2 / (2*n)) / denom
    spread = z * np.sqrt((p * (1-p) + z**2 / (4*n)) / n) / denom
    ci_low = max(0, center - spread)
    ci_high = min(1, center + spread)

    print(f"95% CI: [{ci_low*100:.1f}%, {ci_high*100:.1f}%]")

    if rate == 1.0:
        print("\n🎯 PERFECT 100% COEXISTENCE CONFIRMED")
    elif rate >= 0.95:
        print(f"\n✅ Near-perfect coexistence ({rate*100:.0f}%)")
    else:
        print(f"\n⚠️ Coexistence below expectations ({rate*100:.0f}%)")

    # List any failures
    failures = [r["seed"] for r in results if not r["coexist"]]
    if failures:
        print(f"\nFailed seeds: {failures}")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1643_robustness_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "attack_mult": ATTACK_MULT,
            "magnitude": MAGNITUDE,
            "n_seeds": len(seeds),
            "coexist_count": coexist,
            "rate": rate,
            "ci_95": [ci_low, ci_high],
            "failed_seeds": failures,
            "results": results
        }, f, indent=2)

if __name__ == "__main__":
    main()
