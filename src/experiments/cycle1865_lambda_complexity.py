#!/usr/bin/env python3
"""
CYCLE 1865: λ-COMPLEXITY RELATIONSHIP

Does the wavelength λ correlate with system complexity?
Measure: Total agents, depth distribution, composition rate
at different N values relative to λ.
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

def run_test_complexity(seed, n_initial, repro_prob):
    """Run test and measure complexity metrics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    total_agents_history = []
    compositions = 0
    decompositions = 0

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        total_agents_history.append(total)

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
                    compositions += 1
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
                    decompositions += 1

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    coex = sum(1 for p in final_pops if p > 0) >= 2

    # Complexity metrics
    avg_total = np.mean(total_agents_history) if total_agents_history else 0
    max_total = max(total_agents_history) if total_agents_history else 0
    depth_entropy = 0
    if sum(final_pops) > 0:
        probs = [p / sum(final_pops) for p in final_pops if p > 0]
        depth_entropy = -sum(p * np.log2(p) for p in probs if p > 0)

    return {
        'coex': coex,
        'avg_total': avg_total,
        'max_total': max_total,
        'compositions': compositions,
        'decompositions': decompositions,
        'depth_entropy': depth_entropy,
        'final_total': sum(final_pops)
    }

def main():
    print(f"CYCLE 1865: λ-Complexity Relationship | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Does wavelength correlate with system complexity?")
    print("=" * 80)

    seeds = list(range(1865001, 1865016))
    prob = 0.10
    lambda1 = 14

    # Calculate k-values for each N
    print("\nComplexity metrics by k-value (N/λ):")
    print("-" * 80)
    print(f"{'N':>3} | {'k':>5} | {'Coex':>4} | {'AvgTot':>6} | {'Comp':>5} | {'Entr':>5} | Type")
    print("-" * 80)

    results = []
    for n in range(8, 50):
        metrics = {
            'avg_total': 0, 'max_total': 0, 'compositions': 0,
            'decompositions': 0, 'depth_entropy': 0, 'coex': 0
        }

        for seed in seeds:
            m = run_test_complexity(seed, n, prob)
            for key in metrics:
                if key == 'coex':
                    metrics[key] += 1 if m[key] else 0
                else:
                    metrics[key] += m[key]

        n_seeds = len(seeds)
        for key in metrics:
            if key != 'coex':
                metrics[key] /= n_seeds

        coex_pct = metrics['coex'] / n_seeds * 100
        k = n / lambda1

        # Classify
        zone_type = ""
        if coex_pct < 70:
            zone_type = "DEAD"
        elif abs(k - round(k)) < 0.15:
            zone_type = "harmonic"
        elif abs(k - round(k) - 0.5) < 0.15:
            zone_type = "anti-node"
        else:
            zone_type = "safe"

        results.append({
            'n': n, 'k': k, 'coex': coex_pct,
            'avg_total': metrics['avg_total'],
            'compositions': metrics['compositions'],
            'entropy': metrics['depth_entropy'],
            'type': zone_type
        })

        if n % 7 == 0 or zone_type in ["DEAD", "anti-node"]:
            print(f"{n:>3} | {k:>5.2f} | {coex_pct:>3.0f}% | {metrics['avg_total']:>6.0f} | "
                  f"{metrics['compositions']:>5.0f} | {metrics['depth_entropy']:>5.2f} | {zone_type}")

    # Analysis
    print("\n" + "=" * 80)
    print("COMPLEXITY ANALYSIS")
    print("=" * 80)

    # Compare dead vs safe
    dead = [r for r in results if r['type'] == "DEAD"]
    safe = [r for r in results if r['type'] in ["safe", "anti-node"]]

    if dead and safe:
        avg_comp_dead = np.mean([r['compositions'] for r in dead])
        avg_comp_safe = np.mean([r['compositions'] for r in safe])
        avg_ent_dead = np.mean([r['entropy'] for r in dead])
        avg_ent_safe = np.mean([r['entropy'] for r in safe])

        print(f"\nDead zones (n={len(dead)}):")
        print(f"  Avg compositions: {avg_comp_dead:.0f}")
        print(f"  Avg entropy: {avg_ent_dead:.2f}")

        print(f"\nSafe zones (n={len(safe)}):")
        print(f"  Avg compositions: {avg_comp_safe:.0f}")
        print(f"  Avg entropy: {avg_ent_safe:.2f}")

        print(f"\nRatio (safe/dead):")
        print(f"  Compositions: {avg_comp_safe/avg_comp_dead:.2f}x")
        print(f"  Entropy: {avg_ent_safe/avg_ent_dead:.2f}x")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

if __name__ == "__main__":
    main()
