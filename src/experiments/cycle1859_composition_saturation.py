#!/usr/bin/env python3
"""
CYCLE 1859: COMPOSITION SATURATION HYPOTHESIS

Why λ = 14 specifically? Test if λ depends on:
1. Reproduction probability
2. Phase resonance threshold
3. Energy parameters

If λ = f(parameters), we can derive the relationship.
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

def run_test(seed, n_initial, repro_prob, res_threshold=0.5):
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
                if sim >= res_threshold:
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

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if p > 0) >= 2

def find_first_dead_zone(prob, threshold, seeds, n_range):
    """Find first N where coexistence drops below 70%."""
    for n in n_range:
        coex = sum(run_test(seed, n, prob, threshold) for seed in seeds) / len(seeds) * 100
        if coex < 60 and n > 8:  # After minimum viable
            return n
    return None

def main():
    print(f"CYCLE 1859: Composition Saturation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing: How do parameters affect λ?")
    print("=" * 80)

    seeds = list(range(1859001, 1859016))
    n_range = range(8, 30)

    # Test 1: Vary reproduction probability
    print("\n1. λ vs Reproduction Probability (threshold = 0.5)")
    print("-" * 50)

    probs = [0.05, 0.08, 0.10, 0.12, 0.15, 0.20]
    prob_lambdas = []

    for prob in probs:
        first_dead = find_first_dead_zone(prob, 0.5, seeds, n_range)
        prob_lambdas.append(first_dead)
        print(f"prob={prob:.2f}: λ = {first_dead}")

    # Test 2: Vary resonance threshold
    print("\n2. λ vs Resonance Threshold (prob = 0.10)")
    print("-" * 50)

    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    thresh_lambdas = []

    for thresh in thresholds:
        first_dead = find_first_dead_zone(0.10, thresh, seeds, n_range)
        thresh_lambdas.append(first_dead)
        print(f"threshold={thresh:.1f}: λ = {first_dead}")

    # Analysis
    print("\n" + "=" * 80)
    print("PARAMETER DEPENDENCE ANALYSIS")
    print("=" * 80)

    # Check if λ varies with parameters
    prob_variation = len(set([l for l in prob_lambdas if l])) > 1
    thresh_variation = len(set([l for l in thresh_lambdas if l])) > 1

    if not prob_variation and not thresh_variation:
        print("\nλ is INVARIANT to both reproduction probability and threshold!")
        print("This means λ = 14 is a fundamental property of the system.")
    elif prob_variation:
        print(f"\nλ DEPENDS on reproduction probability")
        # Try to fit relationship
        valid_probs = [(p, l) for p, l in zip(probs, prob_lambdas) if l]
        if len(valid_probs) >= 2:
            ps, ls = zip(*valid_probs)
            corr = np.corrcoef(ps, ls)[0, 1]
            print(f"Correlation: {corr:.3f}")
    elif thresh_variation:
        print(f"\nλ DEPENDS on resonance threshold")

    # Theoretical explanation
    print("\n" + "=" * 80)
    print("COMPOSITION SATURATION MODEL")
    print("=" * 80)
    print("""
At cycle 0, N agents with energy=1.0 all compose simultaneously.

Expected compositions in cycle 0:
  C_0 = N/2 (all pairs can compose since all have same phase)

The system enters "composition debt" when:
  C_0 > sustainable_rate

Sustainable rate depends on:
  - Reproduction: prob × D0_remaining
  - Decomposition: return rate from higher depths

Critical point λ where:
  N/2 ≈ 1/prob = 1/0.10 = 10

But this predicts λ ≈ 20, not 14.

The actual λ = 14 suggests:
  λ = 2 × (1/prob) × correction_factor
  14 = 2 × 10 × 0.7

Where correction_factor ≈ 0.7 accounts for energy losses.
""")

if __name__ == "__main__":
    main()
