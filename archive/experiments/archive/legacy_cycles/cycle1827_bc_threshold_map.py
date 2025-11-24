#!/usr/bin/env python3
"""
CYCLE 1827: B/C THRESHOLD MAPPING
Map precise B/C thresholds for multiple N values.
Goal: Quantitative model of dead zone transitions.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1827"
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

def run_test_bc(seed, n_initial, target_bc):
    """Run with target B/C ratio by adjusting reproduction probability"""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    # Use prob that approximately achieves target B/C
    # From C1825: prob=0.05 → B/C≈0.01, prob=0.35 → B/C≈0.04
    # Linear approximation: prob ≈ target_bc * 8
    repro_prob = min(target_bc * 10, 0.95)

    total_births = 0
    total_comps = 0

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
    actual_bc = total_births / total_comps if total_comps > 0 else 0

    return coex, actual_bc

def main():
    print(f"CYCLE 1827: B/C Threshold Mapping | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Mapping precise B/C thresholds for dead zone transitions")
    print("=" * 80)

    seeds = list(range(1827001, 1827026))  # 25 seeds

    # Key N values to test
    n_values = [14, 24, 29, 35, 43, 58]

    # B/C range to test
    bc_targets = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08]

    print(f"\n{'N':<5} |", end="")
    for bc in bc_targets:
        print(f" {bc:>5} |", end="")
    print("")
    print("-" * (8 + len(bc_targets) * 8))

    results_matrix = {}

    for n in n_values:
        print(f"{n:<5} |", end="")
        results_matrix[n] = {}
        for bc_target in bc_targets:
            results = [run_test_bc(seed, n, bc_target) for seed in seeds]
            coex = sum(r[0] for r in results) / len(results) * 100
            actual_bc = np.mean([r[1] for r in results])
            results_matrix[n][bc_target] = (coex, actual_bc)

            # Color code: < 70% is risky
            marker = "X" if coex < 70 else "."
            print(f" {coex:>4.0f}{marker} |", end="")
        print("")

    # Find thresholds for each N
    print("\n" + "=" * 80)
    print("THRESHOLD ANALYSIS")
    print("=" * 80)
    print(f"\n{'N':<5} | {'Low Thresh':>12} | {'High Thresh':>12} | {'Pattern Type':>15}")
    print("-" * 55)

    for n in n_values:
        coex_values = [results_matrix[n][bc][0] for bc in bc_targets]

        # Find transitions (70% boundary)
        low_thresh = None
        high_thresh = None

        for i, bc in enumerate(bc_targets):
            coex = results_matrix[n][bc][0]
            if i > 0:
                prev_coex = results_matrix[n][bc_targets[i-1]][0]
                if prev_coex < 70 and coex >= 70:
                    low_thresh = bc
                elif prev_coex >= 70 and coex < 70:
                    high_thresh = bc_targets[i-1]

        # Determine pattern type
        min_coex_bc = bc_targets[coex_values.index(min(coex_values))]
        if min_coex_bc <= 0.02:
            pattern = "Original (low B/C)"
        elif 0.03 <= min_coex_bc <= 0.05:
            pattern = "Inverted (mid B/C)"
        elif min_coex_bc >= 0.06:
            pattern = "High B/C"
        else:
            pattern = "Mixed"

        low_str = f"{low_thresh:.3f}" if low_thresh else "N/A"
        high_str = f"{high_thresh:.3f}" if high_thresh else "N/A"
        print(f"{n:<5} | {low_str:>12} | {high_str:>12} | {pattern:>15}")

if __name__ == "__main__":
    main()
