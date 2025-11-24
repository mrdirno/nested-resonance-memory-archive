#!/usr/bin/env python3
"""
CYCLE 1849: PRNG SUBSTRATE TEST
Do wavelength patterns persist with non-transcendental substrate?
Testing PRNG-based phase resonance instead of π, e, φ.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1849"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI

def compute_phase_resonance_transcendental(e1, d1, e2, d2):
    """Original transcendental substrate"""
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

def compute_phase_resonance_prng(e1, d1, e2, d2):
    """PRNG-based substrate using hash function"""
    # Use deterministic hash instead of transcendentals
    def hash_coord(x, seed):
        np.random.seed(int(abs(x * 1000)) + seed)
        return np.random.random() * 2 * PI

    v1 = [hash_coord(e1, 1), hash_coord(d1, 2), hash_coord(e1 + d1, 3)]
    v2 = [hash_coord(e2, 1), hash_coord(d2, 2), hash_coord(e2 + d2, 3)]

    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def compute_phase_resonance_simple(e1, d1, e2, d2):
    """Simple modular arithmetic substrate"""
    # Use simple integer modular ops
    v1 = [(e1 * 7) % (2 * PI), (d1 * 5) % (2 * PI), (e1 + d1) % (2 * PI)]
    v2 = [(e2 * 7) % (2 * PI), (d2 * 5) % (2 * PI), (e2 + d2) % (2 * PI)]

    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def run_test(seed, n_initial, repro_prob, resonance_func):
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
                sim = resonance_func(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

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
    return sum(1 for p in final_pops if len(p) > 0) >= 2

def main():
    print(f"CYCLE 1849: PRNG Substrate Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Do wavelength patterns persist with non-transcendental substrate?")
    print("=" * 80)

    seeds = list(range(1849001, 1849016))  # 15 seeds
    prob = 0.10

    substrates = [
        ("Transcendental (π,e,φ)", compute_phase_resonance_transcendental),
        ("PRNG (hash)", compute_phase_resonance_prng),
        ("Simple (modular)", compute_phase_resonance_simple),
    ]

    # Test k values from 0 to 3
    k_values = [0, 0.5, 1, 1.5, 2, 2.5, 3]

    print("\n" + "=" * 80)
    print("SUBSTRATE COMPARISON")
    print("=" * 80)

    for name, func in substrates:
        print(f"\n{name}:")
        print("-" * 50)

        int_coex = []
        half_coex = []

        for k in k_values:
            n = int(round(29 + k * LAMBDA))
            coex = sum(run_test(seed, n, prob, func) for seed in seeds) / len(seeds) * 100
            marker = "X" if coex < 70 else " "

            if k == int(k):
                int_coex.append(coex)
            else:
                half_coex.append(coex)

            print(f"  k={k:.1f} N={n}: {coex:.0f}%{marker}")

        int_avg = np.mean(int_coex)
        half_avg = np.mean(half_coex)
        diff = half_avg - int_avg
        print(f"  Int avg: {int_avg:.0f}%, Half avg: {half_avg:.0f}%, Diff: {diff:+.0f}%")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY: WAVELENGTH PATTERN BY SUBSTRATE")
    print("=" * 80)

    print("\n" + f"{'Substrate':<25} | {'Int avg':<8} | {'Half avg':<8} | {'Pattern'}")
    print("-" * 60)

    for name, func in substrates:
        int_coex = []
        half_coex = []
        for k in k_values:
            n = int(round(29 + k * LAMBDA))
            coex = sum(run_test(seed, n, prob, func) for seed in seeds) / len(seeds) * 100
            if k == int(k):
                int_coex.append(coex)
            else:
                half_coex.append(coex)

        int_avg = np.mean(int_coex)
        half_avg = np.mean(half_coex)

        if half_avg > int_avg + 10:
            pattern = "RESONANCE"
        elif int_avg > half_avg + 10:
            pattern = "INVERSE"
        else:
            pattern = "NONE"

        print(f"{name:<25} | {int_avg:>6.0f}% | {half_avg:>6.0f}% | {pattern}")

if __name__ == "__main__":
    main()
