#!/usr/bin/env python3
"""
CYCLE 1663: EARLY BOOST INTERVENTION
Based on C1662 finding that successful runs have more turnover in first 100 cycles.
Test boosting reproduction/composition rates during establishment period.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1663"
CYCLES = 30000
N_DEPTHS = 5
BOOST_PERIOD = 100  # Cycles with boosted rates

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

def run_experiment(seed, early_boost=1.0):
    """
    Run experiment with early boost.

    Args:
        early_boost: Multiplier for reproduction rate during first BOOST_PERIOD cycles
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = n_decomps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Early boost period
        if cycle < BOOST_PERIOD:
            repro_rate = BASE_REPRO * early_boost
        else:
            repro_rate = BASE_REPRO

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction (boosted during establishment)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_rate:
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
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}_{n_comps}", d+1, new_e, depth=d+1), d+1)
                    n_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{n_decomps}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1

        # Energy decay
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
        "early_boost": early_boost,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1663: Early Boost | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Testing boosted reproduction during first {BOOST_PERIOD} cycles")
    print("=" * 70)

    seeds = list(range(1040001, 1040031))  # 30 seeds

    boosts = [1.0, 1.5, 2.0, 2.5, 3.0]
    all_results = []

    for boost in boosts:
        print(f"\nearly_boost={boost}x")
        results = [run_experiment(seed, boost) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        rate = coexist_count / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({rate*100:.0f}%), depths={avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("EARLY BOOST RESULTS")
    print("=" * 70)

    for boost in boosts:
        subset = [r for r in all_results if r["early_boost"] == boost]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"boost={boost}x: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1663_early_boost_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
