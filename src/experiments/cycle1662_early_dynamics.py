#!/usr/bin/env python3
"""
CYCLE 1662: EARLY DYNAMICS INVESTIGATION
Analyze what happens in the first 100 cycles that determines success vs failure.
Track detailed metrics to identify failure predictors.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1662"
CYCLES = 30000
N_DEPTHS = 5

DECAY_MULT = 0.1
REPRO_RATE = 0.1
DECOMP_THRESHOLD = 1.3
RESONANCE_THRESHOLD = 0.5

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

def run_experiment(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    early_metrics = {"comps": [], "decomps": [], "d0_pop": [], "total": []}
    n_comps = n_decomps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        ns = [len(p) for p in pops]
        total = sum(ns)
        if total >= 3000 or total == 0: break

        # Track early metrics (first 100 cycles)
        if cycle < 100:
            early_metrics["d0_pop"].append(ns[0])
            early_metrics["total"].append(total)

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_RATE:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
        cycle_comps = 0
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
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}_{n_comps}", d+1, new_e, depth=d+1), d+1)
                    n_comps += 1
                    cycle_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        cycle_decomps = 0
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{n_decomps}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1
                    cycle_decomps += 1

        # Track early metrics
        if cycle < 100:
            early_metrics["comps"].append(cycle_comps)
            early_metrics["decomps"].append(cycle_decomps)

        # Energy decay
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

    # Compute early summary stats
    early_summary = {
        "total_comps_100": sum(early_metrics["comps"]),
        "total_decomps_100": sum(early_metrics["decomps"]),
        "min_d0_pop": min(early_metrics["d0_pop"]) if early_metrics["d0_pop"] else 0,
        "avg_d0_pop": np.mean(early_metrics["d0_pop"]) if early_metrics["d0_pop"] else 0,
        "min_total": min(early_metrics["total"]) if early_metrics["total"] else 0,
    }

    return {
        "seed": seed,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "early": early_summary
    }

def main():
    print(f"CYCLE 1662: Early Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Investigating early-cycle predictors of success/failure")
    print("=" * 70)

    seeds = list(range(1030001, 1030051))  # 50 seeds
    results = [run_experiment(seed) for seed in seeds]

    successes = [r for r in results if r["coexist"]]
    failures = [r for r in results if not r["coexist"]]

    print(f"\nOverall: {len(successes)}/{len(results)} = {len(successes)/len(results)*100:.0f}%")

    # Compare early metrics
    print("\n" + "=" * 70)
    print("EARLY METRICS COMPARISON (first 100 cycles)")
    print("=" * 70)

    metrics = ["total_comps_100", "total_decomps_100", "min_d0_pop", "avg_d0_pop", "min_total"]

    for metric in metrics:
        success_vals = [r["early"][metric] for r in successes]
        failure_vals = [r["early"][metric] for r in failures]

        if success_vals and failure_vals:
            s_mean = np.mean(success_vals)
            f_mean = np.mean(failure_vals)
            diff = s_mean - f_mean
            print(f"\n{metric}:")
            print(f"  Success: {s_mean:.1f}")
            print(f"  Failure: {f_mean:.1f}")
            print(f"  Diff: {diff:+.1f}")

    # Save results
    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1662_early_dynamics_results.json", 'w') as f:
        json.dump({
            "cycle_id": CYCLE_ID,
            "n_success": len(successes),
            "n_failure": len(failures),
            "results": results
        }, f, indent=2)

if __name__ == "__main__":
    main()
