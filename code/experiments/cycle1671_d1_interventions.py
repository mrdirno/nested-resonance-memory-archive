#!/usr/bin/env python3
"""
CYCLE 1671: D1 ESTABLISHMENT INTERVENTIONS
Based on C1670 finding: success requires D1 by cycle 4.
Test interventions to improve D1 establishment.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1671"
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

def run_experiment(seed, intervention='none'):
    """
    Run experiment with different D1 establishment interventions.

    interventions:
    - 'none': Standard initialization
    - 'seed_d1': Start with some D1 agents
    - 'low_transfer': Lower composition energy transfer (0.65 instead of 0.85)
    - 'early_protect': Higher D1 threshold in first 50 cycles
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5
    COMP_TRANSFER = 0.85

    # Intervention parameters
    if intervention == 'low_transfer':
        COMP_TRANSFER = 0.65  # Composed energy: 1.0 + 1.0 = 2.0 * 0.65 = 1.3 (at threshold)
    elif intervention == 'very_low_transfer':
        COMP_TRANSFER = 0.55  # 2.0 * 0.55 = 1.1 (below threshold)

    # Initialize
    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Seed D1 intervention
    if intervention == 'seed_d1':
        for i in range(5):
            reality.add_agent(FractalAgent(f"D1_init_{i}", 1, 1.0, depth=1), 1)

    histories = {d: [] for d in range(N_DEPTHS)}

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
                    new_e = (agents[i].energy + agents[i+1].energy) * COMP_TRANSFER
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Decomposition (with early protection intervention)
        for d in range(1, N_DEPTHS):
            if intervention == 'early_protect' and d == 1 and cycle < 50:
                threshold = 2.0  # Protect D1 early
            else:
                threshold = DECOMP_THRESHOLD
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > threshold:
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
        "intervention": intervention,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)]
    }

def main():
    print(f"CYCLE 1671: D1 Interventions | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1671001, 1671101))  # 100 seeds

    interventions = ['none', 'seed_d1', 'low_transfer', 'very_low_transfer', 'early_protect']
    all_results = []

    for intervention in interventions:
        print(f"\nintervention={intervention}")
        results = [run_experiment(seed, intervention) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    avg depths: {avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("D1 INTERVENTION RESULTS")
    print("=" * 70)

    for intervention in interventions:
        subset = [r for r in all_results if r["intervention"] == intervention]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"{intervention:20s}: {rate*100:.0f}% coexist, {avg_depths:.1f} depths")

if __name__ == "__main__":
    main()
