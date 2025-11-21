#!/usr/bin/env python3
"""
CYCLE 1699: COMPOSITION ENERGY DISTRIBUTION
What energy do D1 agents have at creation? Why does n=25 optimize survival?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1699"
CYCLES = 100
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
DECOMP_THRESHOLD = 1.3

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

def run_energy_analysis(seed, n_initial=25):
    """Track D1 creation energy."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track D1 creation energies
    creation_energies = []
    survival_flags = []  # 1 if survives 10 cycles, 0 otherwise
    d1_created = []  # (cycle, energy, agent_id)

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

        # Track compositions with creation energy
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    agent_id = f"D{d+1}_{cycle}_{seed}"
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(agent_id, d+1, new_e, depth=d+1), d+1)
                    if d == 0:  # D0→D1
                        creation_energies.append(new_e)
                        d1_created.append((cycle, new_e, agent_id))
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

    # Analyze creation energies
    if creation_energies:
        mean_e = np.mean(creation_energies)
        median_e = np.median(creation_energies)
        std_e = np.std(creation_energies)
        # Count by energy range
        very_low = sum(1 for e in creation_energies if e < 1.1)
        low = sum(1 for e in creation_energies if 1.1 <= e < 1.2)
        mid = sum(1 for e in creation_energies if 1.2 <= e < 1.3)
        high = sum(1 for e in creation_energies if e >= 1.3)
        survive_count = very_low + low + mid  # Below decomp threshold
    else:
        mean_e = median_e = std_e = 0
        very_low = low = mid = high = survive_count = 0

    total = len(creation_energies)
    return {
        "seed": seed,
        "n_initial": n_initial,
        "total": total,
        "mean_e": float(mean_e),
        "median_e": float(median_e),
        "std_e": float(std_e),
        "very_low": very_low,
        "low": low,
        "mid": mid,
        "high": high,
        "survive_count": survive_count,
        "survive_ratio": survive_count / total if total > 0 else 0
    }

def main():
    print(f"CYCLE 1699: Composition Energy | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: What energy do D1 agents have at creation?")
    print(f"Decomp threshold: {DECOMP_THRESHOLD}")
    print("=" * 70)

    seeds = list(range(1699001, 1699021))

    population_sizes = [15, 20, 25, 30, 35, 50]
    all_results = []

    for n_init in population_sizes:
        results = [run_energy_analysis(seed, n_init) for seed in seeds]
        avg_mean = np.mean([r["mean_e"] for r in results])
        avg_survive = np.mean([r["survive_ratio"] for r in results])
        print(f"\nn={n_init}: mean_E={avg_mean:.3f}, survive_ratio={avg_survive:.1%}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("D1 CREATION ENERGY BY POPULATION SIZE")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Mean E':>8} | {'Median':>8} | {'Std':>6} | {'Survive%':>9}")
    print("-" * 50)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_mean = np.mean([r["mean_e"] for r in subset])
        avg_median = np.mean([r["median_e"] for r in subset])
        avg_std = np.mean([r["std_e"] for r in subset])
        avg_survive = np.mean([r["survive_ratio"] for r in subset])
        print(f"{n_init:4d} | {avg_mean:8.3f} | {avg_median:8.3f} | {avg_std:6.3f} | {avg_survive:8.1%}")

    # Energy distribution
    print("\n" + "=" * 70)
    print("D1 ENERGY DISTRIBUTION (count by range)")
    print("=" * 70)
    print(f"\n{'N':>4} | {'<1.1':>6} | {'1.1-1.2':>7} | {'1.2-1.3':>7} | {'≥1.3':>6}")
    print("-" * 40)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_vl = np.mean([r["very_low"] for r in subset])
        avg_l = np.mean([r["low"] for r in subset])
        avg_m = np.mean([r["mid"] for r in subset])
        avg_h = np.mean([r["high"] for r in subset])
        print(f"{n_init:4d} | {avg_vl:6.1f} | {avg_l:7.1f} | {avg_m:7.1f} | {avg_h:6.1f}")

    # Correlation
    print("\n" + "=" * 70)
    print("SURVIVE RATIO vs SUCCESS")
    print("=" * 70)
    success_rates = {15: 32, 20: 56, 25: 96, 30: 38, 35: 52, 50: 66}
    print(f"\n{'N':>4} | {'Survive%':>9} | {'Success':>8}")
    print("-" * 30)
    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_survive = np.mean([r["survive_ratio"] for r in subset])
        success = success_rates.get(n_init, 0)
        print(f"{n_init:4d} | {avg_survive:8.1%} | {success:7d}%")

if __name__ == "__main__":
    main()
