#!/usr/bin/env python3
"""
CYCLE 1856D: EARLY CASCADE DYNAMICS

Why does λ = 14 fail? Track detailed dynamics in first 20 cycles.
Hypothesis: At N=14, too many compositions happen before decomposition can return agents.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

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

def run_early_trace(seed, n_initial, repro_prob, trace_cycles=20):
    """Run and trace detailed dynamics for early cycles."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    trace = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(trace_cycles):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        cycle_comps = 0
        cycle_decomps = 0
        cycle_repros = 0

        if total == 0:
            trace.append({
                'cycle': cycle,
                'pops': [0] * N_DEPTHS,
                'total': 0,
                'comps': 0,
                'decomps': 0,
                'repros': 0
            })
            continue

        # Energy recharge
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3
                cycle_repros += 1

        # Composition
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
                    cycle_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    cycle_decomps += 1

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        # Record after all operations
        final_pops = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
        trace.append({
            'cycle': cycle,
            'pops': final_pops,
            'total': sum(final_pops),
            'comps': cycle_comps,
            'decomps': cycle_decomps,
            'repros': cycle_repros
        })

    return trace

def main():
    print(f"CYCLE 1856D: Early Cascade Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # Compare N=13 (safe) vs N=14 (dead) vs N=15 (dead)
    seed = 1856001
    prob = 0.10

    test_ns = [9, 13, 14, 15, 17]  # Mix of safe and dead

    for n in test_ns:
        trace = run_early_trace(seed, n, prob)
        status = "safe" if n in [9, 13, 17] else "DEAD"

        print(f"\nN={n} ({status}):")
        print("-" * 70)
        print(f"{'Cy':>3} | {'D0':>3} {'D1':>3} {'D2':>3} {'D3':>3} {'D4':>3} | {'Tot':>4} | {'C':>2} {'D':>2} {'R':>2}")
        print("-" * 70)

        for t in trace[:15]:
            pops = t['pops']
            print(f"{t['cycle']:>3} | {pops[0]:>3} {pops[1]:>3} {pops[2]:>3} {pops[3]:>3} {pops[4]:>3} | "
                  f"{t['total']:>4} | {t['comps']:>2} {t['decomps']:>2} {t['repros']:>2}")

    # Summary analysis
    print("\n" + "=" * 80)
    print("EARLY CASCADE ANALYSIS")
    print("=" * 80)

    # Calculate first decomposition cycle for each N
    print("\nFirst Decomposition Timing:")
    print("-" * 40)

    for n in range(5, 25):
        trace = run_early_trace(seed, n, prob)
        first_decomp = None
        for t in trace:
            if t['decomps'] > 0:
                first_decomp = t['cycle']
                break

        d1_peak = max(t['pops'][1] for t in trace)
        d0_at_decomp = trace[first_decomp]['pops'][0] if first_decomp else 0

        marker = " ← λ" if 13 <= n <= 14 else ""
        decomp_str = str(first_decomp) if first_decomp else "never"
        print(f"N={n:>2}: first decomp @ cycle {decomp_str:>5}, D1 peak={d1_peak}, D0@decomp={d0_at_decomp}{marker}")

if __name__ == "__main__":
    main()
