#!/usr/bin/env python3
"""
CYCLE 1886: ABSOLUTE EVENT COUNT HYPOTHESIS

Why is β_above > β_below? (Recovery faster above Nc than below)
Hypothesis: Systems above Nc have MORE total events, providing better buffering.
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

def run_with_tracking(seed, n_initial, repro_prob):
    """Track total events and population dynamics."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    total_comps = 0
    total_decomps = 0
    max_pop = n_initial
    avg_pop = 0
    pop_samples = 0

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        max_pop = max(max_pop, total)
        avg_pop += total
        pop_samples += 1

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Count compositions
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= 0.5:
                    total_comps += 1
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Count decompositions
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    total_decomps += 1
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
        'total_events': total_comps + total_decomps,
        'compositions': total_comps,
        'decompositions': total_decomps,
        'max_pop': max_pop,
        'avg_pop': avg_pop / pop_samples if pop_samples > 0 else 0
    }

def main():
    print(f"CYCLE 1886: Absolute Event Count | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: More total events = better buffering = faster recovery")
    print("=" * 80)

    seeds = list(range(1886001, 1886051))
    prob = 0.10
    n_c = 14

    # Test range around critical point
    test_n = list(range(10, 19))

    print(f"\n{'N':>3} | {'Coex':>5} | {'Events':>7} | {'AvgPop':>7} | {'E/Pop':>6}")
    print("-" * 50)

    below_events = []
    above_events = []
    below_epop = []
    above_epop = []

    for n in test_n:
        results = [run_with_tracking(s, n, prob) for s in seeds]

        coex = sum(r['coex'] for r in results) / len(seeds) * 100
        events = np.mean([r['total_events'] for r in results])
        avg_pop = np.mean([r['avg_pop'] for r in results])
        e_per_pop = events / avg_pop if avg_pop > 0 else 0

        if n < n_c:
            below_events.append(events)
            below_epop.append(e_per_pop)
        elif n > n_c:
            above_events.append(events)
            above_epop.append(e_per_pop)

        marker = "**" if n == n_c else "  "
        print(f"{n:>3} | {coex:>4.0f}% | {events:>7.0f} | {avg_pop:>7.1f} | {e_per_pop:>6.2f}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("ASYMMETRY ANALYSIS: Absolute Event Counts")
    print("=" * 80)

    avg_below_events = np.mean(below_events)
    avg_above_events = np.mean(above_events)
    avg_below_epop = np.mean(below_epop)
    avg_above_epop = np.mean(above_epop)

    print(f"\nTotal Events:")
    print(f"  Below Nc: {avg_below_events:.0f}")
    print(f"  Above Nc: {avg_above_events:.0f}")
    print(f"  Ratio: {avg_above_events/avg_below_events:.2f}x")

    print(f"\nEvents per Population:")
    print(f"  Below Nc: {avg_below_epop:.2f}")
    print(f"  Above Nc: {avg_above_epop:.2f}")

    if avg_above_events > avg_below_events:
        print(f"""
HYPOTHESIS SUPPORTED:

Above Nc, systems have {avg_above_events/avg_below_events:.2f}x more total events.

Mechanism:
1. More agents → more total events (comps + decomps)
2. More events → better averaging of stochastic effects
3. Better averaging → more stable trajectories
4. Stable trajectories → faster recovery above Nc

This explains why β_above > β_below.
""")
    else:
        print("\nHypothesis not supported. Other mechanism at work.")

    # Additional: Check if it's events or events/population
    print("\n" + "-" * 50)
    print("Secondary Analysis: Per-capita event rate")
    print("-" * 50)

    if avg_above_epop > avg_below_epop:
        print(f"Per-capita rate also higher above Nc ({avg_above_epop:.2f} vs {avg_below_epop:.2f})")
        print("Both absolute and relative event counts favor above-Nc systems.")
    else:
        print(f"Per-capita rate LOWER above Nc ({avg_above_epop:.2f} vs {avg_below_epop:.2f})")
        print("Asymmetry driven by absolute counts, not activity rate.")

if __name__ == "__main__":
    main()
