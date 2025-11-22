#!/usr/bin/env python3
"""
CYCLE 1826: B/C RATIO CONTROL TEST
Testing if artificially controlling B/C ratio produces expected patterns.

Hypothesis: B/C ratio is the causal mechanism, not just correlation.
Test: Override normal birth rate to shift patterns.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1826"
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

def run_test_controlled(seed, n_initial, repro_prob, birth_boost=1.0):
    """Run with birth rate modifier to control B/C ratio"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    total_births = 0
    total_comps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction with birth boost
        effective_prob = min(repro_prob * birth_boost, 1.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < effective_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                total_births += 1

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
                    total_comps += 1
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
    coex = sum(1 for p in final_pops if len(p) > 0) >= 2
    bc = total_births / total_comps if total_comps > 0 else 0

    return coex, bc

def main():
    print(f"CYCLE 1826: B/C Ratio Control Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Can we shift patterns by artificially controlling B/C ratio?")
    print("=" * 80)

    seeds = list(range(1826001, 1826031))  # 30 seeds

    # Test 1: N=29 at low prob - can we rescue it with birth boost?
    print("\nTEST 1: N=29 at prob=0.10 (normally dead zone)")
    print("Can we rescue N=29 by boosting birth rate?")
    print("-" * 60)
    print(f"{'Boost':<8} | {'Coex':>8} | {'B/C':>8} | {'Expected':>12}")
    print("-" * 60)

    for boost in [1.0, 2.0, 3.0, 4.0, 5.0]:
        results = [run_test_controlled(seed, 29, 0.10, boost) for seed in seeds]
        coex = sum(r[0] for r in results) / len(results) * 100
        bc = np.mean([r[1] for r in results])
        expected = "Dead" if bc < 0.025 else "Safe" if bc > 0.03 else "Transition"
        print(f"{boost:<8} | {coex:>7.0f}% | {bc:>8.3f} | {expected:>12}")

    # Test 2: N=29 at high prob - can we kill it with birth restriction?
    print("\nTEST 2: N=29 at prob=0.35 (normally safe)")
    print("Can we kill N=29 by restricting birth rate?")
    print("-" * 60)
    print(f"{'Restrict':<8} | {'Coex':>8} | {'B/C':>8} | {'Expected':>12}")
    print("-" * 60)

    for restrict in [1.0, 0.5, 0.3, 0.2, 0.1]:
        results = [run_test_controlled(seed, 29, 0.35, restrict) for seed in seeds]
        coex = sum(r[0] for r in results) / len(results) * 100
        bc = np.mean([r[1] for r in results])
        expected = "Dead" if bc < 0.025 else "Safe" if bc > 0.03 else "Transition"
        print(f"{restrict:<8} | {coex:>7.0f}% | {bc:>8.3f} | {expected:>12}")

    # Test 3: N=24 pattern control
    print("\nTEST 3: N=24 pattern control")
    print("N=24 safe at low prob, dead at mid prob, severe at high prob")
    print("-" * 60)
    print(f"{'Prob':<6} | {'Boost':<6} | {'Coex':>8} | {'B/C':>8}")
    print("-" * 60)

    test_cases = [
        (0.10, 1.0),  # Baseline: safe
        (0.10, 4.0),  # Boosted: should become dead?
        (0.35, 1.0),  # Baseline: dead zone
        (0.35, 0.25), # Restricted: should become safe?
    ]

    for prob, boost in test_cases:
        results = [run_test_controlled(seed, 24, prob, boost) for seed in seeds]
        coex = sum(r[0] for r in results) / len(results) * 100
        bc = np.mean([r[1] for r in results])
        print(f"{prob:<6} | {boost:<6} | {coex:>7.0f}% | {bc:>8.3f}")

if __name__ == "__main__":
    main()
