#!/usr/bin/env python3
"""
CYCLE 1913: ENERGY DIVERSITY

Hypothesis: Same-energy agents always compose (resonance=1.0).
Energy diversity might prevent runaway cascade.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 500
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

def run_with_diversity(seed, n_initial, repro_prob, energy_mode):
    """Run with different energy initialization modes."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    # Initialize with different energy modes
    for i in range(n_initial):
        if energy_mode == "uniform":
            e = 1.0
        elif energy_mode == "spread":
            e = 0.5 + (i / n_initial) * 1.0  # 0.5 to 1.5
        elif energy_mode == "random":
            e = 0.5 + np.random.random() * 1.0  # Random 0.5-1.5
        elif energy_mode == "bimodal":
            e = 0.5 if i % 2 == 0 else 1.5  # Alternating
        else:
            e = 1.0

        reality.add_agent(FractalAgent(f"D0_{i}", 0, e, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                # Offspring with random energy
                e = 0.5 + np.random.random() * 0.5  # 0.5-1.0
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, e, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return final_pops[0] > 0 and final_pops[1] > 0

def main():
    print(f"CYCLE 1913: Energy Diversity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Does energy diversity prevent cascade?")
    print("=" * 80)

    seeds = list(range(1913001, 1913031))
    prob = 0.10

    modes = ["uniform", "spread", "random", "bimodal"]

    for n in [14, 17, 20]:
        print(f"\nN = {n}:")
        print(f"{'Mode':>10} | {'Coex%':>6}")
        print("-" * 22)

        for mode in modes:
            coex = np.mean([run_with_diversity(s, n, prob, mode) for s in seeds]) * 100
            print(f"{mode:>10} | {coex:>5.0f}%")

    # Check resonance between different energies
    print("\n" + "=" * 80)
    print("PHASE RESONANCE ANALYSIS")
    print("=" * 80)

    print("\nResonance between D0 agents with different energies:")
    print(f"{'E1':>5} | {'E2':>5} | {'Resonance':>10}")
    print("-" * 28)

    test_energies = [0.5, 0.7, 1.0, 1.3, 1.5]
    for e1 in test_energies:
        for e2 in test_energies:
            res = compute_phase_resonance(e1, 0, e2, 0)
            if res < 0.5:
                flag = "< 0.5"
            else:
                flag = ">= 0.5"
            print(f"{e1:>5.1f} | {e2:>5.1f} | {res:>6.4f} {flag}")

    # Find energy pairs that don't compose
    print("\n" + "=" * 80)
    print("ENERGY PAIRS THAT DON'T COMPOSE (resonance < 0.5)")
    print("=" * 80)

    non_composing = []
    for e1 in np.arange(0.3, 2.0, 0.1):
        for e2 in np.arange(0.3, 2.0, 0.1):
            res = compute_phase_resonance(e1, 0, e2, 0)
            if res < 0.5:
                non_composing.append((e1, e2, res))

    if non_composing:
        print(f"\nFound {len(non_composing)} non-composing pairs")
        for e1, e2, res in non_composing[:10]:
            print(f"  E={e1:.1f}, E={e2:.1f}: resonance={res:.4f}")
    else:
        print("\nALL pairs compose! Resonance >= 0.5 for all energy combinations.")
        print("Energy diversity does NOT prevent composition.")

if __name__ == "__main__":
    main()
