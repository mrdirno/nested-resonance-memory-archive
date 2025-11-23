#!/usr/bin/env python3
"""
CYCLE 1655: OPTIMIZE REPRODUCTION RATE
Test higher reproduction rates to prevent depth 0 collapse.
Target: Improve 72% coexistence to >90%.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1655"
CYCLES = 30000
N_DEPTHS = 5
DECAY_MULT = 0.1  # Keep optimal

def run_experiment(seed, repro_rate):
    """Run experiment with specified reproduction rate."""
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1655_r{repro_rate}_s{seed}.db",
        n_populations=N_DEPTHS, mode="SEARCH"
    )
    np.random.seed(seed)

    for i in range(100):
        agent = FractalAgent(f"D0_{i}", 0, 1.0, depth=0)
        reality.add_agent(agent, 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = 0
    n_decomps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        ns = [len(p) for p in pops]
        total = sum(ns)

        if total >= 3000 or total == 0:
            break

        # Energy input
        for d in range(N_DEPTHS):
            e_input = 0.1 / (1 + d * 0.5)
            for agent in pops[d]:
                agent.recharge_energy(e_input, cap=2.0)

        # Reproduction
        d0_agents = list(reality.get_population_agents(0))
        for agent in d0_agents:
            if agent.energy > 1.0 and np.random.random() < repro_rate:
                child = FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0)
                reality.add_agent(child, 0)
                agent.energy -= 0.3

        # Composition
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2:
                continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                a1 = agents[i]
                a2 = agents[i + 1]
                if abs(a1.energy - a2.energy) < 0.3:
                    new_energy = (a1.energy + a2.energy) * 0.85
                    new_id = f"D{d+1}_{cycle}_{n_comps}"
                    new_agent = FractalAgent(new_id, d + 1, new_energy, depth=d + 1)
                    reality.remove_agent(a1.agent_id, d)
                    reality.remove_agent(a2.agent_id, d)
                    reality.add_agent(new_agent, d + 1)
                    n_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            agents = list(reality.get_population_agents(d))
            for agent in agents:
                if agent.energy > 1.5:
                    child_energy = agent.energy * 0.45
                    for j in range(2):
                        child_id = f"D{d-1}_{cycle}_{n_decomps}_{j}"
                        child = FractalAgent(child_id, d - 1, child_energy, depth=d - 1)
                        reality.add_agent(child, d - 1)
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
        "repro_rate": repro_rate,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1655: Optimize Reproduction | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing higher reproduction rates to improve coexistence")
    print("=" * 70)

    seeds = list(range(900001, 900021))  # 20 seeds per rate

    repro_rates = [0.1, 0.15, 0.2, 0.25, 0.3]
    all_results = []

    for repro_rate in repro_rates:
        print(f"\nrepro={repro_rate}")
        results = [run_experiment(seed, repro_rate) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        rate = coexist_count / len(results)

        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({rate*100:.0f}%), avg depths={avg_depths:.1f}")

        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("OPTIMIZATION RESULTS")
    print("=" * 70)

    for repro_rate in repro_rates:
        subset = [r for r in all_results if r["repro_rate"] == repro_rate]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"repro={repro_rate}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Save
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1655_optimize_reproduction_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
