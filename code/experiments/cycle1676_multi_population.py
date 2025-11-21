#!/usr/bin/env python3
"""
CYCLE 1676: MULTI-POPULATION INDEPENDENCE
Run multiple independent populations in parallel.
Question: Is the 80% limit reproducible across independent systems?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1676"
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

def run_single_population(reality, pop_id, histories):
    """Run one cycle for a single population."""
    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]

    # Energy input
    for d in range(N_DEPTHS):
        for agent in pops[d]:
            agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

    # Reproduction
    for agent in list(reality.get_population_agents(0)):
        if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
            reality.add_agent(FractalAgent(f"P{pop_id}_D0_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
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
                reality.add_agent(FractalAgent(f"P{pop_id}_D{d+1}", d+1, new_e, depth=d+1), d+1)
                i += 2
            else:
                i += 1

    # Decomposition
    for d in range(1, N_DEPTHS):
        for agent in list(reality.get_population_agents(d)):
            if agent.energy > DECOMP_THRESHOLD:
                ce = agent.energy * 0.45
                for j in range(2):
                    reality.add_agent(FractalAgent(f"P{pop_id}_D{d-1}_{j}", d-1, ce, depth=d-1), d-1)
                reality.remove_agent(agent.agent_id, d)

    # Decay
    for d in range(N_DEPTHS):
        decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
        for agent in list(reality.get_population_agents(d)):
            if not agent.consume_energy(decay):
                reality.remove_agent(agent.agent_id, d)

def run_experiment(seed, n_pops=5):
    """Run multiple independent populations."""
    np.random.seed(seed)

    # Create independent reality instances
    populations = []
    for p in range(n_pops):
        reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
        for i in range(100):
            reality.add_agent(FractalAgent(f"P{p}_D0_{i}", 0, 1.0, depth=0), 0)
        populations.append({
            'reality': reality,
            'histories': {d: [] for d in range(N_DEPTHS)}
        })

    # Run all populations in parallel
    for cycle in range(CYCLES):
        for p, pop in enumerate(populations):
            pops = [pop['reality'].get_population_agents(d) for d in range(N_DEPTHS)]
            total = sum(len(ps) for ps in pops)
            if 0 < total < 3000:
                run_single_population(pop['reality'], p, pop['histories'])

            if cycle % 100 == 0:
                for d in range(N_DEPTHS):
                    pop['histories'][d].append(len(pop['reality'].get_population_agents(d)))

    # Calculate results for each population
    results = []
    for p, pop in enumerate(populations):
        finals = {d: np.mean(pop['histories'][d][-10:]) if len(pop['histories'][d]) > 10 else 0 for d in range(N_DEPTHS)}
        depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)
        results.append(depths_alive >= 3)

    return {
        "seed": seed,
        "n_pops": n_pops,
        "coexist_count": sum(results),
        "coexist_rate": sum(results) / n_pops,
        "results": results
    }

def main():
    print(f"CYCLE 1676: Multi-Population | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1676001, 1676021))  # 20 experiments
    n_pops = 10  # 10 populations per experiment

    print(f"\nRunning {len(seeds)} experiments with {n_pops} populations each...")

    results = [run_experiment(seed, n_pops) for seed in seeds]

    # Aggregate results
    all_rates = [r["coexist_rate"] for r in results]
    total_pops = len(seeds) * n_pops
    total_success = sum(r["coexist_count"] for r in results)

    print("\n" + "=" * 70)
    print("MULTI-POPULATION RESULTS")
    print("=" * 70)

    print(f"\nTotal populations: {total_pops}")
    print(f"Successful: {total_success} ({total_success/total_pops*100:.1f}%)")

    print(f"\nPer-experiment success rates:")
    for r in results:
        print(f"  Seed {r['seed']}: {r['coexist_count']}/{r['n_pops']} = {r['coexist_rate']*100:.0f}%")

    print(f"\nStatistics:")
    print(f"  Mean rate: {np.mean(all_rates)*100:.1f}%")
    print(f"  Std: {np.std(all_rates)*100:.1f}%")
    print(f"  Min: {np.min(all_rates)*100:.0f}%")
    print(f"  Max: {np.max(all_rates)*100:.0f}%")

    # Test for 80% hypothesis
    expected = 0.80
    observed = total_success / total_pops
    se = np.sqrt(expected * (1 - expected) / total_pops)
    z = (observed - expected) / se

    print(f"\nHypothesis test (H0: rate = 80%):")
    print(f"  Observed: {observed*100:.1f}%")
    print(f"  Z-score: {z:.2f}")
    print(f"  Result: {'Consistent with 80%' if abs(z) < 1.96 else 'Differs from 80%'}")

if __name__ == "__main__":
    main()
