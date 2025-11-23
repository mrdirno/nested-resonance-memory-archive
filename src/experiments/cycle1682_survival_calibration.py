#!/usr/bin/env python3
"""
CYCLE 1682: SURVIVAL RATE CALIBRATION
C1681 found 15% low-energy ratio at n=25, but binomial model predicts only 31%.
We observe 96%. Need to calibrate actual D1 survival rates.
"""
import sys, json, numpy as np, math
from datetime import datetime
from scipy.stats import binom
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1682"
CYCLES = 30000
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

def compute_phase_resonance(e1, d1, e2, d2):
    pi1 = (e1 * PI * 2) % (2 * PI)
    e_1 = (d1 * E / 4) % (2 * PI)
    phi1 = (e1 * PHI) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    e_2 = (d2 * E / 4) % (2 * PI)
    phi2 = (e2 * PHI) % (2 * PI)
    v1 = [pi1, e_1, phi1]
    v2 = [pi2, e_2, phi2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def run_experiment(seed, n_initial=100):
    """Track D1 creation and survival to calibrate model."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    # Track D1 lifecycle
    d1_created = 0
    d1_decomposed = 0
    d1_peak = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track D1 peak
        d1_count = len(pops[1])
        if d1_count > d1_peak:
            d1_peak = d1_count

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition - track D1 creation
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    if d == 0:  # Created D1
                        d1_created += 1
                    i += 2
                else:
                    i += 1

        # Decomposition - track D1 loss
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    if d == 1:  # D1 decomposed
                        d1_decomposed += 1
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    # Survival rate = (created - decomposed) / created
    d1_survived = max(0, d1_created - d1_decomposed)
    survival_rate = d1_survived / d1_created if d1_created > 0 else 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "d1_created": d1_created,
        "d1_decomposed": d1_decomposed,
        "d1_survived": d1_survived,
        "survival_rate": survival_rate,
        "d1_peak": d1_peak
    }

def main():
    print(f"CYCLE 1682: Survival Calibration | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Calibrate D1 survival rate to explain 96% at n=25")
    print("=" * 70)

    seeds = list(range(1682001, 1682051))  # 50 seeds

    initial_sizes = [15, 20, 25, 30, 50, 100]
    all_results = []

    for n_init in initial_sizes:
        print(f"\nn_initial={n_init}")
        results = [run_experiment(seed, n_init) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        avg_created = np.mean([r["d1_created"] for r in results])
        avg_survived = np.mean([r["d1_survived"] for r in results])
        avg_rate = np.mean([r["survival_rate"] for r in results])
        avg_peak = np.mean([r["d1_peak"] for r in results])

        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    D1 created: {avg_created:.1f}, survived: {avg_survived:.1f}")
        print(f"    survival rate: {avg_rate*100:.1f}%, peak: {avg_peak:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("SURVIVAL CALIBRATION RESULTS")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Success':>7} | {'Created':>7} | {'Survived':>8} | {'Rate':>6} | {'Peak':>5}")
    print("-" * 55)

    for n_init in initial_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_created = np.mean([r["d1_created"] for r in subset])
        avg_survived = np.mean([r["d1_survived"] for r in subset])
        avg_surv_rate = np.mean([r["survival_rate"] for r in subset])
        avg_peak = np.mean([r["d1_peak"] for r in subset])
        print(f"{n_init:4d} | {rate*100:6.0f}% | {avg_created:7.1f} | {avg_survived:8.1f} | {avg_surv_rate*100:5.1f}% | {avg_peak:5.1f}")

    # Model prediction with calibrated rates
    print("\n" + "=" * 70)
    print("MODEL PREDICTION WITH CALIBRATED RATES")
    print("=" * 70)

    for n_init in initial_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        observed = sum(1 for r in subset if r["coexist"]) / len(subset)

        # Get average D1 peak (as proxy for "effective pool")
        avg_peak = np.mean([r["d1_peak"] for r in subset])

        # If peak >= 3, consider it success in simplified model
        # Actually use: P(success) = P(D1 establishes) where establish = peak >= threshold

        # Count how many had D1 peak >= 3
        peak_success = sum(1 for r in subset if r["d1_peak"] >= 3) / len(subset)

        print(f"n={n_init:3d}: observed={observed*100:.0f}%, peak>=3={peak_success*100:.0f}%")

    # Key insight
    print("\n" + "=" * 70)
    print("KEY INSIGHT")
    print("=" * 70)

    n25 = [r for r in all_results if r["n_initial"] == 25]
    n30 = [r for r in all_results if r["n_initial"] == 30]

    print(f"\nn=25 avg D1 peak: {np.mean([r['d1_peak'] for r in n25]):.1f}")
    print(f"n=30 avg D1 peak: {np.mean([r['d1_peak'] for r in n30]):.1f}")
    print(f"\nn=25 survival rate: {np.mean([r['survival_rate'] for r in n25])*100:.1f}%")
    print(f"n=30 survival rate: {np.mean([r['survival_rate'] for r in n30])*100:.1f}%")

if __name__ == "__main__":
    main()
