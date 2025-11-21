#!/usr/bin/env python3
"""
CYCLE 1722: N=35 UNIVERSAL ROBUSTNESS
Why does N=35 succeed across all repro rates while N=30 and N=40 fail?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1722"
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

def run_mechanism_analysis(seed, n_initial, repro):
    """Analyze mechanism for N robustness."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    recharge = 0.1

    original_ids = set()
    for i in range(n_initial):
        agent_id = f"D0_{i}"
        reality.add_agent(FractalAgent(agent_id, 0, 1.0, depth=0), 0)
        original_ids.add(agent_id)

    d1_created = 0
    d2_created = 0
    d1_decomp = 0
    both_orig = 0
    both_off = 0
    total_offspring = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(recharge / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                total_offspring += 1

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    if d == 0:
                        d1_created += 1
                        a1_orig = agents[i].agent_id in original_ids
                        a2_orig = agents[i+1].agent_id in original_ids
                        if a1_orig and a2_orig:
                            both_orig += 1
                        elif not a1_orig and not a2_orig:
                            both_off += 1
                    elif d == 1:
                        d2_created += 1
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    if d == 1:
                        d1_decomp += 1
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

    d1d2_ratio = d2_created / d1_created if d1_created > 0 else 0
    orig_ratio = both_orig / (both_orig + both_off) if (both_orig + both_off) > 0 else 0
    offspring_rate = total_offspring / CYCLES

    return {
        "d1d2_ratio": d1d2_ratio,
        "d1_decomp": d1_decomp,
        "orig_ratio": orig_ratio,
        "offspring_rate": offspring_rate,
        "coexist": coexist
    }

def main():
    print(f"CYCLE 1722: N=35 Mechanism | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Why is N=35 universally robust?")
    print("=" * 70)

    seeds = list(range(1722001, 1722041))  # 40 seeds
    n_vals = [30, 35, 40]
    repro_vals = [0.05, 0.10, 0.15]

    for repro in repro_vals:
        print(f"\n{'='*70}")
        print(f"REPRO = {repro}")
        print("=" * 70)
        print(f"{'N':>4} | {'D1D2':>6} | {'D1Dec':>6} | {'Orig%':>6} | {'OffRt':>6} | {'Coex':>6}")
        print("-" * 50)

        for n in n_vals:
            results = [run_mechanism_analysis(seed, n, repro) for seed in seeds]
            avg_d1d2 = np.mean([r["d1d2_ratio"] for r in results])
            avg_decomp = np.mean([r["d1_decomp"] for r in results])
            avg_orig = np.mean([r["orig_ratio"] for r in results]) * 100
            avg_offrt = np.mean([r["offspring_rate"] for r in results])
            coexist = sum(1 for r in results if r["coexist"]) / len(results) * 100
            marker = "✓" if coexist >= 90 else "✗"
            print(f"{n:4d} | {avg_d1d2:6.2f} | {avg_decomp:6.1f} | {avg_orig:5.0f}% | {avg_offrt:6.2f} | {coexist:5.0f}% {marker}")

if __name__ == "__main__":
    main()
