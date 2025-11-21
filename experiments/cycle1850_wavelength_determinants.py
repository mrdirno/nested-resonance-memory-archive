#!/usr/bin/env python3
"""
CYCLE 1850: WAVELENGTH DETERMINANTS
What parameters determine λ ≈ 14.48 if not the substrate?
Testing decomposition threshold, resonance threshold, and energy parameters.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1850"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI

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

def run_test(seed, n_initial, repro_prob, decomp_thresh=1.3, res_thresh=0.5):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= res_thresh:  # Variable threshold
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:  # Variable threshold
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
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def main():
    print(f"CYCLE 1850: Wavelength Determinants | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("What determines λ ≈ 14.48 if not the substrate?")
    print("=" * 80)

    seeds = list(range(1850001, 1850011))  # 10 seeds for speed
    prob = 0.10
    k_values = [0, 0.5, 1, 1.5, 2]

    # Test 1: Vary decomposition threshold
    print("\n" + "=" * 80)
    print("TEST 1: DECOMPOSITION THRESHOLD")
    print("=" * 80)

    decomp_thresholds = [1.0, 1.3, 1.6, 2.0]

    for dt in decomp_thresholds:
        print(f"\nDecomp threshold = {dt}:")
        int_coex = []
        half_coex = []

        for k in k_values:
            n = int(round(29 + k * LAMBDA))
            coex = sum(run_test(seed, n, prob, decomp_thresh=dt) for seed in seeds) / len(seeds) * 100
            if k == int(k):
                int_coex.append(coex)
            else:
                half_coex.append(coex)

        int_avg = np.mean(int_coex)
        half_avg = np.mean(half_coex)
        diff = half_avg - int_avg
        print(f"  Int avg: {int_avg:.0f}%, Half avg: {half_avg:.0f}%, Diff: {diff:+.0f}%")

    # Test 2: Vary resonance threshold
    print("\n" + "=" * 80)
    print("TEST 2: RESONANCE THRESHOLD")
    print("=" * 80)

    res_thresholds = [0.3, 0.5, 0.7]

    for rt in res_thresholds:
        print(f"\nResonance threshold = {rt}:")
        int_coex = []
        half_coex = []

        for k in k_values:
            n = int(round(29 + k * LAMBDA))
            coex = sum(run_test(seed, n, prob, res_thresh=rt) for seed in seeds) / len(seeds) * 100
            if k == int(k):
                int_coex.append(coex)
            else:
                half_coex.append(coex)

        int_avg = np.mean(int_coex)
        half_avg = np.mean(half_coex)
        diff = half_avg - int_avg
        print(f"  Int avg: {int_avg:.0f}%, Half avg: {half_avg:.0f}%, Diff: {diff:+.0f}%")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    print("\nParameter effects on resonance pattern (Half - Int difference):")
    print("-" * 50)

if __name__ == "__main__":
    main()
