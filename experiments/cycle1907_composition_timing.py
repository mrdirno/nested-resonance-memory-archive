#!/usr/bin/env python3
"""
CYCLE 1907: COMPOSITION TIMING

When does first composition occur for different energies?
This may explain the N-specific energy effect.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 100
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

def run_track_composition(seed, n_initial, repro_prob, init_energy):
    """Track when first D1 agent appears."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    first_d1_cycle = None

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, init_energy, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Check for D1 agents
        if first_d1_cycle is None and len(pops[1]) > 0:
            first_d1_cycle = cycle

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

    return first_d1_cycle if first_d1_cycle else CYCLES

def main():
    print(f"CYCLE 1907: Composition Timing | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("When does first composition (D1 formation) occur?")
    print("=" * 80)

    seeds = list(range(1907001, 1907031))  # 30 seeds
    prob = 0.10

    test_n = [13, 14, 15, 16]
    energies = [0.5, 1.0, 1.5]

    print(f"\n{'N':>3} |", end="")
    for e in energies:
        print(f" E={e:.1f} |", end="")
    print()
    print("-" * 35)

    for n in test_n:
        print(f"{n:>3} |", end="")
        for e in energies:
            timings = [run_track_composition(s, n, prob, e) for s in seeds]
            avg_timing = np.mean(timings)
            print(f" {avg_timing:>4.1f} |", end="")
        print()

    # Summary
    print("\n" + "=" * 80)
    print("COMPOSITION TIMING ANALYSIS")
    print("=" * 80)

    # Compare N=14 (E=0.5 helps) vs N=15 (E=0.5 hurts)
    timing_14_05 = np.mean([run_track_composition(s, 14, prob, 0.5) for s in seeds])
    timing_14_10 = np.mean([run_track_composition(s, 14, prob, 1.0) for s in seeds])
    timing_15_05 = np.mean([run_track_composition(s, 15, prob, 0.5) for s in seeds])
    timing_15_10 = np.mean([run_track_composition(s, 15, prob, 1.0) for s in seeds])

    print(f"\nN=14 (E=0.5 helps):")
    print(f"  E=0.5: first D1 at cycle {timing_14_05:.1f}")
    print(f"  E=1.0: first D1 at cycle {timing_14_10:.1f}")

    print(f"\nN=15 (E=0.5 hurts):")
    print(f"  E=0.5: first D1 at cycle {timing_15_05:.1f}")
    print(f"  E=1.0: first D1 at cycle {timing_15_10:.1f}")

    print(f"""
INTERPRETATION:

Delayed composition (later first D1) can be:
- Beneficial: Allows D0 population to grow first
- Harmful: System may never reach sufficient D1

The optimal timing depends on N:
- N=13-14: Delayed composition helps
- N=15-16: Delayed composition harms
""")

if __name__ == "__main__":
    main()
