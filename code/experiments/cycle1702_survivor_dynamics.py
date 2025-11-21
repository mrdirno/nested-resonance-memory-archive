#!/usr/bin/env python3
"""
CYCLE 1702: SURVIVOR DYNAMICS
What happens to low-energy D1 after creation?
Why does n=25 succeed despite lower product than n=30?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1702"
CYCLES = 1000  # Longer run to see dynamics
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

def run_dynamics_analysis(seed, n_initial):
    """Track D1 survivor dynamics over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track milestones
    d1_at_100 = 0
    d1_at_500 = 0
    d1_at_1000 = 0
    depths_at_end = 0
    coexist = False

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track D1 population
        d1_pop = len(pops[1])
        if cycle == 100:
            d1_at_100 = d1_pop
        elif cycle == 500:
            d1_at_500 = d1_pop
        elif cycle == 999:
            d1_at_1000 = d1_pop

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

    # Final state
    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    depths_at_end = sum(1 for p in final_pops if len(p) > 0)
    coexist = depths_at_end >= 2

    return {
        "seed": seed,
        "n_initial": n_initial,
        "d1_at_100": d1_at_100,
        "d1_at_500": d1_at_500,
        "d1_at_1000": d1_at_1000,
        "depths": depths_at_end,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1702: Survivor Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why does n=25 succeed despite lower product than n=30?")
    print("=" * 70)

    seeds = list(range(1702001, 1702021))  # 20 seeds
    population_sizes = [15, 20, 25, 30, 35]

    all_results = []
    for n_init in population_sizes:
        results = [run_dynamics_analysis(seed, n_init) for seed in seeds]
        coexist_rate = sum(1 for r in results if r["coexist"]) / len(results) * 100
        avg_100 = np.mean([r["d1_at_100"] for r in results])
        avg_500 = np.mean([r["d1_at_500"] for r in results])
        avg_1000 = np.mean([r["d1_at_1000"] for r in results])
        print(f"\nn={n_init}: coexist={coexist_rate:.0f}%, D1@100={avg_100:.1f}, D1@500={avg_500:.1f}, D1@1000={avg_1000:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("D1 POPULATION EVOLUTION")
    print("=" * 70)
    print(f"\n{'N':>4} | {'@100':>6} | {'@500':>6} | {'@1000':>6} | {'Coexist':>8}")
    print("-" * 45)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_100 = np.mean([r["d1_at_100"] for r in subset])
        avg_500 = np.mean([r["d1_at_500"] for r in subset])
        avg_1000 = np.mean([r["d1_at_1000"] for r in subset])
        coexist = sum(1 for r in subset if r["coexist"]) / len(subset) * 100
        print(f"{n_init:4d} | {avg_100:6.1f} | {avg_500:6.1f} | {avg_1000:6.1f} | {coexist:7.0f}%")

    # Success analysis
    print("\n" + "=" * 70)
    print("D1 SURVIVAL → COEXISTENCE")
    print("=" * 70)
    print("\nKey: Need D1 to survive to 500+ cycles for stable coexistence")

if __name__ == "__main__":
    main()
