#!/usr/bin/env python3
"""
CYCLE 1890: ATTRACTOR BASIN STRUCTURE

Why is β_above > β_below?
Hypothesis: Above Nc, basins of attraction for coexistence are wider.

Method: Test sensitivity to initial energy distribution.
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

def run_with_init_energy(seed, n_initial, repro_prob, init_energy):
    """Run with different initial energy distributions."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        e = init_energy + np.random.normal(0, 0.1)  # Add noise
        e = max(0.5, min(2.0, e))
        reality.add_agent(FractalAgent(f"D0_{i}", 0, e, depth=0), 0)

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

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return sum(1 for p in final_pops if p > 0) >= 2

def main():
    print(f"CYCLE 1890: Attractor Basin | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: Wider attractor basins above Nc")
    print("=" * 80)

    seeds = list(range(1890001, 1890026))  # 25 seeds
    prob = 0.10
    n_c = 14

    # Test initial energies
    init_energies = [0.7, 0.85, 1.0, 1.15, 1.3]

    # Test N values below and above Nc
    test_n = [11, 12, 13, 14, 15, 16, 17]

    print(f"\n{'N':>3} |", end="")
    for e in init_energies:
        print(f" E={e:.2f} |", end="")
    print(" Range |")
    print("-" * 60)

    below_ranges = []
    above_ranges = []

    for n in test_n:
        coex_rates = []
        for e in init_energies:
            coex = sum(run_with_init_energy(s, n, prob, e) for s in seeds) / len(seeds) * 100
            coex_rates.append(coex)

        # Range = max - min coexistence across initial energies
        range_val = max(coex_rates) - min(coex_rates)

        if n < n_c:
            below_ranges.append(range_val)
        elif n > n_c:
            above_ranges.append(range_val)

        marker = "**" if n == n_c else "  "
        print(f"{n:>3} |", end="")
        for c in coex_rates:
            print(f"  {c:>4.0f}% |", end="")
        print(f" {range_val:>4.0f}%{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("ASYMMETRY ANALYSIS: Basin Width (Sensitivity)")
    print("=" * 80)

    avg_below = np.mean(below_ranges)
    avg_above = np.mean(above_ranges)

    print(f"\nSensitivity to initial conditions (coex range):")
    print(f"  Below Nc: {avg_below:.1f}%")
    print(f"  Above Nc: {avg_above:.1f}%")

    if avg_above < avg_below:
        print(f"""
HYPOTHESIS SUPPORTED:

Above Nc, systems are LESS sensitive to initial conditions.
Range: {avg_above:.1f}% vs {avg_below:.1f}%

Interpretation:
1. Narrower range = wider attractor basin
2. More initial conditions lead to coexistence
3. Wider basin = faster recovery from perturbation
4. Result: β_above > β_below

The asymmetry is caused by BASIN STRUCTURE, not dynamics.
""")
    else:
        print(f"""
Hypothesis not supported.

Sensitivity similar or higher above Nc.
Range: {avg_above:.1f}% vs {avg_below:.1f}%

Note: May need finer-grained analysis.
""")

if __name__ == "__main__":
    main()
