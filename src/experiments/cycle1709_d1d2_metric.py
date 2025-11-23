#!/usr/bin/env python3
"""
CYCLE 1709: D1→D2 AS SUCCESS PREDICTOR
Does D1→D2 ratio correlate with coexistence better than offspring ratio?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1709"
CYCLES = 1000
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
DECOMP_THRESHOLD = 1.3
RESONANCE_THRESHOLD = 0.5

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

def run_metric_test(seed, n_initial, decomp_thresh):
    """Track D1→D2 metric at different thresholds."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    d0_to_d1 = 0
    d1_to_d2 = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

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
                    if d == 0:
                        d0_to_d1 += 1
                    elif d == 1:
                        d1_to_d2 += 1
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2

    d1d2_ratio = d1_to_d2 / d0_to_d1 if d0_to_d1 > 0 else 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "decomp_thresh": decomp_thresh,
        "d0_to_d1": d0_to_d1,
        "d1_to_d2": d1_to_d2,
        "d1d2_ratio": d1d2_ratio,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1709: D1→D2 Metric | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Does D1→D2 ratio predict success?")
    print("=" * 70)

    seeds = list(range(1709001, 1709021))  # 20 seeds
    population_sizes = [20, 25, 30, 35]
    thresholds = [1.1, 1.3, 1.5]

    for thresh in thresholds:
        print(f"\n{'='*70}")
        print(f"DECOMPOSITION THRESHOLD = {thresh}")
        print(f"{'='*70}")
        print(f"\n{'N':>4} | {'D0→D1':>7} | {'D1→D2':>7} | {'Ratio':>7} | {'Coexist':>8}")
        print("-" * 45)

        results_at_thresh = []
        for n_init in population_sizes:
            results = [run_metric_test(seed, n_init, thresh) for seed in seeds]
            avg_d0d1 = np.mean([r["d0_to_d1"] for r in results])
            avg_d1d2 = np.mean([r["d1_to_d2"] for r in results])
            avg_ratio = np.mean([r["d1d2_ratio"] for r in results])
            coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100
            results_at_thresh.append((n_init, avg_d0d1, avg_d1d2, avg_ratio, coexist))
            print(f"{n_init:4d} | {avg_d0d1:7.1f} | {avg_d1d2:7.1f} | {avg_ratio:7.2f} | {coexist:7.0f}%")

        # Find optimal by ratio and coexistence
        best_ratio = max(results_at_thresh, key=lambda x: x[3])
        best_coex = max(results_at_thresh, key=lambda x: x[4])
        print(f"\nHighest D1→D2 ratio: n={best_ratio[0]} ({best_ratio[3]:.2f})")
        print(f"Highest coexistence: n={best_coex[0]} ({best_coex[4]:.0f}%)")

if __name__ == "__main__":
    main()
