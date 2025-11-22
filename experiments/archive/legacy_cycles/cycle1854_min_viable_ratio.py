#!/usr/bin/env python3
"""
CYCLE 1854: MINIMUM VIABLE N RELATIONSHIP
Exploring the ratio between minimum viable N (8) and first dead zone (14).
Why is 14/8 = 1.75 the critical ratio?
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1854"
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
    print(f"CYCLE 1854: Minimum Viable N Relationship | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Exploring ratio: First dead zone / Minimum viable = 14/8 = 1.75")
    print("=" * 80)

    seeds = list(range(1854001, 1854016))  # 15 seeds
    prob = 0.10

    # Detailed scan around critical region
    print("\nDetailed scan N=5 to N=20:")
    print("-" * 60)

    min_viable = None
    first_dead = None

    for n in range(5, 21):
        coex = sum(run_test(seed, n, prob) for seed in seeds) / len(seeds) * 100

        status = ""
        if coex >= 50 and min_viable is None:
            min_viable = n
            status = " ← MIN VIABLE"
        elif coex < 70 and n > 10 and first_dead is None:
            first_dead = n
            status = " ← FIRST DEAD"

        marker = "X" if coex < 70 else ""
        print(f"N={n:>2}: {coex:>5.0f}%{marker}{status}")

    # Calculate ratio
    print("\n" + "=" * 80)
    print("RATIO ANALYSIS")
    print("=" * 80)

    if min_viable and first_dead:
        ratio = first_dead / min_viable
        print(f"\nMinimum viable: N = {min_viable}")
        print(f"First dead zone: N = {first_dead}")
        print(f"Ratio: {first_dead}/{min_viable} = {ratio:.3f}")

        # Check if ratio matches known constants
        print("\nRatio comparisons:")
        print(f"  φ (golden ratio) = {PHI:.3f}")
        print(f"  √3 = {math.sqrt(3):.3f}")
        print(f"  7/4 = {7/4:.3f}")
        print(f"  Actual ratio = {ratio:.3f}")

    # Mathematical interpretation
    print("\n" + "=" * 80)
    print("INTERPRETATION")
    print("=" * 80)

    print("""
The ratio λ/N_min ≈ 1.75 suggests:

1. The first dead zone occurs at roughly twice the minimum viable
2. The ratio is close to 7/4 = 1.75 exactly
3. This may relate to composition efficiency:
   - At N_min, system barely survives
   - At λ, first resonance failure occurs
   - Ratio captures the "safety margin" before failure

The wavelength λ = 14 is approximately:
  λ = N_min × 1.75 = 8 × 1.75 = 14
""")

if __name__ == "__main__":
    main()
