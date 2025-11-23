#!/usr/bin/env python3
"""
CYCLE 1653: BALANCED COMPOSITION-DECOMPOSITION
Fix energy balance issues from C1652:
- Energy input to all depths (not just depth 0)
- Lower decay rates
- Spontaneous reproduction at depth 0
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1653"
CYCLES = 30000
N_DEPTHS = 5

def run_experiment(seed, decay_mult=1.0, repro_rate=0.05):
    """
    Run balanced composition-decomposition experiment.
    """
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1653_d{decay_mult}_r{repro_rate}_s{seed}.db",
        n_populations=N_DEPTHS, mode="SEARCH"
    )
    np.random.seed(seed)

    # Initialize depth 0 agents
    initial_agents = 100
    for i in range(initial_agents):
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

        # =========== ENERGY INPUT ===========
        # All agents receive some energy (depth 0 gets most)
        for d in range(N_DEPTHS):
            e_input = 0.1 / (1 + d * 0.5)  # Decreases with depth
            for agent in pops[d]:
                agent.recharge_energy(e_input, cap=2.0)

        # =========== REPRODUCTION (depth 0 only) ===========
        d0_agents = list(reality.get_population_agents(0))
        for agent in d0_agents:
            if agent.energy > 1.0 and np.random.random() < repro_rate:
                child = FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0)
                reality.add_agent(child, 0)
                agent.energy -= 0.3

        # =========== COMPOSITION ===========
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2:
                continue

            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                a1 = agents[i]
                a2 = agents[i + 1]

                # Resonance check: similar energy
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

        # =========== DECOMPOSITION ===========
        for d in range(1, N_DEPTHS):
            agents = list(reality.get_population_agents(d))

            for agent in agents:
                if agent.energy > 1.5:  # Lower threshold
                    child_energy = agent.energy * 0.45

                    for j in range(2):
                        child_id = f"D{d-1}_{cycle}_{n_decomps}_{j}"
                        child = FractalAgent(child_id, d - 1, child_energy, depth=d - 1)
                        reality.add_agent(child, d - 1)

                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1

        # =========== ENERGY DECAY ===========
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * decay_mult  # Reduced decay
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        # Record history
        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    # Calculate finals
    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "decay_mult": decay_mult,
        "repro_rate": repro_rate,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "hist_len": len(histories[0]),
        "n_comps": n_comps,
        "n_decomps": n_decomps,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1653: Balanced Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing balanced energy input/decay with reproduction")
    print("=" * 70)

    seeds = [700001, 700002, 700003, 700004, 700005]

    # Test configurations: (decay_mult, repro_rate)
    configs = [
        # Baseline
        (1.0, 0.05),

        # Vary decay
        (0.5, 0.05),
        (0.3, 0.05),
        (0.1, 0.05),

        # Vary reproduction
        (0.5, 0.1),
        (0.5, 0.15),
        (0.3, 0.1),

        # Low decay + high reproduction
        (0.1, 0.1),
        (0.1, 0.15),
    ]

    all_results = []

    for decay_mult, repro_rate in configs:
        label = f"decay={decay_mult}x, repro={repro_rate}"
        print(f"\n{label}")

        results = [run_experiment(seed, decay_mult, repro_rate) for seed in seeds]
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

    configs_results = {}
    for r in all_results:
        key = (r["decay_mult"], r["repro_rate"])
        if key not in configs_results:
            configs_results[key] = []
        configs_results[key].append(r)

    for key in sorted(configs_results.keys()):
        results = configs_results[key]
        rate = sum(1 for r in results if r["coexist"]) / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"decay={key[0]}x, repro={key[1]}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1653_balanced_dynamics_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "results": all_results
        }, f, indent=2)

if __name__ == "__main__":
    main()
