#!/usr/bin/env python3
"""
CYCLE 1788: TIME DYNAMICS ANALYSIS
How quickly do dead zone systems fail vs safe zone systems stabilize?
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1788"
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

def run_test(seed, n_initial):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    first_failure = None  # First cycle with <2 depths
    first_stable = None   # First cycle with stable coexistence (10 consecutive)
    stable_count = 0
    depth_history = []

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        depths_occupied = sum(1 for p in pops if len(p) > 0)
        depth_history.append(depths_occupied)

        if depths_occupied < 2 and first_failure is None:
            first_failure = cycle

        if depths_occupied >= 2:
            stable_count += 1
            if stable_count >= 10 and first_stable is None:
                first_stable = cycle - 9
        else:
            stable_count = 0

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

    return {
        'coexist': coexist,
        'first_failure': first_failure,
        'first_stable': first_stable,
        'final_cycle': len(depth_history)
    }

def main():
    print(f"CYCLE 1788: Time Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Analyzing time to failure/stabilization at peaks vs troughs")
    print("=" * 70)

    seeds = list(range(1788001, 1788031))

    test_points = [
        ("Trough", 25), ("Peak Z0", 29), ("Trough", 35),
        ("Peak Z1", 44), ("Trough", 50), ("Peak Z2", 58)
    ]

    print(f"\n{'Type':<10} | {'N':>4} | {'Coexist':>8} | {'Fail@':>8} | {'Stable@':>8}")
    print("-" * 50)

    for name, n in test_points:
        results = [run_test(seed, n) for seed in seeds]
        coexist = sum(r['coexist'] for r in results) / len(results) * 100

        # Average first failure (for failures only)
        failures = [r['first_failure'] for r in results if r['first_failure'] is not None]
        avg_fail = sum(failures) / len(failures) if failures else None

        # Average first stable (for successes only)
        stables = [r['first_stable'] for r in results if r['first_stable'] is not None]
        avg_stable = sum(stables) / len(stables) if stables else None

        fail_str = f"{avg_fail:.0f}" if avg_fail else "-"
        stable_str = f"{avg_stable:.0f}" if avg_stable else "-"

        print(f"{name:<10} | {n:>4} | {coexist:>7.0f}% | {fail_str:>8} | {stable_str:>8}")

if __name__ == "__main__":
    main()
