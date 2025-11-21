#!/usr/bin/env python3
"""
CYCLE 1674: ENTROPY AS EARLY PREDICTOR
Test if entropy at cycle 100/500 can predict final success/failure.
"""
import sys, json, numpy as np, math
from datetime import datetime
from collections import Counter
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1674"
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

def run_experiment(seed):
    """Run experiment tracking entropy at checkpoints."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    entropy_100 = entropy_500 = entropy_1000 = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)
        if total >= 3000 or total == 0: break

        # Capture entropy at checkpoints
        if cycle == 100:
            entropy_100 = compute_entropy(pop_counts)
        elif cycle == 500:
            entropy_500 = compute_entropy(pop_counts)
        elif cycle == 1000:
            entropy_1000 = compute_entropy(pop_counts)

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

    return {
        "seed": seed,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "entropy_100": round(entropy_100, 3),
        "entropy_500": round(entropy_500, 3),
        "entropy_1000": round(entropy_1000, 3)
    }

def main():
    print(f"CYCLE 1674: Entropy Predictor | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1674001, 1674101))  # 100 seeds
    results = [run_experiment(seed) for seed in seeds]

    success = [r for r in results if r["coexist"]]
    failure = [r for r in results if not r["coexist"]]

    rate = len(success) / len(results)
    print(f"\nOverall: {len(success)}/{len(results)} coexist ({rate*100:.0f}%)")

    # Entropy at different checkpoints
    print("\n" + "=" * 70)
    print("ENTROPY AT CHECKPOINTS")
    print("=" * 70)

    checkpoints = [("entropy_100", "Cycle 100"), ("entropy_500", "Cycle 500"), ("entropy_1000", "Cycle 1000")]

    print(f"\n{'Checkpoint':<15s} {'Success':>10s} {'Failure':>10s} {'Diff':>10s}")
    print("-" * 50)

    for key, name in checkpoints:
        if success and failure:
            s_val = np.mean([r[key] for r in success])
            f_val = np.mean([r[key] for r in failure])
            diff = s_val - f_val
            print(f"{name:<15s} {s_val:>10.3f} {f_val:>10.3f} {diff:>+10.3f}")

    # Test prediction accuracy
    print("\n" + "=" * 70)
    print("PREDICTION ACCURACY")
    print("=" * 70)

    for threshold in [0.3, 0.5, 0.7, 0.9]:
        # Predict based on entropy_100
        predictions_100 = [(r["entropy_100"] >= threshold, r["coexist"]) for r in results]
        correct_100 = sum(1 for pred, actual in predictions_100 if pred == actual)
        acc_100 = correct_100 / len(results)

        predictions_500 = [(r["entropy_500"] >= threshold, r["coexist"]) for r in results]
        correct_500 = sum(1 for pred, actual in predictions_500 if pred == actual)
        acc_500 = correct_500 / len(results)

        print(f"threshold={threshold:.1f}: cycle100 {acc_100*100:.0f}%, cycle500 {acc_500*100:.0f}%")

if __name__ == "__main__":
    main()
