#!/usr/bin/env python3
"""
CYCLE 1690: ADAPTIVE POPULATION STRATEGIES
Can we achieve >96% by adapting population based on early dynamics?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1690"
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

def run_adaptive_experiment(seed, strategy="fixed"):
    """Run with adaptive population strategy."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    # Initial population depends on strategy
    if strategy == "fixed":
        n_initial = 25
    elif strategy == "overshoot":
        n_initial = 30  # Start higher, then cull
    elif strategy == "undershoot":
        n_initial = 20  # Start lower, then add
    elif strategy == "bootstrap":
        n_initial = 50  # Big start, let system find balance

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    adaptations_made = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Adaptive interventions at cycle 10
        if cycle == 10:
            d1_count = len(pops[1])

            if strategy == "overshoot":
                # If D1 is 0, we overshot - remove some D0
                if d1_count == 0 and len(pops[0]) > 10:
                    to_remove = list(pops[0])[:5]
                    for agent in to_remove:
                        reality.remove_agent(agent.agent_id, 0)
                    adaptations_made = 1

            elif strategy == "undershoot":
                # If D1 is 0, we undershot - add more D0
                if d1_count == 0:
                    for i in range(5):
                        reality.add_agent(FractalAgent(f"D0_add_{i}", 0, 1.0, depth=0), 0)
                    adaptations_made = 1

            elif strategy == "bootstrap":
                # If we have D1, we're good - otherwise intervention needed
                if d1_count == 0:
                    # Add low-energy D1 directly
                    for i in range(3):
                        reality.add_agent(FractalAgent(f"D1_seed_{i}", 1, 0.9, depth=1), 1)
                    adaptations_made = 1

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
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
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Decay
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
        "strategy": strategy,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "adaptations": adaptations_made
    }

def main():
    print(f"CYCLE 1690: Adaptive Population | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Can adaptive strategies beat fixed n=25 (96%)?")
    print("=" * 70)

    seeds = list(range(1690001, 1690101))  # 100 seeds

    strategies = ["fixed", "overshoot", "undershoot", "bootstrap"]
    all_results = []

    for strategy in strategies:
        print(f"\nStrategy: {strategy}")
        results = [run_adaptive_experiment(seed, strategy) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        adapt_count = sum(r["adaptations"] for r in results)
        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    Adaptations triggered: {adapt_count}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("ADAPTIVE STRATEGY COMPARISON")
    print("=" * 70)
    print(f"\n{'Strategy':>12} | {'Success':>10} | {'Adaptations':>12}")
    print("-" * 40)

    for strategy in strategies:
        subset = [r for r in all_results if r["strategy"] == strategy]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        adapts = sum(r["adaptations"] for r in subset)
        print(f"{strategy:>12} | {rate*100:9.0f}% | {adapts:12d}")

if __name__ == "__main__":
    main()
