#!/usr/bin/env python3
"""
CYCLE 1706: AGENT ORIGIN ANALYSIS
Do n=25 compositions involve reproduced agents (E=0.5)?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1706"
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

def run_origin_analysis(seed, n_initial):
    """Track whether composing agents are originals or offspring."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1

    # Track original vs offspring
    original_ids = set()
    for i in range(n_initial):
        agent_id = f"D0_{i}"
        reality.add_agent(FractalAgent(agent_id, 0, 1.0, depth=0), 0)
        original_ids.add(agent_id)

    # Count compositions by origin
    both_original = 0
    one_original = 0
    both_offspring = 0
    total_reproductions = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                offspring_id = f"D0_{cycle}_{agent.agent_id[-6:]}"
                reality.add_agent(FractalAgent(offspring_id, 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                total_reproductions += 1

        # Composition with origin tracking
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85

                    if d == 0:
                        # Check origin
                        a1_orig = agents[i].agent_id in original_ids
                        a2_orig = agents[i+1].agent_id in original_ids

                        if a1_orig and a2_orig:
                            both_original += 1
                        elif a1_orig or a2_orig:
                            one_original += 1
                        else:
                            both_offspring += 1

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

    total_comps = both_original + one_original + both_offspring
    return {
        "seed": seed,
        "n_initial": n_initial,
        "total_comps": total_comps,
        "both_original": both_original,
        "one_original": one_original,
        "both_offspring": both_offspring,
        "total_reproductions": total_reproductions,
        "offspring_ratio": (one_original + 2*both_offspring) / (2*total_comps) if total_comps > 0 else 0
    }

def main():
    print(f"CYCLE 1706: Agent Origin | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Do n=25 compositions involve reproduced agents?")
    print("=" * 70)

    seeds = list(range(1706001, 1706031))  # 30 seeds
    population_sizes = [15, 20, 25, 30, 35, 50]

    all_results = []
    for n_init in population_sizes:
        results = [run_origin_analysis(seed, n_init) for seed in seeds]
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("COMPOSITION ORIGIN BREAKDOWN")
    print("=" * 70)
    print(f"\n{'N':>4} | {'BothOrig':>9} | {'OneOrig':>8} | {'BothOff':>8} | {'Total':>6} | {'Off%':>6}")
    print("-" * 55)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_bo = np.mean([r["both_original"] for r in subset])
        avg_oo = np.mean([r["one_original"] for r in subset])
        avg_bf = np.mean([r["both_offspring"] for r in subset])
        avg_tot = np.mean([r["total_comps"] for r in subset])
        avg_off = np.mean([r["offspring_ratio"] for r in subset])
        print(f"{n_init:4d} | {avg_bo:9.1f} | {avg_oo:8.1f} | {avg_bf:8.1f} | {avg_tot:6.1f} | {avg_off:5.1%}")

    # Reproduction rate
    print("\n" + "=" * 70)
    print("REPRODUCTION EVENTS")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Reproductions':>13} | {'Comps':>6} | {'Ratio':>6}")
    print("-" * 35)

    for n_init in population_sizes:
        subset = [r for r in all_results if r["n_initial"] == n_init]
        avg_repro = np.mean([r["total_reproductions"] for r in subset])
        avg_comp = np.mean([r["total_comps"] for r in subset])
        ratio = avg_repro / avg_comp if avg_comp > 0 else 0
        print(f"{n_init:4d} | {avg_repro:13.1f} | {avg_comp:6.1f} | {ratio:6.2f}")

if __name__ == "__main__":
    main()
