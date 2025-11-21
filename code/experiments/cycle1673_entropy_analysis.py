#!/usr/bin/env python3
"""
CYCLE 1673: INFORMATION-THEORETIC ANALYSIS
Measure entropy and information content to understand the 80% limit.
Question: What distinguishes successful vs failed runs in information terms?
"""
import sys, json, numpy as np, math
from datetime import datetime
from collections import Counter
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1673"
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

def compute_entropy(populations):
    """Compute Shannon entropy of population distribution."""
    total = sum(populations)
    if total == 0:
        return 0.0
    probs = [p / total for p in populations if p > 0]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def compute_energy_entropy(agents):
    """Compute entropy of energy distribution (discretized)."""
    if not agents:
        return 0.0
    # Discretize energy into bins
    energies = [a.energy for a in agents]
    bins = [int(e * 10) for e in energies]  # 0.1 resolution
    counts = Counter(bins)
    total = len(bins)
    probs = [c / total for c in counts.values()]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def run_experiment(seed):
    """Run experiment with entropy tracking."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    # Entropy tracking
    pop_entropy_history = []
    energy_entropy_history = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)
        if total >= 3000 or total == 0: break

        # Calculate entropies every 100 cycles
        if cycle % 100 == 0:
            pop_entropy = compute_entropy(pop_counts)
            pop_entropy_history.append(pop_entropy)

            all_agents = []
            for d in range(N_DEPTHS):
                all_agents.extend(pops[d])
            energy_entropy = compute_energy_entropy(all_agents)
            energy_entropy_history.append(energy_entropy)

        # Standard dynamics
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

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

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

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

    # Calculate summary entropy metrics
    avg_pop_entropy = np.mean(pop_entropy_history) if pop_entropy_history else 0
    final_pop_entropy = pop_entropy_history[-1] if pop_entropy_history else 0
    avg_energy_entropy = np.mean(energy_entropy_history) if energy_entropy_history else 0
    final_energy_entropy = energy_entropy_history[-1] if energy_entropy_history else 0

    return {
        "seed": seed,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "avg_pop_entropy": round(avg_pop_entropy, 3),
        "final_pop_entropy": round(final_pop_entropy, 3),
        "avg_energy_entropy": round(avg_energy_entropy, 3),
        "final_energy_entropy": round(final_energy_entropy, 3)
    }

def main():
    print(f"CYCLE 1673: Entropy Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1673001, 1673101))  # 100 seeds
    results = [run_experiment(seed) for seed in seeds]

    # Separate success and failure
    success = [r for r in results if r["coexist"]]
    failure = [r for r in results if not r["coexist"]]

    rate = len(success) / len(results)
    print(f"\nOverall: {len(success)}/{len(results)} coexist ({rate*100:.0f}%)")

    # Compare entropy metrics
    print("\n" + "=" * 70)
    print("ENTROPY ANALYSIS")
    print("=" * 70)

    metrics = [
        ("avg_pop_entropy", "Avg population entropy"),
        ("final_pop_entropy", "Final population entropy"),
        ("avg_energy_entropy", "Avg energy entropy"),
        ("final_energy_entropy", "Final energy entropy")
    ]

    print(f"\n{'Metric':<30s} {'Success':>10s} {'Failure':>10s} {'Diff':>10s}")
    print("-" * 65)

    for key, name in metrics:
        if success and failure:
            s_val = np.mean([r[key] for r in success])
            f_val = np.mean([r[key] for r in failure])
            diff = s_val - f_val
            print(f"{name:<30s} {s_val:>10.3f} {f_val:>10.3f} {diff:>+10.3f}")

    # Distribution analysis
    print("\n" + "=" * 70)
    print("ENTROPY DISTRIBUTIONS")
    print("=" * 70)

    for key, name in metrics:
        values = [r[key] for r in results]
        print(f"{name}: mean={np.mean(values):.3f}, std={np.std(values):.3f}, "
              f"min={np.min(values):.3f}, max={np.max(values):.3f}")

if __name__ == "__main__":
    main()
