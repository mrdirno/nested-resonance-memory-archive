#!/usr/bin/env python3
"""
CYCLE 1658: CIRCULAR FLOW ARCHITECTURE
Test architectural improvement: depth 4 agents can decompose directly to depth 0.
This creates a complete cycle (0→1→2→3→4→0) instead of linear (0→1→2→3→4→3→2→1→0).
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1658"
CYCLES = 30000
N_DEPTHS = 5

DECAY_MULT = 0.1
REPRO_RATE = 0.1
DECOMP_THRESHOLD = 1.3

def run_experiment(seed, circular_prob=0.0):
    """
    Run experiment with circular flow.

    Args:
        circular_prob: Probability that depth 4 decomposition goes to depth 0
                      instead of depth 3 (creates closed loop)
    """
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1658_c{circular_prob}_s{seed}.db",
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

        # Decomposition with circular flow
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45

                    # Determine target depth
                    if d == N_DEPTHS - 1 and np.random.random() < circular_prob:
                        # Circular: depth 4 → depth 0
                        target_depth = 0
                    else:
                        # Normal: depth d → depth d-1
                        target_depth = d - 1

                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{target_depth}_{cycle}_{n_decomps}_{j}", target_depth, ce, depth=target_depth), target_depth)
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
        "circular_prob": circular_prob,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1658: Circular Flow Architecture | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing circular flow: depth 4 → depth 0 creates closed loop")
    print("=" * 70)

    seeds = list(range(970001, 970031))  # 30 seeds

    circular_probs = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    all_results = []

    for circular_prob in circular_probs:
        print(f"\ncircular={circular_prob}")
        results = [run_experiment(seed, circular_prob) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        rate = coexist_count / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({rate*100:.0f}%), avg depths={avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("CIRCULAR FLOW RESULTS")
    print("=" * 70)

    for circular_prob in circular_probs:
        subset = [r for r in all_results if r["circular_prob"] == circular_prob]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"circular={circular_prob}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Save
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1658_circular_flow_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
