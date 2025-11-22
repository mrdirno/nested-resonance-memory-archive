#!/usr/bin/env python3
"""
CYCLE 1899: INTERVENTION SYSTEM VALIDATION

Test early warning + intervention at p=0.12.
Verify the complete E2E system works at the new probability.
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
    total = sum(pops)
    if total == 0: return 0
    probs = [p/total for p in pops if p > 0]
    return -sum(p * math.log2(p) for p in probs)

def run_with_intervention(seed, n_initial, repro_prob, intervene=False):
    """Run with optional intervention at cycle 10."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
        total = sum(pops)
        if total >= 3000 or total == 0: break

        # Intervention check at cycle 10
        if cycle == 10 and intervene:
            entropy = compute_entropy(pops)
            if entropy < 0.75:
                # Inject 10 D0 agents
                for j in range(10):
                    reality.add_agent(FractalAgent(f"RESCUE_{j}", 0, 1.0, depth=0), 0)

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
    return sum(1 for p in final_pops if p > 0) >= 2

def main():
    print(f"CYCLE 1899: Intervention Validation | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing E2E intervention system at p = 0.12")
    print("=" * 80)

    seeds = list(range(1899001, 1899051))  # 50 seeds
    prob = 0.12
    lam = 16 - 13 * prob
    nc = int(round(lam))

    # Test at dead zone and nearby
    test_n = list(range(nc - 2, nc + 4))

    print(f"\n{'N':>3} | {'Baseline':>8} | {'With Int':>8} | {'Δ':>6}")
    print("-" * 40)

    improvements = []

    for n in test_n:
        baseline = sum(run_with_intervention(s, n, prob, False) for s in seeds) / len(seeds) * 100
        with_int = sum(run_with_intervention(s, n, prob, True) for s in seeds) / len(seeds) * 100
        delta = with_int - baseline
        improvements.append(delta)

        marker = "**" if n == nc else "  "
        print(f"{n:>3} | {baseline:>7.0f}% | {with_int:>7.0f}% | {delta:>+5.0f}%{marker}")

    # Summary
    print("\n" + "=" * 80)
    print("INTERVENTION SYSTEM VALIDATION")
    print("=" * 80)

    avg_improvement = np.mean(improvements)
    max_improvement = max(improvements)

    print(f"\nIntervention performance at p = {prob}:")
    print(f"  Average improvement: {avg_improvement:+.1f}%")
    print(f"  Maximum improvement: {max_improvement:+.1f}%")

    if avg_improvement > 5:
        print("\nINTERVENTION SYSTEM VALIDATED ✓")
        print("Early warning + intervention effective at new probability.")
    else:
        print("\nIntervention effect weak at this probability.")

if __name__ == "__main__":
    main()
