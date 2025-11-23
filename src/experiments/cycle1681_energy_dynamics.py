#!/usr/bin/env python3
"""
CYCLE 1681: ENERGY DYNAMICS AT OPTIMAL POPULATION
Why does n=25 give 96% while n=30 gives 38%?
Hypothesis: Energy accumulation rate determines low-energy composition window.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1681"
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

def run_experiment(seed, n_initial=100):
    """Track energy dynamics to understand n=25 optimum."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    energy_histories = {d: [] for d in range(N_DEPTHS)}
    compositions = []
    decompositions = []
    low_energy_comps = []  # Compositions where combined energy < 1.3

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track energy distributions
        for d in range(N_DEPTHS):
            agents = pops[d]
            if agents:
                avg_e = np.mean([a.energy for a in agents])
            else:
                avg_e = 0
            if cycle % 100 == 0:
                energy_histories[d].append(avg_e)

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition with tracking
        cycle_comps = 0
        cycle_low_e_comps = 0
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    combined_e = agents[i].energy + agents[i+1].energy
                    new_e = combined_e * 0.85
                    cycle_comps += 1
                    if new_e < DECOMP_THRESHOLD:
                        cycle_low_e_comps += 1
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        if cycle % 100 == 0:
            compositions.append(cycle_comps)
            low_energy_comps.append(cycle_low_e_comps)

        # Decomposition with tracking
        cycle_decomps = 0
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    cycle_decomps += 1
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            decompositions.append(cycle_decomps)

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

    # Compute early-phase metrics (first 10 checkpoints = 1000 cycles)
    early_comps = sum(compositions[:10]) if len(compositions) >= 10 else sum(compositions)
    early_low_e = sum(low_energy_comps[:10]) if len(low_energy_comps) >= 10 else sum(low_energy_comps)
    early_decomps = sum(decompositions[:10]) if len(decompositions) >= 10 else sum(decompositions)

    # Compute average D0 energy in early phase
    early_d0_energy = np.mean(energy_histories[0][:10]) if len(energy_histories[0]) >= 10 else 0

    return {
        "seed": seed,
        "n_initial": n_initial,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "early_comps": early_comps,
        "early_low_e_comps": early_low_e,
        "early_decomps": early_decomps,
        "early_d0_energy": float(early_d0_energy),
        "low_e_ratio": early_low_e / early_comps if early_comps > 0 else 0
    }

def main():
    print(f"CYCLE 1681: Energy Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Hypothesis: n=25 has optimal low-energy composition window")
    print("=" * 70)

    seeds = list(range(1681001, 1681051))  # 50 seeds

    # Test sizes around the optimum
    initial_sizes = [15, 20, 25, 30, 35, 50, 100]
    all_results = []

    for n_init in initial_sizes:
        print(f"\nn_initial={n_init}")
        results = [run_experiment(seed, n_init) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        avg_comps = np.mean([r["early_comps"] for r in results])
        avg_low_e = np.mean([r["early_low_e_comps"] for r in results])
        avg_decomps = np.mean([r["early_decomps"] for r in results])
        avg_d0_e = np.mean([r["early_d0_energy"] for r in results])
        avg_ratio = np.mean([r["low_e_ratio"] for r in results])

        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    early comps: {avg_comps:.1f}, low-e: {avg_low_e:.1f} ({avg_ratio*100:.0f}%)")
        print(f"    early decomps: {avg_decomps:.1f}, D0 energy: {avg_d0_e:.2f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("ENERGY DYNAMICS ANALYSIS")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Success':>7} | {'Comps':>6} | {'Low-E':>6} | {'Ratio':>5} | {'Decomps':>7} | {'D0 E':>5}")
    print("-" * 60)

    for n_init in initial_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_comps = np.mean([r["early_comps"] for r in subset])
        avg_low_e = np.mean([r["early_low_e_comps"] for r in subset])
        avg_ratio = np.mean([r["low_e_ratio"] for r in subset])
        avg_decomps = np.mean([r["early_decomps"] for r in subset])
        avg_d0_e = np.mean([r["early_d0_energy"] for r in subset])
        print(f"{n_init:4d} | {rate*100:6.0f}% | {avg_comps:6.1f} | {avg_low_e:6.1f} | {avg_ratio*100:4.0f}% | {avg_decomps:7.1f} | {avg_d0_e:5.2f}")

    # Test hypothesis
    print("\n" + "=" * 70)
    print("HYPOTHESIS TEST: Low-Energy Composition Window")
    print("=" * 70)

    # Compare n=25 vs n=30
    n25 = [r for r in all_results if r["n_initial"] == 25]
    n30 = [r for r in all_results if r["n_initial"] == 30]

    n25_ratio = np.mean([r["low_e_ratio"] for r in n25])
    n30_ratio = np.mean([r["low_e_ratio"] for r in n30])
    n25_success = sum(1 for r in n25 if r["coexist"]) / len(n25)
    n30_success = sum(1 for r in n30 if r["coexist"]) / len(n30)

    print(f"\nn=25: {n25_success*100:.0f}% success, {n25_ratio*100:.0f}% low-energy compositions")
    print(f"n=30: {n30_success*100:.0f}% success, {n30_ratio*100:.0f}% low-energy compositions")

    if n25_ratio > n30_ratio:
        print("\n✓ Hypothesis SUPPORTED: n=25 has more low-energy compositions")
    else:
        print("\n✗ Hypothesis REJECTED: Need alternative explanation")

if __name__ == "__main__":
    main()
