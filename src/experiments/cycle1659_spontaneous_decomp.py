#!/usr/bin/env python3
"""
CYCLE 1659: SPONTANEOUS DECOMPOSITION
Test architectural improvement: small random chance to decompose at high depths
regardless of energy. This prevents accumulation without disrupting energy balance.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1659"
CYCLES = 30000
N_DEPTHS = 5

DECAY_MULT = 0.1
REPRO_RATE = 0.1
DECOMP_THRESHOLD = 1.3

def run_experiment(seed, spontaneous_rate=0.0):
    """
    Run experiment with spontaneous decomposition.

    Args:
        spontaneous_rate: Base rate of spontaneous decomposition
                         Actual rate = spontaneous_rate * depth
    """
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1659_s{spontaneous_rate}_s{seed}.db",
        n_populations=N_DEPTHS, mode="SEARCH"
    )
    np.random.seed(seed)

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = n_decomps = 0

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
            if agent.energy > 1.0 and np.random.random() < REPRO_RATE:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                if abs(agents[i].energy - agents[i+1].energy) < 0.3:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}_{n_comps}", d+1, new_e, depth=d+1), d+1)
                    n_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition (energy-based + spontaneous)
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                # Energy-based decomposition
                decompose = agent.energy > DECOMP_THRESHOLD

                # Spontaneous decomposition (rate increases with depth)
                if not decompose and np.random.random() < spontaneous_rate * d:
                    decompose = True

                if decompose:
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
        "spontaneous_rate": spontaneous_rate,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1659: Spontaneous Decomposition | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing spontaneous decomposition to prevent top-heavy accumulation")
    print("=" * 70)

    seeds = list(range(980001, 980031))  # 30 seeds

    spontaneous_rates = [0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]
    all_results = []

    for rate in spontaneous_rates:
        print(f"\nspontaneous={rate}")
        results = [run_experiment(seed, rate) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        coex_rate = coexist_count / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({coex_rate*100:.0f}%), avg depths={avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("SPONTANEOUS DECOMPOSITION RESULTS")
    print("=" * 70)

    for rate in spontaneous_rates:
        subset = [r for r in all_results if r["spontaneous_rate"] == rate]
        coex_rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"spontaneous={rate}: {coex_rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Save
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1659_spontaneous_decomp_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
