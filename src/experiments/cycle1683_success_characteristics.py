#!/usr/bin/env python3
"""
CYCLE 1683: SUCCESS VS FAILURE CHARACTERISTICS
C1682 survival rate didn't correlate well. Need to separate
successful and failed runs to identify distinguishing features.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1683"
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
    """Track early-phase characteristics for success/failure analysis."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    # Track early phase (first 500 cycles)
    first_d1_cycle = -1
    d1_at_100 = 0
    d1_at_500 = 0
    comps_first_100 = 0
    low_e_comps_first_100 = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track D1 population at checkpoints
        d1_count = len(pops[1])
        if first_d1_cycle == -1 and d1_count > 0:
            first_d1_cycle = cycle
        if cycle == 100:
            d1_at_100 = d1_count
        if cycle == 500:
            d1_at_500 = d1_count

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
                    if d == 0 and cycle < 100:
                        comps_first_100 += 1
                        if new_e < DECOMP_THRESHOLD:
                            low_e_comps_first_100 += 1
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
        "n_initial": n_initial,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "first_d1_cycle": first_d1_cycle,
        "d1_at_100": d1_at_100,
        "d1_at_500": d1_at_500,
        "comps_first_100": comps_first_100,
        "low_e_comps_first_100": low_e_comps_first_100,
        "low_e_ratio": low_e_comps_first_100 / comps_first_100 if comps_first_100 > 0 else 0
    }

def main():
    print(f"CYCLE 1683: Success Characteristics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Compare successful vs failed runs to identify mechanism")
    print("=" * 70)

    seeds = list(range(1683001, 1683101))  # 100 seeds for better statistics

    initial_sizes = [20, 25, 30, 100]
    all_results = []

    for n_init in initial_sizes:
        print(f"\nn_initial={n_init}")
        results = [run_experiment(seed, n_init) for seed in seeds]
        all_results.extend(results)

        # Separate successes and failures
        successes = [r for r in results if r["coexist"]]
        failures = [r for r in results if not r["coexist"]]

        success_rate = len(successes) / len(results)
        print(f"  → {len(successes)}/{len(results)} coexist ({success_rate*100:.0f}%)")

        if successes:
            avg_first = np.mean([r["first_d1_cycle"] for r in successes])
            avg_d1_100 = np.mean([r["d1_at_100"] for r in successes])
            avg_d1_500 = np.mean([r["d1_at_500"] for r in successes])
            avg_ratio = np.mean([r["low_e_ratio"] for r in successes])
            print(f"  SUCCESS: first_d1={avg_first:.0f}, d1@100={avg_d1_100:.1f}, d1@500={avg_d1_500:.1f}, low-e={avg_ratio*100:.0f}%")

        if failures:
            avg_first = np.mean([r["first_d1_cycle"] for r in failures])
            avg_d1_100 = np.mean([r["d1_at_100"] for r in failures])
            avg_d1_500 = np.mean([r["d1_at_500"] for r in failures])
            avg_ratio = np.mean([r["low_e_ratio"] for r in failures])
            print(f"  FAILURE: first_d1={avg_first:.0f}, d1@100={avg_d1_100:.1f}, d1@500={avg_d1_500:.1f}, low-e={avg_ratio*100:.0f}%")

    # Cross-population comparison
    print("\n" + "=" * 70)
    print("SUCCESS VS FAILURE COMPARISON (All N)")
    print("=" * 70)

    all_success = [r for r in all_results if r["coexist"]]
    all_failure = [r for r in all_results if not r["coexist"]]

    print(f"\n{'Metric':<20} | {'Success':>10} | {'Failure':>10} | {'Delta':>10}")
    print("-" * 55)

    metrics = [
        ("first_d1_cycle", "First D1 cycle"),
        ("d1_at_100", "D1 @ cycle 100"),
        ("d1_at_500", "D1 @ cycle 500"),
        ("low_e_ratio", "Low-E ratio")
    ]

    for key, label in metrics:
        s_val = np.mean([r[key] for r in all_success])
        f_val = np.mean([r[key] for r in all_failure])
        if key == "low_e_ratio":
            print(f"{label:<20} | {s_val*100:9.1f}% | {f_val*100:9.1f}% | {(s_val-f_val)*100:9.1f}%")
        else:
            print(f"{label:<20} | {s_val:10.1f} | {f_val:10.1f} | {s_val-f_val:10.1f}")

    # Key insight: Why does n=25 have more successes?
    print("\n" + "=" * 70)
    print("WHY N=25 SUCCEEDS MORE OFTEN")
    print("=" * 70)

    for n_init in initial_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        successes = [r for r in subset if r["coexist"]]
        failures = [r for r in subset if not r["coexist"]]

        if successes and failures:
            s_ratio = np.mean([r["low_e_ratio"] for r in successes])
            f_ratio = np.mean([r["low_e_ratio"] for r in failures])
            s_d1 = np.mean([r["d1_at_100"] for r in successes])
            f_d1 = np.mean([r["d1_at_100"] for r in failures])
            print(f"\nn={n_init}: Success rate {len(successes)/len(subset)*100:.0f}%")
            print(f"  Success low-e: {s_ratio*100:.0f}%, Failure low-e: {f_ratio*100:.0f}%")
            print(f"  Success D1@100: {s_d1:.1f}, Failure D1@100: {f_d1:.1f}")

if __name__ == "__main__":
    main()
