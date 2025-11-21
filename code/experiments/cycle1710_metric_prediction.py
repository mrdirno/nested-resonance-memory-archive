#!/usr/bin/env python3
"""
CYCLE 1710: METRIC-BASED PREDICTION
Can D1→D2 ratio predict optimal N at different parameters?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1710"
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

def run_prediction_test(seed, n_initial, recharge_rate):
    """Test metric at different recharge rates."""
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

        # Use specified recharge rate
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge_rate / (1 + d * 0.5), cap=2.0)

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
                if agent.energy > DECOMP_THRESHOLD:
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
        "recharge_rate": recharge_rate,
        "d1d2_ratio": d1d2_ratio,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1710: Metric Prediction | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Can D1→D2 ratio predict optimal N?")
    print("=" * 70)

    seeds = list(range(1710001, 1710021))  # 20 seeds
    population_sizes = [20, 25, 30, 35]
    recharge_rates = [0.05, 0.10, 0.15]

    for rate in recharge_rates:
        print(f"\n{'='*70}")
        print(f"RECHARGE RATE = {rate}")
        print(f"{'='*70}")
        print(f"\n{'N':>4} | {'D1→D2':>7} | {'Coexist':>8}")
        print("-" * 25)

        results_at_rate = []
        for n_init in population_sizes:
            results = [run_prediction_test(seed, n_init, rate) for seed in seeds]
            avg_ratio = np.mean([r["d1d2_ratio"] for r in results])
            coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100
            results_at_rate.append((n_init, avg_ratio, coexist))
            print(f"{n_init:4d} | {avg_ratio:7.2f} | {coexist:7.0f}%")

        # Find optimal
        best_ratio = max(results_at_rate, key=lambda x: x[1])
        best_coex = max(results_at_rate, key=lambda x: x[2])
        print(f"\nHighest D1→D2: n={best_ratio[0]} ({best_ratio[1]:.2f})")
        print(f"Highest coexist: n={best_coex[0]} ({best_coex[2]:.0f}%)")
        print(f"Prediction: {'CORRECT' if best_ratio[0] == best_coex[0] else 'INCORRECT'}")

if __name__ == "__main__":
    main()
