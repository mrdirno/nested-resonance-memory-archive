#!/usr/bin/env python3
"""
CYCLE 1856C: PHASE ALIGNMENT HYPOTHESIS

Hypothesis: At N=14, initial agents have phase vectors that create poor resonance.
Test: Measure average pairwise resonance quality at different N values.
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

def analyze_initial_phase_distribution(n_initial):
    """Analyze phase distribution of initial N agents with energy=1.0."""
    agents = [(1.0, 0) for _ in range(n_initial)]  # (energy, depth)

    # Calculate all pairwise resonances
    resonances = []
    good_pairs = 0
    for i in range(len(agents)):
        for j in range(i+1, len(agents)):
            res = compute_phase_resonance(agents[i][0], agents[i][1],
                                         agents[j][0], agents[j][1])
            resonances.append(res)
            if res >= 0.5:
                good_pairs += 1

    n_pairs = len(resonances)
    return {
        'n_pairs': n_pairs,
        'good_pairs': good_pairs,
        'good_ratio': good_pairs / n_pairs if n_pairs > 0 else 0,
        'avg_resonance': np.mean(resonances) if resonances else 0,
        'min_resonance': min(resonances) if resonances else 0,
        'max_resonance': max(resonances) if resonances else 0
    }

def run_test_resonance_quality(seed, n_initial, repro_prob):
    """Track resonance quality over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    good_resonance_events = 0
    poor_resonance_checks = 0
    total_checks = 0

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
                total_checks += 1
                if sim >= 0.5:
                    good_resonance_events += 1
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    poor_resonance_checks += 1
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

    success_rate = good_resonance_events / total_checks if total_checks > 0 else 0

    return {
        'coex': coex,
        'resonance_success_rate': success_rate,
        'total_checks': total_checks
    }

def main():
    print(f"CYCLE 1856C: Phase Alignment Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: λ = 14 creates poor initial phase alignment")
    print("=" * 80)

    # First, analyze initial phase distribution (deterministic)
    print("\nInitial Phase Distribution (all agents energy=1.0):")
    print("-" * 60)
    print(f"{'N':>3} | {'Pairs':>5} | {'Good':>4} | {'Ratio':>6} | {'AvgRes':>6} | Note")
    print("-" * 60)

    for n in range(5, 25):
        ph = analyze_initial_phase_distribution(n)
        note = ""
        if 13 <= n <= 14:
            note = " ← λ"
        print(f"{n:>3} | {ph['n_pairs']:>5} | {ph['good_pairs']:>4} | {ph['good_ratio']:>5.2f} | {ph['avg_resonance']:>6.3f} |{note}")

    # Now test resonance success rate over full run
    print("\n" + "=" * 80)
    print("Runtime Resonance Success Rate:")
    print("-" * 80)

    seeds = list(range(1856001, 1856016))
    prob = 0.10

    print(f"{'N':>3} | {'Coex':>5} | {'Res%':>6} | {'Checks':>7} | Status")
    print("-" * 60)

    for n in range(5, 25):
        total_rate = 0
        total_checks = 0
        coex_count = 0

        for seed in seeds:
            m = run_test_resonance_quality(seed, n, prob)
            total_rate += m['resonance_success_rate']
            total_checks += m['total_checks']
            if m['coex']:
                coex_count += 1

        avg_rate = total_rate / len(seeds) * 100
        avg_checks = total_checks / len(seeds)
        coex_pct = coex_count / len(seeds) * 100

        status = "DEAD" if coex_pct < 70 else "safe"
        marker = " ← λ" if 13 <= n <= 14 else ""

        print(f"{n:>3} | {coex_pct:>4.0f}% | {avg_rate:>5.1f}% | {avg_checks:>7.0f} | {status}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("PHASE ALIGNMENT ANALYSIS")
    print("=" * 80)

if __name__ == "__main__":
    main()
