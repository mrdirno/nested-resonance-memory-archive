#!/usr/bin/env python3
"""
CYCLE 1667: DEPTH 4 THRESHOLD OPTIMIZATION
Problem: D4 compositions ≈ decompositions because threshold (1.3) < composed energy (1.7).
Test: Higher decomposition threshold at depth 4 to allow accumulation.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1667"
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

def run_experiment(seed, d4_threshold=1.3):
    """
    Run experiment with modified depth 4 decomposition threshold.
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    BASE_DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
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
                    i += 2
                else:
                    i += 1

        # Decomposition (depth-specific threshold for D4)
        for d in range(1, N_DEPTHS):
            threshold = d4_threshold if d == 4 else BASE_DECOMP_THRESHOLD
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > threshold:
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

    return {
        "seed": seed,
        "d4_threshold": d4_threshold,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "all5": depths_alive == 5
    }

def main():
    print(f"CYCLE 1667: Depth 4 Threshold | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1667001, 1667051))  # 50 seeds

    # Composed energy is ~1.7, so test thresholds above that
    thresholds = [1.3, 1.5, 1.8, 2.0, 2.5, 3.0]
    all_results = []

    for threshold in thresholds:
        print(f"\nd4_threshold={threshold}")
        results = [run_experiment(seed, threshold) for seed in seeds]

        all5_count = sum(1 for r in results if r["all5"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        avg_d4 = np.mean([r["finals"][4] for r in results])

        print(f"  → all 5: {all5_count}/{len(results)} ({all5_count/len(results)*100:.0f}%)")
        print(f"    avg depths: {avg_depths:.1f}, D4 final: {avg_d4:.1f}")

        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("DEPTH 4 THRESHOLD RESULTS")
    print("=" * 70)

    for threshold in thresholds:
        subset = [r for r in all_results if r["d4_threshold"] == threshold]
        all5_rate = sum(1 for r in subset if r["all5"]) / len(subset)
        three_plus = sum(1 for r in subset if r["depths_alive"] >= 3) / len(subset)
        avg_d4 = np.mean([r["finals"][4] for r in subset])
        print(f"threshold={threshold:.1f}: {all5_rate*100:5.1f}% all-5, {three_plus*100:.0f}% 3+, D4={avg_d4:.1f}")

if __name__ == "__main__":
    main()
