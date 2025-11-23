#!/usr/bin/env python3
"""
CYCLE 1672: ADAPTIVE SELF-TUNING PARAMETERS
Test systems that adjust parameters based on current state.
Can dynamic tuning improve on the 80% limit?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1672"
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

def run_experiment(seed, adaptive='none'):
    """
    Run experiment with different adaptive strategies.

    adaptive:
    - 'none': Fixed parameters
    - 'population': Adjust based on total population
    - 'd1_rescue': Boost D1 when population low
    - 'full': Multiple adaptive rules
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # Base parameters
    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Adaptive parameter tuning
        repro = BASE_REPRO
        decay_mult = DECAY_MULT
        decomp_threshold = DECOMP_THRESHOLD
        resonance_threshold = RESONANCE_THRESHOLD

        if adaptive == 'population':
            # Adjust based on total population
            if total < 50:
                repro = 0.2  # Boost reproduction
                decay_mult = 0.05  # Reduce decay
            elif total > 200:
                repro = 0.05
                decay_mult = 0.15

        elif adaptive == 'd1_rescue':
            # Rescue D1 when low
            d1_pop = len(pops[1])
            if d1_pop == 0:
                resonance_threshold = 0.3  # Easier composition
                decomp_threshold = 2.0  # Protect D1
            elif d1_pop < 3:
                decomp_threshold = 1.8

        elif adaptive == 'full':
            # Multiple adaptive rules
            d1_pop = len(pops[1])

            # Population-based
            if total < 50:
                repro = 0.2
                decay_mult = 0.05
            elif total > 200:
                repro = 0.05
                decay_mult = 0.15

            # D1-based
            if d1_pop == 0:
                resonance_threshold = 0.3
                decomp_threshold = 2.0
            elif d1_pop < 3:
                decomp_threshold = 1.8

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro:
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
                if sim >= resonance_threshold:
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
                if agent.energy > decomp_threshold:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * decay_mult
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
        "adaptive": adaptive,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1672: Adaptive Parameters | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1672001, 1672101))  # 100 seeds

    strategies = ['none', 'population', 'd1_rescue', 'full']
    all_results = []

    for strategy in strategies:
        print(f"\nadaptive={strategy}")
        results = [run_experiment(seed, strategy) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    avg depths: {avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("ADAPTIVE PARAMETER RESULTS")
    print("=" * 70)

    for strategy in strategies:
        subset = [r for r in all_results if r["adaptive"] == strategy]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"{strategy:15s}: {rate*100:.0f}% coexist, {avg_depths:.1f} depths")

if __name__ == "__main__":
    main()
