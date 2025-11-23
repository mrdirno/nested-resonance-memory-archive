#!/usr/bin/env python3
"""
CYCLE 1887: VARIANCE REDUCTION HYPOTHESIS

Why is β_above > β_below? (Recovery faster above Nc than below)
Hypothesis: Larger N reduces stochastic variance, stabilizing trajectories.
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

def run_with_variance(seed, n_initial, repro_prob):
    """Track population variance across time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    pop_history = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        pop_history.append(total)

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
    coex = sum(1 for p in final_pops if p > 0) >= 2

    # Compute trajectory variance (coefficient of variation)
    if len(pop_history) > 10:
        mean_pop = np.mean(pop_history)
        std_pop = np.std(pop_history)
        cv = std_pop / mean_pop if mean_pop > 0 else 0
    else:
        cv = 1.0

    return {
        'coex': coex,
        'cv': cv,
        'mean_pop': np.mean(pop_history) if pop_history else 0,
        'std_pop': np.std(pop_history) if pop_history else 0
    }

def main():
    print(f"CYCLE 1887: Variance Reduction | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: Larger N → lower variance → more stable trajectories")
    print("=" * 80)

    seeds = list(range(1887001, 1887051))
    prob = 0.10
    n_c = 14

    test_n = list(range(10, 19))

    print(f"\n{'N':>3} | {'Coex':>5} | {'CV':>6} | {'Mean':>6} | {'Std':>6}")
    print("-" * 45)

    below_cv = []
    above_cv = []

    # Also compute cross-seed variance
    below_coex_var = []
    above_coex_var = []

    for n in test_n:
        results = [run_with_variance(s, n, prob) for s in seeds]

        coex = sum(r['coex'] for r in results) / len(seeds) * 100
        avg_cv = np.mean([r['cv'] for r in results])
        mean_pop = np.mean([r['mean_pop'] for r in results])
        std_pop = np.mean([r['std_pop'] for r in results])

        # Cross-seed variance
        coex_values = [1 if r['coex'] else 0 for r in results]
        coex_variance = np.var(coex_values)

        if n < n_c:
            below_cv.append(avg_cv)
            below_coex_var.append(coex_variance)
        elif n > n_c:
            above_cv.append(avg_cv)
            above_coex_var.append(coex_variance)

        marker = "**" if n == n_c else "  "
        print(f"{n:>3} | {coex:>4.0f}% | {avg_cv:>6.3f} | {mean_pop:>6.1f} | {std_pop:>6.1f}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("ASYMMETRY ANALYSIS: Variance Reduction")
    print("=" * 80)

    avg_below_cv = np.mean(below_cv)
    avg_above_cv = np.mean(above_cv)
    avg_below_var = np.mean(below_coex_var)
    avg_above_var = np.mean(above_coex_var)

    print(f"\nTrajectory CV (coefficient of variation):")
    print(f"  Below Nc: {avg_below_cv:.3f}")
    print(f"  Above Nc: {avg_above_cv:.3f}")

    print(f"\nCross-seed coexistence variance:")
    print(f"  Below Nc: {avg_below_var:.3f}")
    print(f"  Above Nc: {avg_above_var:.3f}")

    if avg_above_cv < avg_below_cv:
        print(f"""
HYPOTHESIS SUPPORTED:

Above Nc, trajectories have lower CV ({avg_above_cv:.3f} vs {avg_below_cv:.3f}).

Mechanism:
1. Larger N → more agents averaging fluctuations
2. Lower variance → trajectories cluster around stable solutions
3. Stable trajectories → lower extinction probability
4. Lower extinction → faster recovery above Nc

This explains why β_above > β_below: variance reduction above Nc.
""")
    else:
        print("\nHypothesis not supported. Variance is similar or higher above Nc.")

    # Check cross-seed variance
    print("\n" + "-" * 50)
    print("Secondary: Cross-seed variance in outcomes")
    print("-" * 50)
    if avg_above_var < avg_below_var:
        print(f"Less variable outcomes above Nc ({avg_above_var:.3f} vs {avg_below_var:.3f})")
        print("Systems above Nc are more predictable.")
    else:
        print(f"More variable outcomes above Nc ({avg_above_var:.3f} vs {avg_below_var:.3f})")
        print("Asymmetry not explained by outcome predictability.")

if __name__ == "__main__":
    main()
