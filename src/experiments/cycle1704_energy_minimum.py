#!/usr/bin/env python3
"""
CYCLE 1704: WHY DOES N=25 MINIMIZE MEAN CREATION ENERGY?
Investigate agent energy distribution at composition time.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1704"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
DECOMP_THRESHOLD = 1.3
RESONANCE_THRESHOLD = 0.5

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

def run_energy_distribution(seed, n_initial):
    """Track energy distribution at composition time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track individual agent energies at composition
    agent_energies_at_comp = []  # Individual agent energies (not combined)
    combined_energies = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

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
                    e1, e2 = agents[i].energy, agents[i+1].energy
                    combined = e1 + e2
                    new_e = combined * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    if d == 0:
                        agent_energies_at_comp.extend([e1, e2])
                        combined_energies.append(combined)
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

    # Compute distributions
    if agent_energies_at_comp:
        agent_mean = np.mean(agent_energies_at_comp)
        agent_std = np.std(agent_energies_at_comp)
        agent_min = np.min(agent_energies_at_comp)
        agent_max = np.max(agent_energies_at_comp)
        combined_mean = np.mean(combined_energies)
    else:
        agent_mean = agent_std = agent_min = agent_max = combined_mean = 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "n_comps": len(combined_energies),
        "agent_mean": agent_mean,
        "agent_std": agent_std,
        "agent_min": agent_min,
        "agent_max": agent_max,
        "combined_mean": combined_mean
    }

def main():
    print(f"CYCLE 1704: Energy Minimum Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why does n=25 minimize mean creation energy?")
    print("=" * 70)

    seeds = list(range(1704001, 1704031))  # 30 seeds
    population_sizes = [15, 20, 25, 30, 35, 50]

    all_results = []
    for n_init in population_sizes:
        results = [run_energy_distribution(seed, n_init) for seed in seeds]
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("AGENT ENERGY AT COMPOSITION TIME")
    print("=" * 70)
    print(f"\n{'N':>4} | {'AgentMean':>10} | {'AgentStd':>9} | {'Min':>6} | {'Max':>6} | {'Combined':>9}")
    print("-" * 60)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_mean = np.mean([r["agent_mean"] for r in subset])
        avg_std = np.mean([r["agent_std"] for r in subset])
        avg_min = np.mean([r["agent_min"] for r in subset])
        avg_max = np.mean([r["agent_max"] for r in subset])
        avg_comb = np.mean([r["combined_mean"] for r in subset])
        print(f"{n_init:4d} | {avg_mean:10.3f} | {avg_std:9.3f} | {avg_min:6.3f} | {avg_max:6.3f} | {avg_comb:9.3f}")

    # Analysis: Is it about minimum energy or standard deviation?
    print("\n" + "=" * 70)
    print("ENERGY DISTRIBUTION ANALYSIS")
    print("=" * 70)

    # Check correlation with combined mean
    print("\nHypothesis 1: Lower agent energy → lower combined energy")
    print(f"{'N':>4} | {'AgentMean':>10} | {'Combined':>9} | {'Ratio':>7}")
    print("-" * 40)
    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_agent = np.mean([r["agent_mean"] for r in subset])
        avg_comb = np.mean([r["combined_mean"] for r in subset])
        ratio = avg_comb / (2 * avg_agent) if avg_agent > 0 else 0
        print(f"{n_init:4d} | {avg_agent:10.3f} | {avg_comb:9.3f} | {ratio:7.3f}")

    # Check if lower variability helps
    print("\nHypothesis 2: Lower std → more consistent compositions")
    print(f"{'N':>4} | {'AgentStd':>9} | {'Combined':>9}")
    print("-" * 35)
    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_std = np.mean([r["agent_std"] for r in subset])
        avg_comb = np.mean([r["combined_mean"] for r in subset])
        print(f"{n_init:4d} | {avg_std:9.3f} | {avg_comb:9.3f}")

if __name__ == "__main__":
    main()
