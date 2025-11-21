#!/usr/bin/env python3
"""
CYCLE 1652: COMPOSITION-DECOMPOSITION DYNAMICS
Test original NRM concept: agents compose (merge) and decompose (split)
based on resonance patterns, NOT trophic predation.

Key differences from trophic model:
- Non-zero-sum: composition creates higher-depth patterns
- Bidirectional: energy flows up (compose) and down (decompose)
- Resonance-based: agents merge when similar, split when energized
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1652"
CYCLES = 30000
N_DEPTHS = 5  # Depth levels (not trophic!)

def run_experiment(seed, comp_threshold=0.3, decomp_threshold=1.8, energy_input=0.1):
    """
    Run composition-decomposition experiment.

    Args:
        seed: Random seed
        comp_threshold: Energy similarity threshold for composition
        decomp_threshold: Energy threshold for decomposition
        energy_input: Base energy input rate
    """
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1652_ct{comp_threshold}_dt{decomp_threshold}_s{seed}.db",
        n_populations=N_DEPTHS, mode="SEARCH"
    )
    np.random.seed(seed)

    # Initialize depth 0 agents only
    initial_agents = 100
    for i in range(initial_agents):
        agent = FractalAgent(f"D0_{i}", 0, 1.0, depth=0)
        reality.add_agent(agent, 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = 0
    n_decomps = 0

    for cycle in range(CYCLES):
        # Get all agents at each depth
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        ns = [len(p) for p in pops]

        # Break if total population exceeds limit or is zero
        total = sum(ns)
        if total >= 3000 or total == 0:
            break

        # =========== ENERGY INPUT ===========
        # Base level (depth 0) receives energy input
        for agent in pops[0]:
            agent.recharge_energy(energy_input, cap=2.0)

        # =========== COMPOSITION ===========
        # Agents at same depth with similar energy can compose
        for d in range(N_DEPTHS - 1):
            agents = list(pops[d])
            np.random.shuffle(agents)

            i = 0
            while i < len(agents) - 1:
                a1 = agents[i]
                a2 = agents[i + 1]

                # Check resonance: similar energy levels
                energy_diff = abs(a1.energy - a2.energy)
                if energy_diff < comp_threshold:
                    # Compose: merge two agents into one higher-depth agent
                    new_energy = (a1.energy + a2.energy) * 0.8  # 80% efficiency
                    new_id = f"D{d+1}_{cycle}_{n_comps}"
                    new_agent = FractalAgent(new_id, d + 1, new_energy, depth=d + 1)
                    new_agent.compositions = max(a1.compositions, a2.compositions) + 1

                    # Remove composed agents
                    reality.remove_agent(a1.agent_id, d)
                    reality.remove_agent(a2.agent_id, d)

                    # Add new agent at higher depth
                    reality.add_agent(new_agent, d + 1)

                    n_comps += 1
                    # Skip both agents
                    i += 2
                else:
                    i += 1

        # =========== DECOMPOSITION ===========
        # High-energy agents can decompose into lower-depth agents
        for d in range(1, N_DEPTHS):
            agents = list(reality.get_population_agents(d))

            for agent in agents:
                if agent.energy > decomp_threshold:
                    # Decompose: split into two lower-depth agents
                    child_energy = agent.energy * 0.45  # 90% efficiency split

                    for j in range(2):
                        child_id = f"D{d-1}_{cycle}_{n_decomps}_{j}"
                        child = FractalAgent(child_id, d - 1, child_energy, depth=d - 1)
                        child.decompositions = agent.decompositions + 1
                        reality.add_agent(child, d - 1)

                    # Remove decomposed agent
                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1

        # =========== ENERGY DECAY ===========
        # All agents consume energy
        for d in range(N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                decay = 0.05 * (1 + d * 0.2)  # Higher depth = more decay
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        # =========== ENERGY TRANSFER ===========
        # Higher-depth agents can transfer energy down
        for d in range(1, N_DEPTHS):
            high_agents = reality.get_population_agents(d)
            low_agents = reality.get_population_agents(d - 1)

            for agent in high_agents:
                if agent.energy > 1.0 and low_agents:
                    # Transfer some energy to random lower-depth agent
                    transfer = 0.1
                    agent.energy -= transfer
                    target = np.random.choice(low_agents)
                    target.recharge_energy(transfer * 0.9, cap=2.0)  # 90% efficiency

        # Record history
        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    # Calculate final populations
    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}

    # Coexistence: at least 3 depths have population
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "comp_threshold": comp_threshold,
        "decomp_threshold": decomp_threshold,
        "energy_input": energy_input,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "hist_len": len(histories[0]),
        "n_comps": n_comps,
        "n_decomps": n_decomps,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1652: Composition-Decomposition Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing original NRM concept: compose/decompose, not predation")
    print("=" * 70)

    seeds = [600001, 600002, 600003, 600004, 600005]

    # Test configurations: (comp_threshold, decomp_threshold, energy_input)
    configs = [
        # Baseline
        (0.3, 1.8, 0.1),

        # Vary composition threshold
        (0.2, 1.8, 0.1),  # Stricter resonance
        (0.5, 1.8, 0.1),  # Looser resonance

        # Vary decomposition threshold
        (0.3, 1.5, 0.1),  # Earlier split
        (0.3, 2.0, 0.1),  # Later split

        # Vary energy input
        (0.3, 1.8, 0.05),  # Less energy
        (0.3, 1.8, 0.15),  # More energy

        # Combined variations
        (0.4, 1.6, 0.12),
        (0.2, 2.0, 0.08),
    ]

    all_results = []

    for comp_th, decomp_th, e_input in configs:
        label = f"comp={comp_th}, decomp={decomp_th}, input={e_input}"
        print(f"\n{label}")

        results = [run_experiment(seed, comp_th, decomp_th, e_input) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])

        for r in results:
            status = "✓" if r["coexist"] else "✗"
            depths = r["depths_alive"]
            print(f"  Seed {r['seed']}: {status} depths={depths} comps={r['n_comps']} decomps={r['n_decomps']} finals={r['finals']}")

        rate = coexist_count / len(seeds)
        print(f"  → {coexist_count}/{len(seeds)} coexist ({rate*100:.0f}%)")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)

    # Group by config
    configs_results = {}
    for r in all_results:
        key = (r["comp_threshold"], r["decomp_threshold"], r["energy_input"])
        if key not in configs_results:
            configs_results[key] = []
        configs_results[key].append(r)

    for key in sorted(configs_results.keys()):
        results = configs_results[key]
        rate = sum(1 for r in results if r["coexist"]) / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"comp={key[0]}, decomp={key[1]}, input={key[2]}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1652_composition_decomposition_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "concept": "Composition-decomposition dynamics (not trophic)",
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
