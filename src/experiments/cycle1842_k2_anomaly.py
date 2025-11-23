#!/usr/bin/env python3
"""
CYCLE 1842: K=2 ANOMALY INVESTIGATION
Why does N=58 show severe dead zone (55%) when model predicts 76%?
Testing even vs odd harmonics and secondary wavelengths.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1842"
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

def run_test(seed, n_initial, repro_prob):
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
    print(f"CYCLE 1842: K=2 Anomaly Investigation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Why does N=58 (k=2) have 55% coexistence when model predicts 76%?")
    print("=" * 80)

    seeds = list(range(1842001, 1842021))  # 20 seeds
    prob = 0.10

    # Test 1: Even vs odd harmonics
    print("\n" + "=" * 80)
    print("TEST 1: EVEN VS ODD HARMONICS")
    print("=" * 80)

    print(f"\n{'k':<8} | {'N':<6} | {'Type':<8} | {'Coex':>8}")
    print("-" * 40)

    even_coex = []
    odd_coex = []

    for k in range(0, 6):
        n = int(round(29 + k * LAMBDA))
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        k_type = "even" if k % 2 == 0 else "odd"
        marker = "X" if coex < 70 else "."

        if k % 2 == 0:
            even_coex.append(coex)
        else:
            odd_coex.append(coex)

        print(f"{k:<8} | {n:<6} | {k_type:<8} | {coex:>6.0f}%{marker}")

    print("-" * 40)
    print(f"Even average: {sum(even_coex)/len(even_coex):.0f}%")
    print(f"Odd average: {sum(odd_coex)/len(odd_coex):.0f}%")

    # Test 2: Fine-grained around k=2
    print("\n" + "=" * 80)
    print("TEST 2: FINE-GRAINED AROUND K=2")
    print("=" * 80)

    print(f"\n{'k':<8} | {'N':<6} | {'Coex':>8}")
    print("-" * 30)

    for k_cent in range(150, 251, 10):  # k from 1.5 to 2.5
        k = k_cent / 100.0
        n = int(round(29 + k * LAMBDA))
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100
        marker = "X" if coex < 70 else "."
        k_marker = "*" if k == 2.0 else " "
        print(f"{k:<7.2f}{k_marker} | {n:<6} | {coex:>6.0f}%{marker}")

    # Test 3: Check for secondary wavelength
    print("\n" + "=" * 80)
    print("TEST 3: SECONDARY WAVELENGTH SEARCH")
    print("=" * 80)

    # N=58 is 4 × 14.5, test multiples of different wavelengths
    wavelengths = [
        ("λ = π+e+φ+22/π", LAMBDA),
        ("λ/2 = 7.24", LAMBDA/2),
        ("29 (N1)", 29),
        ("π²", PI**2),
        ("e × φ", E * PHI),
    ]

    print(f"\n{'Wavelength':<20} | {'N=58 k':<10} | {'Type':>10}")
    print("-" * 45)

    for name, wl in wavelengths:
        k_val = (58 - 29) / wl if wl != 0 else 0
        k_type = "integer" if abs(k_val - round(k_val)) < 0.1 else "non-int"
        print(f"{name:<20} | {k_val:<10.2f} | {k_type:>10}")

    # Test 4: Multiple probabilities at k=2
    print("\n" + "=" * 80)
    print("TEST 4: K=2 (N=58) ACROSS PROBABILITIES")
    print("=" * 80)

    probs = [0.05, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50]
    print(f"\n{'Prob':<8} | {'N=58 (k=2)':<12} | {'N=51 (k=1.5)':<14} | {'Diff':>8}")
    print("-" * 50)

    for p in probs:
        coex_58 = sum(run_test(seed, 58, p) for seed in seeds) / len(seeds) * 100
        coex_51 = sum(run_test(seed, 51, p) for seed in seeds) / len(seeds) * 100
        diff = coex_51 - coex_58
        m58 = "X" if coex_58 < 70 else "."
        m51 = "X" if coex_51 < 70 else "."
        print(f"{p:<8} | {coex_58:>6.0f}%{m58}     | {coex_51:>6.0f}%{m51}       | {diff:>+6.0f}%")

if __name__ == "__main__":
    main()
