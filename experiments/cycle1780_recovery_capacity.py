#!/usr/bin/env python3
"""
CYCLE 1780: POPULATION RECOVERY CAPACITY
Why does the dead zone effect weaken at higher N?
Hypothesis: Larger populations recover better from high pairing.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1780"
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

def run_detailed(seed, n_initial):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    d0_min = n_initial
    d0_after_pair = []
    d0_recoveries = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        d0_before = len(pops[0])

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        spawned = 0
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                spawned += 1

        # Composition
        composed = 0
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
                        composed += 2
                    i += 2
                else:
                    i += 1

        d0_after = len(reality.get_population_agents(0))
        if d0_after < d0_min:
            d0_min = d0_after
        d0_after_pair.append(d0_after)

        # Check if D0 recovered from depletion
        if d0_before < 5 and d0_after > d0_before:
            d0_recoveries += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
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
        'coexist': coexist,
        'd0_min': d0_min,
        'd0_mean': np.mean(d0_after_pair) if d0_after_pair else 0,
        'recoveries': d0_recoveries,
        'final_d0': len(final_pops[0])
    }

def main():
    print(f"CYCLE 1780: Recovery Capacity | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing population recovery capacity at peaks")
    print("=" * 70)

    seeds = list(range(1780001, 1780031))

    print(f"\n{'Zone':<6} | {'N':>4} | {'Coexist':>8} | {'D0 Min':>7} | {'D0 Mean':>8} | {'Recov':>6}")
    print("-" * 55)

    # Test all peaks and adjacent troughs
    points = [
        ("Z1-", 25), ("Z1", 29), ("Z1+", 35),
        ("Z2-", 40), ("Z2", 44), ("Z2+", 50),
        ("Z3-", 54), ("Z3", 58), ("Z3+", 65),
        ("Z4-", 70), ("Z4", 75), ("Z4+", 80),
    ]

    for label, n in points:
        results = [run_detailed(seed, n) for seed in seeds]
        coexist = sum(r['coexist'] for r in results) / len(results) * 100
        d0_min = sum(r['d0_min'] for r in results) / len(results)
        d0_mean = sum(r['d0_mean'] for r in results) / len(results)
        recov = sum(r['recoveries'] for r in results) / len(results)
        marker = " ***" if "Z" in label and "-" not in label and "+" not in label else ""
        print(f"{label:<6} | {n:>4} | {coexist:>7.0f}% | {d0_min:>7.1f} | {d0_mean:>8.1f} | {recov:>6.1f}{marker}")

if __name__ == "__main__":
    main()
