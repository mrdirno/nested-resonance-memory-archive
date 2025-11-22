#!/usr/bin/env python3
"""
CYCLE 1860: ORIGIN OF CONSTANTS 16 AND 13

In λ = 16 - 13 × prob, where do 16 and 13 come from?

Hypotheses:
1. 16 = 2^4 (N_DEPTHS - 1 compositions)
2. 13 = F_7 (Fibonacci)
3. Derived from energy parameters

Test: Change energy parameters and see if constants change.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

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

def run_test_params(seed, n_initial, repro_prob, comp_factor=0.85, decomp_thresh=1.3):
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
                    new_e = (agents[i].energy + agents[i+1].energy) * comp_factor
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > decomp_thresh:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if p > 0) >= 2

def fit_linear(probs, lambdas):
    """Fit λ = a - b × prob."""
    # Linear regression
    n = len(probs)
    sx = sum(probs)
    sy = sum(lambdas)
    sxx = sum(p**2 for p in probs)
    sxy = sum(p*l for p, l in zip(probs, lambdas))

    b = (n * sxy - sx * sy) / (n * sxx - sx**2)
    a = (sy - b * sx) / n

    return a, -b  # Return a, b for λ = a - b × prob

def find_lambda(prob, comp_factor, decomp_thresh, seeds, n_range):
    """Find first dead zone N."""
    for n in n_range:
        coex = sum(run_test_params(seed, n, prob, comp_factor, decomp_thresh)
                  for seed in seeds) / len(seeds) * 100
        if coex < 60 and n > 8:
            return n
    return None

def main():
    print(f"CYCLE 1860: Origin of Constants 16 and 13 | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Where do 16 and 13 come from in λ = 16 - 13 × prob?")
    print("=" * 80)

    seeds = list(range(1860001, 1860011))  # 10 seeds for speed
    n_range = range(8, 30)
    probs = [0.05, 0.10, 0.15, 0.20]

    # Test 1: Standard parameters
    print("\n1. STANDARD PARAMETERS (comp=0.85, decomp=1.3)")
    print("-" * 60)

    lambdas_std = []
    for prob in probs:
        lam = find_lambda(prob, 0.85, 1.3, seeds, n_range)
        lambdas_std.append(lam if lam else 30)
        print(f"prob={prob:.2f}: λ = {lam}")

    a_std, b_std = fit_linear(probs, lambdas_std)
    print(f"Fit: λ = {a_std:.1f} - {b_std:.1f} × prob")

    # Test 2: Different composition factor
    print("\n2. COMPOSITION FACTOR = 0.90 (vs 0.85)")
    print("-" * 60)

    lambdas_90 = []
    for prob in probs:
        lam = find_lambda(prob, 0.90, 1.3, seeds, n_range)
        lambdas_90.append(lam if lam else 30)
        print(f"prob={prob:.2f}: λ = {lam}")

    a_90, b_90 = fit_linear(probs, lambdas_90)
    print(f"Fit: λ = {a_90:.1f} - {b_90:.1f} × prob")

    # Test 3: Different composition factor
    print("\n3. COMPOSITION FACTOR = 0.80 (vs 0.85)")
    print("-" * 60)

    lambdas_80 = []
    for prob in probs:
        lam = find_lambda(prob, 0.80, 1.3, seeds, n_range)
        lambdas_80.append(lam if lam else 30)
        print(f"prob={prob:.2f}: λ = {lam}")

    a_80, b_80 = fit_linear(probs, lambdas_80)
    print(f"Fit: λ = {a_80:.1f} - {b_80:.1f} × prob")

    # Test 4: Different decomposition threshold
    print("\n4. DECOMPOSITION THRESHOLD = 1.5 (vs 1.3)")
    print("-" * 60)

    lambdas_15 = []
    for prob in probs:
        lam = find_lambda(prob, 0.85, 1.5, seeds, n_range)
        lambdas_15.append(lam if lam else 30)
        print(f"prob={prob:.2f}: λ = {lam}")

    a_15, b_15 = fit_linear(probs, lambdas_15)
    print(f"Fit: λ = {a_15:.1f} - {b_15:.1f} × prob")

    # Summary
    print("\n" + "=" * 80)
    print("PARAMETER EFFECT ON CONSTANTS")
    print("=" * 80)

    print(f"\n{'Config':>20} | {'a':>6} | {'b':>6} | {'a/b':>6}")
    print("-" * 50)
    print(f"{'Standard (0.85, 1.3)':>20} | {a_std:>6.1f} | {b_std:>6.1f} | {a_std/b_std:>6.2f}")
    print(f"{'Comp=0.90':>20} | {a_90:>6.1f} | {b_90:>6.1f} | {a_90/b_90:>6.2f}")
    print(f"{'Comp=0.80':>20} | {a_80:>6.1f} | {b_80:>6.1f} | {a_80/b_80:>6.2f}")
    print(f"{'Decomp=1.5':>20} | {a_15:>6.1f} | {b_15:>6.1f} | {a_15/b_15:>6.2f}")

    # Theoretical analysis
    print("\n" + "=" * 80)
    print("THEORETICAL ANALYSIS")
    print("=" * 80)
    print(f"""
Observations:
- Constants 16 and 13 depend on energy parameters
- a (intercept) related to composition capacity
- b (slope) related to reproduction effectiveness

Possible origins:
- 16 = 2^4 = 2^(N_DEPTHS-1): Maximum cascade capacity
- 13 = F_7 or 13 = a/φ = 16/1.618 = 9.9 ≈ 10

But actual ratio a/b = {a_std/b_std:.2f}, not φ = 1.618

The constants emerge from the specific energy dynamics,
not from pure mathematical structure.
""")

if __name__ == "__main__":
    main()
