#!/usr/bin/env python3
"""
CYCLE 1730: FIFTH DEAD ZONE TEST
Formula: N = 29 + 14.5k
Predicted: k=4 → N≈87.5-88
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1730"
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

def run_zone_test(seed, n_initial):
    """Test for dead zone."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    recharge = 0.1
    repro = 0.1

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

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
    coexist = sum(1 for p in final_pops if len(p) > 0) >= 2
    return coexist

def main():
    print(f"CYCLE 1730: Fifth Dead Zone | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Test prediction N = 29 + 14.5*4 ≈ 87")
    print("=" * 70)

    seeds = list(range(1730001, 1730051))  # 50 seeds

    # Test N values around predicted fifth dead zone
    n_values = list(range(82, 97))  # 82-96

    print("\n" + "=" * 70)
    print("COEXISTENCE BY N")
    print("=" * 70)
    print(f"{'N':>4} | {'Coexist':>8} | Status")
    print("-" * 30)

    results = []
    for n in n_values:
        outcomes = [run_zone_test(seed, n) for seed in seeds]
        coexist = sum(outcomes) / len(outcomes) * 100
        results.append((n, coexist))

        if coexist >= 90:
            status = "✓ Safe"
        elif coexist >= 70:
            status = "~ Marginal"
        else:
            status = "✗ Dead zone"

        print(f"{n:4d} | {coexist:7.0f}% | {status}")

    # Find boundaries
    print("\n" + "=" * 70)
    print("PREDICTION VALIDATION")
    print("=" * 70)

    in_zone = [n for n, c in results if c < 80]
    if in_zone:
        print(f"\nFifth dead zone (coexist < 80%): N = {min(in_zone)}-{max(in_zone)}")
        min_n, min_c = min(results, key=lambda x: x[1])
        print(f"Minimum: N={min_n} ({min_c:.0f}%)")
        predicted = 29 + 14.5 * 4
        print(f"\nPredicted minimum: N={predicted:.1f}")
        print(f"Actual minimum: N={min_n}")
        error = abs(min_n - predicted)
        print(f"Prediction error: {error:.1f}")
        if error <= 2:
            print("\n✓ PREDICTION VALIDATED!")
    else:
        print("\nNo fifth dead zone found at N~87")

    # Complete pattern
    print("\n" + "=" * 70)
    print("COMPLETE PATTERN (5 zones)")
    print("=" * 70)
    print("\nDead zone minima:")
    print("  Zone 1: N=29 (k=0)")
    print("  Zone 2: N=43 (k=1)")
    print("  Zone 3: N=59 (k=2)")
    print("  Zone 4: N=73 (k=3)")
    if in_zone:
        min_n, _ = min(results, key=lambda x: x[1])
        print(f"  Zone 5: N={min_n} (k=4)")

if __name__ == "__main__":
    main()
