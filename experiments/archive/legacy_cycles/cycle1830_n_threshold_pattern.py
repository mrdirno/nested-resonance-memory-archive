#!/usr/bin/env python3
"""
CYCLE 1830: N → THRESHOLD RELATIONSHIP
Find pattern relating N to its dead zone probability range.

Hypothesis: Position in wavelength formula determines sensitivity.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1830"
CYCLES = 500
N_DEPTHS = 5

PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
LAMBDA = PI + E + PHI + 22/PI  # ≈ 14.48
N1 = 22/PI + 22  # ≈ 29.0

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
    print(f"CYCLE 1830: N → Threshold Pattern | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Finding pattern relating N to dead zone probability")
    print(f"Wavelength formula: N_k = {N1:.2f} + k × {LAMBDA:.2f}")
    print("=" * 80)

    seeds = list(range(1830001, 1830021))  # 20 seeds

    # Test N values and calculate their k position
    n_values = [11, 12, 14, 15, 24, 29, 34, 35, 43, 46, 58, 60]
    probs = [0.05, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.80]

    print(f"\n{'N':<4} | {'k':<6} | {'k mod 1':<8} |", end="")
    for p in probs:
        print(f" {p:<5} |", end="")
    print("")
    print("-" * (30 + len(probs) * 8))

    results = {}

    for n in n_values:
        # Calculate k (can be negative for N < N1)
        k = (n - N1) / LAMBDA
        k_mod = k % 1  # Fractional part

        print(f"{n:<4} | {k:>5.2f} | {k_mod:>8.2f} |", end="")

        results[n] = {'k': k, 'k_mod': k_mod, 'dead_probs': []}

        for prob in probs:
            coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100

            marker = "X" if coex < 70 else "."
            print(f" {coex:>3.0f}{marker} |", end="")

            if coex < 70:
                results[n]['dead_probs'].append(prob)

        print("")

    # Analyze pattern
    print("\n" + "=" * 80)
    print("PATTERN ANALYSIS")
    print("=" * 80)

    print(f"\n{'N':<4} | {'k':<6} | {'Dead Prob Range':>20} | {'Pattern Type':>15}")
    print("-" * 55)

    for n in n_values:
        k = results[n]['k']
        dead_probs = results[n]['dead_probs']

        if not dead_probs:
            pattern = "Always safe"
            range_str = "None"
        elif len(dead_probs) == len(probs):
            pattern = "Always dead"
            range_str = "All"
        else:
            min_p = min(dead_probs)
            max_p = max(dead_probs)
            if max_p <= 0.2:
                pattern = "Low prob"
            elif min_p >= 0.5:
                pattern = "High prob"
            elif 0.2 <= min_p <= 0.4:
                pattern = "Mid prob"
            else:
                pattern = "Mixed"
            range_str = f"{min_p}-{max_p}"

        print(f"{n:<4} | {k:>5.2f} | {range_str:>20} | {pattern:>15}")

    # Look for k correlation
    print("\n" + "=" * 80)
    print("K VALUE CORRELATION")
    print("=" * 80)

    print("\nOriginal wavelength N values (k = integer):")
    for n in n_values:
        k = results[n]['k']
        if abs(k - round(k)) < 0.1:
            dead = results[n]['dead_probs']
            print(f"  N={n}, k={k:.2f}: Dead at {dead}")

    print("\nInverted pattern N values (k ≈ 0.5):")
    for n in n_values:
        k = results[n]['k']
        if 0.4 < (k % 1) < 0.6:
            dead = results[n]['dead_probs']
            print(f"  N={n}, k={k:.2f}: Dead at {dead}")

if __name__ == "__main__":
    main()
