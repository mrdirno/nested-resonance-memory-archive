#!/usr/bin/env python3
"""
CYCLE 1840: K RESONANCE STRUCTURE
Testing integer vs half-integer k values at low probability.
If integer k are dead and half-integer k are safe, confirms wavelength resonance.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1840"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI  # 14.4844...

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
    print(f"CYCLE 1840: K Resonance Structure | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing integer vs half-integer k values at low probability")
    print("=" * 80)

    seeds = list(range(1840001, 1840016))  # 15 seeds
    prob = 0.10  # Low prob where C1839 showed all integer k dead

    # Test k from -1 to 5 in 0.25 increments
    print(f"\nK values from -1 to 5 (prob=0.10)")
    print("-" * 60)
    print(f"{'k':<8} | {'N (exact)':<10} | {'N (int)':<8} | {'Coex':>8}")
    print("-" * 60)

    for k_quarter in range(-4, 21):  # -1 to 5 in 0.25 steps
        k = k_quarter / 4.0
        n_exact = 29 + k * LAMBDA
        if n_exact < 5:  # Skip invalid N values
            continue
        n_int = int(round(n_exact))
        coex = sum(run_test(seed, n_int, prob) for seed in seeds) / len(seeds) * 100

        # Mark integer k values
        k_type = "*" if k == int(k) else " "
        marker = "X" if coex < 70 else "."
        print(f"{k:<7.2f}{k_type} | {n_exact:<10.2f} | {n_int:<8} | {coex:>6.0f}%{marker}")

    # Summary table: integer vs half-integer
    print("\n" + "=" * 80)
    print("SUMMARY: INTEGER VS HALF-INTEGER K")
    print("=" * 80)

    int_k = []
    half_k = []

    for k in range(0, 6):  # k = 0, 1, 2, 3, 4, 5
        n_int = int(round(29 + k * LAMBDA))
        n_half = int(round(29 + (k + 0.5) * LAMBDA))

        coex_int = sum(run_test(seed, n_int, prob) for seed in seeds) / len(seeds) * 100
        coex_half = sum(run_test(seed, n_half, prob) for seed in seeds) / len(seeds) * 100

        int_k.append(coex_int)
        half_k.append(coex_half)

        print(f"k={k}: N={n_int} → {coex_int:.0f}% | k={k+0.5}: N={n_half} → {coex_half:.0f}%")

    print("-" * 60)
    avg_int = sum(int_k) / len(int_k)
    avg_half = sum(half_k) / len(half_k)
    print(f"Average: Integer k = {avg_int:.1f}% | Half-integer k = {avg_half:.1f}%")

    if avg_half > avg_int + 10:
        print("\n** RESONANCE CONFIRMED: Half-integer k significantly safer **")
    elif avg_int > avg_half + 10:
        print("\n** INVERSE PATTERN: Integer k safer than half-integer **")
    else:
        print("\n** NO CLEAR PATTERN: Integer and half-integer similar **")

if __name__ == "__main__":
    main()
