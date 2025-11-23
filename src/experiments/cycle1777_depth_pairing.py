#!/usr/bin/env python3
"""
CYCLE 1777: DEPTH EFFECT ON PAIRING PEAKS
Test if pairing peaks at dead zones hold for different depth counts.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1777"
CYCLES = 100

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

def run_test(seed, n_initial, n_depths):
    reality = RealityInterface(n_populations=n_depths, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    total_before = 0
    total_composed = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(n_depths)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(n_depths):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < 0.1:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(n_depths - 1):
            agents = list(reality.get_population_agents(d))
            total_before += len(agents)

            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            composed = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    composed += 2
                    i += 2
                else:
                    i += 1
            total_composed += composed

        for d in range(1, n_depths):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(n_depths):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    if total_before > 0:
        return total_composed / total_before
    return 0.0

def main():
    print(f"CYCLE 1777: Depth Pairing | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing pairing peaks for different depth counts")
    print("=" * 70)

    seeds = list(range(1777001, 1777011))

    # Test Zone 1 area for different depths
    print(f"\n{'Depths':<8} | {'N=25':>8} | {'N=29':>8} | {'N=35':>8}")
    print("-" * 40)

    for n_depths in [3, 4, 5, 6, 7]:
        r25 = sum(run_test(seed, 25, n_depths) for seed in seeds) / len(seeds) * 100
        r29 = sum(run_test(seed, 29, n_depths) for seed in seeds) / len(seeds) * 100
        r35 = sum(run_test(seed, 35, n_depths) for seed in seeds) / len(seeds) * 100
        peak = " ***" if r29 > r25 and r29 > r35 else ""
        print(f"{n_depths:<8} | {r25:>7.1f}% | {r29:>7.1f}%{peak:<4} | {r35:>7.1f}%")

if __name__ == "__main__":
    main()
