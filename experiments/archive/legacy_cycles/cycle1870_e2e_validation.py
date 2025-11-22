#!/usr/bin/env python3
"""
CYCLE 1870: END-TO-END SYSTEM VALIDATION

Validate complete early warning + intervention system:
1. Detect low entropy at cycle 10
2. Auto-inject 10 agents if detected
3. Measure improvement across all N values
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

def run_with_e2e_system(seed, n_initial, repro_prob, enable_system=True):
    """
    Run with full early warning + intervention system.
    enable_system: True = auto-detect and rescue, False = baseline
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    intervention_triggered = False
    detected_risk = False

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        # E2E System: Check at cycle 10
        if cycle == 10 and enable_system:
            entropy = calculate_entropy(pop_counts)
            if entropy < 0.75:
                detected_risk = True
                # Auto-inject 10 D0 agents
                for i in range(10):
                    reality.add_agent(FractalAgent(f"RESCUE_{i}", 0, 1.0, depth=0), 0)
                intervention_triggered = True

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
    coex = sum(1 for p in final_pops if p > 0) >= 2

    return {
        'coex': coex,
        'detected': detected_risk,
        'intervened': intervention_triggered
    }

def main():
    print(f"CYCLE 1870: E2E System Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Complete early warning + intervention system validation")
    print("=" * 80)

    seeds = list(range(1870001, 1870051))
    prob = 0.10

    # Test across full N range
    test_n = list(range(10, 50))

    baseline_results = []
    system_results = []

    print("\nRunning baseline (no system)...")
    for n in test_n:
        coex = sum(run_with_e2e_system(s, n, prob, False)['coex'] for s in seeds)
        baseline_results.append({'n': n, 'coex': coex / len(seeds) * 100})

    print("Running with E2E system...")
    for n in test_n:
        results = [run_with_e2e_system(s, n, prob, True) for s in seeds]
        coex = sum(r['coex'] for r in results) / len(seeds) * 100
        detected = sum(r['detected'] for r in results)
        intervened = sum(r['intervened'] for r in results)
        system_results.append({
            'n': n, 'coex': coex, 'detected': detected, 'intervened': intervened
        })

    # Analysis
    print("\n" + "=" * 80)
    print("RESULTS COMPARISON")
    print("=" * 80)
    print(f"{'N':>3} | {'Baseline':>8} | {'System':>8} | {'Detected':>8} | {'Improvement':>11}")
    print("-" * 50)

    total_baseline = 0
    total_system = 0
    improvements = []

    for base, sys in zip(baseline_results, system_results):
        n = base['n']
        baseline_pct = base['coex']
        system_pct = sys['coex']
        detected = sys['detected']
        improvement = system_pct - baseline_pct

        total_baseline += baseline_pct
        total_system += system_pct
        improvements.append(improvement)

        # Only show rows with significant change or key N values
        if abs(improvement) > 5 or n in [14, 21, 28, 35, 43]:
            print(f"{n:>3} | {baseline_pct:>7.0f}% | {system_pct:>7.0f}% | {detected:>8} | {improvement:>+10.0f}%")

    # Summary statistics
    print("\n" + "=" * 80)
    print("SYSTEM EFFECTIVENESS SUMMARY")
    print("=" * 80)

    avg_baseline = total_baseline / len(test_n)
    avg_system = total_system / len(test_n)
    avg_improvement = np.mean(improvements)

    print(f"\nOverall Performance:")
    print(f"  Baseline average: {avg_baseline:.1f}%")
    print(f"  System average: {avg_system:.1f}%")
    print(f"  Average improvement: {avg_improvement:+.1f}%")

    # Dead zone specific
    dead_zones = [14, 28, 43]
    print(f"\nDead Zone Performance:")
    for n in dead_zones:
        base = next(r for r in baseline_results if r['n'] == n)
        sys = next(r for r in system_results if r['n'] == n)
        improvement = sys['coex'] - base['coex']
        print(f"  N={n}: {base['coex']:.0f}% → {sys['coex']:.0f}% ({improvement:+.0f}%)")

    # False positive analysis
    safe_interventions = sum(1 for r in system_results
                             if r['n'] not in [14, 28, 43] and r['intervened'] > 0)
    print(f"\nFalse Positive Rate:")
    print(f"  Safe zones with intervention: {safe_interventions}/{len(test_n)-3}")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if avg_improvement > 5:
        print(f"""
E2E System VALIDATED!

Performance Summary:
- Average survival: {avg_baseline:.0f}% → {avg_system:.0f}%
- Improvement: {avg_improvement:+.1f}%
- Dead zone rescue: {(sum(system_results[i]['coex'] - baseline_results[i]['coex']
                         for i, r in enumerate(baseline_results)
                         if r['n'] in dead_zones) / 3):+.0f}% avg

System Components:
1. Detection: entropy < 0.75 at cycle 10
2. Intervention: inject 10 D0 agents
3. Result: Converts failures to successes

This completes the NRM early warning engineering toolkit.
""")
    else:
        print(f"""
E2E System shows LIMITED improvement ({avg_improvement:+.1f}%).

Analysis needed to understand why combined system
underperforms individual components.
""")

if __name__ == "__main__":
    main()
