#!/usr/bin/env python3
"""
CYCLE 1656: OPTIMIZE DECOMPOSITION
Test lower decomposition thresholds to prevent top-heavy accumulation.
Also test depth-dependent decomposition (higher depths decompose more easily).
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1656"
CYCLES = 30000
N_DEPTHS = 5
DECAY_MULT = 0.1
REPRO_RATE = 0.1

def run_experiment(seed, decomp_base, decomp_depth_factor=0.0):
    """
    Run experiment with configurable decomposition.

    Args:
        decomp_base: Base decomposition threshold
        decomp_depth_factor: How much threshold decreases per depth
                            (higher depths decompose more easily)
    """
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1656_d{decomp_base}_f{decomp_depth_factor}_s{seed}.db",
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
            if agent.energy > 1.0 and np.random.random() < REPRO_RATE:
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

        # Decomposition with depth-dependent threshold
        for d in range(1, N_DEPTHS):
            # Threshold decreases with depth (higher depths decompose more easily)
            threshold = decomp_base - d * decomp_depth_factor
            threshold = max(threshold, 0.5)  # Floor

            agents = list(reality.get_population_agents(d))
            for agent in agents:
                if agent.energy > threshold:
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
        "decomp_base": decomp_base,
        "decomp_depth_factor": decomp_depth_factor,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1656: Optimize Decomposition | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing lower/depth-dependent decomposition thresholds")
    print("=" * 70)

    seeds = list(range(950001, 950021))  # 20 seeds

    # Test configurations: (decomp_base, decomp_depth_factor)
    configs = [
        # Uniform threshold
        (1.5, 0.0),   # Current optimal
        (1.3, 0.0),   # Lower
        (1.1, 0.0),   # Even lower
        (1.0, 0.0),   # Aggressive

        # Depth-dependent
        (1.5, 0.1),   # Slight decrease per depth
        (1.5, 0.2),   # Moderate decrease
        (1.3, 0.1),   # Combined
        (1.3, 0.2),   # Combined aggressive
    ]

    all_results = []

    for decomp_base, depth_factor in configs:
        label = f"base={decomp_base}, factor={depth_factor}"
        print(f"\n{label}")

        results = [run_experiment(seed, decomp_base, depth_factor) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        rate = coexist_count / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])

        print(f"  → {coexist_count}/{len(results)} coexist ({rate*100:.0f}%), avg depths={avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("OPTIMIZATION RESULTS")
    print("=" * 70)

    for decomp_base, depth_factor in configs:
        subset = [r for r in all_results if r["decomp_base"] == decomp_base and r["decomp_depth_factor"] == depth_factor]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"base={decomp_base}, factor={depth_factor}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Save
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1656_optimize_decomposition_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
