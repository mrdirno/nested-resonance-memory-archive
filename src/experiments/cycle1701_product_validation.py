#!/usr/bin/env python3
"""
CYCLE 1701: PRODUCT MODEL VALIDATION
Does Matched × Low_Ratio predict success across parameter variations?
Test at different decomposition thresholds.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1701"
CYCLES = 100
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
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

def run_product_analysis(seed, n_initial, decomp_threshold):
    """Track product metric at given parameters."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    matched = 0
    low_count = 0

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
                        matched += 1
                        if new_e < decomp_threshold:
                            low_count += 1
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_threshold:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    low_ratio = low_count / matched if matched > 0 else 0
    effective = matched * low_ratio

    return {
        "seed": seed,
        "n_initial": n_initial,
        "decomp_threshold": decomp_threshold,
        "matched": matched,
        "low_count": low_count,
        "low_ratio": low_ratio,
        "effective": effective
    }

def main():
    print(f"CYCLE 1701: Product Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Does Matched × Low_Ratio predict across parameters?")
    print("=" * 70)

    seeds = list(range(1701001, 1701011))  # 10 seeds for speed
    population_sizes = [15, 20, 25, 30, 35]
    thresholds = [1.1, 1.3, 1.5, 1.7]

    for thresh in thresholds:
        print(f"\n{'='*70}")
        print(f"DECOMPOSITION THRESHOLD = {thresh}")
        print(f"{'='*70}")
        print(f"\n{'N':>4} | {'Matched':>8} | {'Low%':>6} | {'Effective':>10}")
        print("-" * 40)

        results_at_thresh = []
        for n_init in population_sizes:
            results = [run_product_analysis(seed, n_init, thresh) for seed in seeds]
            avg_matched = np.mean([r["matched"] for r in results])
            avg_low = np.mean([r["low_ratio"] for r in results])
            avg_eff = np.mean([r["effective"] for r in results])
            results_at_thresh.append((n_init, avg_matched, avg_low, avg_eff))
            print(f"{n_init:4d} | {avg_matched:8.1f} | {avg_low:5.1%} | {avg_eff:10.1f}")

        # Find optimal N
        optimal_n = max(results_at_thresh, key=lambda x: x[3])
        print(f"\nOptimal N at thresh={thresh}: n={optimal_n[0]} (eff={optimal_n[3]:.1f})")

if __name__ == "__main__":
    main()
