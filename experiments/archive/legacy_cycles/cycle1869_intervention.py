#!/usr/bin/env python3
"""
CYCLE 1869: INTERVENTION TESTING

Can we rescue dead zones by injecting D0 agents at cycle 10?
Test: if entropy < 0.75, add agents to reach safe zone N
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

def run_test_with_intervention(seed, n_initial, repro_prob, intervention_n=0):
    """
    Run test with optional intervention at cycle 10.
    intervention_n: number of D0 agents to add if entropy < 0.75
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    intervention_triggered = False

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        # Check for intervention at cycle 10
        if cycle == 10 and intervention_n > 0:
            entropy = calculate_entropy(pop_counts)
            if entropy < 0.75:
                # Inject new D0 agents
                for i in range(intervention_n):
                    reality.add_agent(FractalAgent(f"INT_{i}", 0, 1.0, depth=0), 0)
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
        'intervention_triggered': intervention_triggered
    }

def main():
    print(f"CYCLE 1869: Intervention Testing | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Can we rescue dead zones by injecting D0 agents?")
    print("=" * 80)

    seeds = list(range(1869001, 1869051))
    prob = 0.10

    # Test dead zones with various intervention sizes
    dead_zones = [14, 28, 43]  # λ₁, λ₂, λ₃
    intervention_sizes = [0, 5, 7, 10, 14, 21]  # 0 = no intervention

    print("\nIntervention Results by Dead Zone")
    print("=" * 80)

    for n in dead_zones:
        print(f"\n{'-'*60}")
        print(f"N = {n} (dead zone)")
        print(f"{'-'*60}")
        print(f"{'Inject':>6} | {'Coex %':>7} | {'Rescued':>8} | {'Effect':>8}")
        print("-" * 40)

        baseline_coex = 0
        for idx, inject in enumerate(intervention_sizes):
            coex_count = 0
            triggered_count = 0

            for seed in seeds:
                result = run_test_with_intervention(seed, n, prob, inject)
                if result['coex']:
                    coex_count += 1
                if result['intervention_triggered']:
                    triggered_count += 1

            coex_pct = coex_count / len(seeds) * 100

            if inject == 0:
                baseline_coex = coex_pct
                effect = "baseline"
            else:
                improvement = coex_pct - baseline_coex
                effect = f"{improvement:+.0f}%"

            print(f"{inject:>6} | {coex_pct:>6.0f}% | {triggered_count:>8} | {effect:>8}")

    # Summary
    print("\n" + "=" * 80)
    print("INTERVENTION EFFECTIVENESS")
    print("=" * 80)

    # Detailed test for N=14
    print("\nDetailed analysis for N=14:")
    n = 14
    baseline = sum(run_test_with_intervention(s, n, prob, 0)['coex'] for s in seeds) / len(seeds) * 100

    best_inject = 0
    best_coex = baseline
    for inject in [5, 7, 10, 14]:
        coex = sum(run_test_with_intervention(s, n, prob, inject)['coex'] for s in seeds) / len(seeds) * 100
        if coex > best_coex:
            best_coex = coex
            best_inject = inject

    print(f"  Baseline: {baseline:.0f}%")
    print(f"  Best intervention: inject {best_inject} agents → {best_coex:.0f}%")
    print(f"  Improvement: {best_coex - baseline:+.0f}%")

    # Target for rescue
    target_n = 21  # safe zone
    delta = target_n - n
    print(f"\n  To move from N=14 to N=21 (safe zone):")
    print(f"  Need to inject {delta} agents")

    coex_21 = sum(run_test_with_intervention(s, n, prob, delta)['coex'] for s in seeds) / len(seeds) * 100
    print(f"  Result: {coex_21:.0f}% coexistence")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)

    if best_coex > baseline + 20:
        print(f"""
Intervention IS effective!

Protocol:
1. Monitor entropy at cycle 10
2. If entropy < 0.75 (collapse risk)
3. Inject {best_inject} D0 agents
4. Expected improvement: {best_coex - baseline:+.0f}%

This converts dead zones to safe zones via targeted intervention.
""")
    else:
        print(f"""
Intervention has LIMITED effect.

Even with {best_inject} agents injected:
- Improvement only {best_coex - baseline:+.0f}%
- System dynamics dominate initial conditions

Dead zone behavior is resistant to late-stage rescue.
Prevention (choosing safe N) better than intervention.
""")

if __name__ == "__main__":
    main()
