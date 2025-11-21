#!/usr/bin/env python3
"""
CYCLE 1647: EMERGENT DYNAMICS ANALYSIS
Analyzes population dynamics at optimal parameters for:
- Oscillations, cycles, or stable equilibrium
- Cross-level correlations
- Phase relationships between trophic levels
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2/experiments')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1647"
CYCLES = 30000
K_START, K_END, DECLINE_CYCLES = 600, 200, 40
MAGNITUDE = 0.25
ATTACK_MULT = 0.5
INITIAL = [300, 30, 10, 5, 3, 2, 2]

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
    reality = RealityInterface(db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1647_seed{seed}.db", n_populations=n_levels, mode="DYNAMICS")
    np.random.seed(seed)

    for lvl in range(n_levels):
        for i in range(INITIAL[lvl]):
            reality.add_agent(FractalAgent(f"L{lvl}_{i}", lvl, 1.0 + lvl * 0.5), lvl)

    # High-resolution history for dynamics analysis
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

        # Record every 10 cycles for higher resolution
        if cycle % 10 == 0:
            for i in range(n_levels):
                histories[i].append(len(reality.get_population_agents(i)))

        if all(n == 0 for n in ns[:3]): break

    return histories

def analyze_dynamics(histories, n_levels=7):
    """Analyze population dynamics for patterns."""
    results = {}

    for lvl in range(n_levels):
        data = np.array(histories[lvl])
        if len(data) < 100:
            results[lvl] = {"status": "collapsed"}
            continue

        # Use last 2000 cycles (200 data points) for equilibrium analysis
        eq_data = data[-200:] if len(data) >= 200 else data

        mean = np.mean(eq_data)
        std = np.std(eq_data)
        cv = std / mean if mean > 0 else 0  # Coefficient of variation

        # FFT for oscillation detection
        if len(eq_data) >= 50:
            fft = np.abs(np.fft.fft(eq_data - mean))
            freqs = np.fft.fftfreq(len(eq_data))
            # Find dominant frequency (excluding DC)
            pos_freqs = freqs[1:len(freqs)//2]
            pos_fft = fft[1:len(fft)//2]
            if len(pos_fft) > 0:
                dom_idx = np.argmax(pos_fft)
                dom_freq = abs(pos_freqs[dom_idx])
                dom_power = pos_fft[dom_idx] / np.sum(pos_fft) if np.sum(pos_fft) > 0 else 0
            else:
                dom_freq = 0
                dom_power = 0
        else:
            dom_freq = 0
            dom_power = 0

        results[lvl] = {
            "mean": float(mean),
            "std": float(std),
            "cv": float(cv),
            "dom_freq": float(dom_freq),
            "dom_power": float(dom_power)
        }

    return results

def cross_correlations(histories, n_levels=7):
    """Calculate cross-correlations between adjacent levels."""
    correlations = []
    for lvl in range(n_levels - 1):
        data1 = np.array(histories[lvl])
        data2 = np.array(histories[lvl + 1])
        min_len = min(len(data1), len(data2))
        if min_len > 100:
            # Use last portion for correlation
            d1 = data1[-200:] if len(data1) >= 200 else data1
            d2 = data2[-200:] if len(data2) >= 200 else data2
            min_eq = min(len(d1), len(d2))
            corr = np.corrcoef(d1[:min_eq], d2[:min_eq])[0, 1]
            correlations.append({"levels": f"L{lvl}-L{lvl+1}", "correlation": float(corr)})
    return correlations

def main():
    print(f"CYCLE 1647: Emergent Dynamics Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Analyzing population dynamics at optimal parameters")
    print("=" * 70)

    seeds = list(range(180001, 180011))  # 10 seeds for detailed analysis
    all_dynamics = []
    all_correlations = []

    for seed in seeds:
        print(f"\nSeed {seed}")
        histories = run_experiment(seed)
        dynamics = analyze_dynamics(histories)
        correlations = cross_correlations(histories)

        all_dynamics.append({"seed": seed, "dynamics": dynamics})
        all_correlations.append({"seed": seed, "correlations": correlations})

        # Print summary
        for lvl in range(7):
            d = dynamics[lvl]
            if "status" in d:
                print(f"  L{lvl}: {d['status']}")
            else:
                osc = "oscillating" if d['dom_power'] > 0.2 else "stable"
                print(f"  L{lvl}: mean={d['mean']:.1f}, cv={d['cv']:.2f} ({osc})")

    # Aggregate analysis
    print("\n" + "=" * 70)
    print("AGGREGATE DYNAMICS ANALYSIS")
    print("=" * 70)

    # Average CV and oscillation across seeds
    avg_cv = {lvl: [] for lvl in range(7)}
    avg_osc = {lvl: [] for lvl in range(7)}

    for result in all_dynamics:
        for lvl in range(7):
            d = result["dynamics"][lvl]
            if "cv" in d:
                avg_cv[lvl].append(d["cv"])
                avg_osc[lvl].append(d["dom_power"])

    print("\nLevel | Mean CV | Mean Osc Power | Behavior")
    print("-" * 50)
    for lvl in range(7):
        if avg_cv[lvl]:
            cv = np.mean(avg_cv[lvl])
            osc = np.mean(avg_osc[lvl])
            behavior = "oscillating" if osc > 0.2 else ("noisy" if cv > 0.3 else "stable")
            print(f"  L{lvl}  |  {cv:.3f}  |     {osc:.3f}      | {behavior}")

    # Average correlations
    print("\n" + "=" * 70)
    print("CROSS-LEVEL CORRELATIONS")
    print("=" * 70)

    avg_corrs = {}
    for result in all_correlations:
        for c in result["correlations"]:
            key = c["levels"]
            if key not in avg_corrs:
                avg_corrs[key] = []
            avg_corrs[key].append(c["correlation"])

    print("\nLevel Pair | Mean Correlation | Interpretation")
    print("-" * 55)
    for pair, values in avg_corrs.items():
        mean_corr = np.mean(values)
        if mean_corr > 0.5:
            interp = "strongly coupled"
        elif mean_corr > 0:
            interp = "positively coupled"
        elif mean_corr > -0.5:
            interp = "weakly anti-coupled"
        else:
            interp = "predator-prey cycle"
        print(f"  {pair}   |      {mean_corr:.3f}       | {interp}")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1647_emergent_dynamics_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "attack_mult": ATTACK_MULT,
            "magnitude": MAGNITUDE,
            "n_seeds": len(seeds),
            "dynamics": all_dynamics,
            "correlations": all_correlations
        }, f, indent=2)

if __name__ == "__main__":
    main()
