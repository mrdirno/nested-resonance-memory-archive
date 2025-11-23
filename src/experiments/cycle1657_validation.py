#!/usr/bin/env python3
"""
CYCLE 1657: VALIDATION - OPTIMAL PARAMETERS
Validate optimal parameters (decay=0.1, repro=0.1, decomp=1.3) with 50 seeds.
"""
import sys, json, numpy as np
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1657"
CYCLES = 30000
N_DEPTHS = 5

# Optimal parameters
DECAY_MULT = 0.1
REPRO_RATE = 0.1
DECOMP_THRESHOLD = 1.3

def run_experiment(seed):
    reality = RealityInterface(
        db_path=f"/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1657_s{seed}.db",
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
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1657: Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print(f"Validating optimal: decay={DECAY_MULT}, repro={REPRO_RATE}, decomp={DECOMP_THRESHOLD}")
    print("=" * 70)

    seeds = list(range(960001, 960051))  # 50 seeds
    results = [run_experiment(seed) for seed in seeds]

    coexist_count = sum(1 for r in results if r["coexist"])
    rate = coexist_count / len(results)

    print(f"\nResult: {coexist_count}/{len(results)} = {rate*100:.1f}%")

    # Wilson CI
    z = 1.96
    n = len(results)
    p = rate
    denom = 1 + z**2/n
    center = (p + z**2/(2*n))/denom
    spread = z * np.sqrt(p*(1-p)/n + z**2/(4*n**2))/denom
    ci_low = max(0, center - spread) * 100
    ci_high = min(1, center + spread) * 100
    print(f"95% CI: [{ci_low:.1f}%, {ci_high:.1f}%]")

    avg_depths = np.mean([r["depths_alive"] for r in results])
    print(f"Average depths: {avg_depths:.2f}")

    # Save
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1657_validation_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "parameters": {"decay_mult": DECAY_MULT, "repro_rate": REPRO_RATE, "decomp_threshold": DECOMP_THRESHOLD},
            "coexistence_rate": rate,
            "ci_95": [ci_low, ci_high],
            "results": results
        }, f, indent=2)

if __name__ == "__main__":
    main()
