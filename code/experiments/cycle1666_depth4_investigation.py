#!/usr/bin/env python3
"""
CYCLE 1666: DEPTH 4 INVESTIGATION
Why can't the system sustain all 5 depths? Investigate depth 4 dynamics.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1666"
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

def run_experiment(seed, depth4_boost=1.0):
    """
    Run experiment with boosted depth 4 energy.

    Args:
        depth4_boost: Multiplier for depth 4 energy input
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    d4_stats = {"comps_to": 0, "decomps_from": 0, "decayed": 0, "max_pop": 0}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Track depth 4 max
        d4_pop = len(pops[4])
        if d4_pop > d4_stats["max_pop"]:
            d4_stats["max_pop"] = d4_pop

        # Energy input (boosted for depth 4)
        for d in range(N_DEPTHS):
            base = 0.1 / (1 + d * 0.5)
            if d == 4:
                base *= depth4_boost
            for agent in pops[d]:
                agent.recharge_energy(base, cap=2.0)

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
                    if d == 3:  # Composition to depth 4
                        d4_stats["comps_to"] += 1
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
                    if d == 4:  # Decomposition from depth 4
                        d4_stats["decomps_from"] += 1

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)
                    if d == 4:
                        d4_stats["decayed"] += 1

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "depth4_boost": depth4_boost,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "d4_comps": d4_stats["comps_to"],
        "d4_decomps": d4_stats["decomps_from"],
        "d4_decayed": d4_stats["decayed"],
        "d4_max": d4_stats["max_pop"],
        "all5": depths_alive == 5
    }

def main():
    print(f"CYCLE 1666: Depth 4 Investigation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1666001, 1666051))  # 50 seeds

    # Test different depth 4 boosts
    boosts = [1.0, 2.0, 3.0, 5.0, 10.0]
    all_results = []

    for boost in boosts:
        print(f"\ndepth4_boost={boost}x")
        results = [run_experiment(seed, boost) for seed in seeds]

        all5_count = sum(1 for r in results if r["all5"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        avg_d4_comps = np.mean([r["d4_comps"] for r in results])
        avg_d4_decomps = np.mean([r["d4_decomps"] for r in results])
        avg_d4_max = np.mean([r["d4_max"] for r in results])

        print(f"  → all 5 depths: {all5_count}/{len(results)} ({all5_count/len(results)*100:.0f}%)")
        print(f"    avg depths: {avg_depths:.1f}, max D4: {avg_d4_max:.0f}")
        print(f"    D4 comps: {avg_d4_comps:.0f}, decomps: {avg_d4_decomps:.0f}")

        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("DEPTH 4 BOOST RESULTS")
    print("=" * 70)

    for boost in boosts:
        subset = [r for r in all_results if r["depth4_boost"] == boost]
        all5_rate = sum(1 for r in subset if r["all5"]) / len(subset)
        avg_final_d4 = np.mean([r["finals"][4] for r in subset])
        print(f"boost={boost:4.1f}x: {all5_rate*100:5.1f}% all-5, D4 final={avg_final_d4:.1f}")

if __name__ == "__main__":
    main()
