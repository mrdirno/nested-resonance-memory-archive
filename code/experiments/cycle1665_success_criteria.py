#!/usr/bin/env python3
"""
CYCLE 1665: ALTERNATIVE SUCCESS CRITERIA
Test different definitions of "successful" coexistence beyond 3+ depths alive.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1665"
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

def run_experiment(seed):
    """Run experiment and collect multiple success metrics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    total_history = []

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
            total_history.append(sum(len(reality.get_population_agents(d)) for d in range(N_DEPTHS)))

    # Calculate metrics
    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    # Alternative success criteria
    min_pop_per_depth = min(finals[d] for d in range(N_DEPTHS) if finals[d] > 0) if depths_alive > 0 else 0
    total_final = sum(finals[d] for d in range(N_DEPTHS))
    complexity = sum(d * finals[d] for d in range(N_DEPTHS))  # Depth-weighted population

    # Stability: variance in last 50 samples
    stability = 1 / (1 + np.var(total_history[-50:])) if len(total_history) >= 50 else 0

    return {
        "seed": seed,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "total_final": round(total_final, 1),
        "min_pop": round(min_pop_per_depth, 1),
        "complexity": round(complexity, 1),
        "stability": round(stability, 4),
        # Success by different criteria
        "success_3plus": depths_alive >= 3,
        "success_4plus": depths_alive >= 4,
        "success_all5": depths_alive == 5,
        "success_stable": stability > 0.01,
        "success_complex": complexity > 50
    }

def main():
    print(f"CYCLE 1665: Alternative Success Criteria | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1665001, 1665101))  # 100 seeds for statistical power
    results = [run_experiment(seed) for seed in seeds]

    # Results by different criteria
    print("\nSUCCESS RATES BY CRITERIA")
    print("=" * 70)

    criteria = [
        ("3+ depths alive", "success_3plus"),
        ("4+ depths alive", "success_4plus"),
        ("All 5 depths", "success_all5"),
        ("High stability", "success_stable"),
        ("High complexity (>50)", "success_complex")
    ]

    for name, key in criteria:
        rate = sum(1 for r in results if r[key]) / len(results)
        print(f"{name:25s}: {rate*100:5.1f}%")

    # Summary statistics
    print("\n" + "=" * 70)
    print("METRIC DISTRIBUTIONS")
    print("=" * 70)

    metrics = ["depths_alive", "total_final", "complexity", "stability"]
    for metric in metrics:
        values = [r[metric] for r in results]
        print(f"{metric:15s}: mean={np.mean(values):.1f}, std={np.std(values):.1f}, "
              f"min={np.min(values):.1f}, max={np.max(values):.1f}")

    # Cross-tabulation
    print("\n" + "=" * 70)
    print("CORRELATION: 3+ depths vs other criteria")
    print("=" * 70)

    base_success = [r for r in results if r["success_3plus"]]
    base_fail = [r for r in results if not r["success_3plus"]]

    for name, key in criteria[1:]:
        if base_success:
            rate_given_success = sum(1 for r in base_success if r[key]) / len(base_success)
        else:
            rate_given_success = 0
        if base_fail:
            rate_given_fail = sum(1 for r in base_fail if r[key]) / len(base_fail)
        else:
            rate_given_fail = 0
        print(f"{name:25s}: {rate_given_success*100:.0f}% if 3+ | {rate_given_fail*100:.0f}% if <3")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1665_success_criteria_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": results}, f, indent=2)

if __name__ == "__main__":
    main()
