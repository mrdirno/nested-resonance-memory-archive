#!/usr/bin/env python3
"""
CYCLE 1872: MULTI-PROBABILITY SYSTEM TEST

Does the entropy < 0.75 threshold work across all probabilities?
Test E2E system at prob = 0.05, 0.10, 0.15, 0.20
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

def calculate_entropy(pop_counts):
    total = sum(pop_counts)
    if total == 0:
        return 0
    probs = [p / total for p in pop_counts if p > 0]
    return -sum(p * np.log2(p) for p in probs if p > 0)

def run_with_system(seed, n_initial, repro_prob, enable_system=True, threshold=0.75):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        if cycle == 10 and enable_system:
            entropy = calculate_entropy(pop_counts)
            if entropy < threshold:
                for i in range(10):
                    reality.add_agent(FractalAgent(f"RESCUE_{i}", 0, 1.0, depth=0), 0)

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
    print(f"CYCLE 1872: Multi-Probability Test | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Does threshold=0.75 work across all probabilities?")
    print("=" * 80)

    seeds = list(range(1872001, 1872031))  # 30 seeds
    test_probs = [0.05, 0.10, 0.15, 0.20]

    results = []

    for prob in test_probs:
        # Calculate predicted λ
        pred_lambda = 16 - 13 * prob

        # Test dead zone for this prob
        dead_zone = int(pred_lambda)

        # Test range around dead zone
        test_n = list(range(dead_zone - 3, dead_zone + 4))

        print(f"\n{'='*60}")
        print(f"PROB = {prob:.2f}, λ = {pred_lambda:.1f}")
        print("=" * 60)
        print(f"{'N':>3} | {'Baseline':>8} | {'System':>8} | {'Improvement':>11}")
        print("-" * 40)

        total_base = 0
        total_sys = 0

        for n in test_n:
            baseline = sum(run_with_system(s, n, prob, False) for s in seeds) / len(seeds) * 100
            system = sum(run_with_system(s, n, prob, True) for s in seeds) / len(seeds) * 100
            improvement = system - baseline

            total_base += baseline
            total_sys += system

            marker = "***" if n == dead_zone else ""
            print(f"{n:>3} | {baseline:>7.0f}% | {system:>7.0f}% | {improvement:>+10.0f}% {marker}")

        avg_base = total_base / len(test_n)
        avg_sys = total_sys / len(test_n)
        avg_imp = avg_sys - avg_base

        results.append({
            'prob': prob,
            'lambda': pred_lambda,
            'baseline': avg_base,
            'system': avg_sys,
            'improvement': avg_imp
        })

        print("-" * 40)
        print(f"Avg | {avg_base:>7.1f}% | {avg_sys:>7.1f}% | {avg_imp:>+10.1f}%")

    # Summary
    print("\n" + "=" * 80)
    print("CROSS-PROBABILITY SUMMARY")
    print("=" * 80)
    print(f"{'Prob':>5} | {'λ':>4} | {'Baseline':>8} | {'System':>8} | {'Improvement':>11}")
    print("-" * 50)

    for r in results:
        print(f"{r['prob']:>5.2f} | {r['lambda']:>4.1f} | {r['baseline']:>7.1f}% | "
              f"{r['system']:>7.1f}% | {r['improvement']:>+10.1f}%")

    avg_improvement = np.mean([r['improvement'] for r in results])
    print("-" * 50)
    print(f"Overall average improvement: {avg_improvement:+.1f}%")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if avg_improvement > 5:
        print(f"""
Threshold = 0.75 WORKS across probabilities!

System performance by prob:""")
        for r in results:
            print(f"  prob={r['prob']:.2f}: {r['improvement']:+.1f}% improvement")
        print(f"""
Average improvement: {avg_improvement:+.1f}%

The E2E system is probability-agnostic and generalizes well.
""")
    else:
        print(f"""
Threshold = 0.75 may need tuning for different probabilities.
Average improvement only {avg_improvement:+.1f}%.
""")

if __name__ == "__main__":
    main()
