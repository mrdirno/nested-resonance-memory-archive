#!/usr/bin/env python3
"""
CYCLE 1705: COMPOSITION TIMING DISTRIBUTION
When do compositions occur? Does n=25 compose earlier?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1705"
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

def run_timing_distribution(seed, n_initial):
    """Track detailed timing of compositions."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track composition times
    comp_times = []

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
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    if d == 0:
                        comp_times.append(cycle)
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

    # Compute timing statistics
    if comp_times:
        mean_time = np.mean(comp_times)
        median_time = np.median(comp_times)
        std_time = np.std(comp_times)
        first_10 = sum(1 for t in comp_times if t < 10)
        first_50 = sum(1 for t in comp_times if t < 50)
        first_100 = sum(1 for t in comp_times if t < 100)
    else:
        mean_time = median_time = std_time = first_10 = first_50 = first_100 = 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "total": len(comp_times),
        "mean_time": mean_time,
        "median_time": median_time,
        "std_time": std_time,
        "first_10": first_10,
        "first_50": first_50,
        "first_100": first_100
    }

def main():
    print(f"CYCLE 1705: Timing Distribution | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: When do compositions occur? Does n=25 compose earlier?")
    print("=" * 70)

    seeds = list(range(1705001, 1705031))  # 30 seeds
    population_sizes = [15, 20, 25, 30, 35, 50]

    all_results = []
    for n_init in population_sizes:
        results = [run_timing_distribution(seed, n_init) for seed in seeds]
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("COMPOSITION TIMING STATISTICS")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Mean':>7} | {'Median':>7} | {'Std':>7} | {'<10':>5} | {'<50':>5} | {'<100':>5}")
    print("-" * 55)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_mean = np.mean([r["mean_time"] for r in subset])
        avg_med = np.mean([r["median_time"] for r in subset])
        avg_std = np.mean([r["std_time"] for r in subset])
        avg_10 = np.mean([r["first_10"] for r in subset])
        avg_50 = np.mean([r["first_50"] for r in subset])
        avg_100 = np.mean([r["first_100"] for r in subset])
        print(f"{n_init:4d} | {avg_mean:7.1f} | {avg_med:7.1f} | {avg_std:7.1f} | {avg_10:5.1f} | {avg_50:5.1f} | {avg_100:5.1f}")

    # Analysis
    print("\n" + "=" * 70)
    print("EARLY COMPOSITION RATE")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Total':>6} | {'<10':>5} | {'%<10':>7}")
    print("-" * 30)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_total = np.mean([r["total"] for r in subset])
        avg_10 = np.mean([r["first_10"] for r in subset])
        pct_10 = (avg_10 / avg_total * 100) if avg_total > 0 else 0
        print(f"{n_init:4d} | {avg_total:6.1f} | {avg_10:5.1f} | {pct_10:6.1f}%")

if __name__ == "__main__":
    main()
