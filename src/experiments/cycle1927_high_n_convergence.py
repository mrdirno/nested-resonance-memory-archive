#!/usr/bin/env python3
"""
CYCLE 1927: HIGH N CONVERGENCE TEST

C1926 showed N=10 (88%) broke the odd-even pattern.
Test N=10-20 to map convergence behavior.
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

DECOMP_THRESH = 0.8
COMP_THRESH = 0.99
RECHARGE_BASE = 0.2
REPRO_PROB = 0.17

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

def run_simulation(seed, n_initial):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)
    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < REPRO_PROB:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= COMP_THRESH:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESH:
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
    return final_pops[0] > 0 and final_pops[1] > 0

def main():
    print(f"CYCLE 1927: High N Convergence | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print(f"Testing N=10-20 at p = {REPRO_PROB} to map convergence")
    print("=" * 80)

    seeds = list(range(1927001, 1927041))  # 40 seeds
    n_values = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]

    print(f"\n{'N':>3} | {'Coex %':>7} | {'Type':>5}")
    print("-" * 24)

    results = {}
    for n in n_values:
        coex = np.mean([run_simulation(s, n) for s in seeds]) * 100
        results[n] = coex
        parity = "ODD" if n % 2 == 1 else "EVEN"
        print(f"{n:>3} | {coex:>6.1f}% | {parity:>5}")

    # Analysis
    print("\n" + "=" * 80)
    print("CONVERGENCE ANALYSIS")
    print("=" * 80)

    odd_avg = np.mean([results[n] for n in n_values if n % 2 == 1])
    even_avg = np.mean([results[n] for n in n_values if n % 2 == 0])
    avg_all = np.mean(list(results.values()))
    std_all = np.std(list(results.values()))

    print(f"\nOdd N average:  {odd_avg:.1f}%")
    print(f"Even N average: {even_avg:.1f}%")
    print(f"Overall average: {avg_all:.1f}% ± {std_all:.1f}%")

    # Check convergence
    converged = std_all < 5.0

    print(f"""
CONCLUSION:

High N convergence analysis (N=10-20):

1. Average coexistence: {avg_all:.1f}% ± {std_all:.1f}%
2. Odd-even difference: {odd_avg - even_avg:+.1f}%
3. Convergence: {'YES (σ < 5%)' if converged else 'NO (σ ≥ 5%)'}

Physical interpretation:
- System {'has converged' if converged else 'still shows variation'} at high N
- Odd-even effect {'eliminated' if abs(odd_avg - even_avg) < 3 else 'persists weakly'}
- Population dynamics {'stabilize' if converged else 'remain sensitive'}

Optimal high-N: {max(results, key=results.get)} ({max(results.values()):.0f}%)

Session status: 264 cycles completed (C1664-C1927).
""")

if __name__ == "__main__":
    main()
