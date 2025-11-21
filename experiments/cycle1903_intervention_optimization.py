#!/usr/bin/env python3
"""
CYCLE 1903: INTERVENTION OPTIMIZATION

Find optimal injection size for maximum efficiency.
Test sizes: 5, 10, 15, 20 agents.
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

def run_with_injection(seed, n_initial, repro_prob, inject_size):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
        total = sum(pops)
        if total >= 3000 or total == 0: break

        # Intervention at cycle 10
        if cycle == 10:
            entropy = compute_entropy(pops)
            if entropy < 0.75:
                for j in range(inject_size):
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
    print(f"CYCLE 1903: Intervention Optimization | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Finding optimal injection size")
    print("=" * 80)

    seeds = list(range(1903001, 1903051))  # 50 seeds
    prob = 0.10
    n_test = 14  # Dead zone center

    # Baseline
    baseline = sum(run_with_injection(s, n_test, prob, 0) for s in seeds) / len(seeds) * 100

    # Test different injection sizes
    inject_sizes = [5, 10, 15, 20]

    print(f"\nBaseline at N={n_test}: {baseline:.0f}%")
    print(f"\n{'Size':>5} | {'Coex':>5} | {'Δ':>6} | {'Eff':>6}")
    print("-" * 35)

    best_eff = 0
    best_size = 0

    for size in inject_sizes:
        coex = sum(run_with_injection(s, n_test, prob, size) for s in seeds) / len(seeds) * 100
        delta = coex - baseline
        efficiency = delta / size if size > 0 else 0

        if efficiency > best_eff:
            best_eff = efficiency
            best_size = size

        print(f"{size:>5} | {coex:>4.0f}% | {delta:>+5.0f}% | {efficiency:>5.2f}%/agent")

    # Summary
    print("\n" + "=" * 80)
    print("OPTIMIZATION RESULTS")
    print("=" * 80)

    print(f"\nOptimal injection size: {best_size} agents")
    print(f"Efficiency: {best_eff:.2f}%/agent")

    print(f"""
ENGINEERING RECOMMENDATION:

Inject {best_size} D0 agents when S(10) < 0.75

This provides the best cost-benefit:
- Improvement per agent: {best_eff:.2f}%
- Expected total improvement: {best_size * best_eff:.0f}%

Larger injections have diminishing returns.
""")

if __name__ == "__main__":
    main()
