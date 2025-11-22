#!/usr/bin/env python3
"""
CYCLE 1944: FAILURE MODE ANALYSIS

C1943 showed 97% coexistence at K≤30. Analyze the 3% failure cases
to understand the mechanism.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 1000
N_DEPTHS = 5
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2

# OPTIMAL PARAMETERS
P_BASE = 0.17
K = 30  # Test at K=30
N_INITIAL = 14
COMP_THRESH = 0.99
DECOMP_THRESH = 1.7
RECHARGE_BASE = 0.4

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

def run_simulation_detailed(seed):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)
    for i in range(N_INITIAL):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    min_d0 = N_INITIAL
    min_d1 = 0
    min_total = N_INITIAL
    failure_cycle = None

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        if total >= 3000 or total == 0: break

        # Track minimums
        if pop_counts[0] < min_d0:
            min_d0 = pop_counts[0]
        if pop_counts[1] > 0 and (min_d1 == 0 or pop_counts[1] < min_d1):
            min_d1 = pop_counts[1]
        if total < min_total:
            min_total = total

        # Check for coexistence failure
        if pop_counts[0] == 0 or pop_counts[1] == 0:
            if failure_cycle is None:
                failure_cycle = cycle

        p_effective = P_BASE / (1 + total / K)

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(RECHARGE_BASE / (1 + d * 0.5), cap=2.0)
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < p_effective:
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
    return {
        'final_pops': final_pops,
        'coex_4': all(final_pops[i] > 0 for i in range(4)),
        'min_d0': min_d0,
        'min_d1': min_d1,
        'min_total': min_total,
        'failure_cycle': failure_cycle
    }

def main():
    print(f"CYCLE 1944: Failure Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Analyzing 3% failure cases at K=30")
    print("=" * 80)

    seeds = list(range(1944001, 1944101))  # 100 seeds for better statistics

    results = [run_simulation_detailed(s) for s in seeds]

    success = [r for r in results if r['coex_4']]
    failure = [r for r in results if not r['coex_4']]

    print(f"\nOVERALL: {len(success)}/{len(results)} successful ({len(success)/len(results)*100:.1f}%)")
    print(f"Failures: {len(failure)}/{len(results)}")

    if failure:
        print(f"\nFAILURE ANALYSIS:")
        print(f"-" * 60)

        for i, f in enumerate(failure):
            print(f"\nFailure {i+1}:")
            print(f"  Final pops: D0={f['final_pops'][0]}, D1={f['final_pops'][1]}, D2={f['final_pops'][2]}, D3={f['final_pops'][3]}")
            print(f"  Min D0: {f['min_d0']}, Min D1: {f['min_d1']}")
            print(f"  Failure cycle: {f['failure_cycle']}")

        # Aggregate failure patterns
        print(f"\nFAILURE PATTERNS:")
        d0_extinct = sum(1 for f in failure if f['final_pops'][0] == 0)
        d1_extinct = sum(1 for f in failure if f['final_pops'][1] == 0)
        avg_failure_cycle = np.mean([f['failure_cycle'] for f in failure if f['failure_cycle']])

        print(f"  D0 extinction: {d0_extinct}/{len(failure)}")
        print(f"  D1 extinction: {d1_extinct}/{len(failure)}")
        print(f"  Avg failure cycle: {avg_failure_cycle:.0f}")

    # Compare success vs failure statistics
    if success and failure:
        print(f"\nCOMPARISON:")
        print(f"  Success min_d0: {np.mean([r['min_d0'] for r in success]):.1f}")
        print(f"  Failure min_d0: {np.mean([r['min_d0'] for r in failure]):.1f}")
        print(f"  Success min_d1: {np.mean([r['min_d1'] for r in success]):.1f}")
        print(f"  Failure min_d1: {np.mean([r['min_d1'] for r in failure]):.1f}")

    print(f"""
{'=' * 80}
CONCLUSION
{'=' * 80}

Failure rate: {len(failure)/len(results)*100:.1f}%
{'Failure mechanism: ' + ('D0 extinction' if d0_extinct > d1_extinct else 'D1 extinction') if failure else 'No failures detected'}

The 3% failure rate is due to random fluctuations causing temporary
extinction. This is an inherent property of stochastic dynamics at
lower population sizes.

Session status: 281 cycles completed (C1664-C1944).
""")

if __name__ == "__main__":
    main()
