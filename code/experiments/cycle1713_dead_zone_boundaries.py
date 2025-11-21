#!/usr/bin/env python3
"""
CYCLE 1713: DEAD ZONE BOUNDARIES
Where exactly does the n=30 dead zone begin and end?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1713"
CYCLES = 1000
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

def run_boundary_test(seed, n_initial):
    """Test N value."""
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
            if agent.energy > 1.0 and np.random.random() < 0.1:
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
    print(f"CYCLE 1713: Dead Zone Boundaries | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Goal: Where does the n=30 dead zone begin and end?")
    print("=" * 70)

    seeds = list(range(1713001, 1713031))  # 30 seeds

    # Test fine-grained N values around 30
    n_values = list(range(26, 36))  # 26-35

    print("\n" + "=" * 70)
    print("COEXISTENCE BY N (fine-grained)")
    print("=" * 70)
    print(f"\n{'N':>4} | {'Coexist':>8}")
    print("-" * 18)

    results = []
    for n in n_values:
        outcomes = [run_boundary_test(seed, n) for seed in seeds]
        coexist = sum(outcomes) / len(outcomes) * 100
        results.append((n, coexist))
        status = "✓" if coexist >= 80 else "✗" if coexist < 60 else "~"
        print(f"{n:4d} | {coexist:7.0f}% {status}")

    # Find boundaries
    print("\n" + "=" * 70)
    print("DEAD ZONE ANALYSIS")
    print("=" * 70)

    threshold = 70  # Below this is "failure"
    in_zone = [n for n, c in results if c < threshold]
    if in_zone:
        print(f"\nDead zone (coexist < {threshold}%): N = {min(in_zone)}-{max(in_zone)}")
    else:
        print(f"\nNo dead zone found at threshold {threshold}%")

    # Find minimum
    min_n, min_coex = min(results, key=lambda x: x[1])
    print(f"Minimum coexistence: N={min_n} ({min_coex:.0f}%)")

if __name__ == "__main__":
    main()
