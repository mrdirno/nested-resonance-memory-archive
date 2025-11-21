#!/usr/bin/env python3
"""
CYCLE 1712: WHY DOES N=30 UNIVERSALLY FAIL?
Investigate fundamental cause of n=30 failure across all parameters.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1712"
CYCLES = 500
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

def run_n30_analysis(seed):
    """Deep analysis of n=30 dynamics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    n_initial = 30
    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Track detailed metrics
    d0_to_d1 = 0
    d1_to_d2 = 0
    d1_decomps = 0
    early_comps = 0  # First 50 cycles
    late_comps = 0   # After 50 cycles

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    if d == 0:
                        d0_to_d1 += 1
                        if cycle < 50:
                            early_comps += 1
                        else:
                            late_comps += 1
                    elif d == 1:
                        d1_to_d2 += 1
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    if d == 1:
                        d1_decomps += 1
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2

    return {
        "d0_to_d1": d0_to_d1,
        "d1_to_d2": d1_to_d2,
        "d1_decomps": d1_decomps,
        "early_comps": early_comps,
        "late_comps": late_comps,
        "coexist": coexist
    }

def run_comparison(seed, n_initial):
    """Compare with other N values."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    d0_to_d1 = 0
    d1_decomps = 0
    early_comps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    if d == 0:
                        d0_to_d1 += 1
                        if cycle < 50:
                            early_comps += 1
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    if d == 1:
                        d1_decomps += 1
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    return {
        "n": n_initial,
        "d0_to_d1": d0_to_d1,
        "d1_decomps": d1_decomps,
        "early_comps": early_comps,
        "decomp_ratio": d1_decomps / d0_to_d1 if d0_to_d1 > 0 else 0
    }

def main():
    print(f"CYCLE 1712: N=30 Universal Failure | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why does n=30 fail across all parameters?")
    print("=" * 70)

    seeds = list(range(1712001, 1712031))  # 30 seeds

    # Detailed n=30 analysis
    print("\nN=30 Detailed Analysis (30 seeds):")
    results = [run_n30_analysis(seed) for seed in seeds]
    avg_d0d1 = np.mean([r["d0_to_d1"] for r in results])
    avg_d1d2 = np.mean([r["d1_to_d2"] for r in results])
    avg_decomp = np.mean([r["d1_decomps"] for r in results])
    avg_early = np.mean([r["early_comps"] for r in results])
    avg_late = np.mean([r["late_comps"] for r in results])
    coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100

    print(f"  D0→D1: {avg_d0d1:.1f}")
    print(f"  D1→D2: {avg_d1d2:.1f}")
    print(f"  D1 Decomps: {avg_decomp:.1f}")
    print(f"  Early comps (<50): {avg_early:.1f}")
    print(f"  Late comps (≥50): {avg_late:.1f}")
    print(f"  Coexistence: {coexist:.0f}%")

    # Compare with other N
    print("\n" + "=" * 70)
    print("COMPARISON WITH OTHER N VALUES")
    print("=" * 70)
    print(f"\n{'N':>4} | {'D0→D1':>7} | {'D1 Decomp':>10} | {'Ratio':>6} | {'Early':>6}")
    print("-" * 45)

    for n in [20, 25, 30, 35]:
        results = [run_comparison(seed, n) for seed in seeds]
        avg_d0d1 = np.mean([r["d0_to_d1"] for r in results])
        avg_decomp = np.mean([r["d1_decomps"] for r in results])
        avg_ratio = np.mean([r["decomp_ratio"] for r in results])
        avg_early = np.mean([r["early_comps"] for r in results])
        print(f"{n:4d} | {avg_d0d1:7.1f} | {avg_decomp:10.1f} | {avg_ratio:6.2f} | {avg_early:6.1f}")

if __name__ == "__main__":
    main()
