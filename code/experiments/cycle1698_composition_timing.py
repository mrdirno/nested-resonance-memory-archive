#!/usr/bin/env python3
"""
CYCLE 1698: COMPOSITION TIMING DISTRIBUTION
When do compositions occur? Is n=25 optimal because of timing?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1698"
CYCLES = 100  # First 100 cycles
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

def run_timing_analysis(seed, n_initial=25):
    """Track when compositions occur."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track composition timing
    composition_cycles = []
    d1_energies = []

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

        # Track compositions
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
                    if d == 0:  # D0→D1 composition
                        composition_cycles.append(cycle)
                        d1_energies.append(new_e)
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
    if composition_cycles:
        mean_cycle = np.mean(composition_cycles)
        median_cycle = np.median(composition_cycles)
        first_10 = sum(1 for c in composition_cycles if c < 10)
        low_e_count = sum(1 for e in d1_energies if e < DECOMP_THRESHOLD)
    else:
        mean_cycle = 0
        median_cycle = 0
        first_10 = 0
        low_e_count = 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "total_comps": len(composition_cycles),
        "mean_cycle": float(mean_cycle),
        "median_cycle": float(median_cycle),
        "first_10": first_10,
        "low_e_count": low_e_count,
        "low_e_ratio": low_e_count / len(composition_cycles) if composition_cycles else 0
    }

def main():
    print(f"CYCLE 1698: Composition Timing | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: When do compositions occur? Is timing key to n=25?")
    print("=" * 70)

    seeds = list(range(1698001, 1698021))  # 20 seeds

    population_sizes = [15, 20, 25, 30, 35, 50]
    all_results = []

    for n_init in population_sizes:
        results = [run_timing_analysis(seed, n_init) for seed in seeds]
        avg_comps = np.mean([r["total_comps"] for r in results])
        avg_mean = np.mean([r["mean_cycle"] for r in results])
        avg_first10 = np.mean([r["first_10"] for r in results])
        avg_low_e = np.mean([r["low_e_ratio"] for r in results])
        print(f"\nn={n_init}: comps={avg_comps:.1f}, mean_cycle={avg_mean:.1f}, first_10={avg_first10:.1f}, low_e={avg_low_e:.2%}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("COMPOSITION TIMING BY POPULATION SIZE")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Total':>6} | {'Mean':>6} | {'First10':>8} | {'Low-E%':>8}")
    print("-" * 45)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_comps = np.mean([r["total_comps"] for r in subset])
        avg_mean = np.mean([r["mean_cycle"] for r in subset])
        avg_first10 = np.mean([r["first_10"] for r in subset])
        avg_low_e = np.mean([r["low_e_ratio"] for r in subset])
        print(f"{n_init:4d} | {avg_comps:6.1f} | {avg_mean:6.1f} | {avg_first10:8.1f} | {avg_low_e:7.1%}")

    # Correlation with success
    print("\n" + "=" * 70)
    print("TIMING-SUCCESS CORRELATION")
    print("=" * 70)

    # Known success rates
    success_rates = {15: 32, 20: 56, 25: 96, 30: 38, 35: 52, 50: 66}

    print(f"\n{'N':>4} | {'First10':>8} | {'Low-E%':>8} | {'Success':>8}")
    print("-" * 40)
    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_first10 = np.mean([r["first_10"] for r in subset])
        avg_low_e = np.mean([r["low_e_ratio"] for r in subset])
        success = success_rates.get(n_init, 0)
        print(f"{n_init:4d} | {avg_first10:8.1f} | {avg_low_e:7.1%} | {success:7d}%")

if __name__ == "__main__":
    main()
