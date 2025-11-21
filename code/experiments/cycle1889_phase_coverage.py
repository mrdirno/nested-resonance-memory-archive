#!/usr/bin/env python3
"""
CYCLE 1889: PHASE SPACE COVERAGE HYPOTHESIS

Why is β_above > β_below?
Hypothesis: More agents = better depth distribution coverage = stability.
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

def compute_entropy(pops):
    """Shannon entropy of depth distribution."""
    total = sum(pops)
    if total == 0: return 0
    probs = [p/total for p in pops if p > 0]
    return -sum(p * math.log2(p) for p in probs)

def run_with_coverage(seed, n_initial, repro_prob):
    """Track depth distribution coverage."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    entropy_samples = []
    depth_coverage = []  # How many depths occupied

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
        total = sum(pops)
        if total >= 3000 or total == 0: break

        # Track coverage metrics
        entropy = compute_entropy(pops)
        coverage = sum(1 for p in pops if p > 0)
        entropy_samples.append(entropy)
        depth_coverage.append(coverage)

        for d in range(N_DEPTHS):
            for agent in reality.get_population_agents(d):
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

    # Metrics
    avg_entropy = np.mean(entropy_samples) if entropy_samples else 0
    max_coverage = max(depth_coverage) if depth_coverage else 0
    avg_coverage = np.mean(depth_coverage) if depth_coverage else 0

    return {
        'coex': coex,
        'avg_entropy': avg_entropy,
        'max_coverage': max_coverage,
        'avg_coverage': avg_coverage
    }

def main():
    print(f"CYCLE 1889: Phase Space Coverage | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: Better depth coverage above Nc → stability")
    print("=" * 80)

    seeds = list(range(1889001, 1889051))
    prob = 0.10
    n_c = 14

    test_n = list(range(10, 19))

    print(f"\n{'N':>3} | {'Coex':>5} | {'AvgEnt':>6} | {'MaxCov':>6} | {'AvgCov':>6}")
    print("-" * 50)

    below_ent = []
    above_ent = []
    below_cov = []
    above_cov = []

    for n in test_n:
        results = [run_with_coverage(s, n, prob) for s in seeds]

        coex = sum(r['coex'] for r in results) / len(seeds) * 100
        avg_ent = np.mean([r['avg_entropy'] for r in results])
        max_cov = np.mean([r['max_coverage'] for r in results])
        avg_cov = np.mean([r['avg_coverage'] for r in results])

        if n < n_c:
            below_ent.append(avg_ent)
            below_cov.append(avg_cov)
        elif n > n_c:
            above_ent.append(avg_ent)
            above_cov.append(avg_cov)

        marker = "**" if n == n_c else "  "
        print(f"{n:>3} | {coex:>4.0f}% | {avg_ent:>6.3f} | {max_cov:>6.1f} | {avg_cov:>6.2f}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("ASYMMETRY ANALYSIS: Phase Space Coverage")
    print("=" * 80)

    avg_below_ent = np.mean(below_ent)
    avg_above_ent = np.mean(above_ent)
    avg_below_cov = np.mean(below_cov)
    avg_above_cov = np.mean(above_cov)

    print(f"\nAverage depth entropy:")
    print(f"  Below Nc: {avg_below_ent:.3f}")
    print(f"  Above Nc: {avg_above_ent:.3f}")

    print(f"\nAverage depth coverage:")
    print(f"  Below Nc: {avg_below_cov:.2f}")
    print(f"  Above Nc: {avg_above_cov:.2f}")

    if avg_above_cov > avg_below_cov:
        print(f"""
HYPOTHESIS SUPPORTED:

Above Nc, systems have better coverage ({avg_above_cov:.2f} vs {avg_below_cov:.2f}).

Mechanism:
1. More initial agents → more early compositions
2. More compositions → agents at multiple depths
3. Multi-depth presence → redundant stability pathways
4. Redundancy → faster recovery above Nc

This explains why β_above > β_below.
""")
    else:
        print("\nHypothesis not supported. Coverage similar or lower above Nc.")

if __name__ == "__main__":
    main()
