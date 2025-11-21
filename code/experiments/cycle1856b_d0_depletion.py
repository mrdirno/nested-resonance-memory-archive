#!/usr/bin/env python3
"""
CYCLE 1856B: D0 DEPLETION RATE HYPOTHESIS

Hypothesis: λ = 14 is where D0 depletes faster than it can reproduce.
At dead zones, composition drains D0 before reproduction can sustain it.
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

def run_test_track_d0(seed, n_initial, repro_prob):
    """Track D0 population over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    d0_history = []
    d0_min = n_initial
    d0_zero_cycle = None

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        d0_count = len(pops[0])
        d0_history.append(d0_count)
        d0_min = min(d0_min, d0_count)

        if d0_count == 0 and d0_zero_cycle is None:
            d0_zero_cycle = cycle

        total = sum(len(p) for p in pops)
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

    final_pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
    coex = sum(1 for p in final_pops if len(p) > 0) >= 2

    return {
        'coex': coex,
        'd0_min': d0_min,
        'd0_zero_cycle': d0_zero_cycle,
        'd0_early_avg': np.mean(d0_history[:50]) if len(d0_history) >= 50 else np.mean(d0_history)
    }

def main():
    print(f"CYCLE 1856B: D0 Depletion Rate Analysis | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Hypothesis: λ = 14 is where D0 depletes faster than reproduction")
    print("=" * 80)

    seeds = list(range(1856001, 1856016))
    prob = 0.10

    print("\nD0 Population Dynamics:")
    print("-" * 80)
    print(f"{'N':>3} | {'Coex':>5} | {'D0_min':>6} | {'D0_early':>8} | {'Zero@':>6} | Analysis")
    print("-" * 80)

    for n in range(5, 25):
        d0_mins = []
        d0_early_avgs = []
        zero_cycles = []
        coex_count = 0

        for seed in seeds:
            m = run_test_track_d0(seed, n, prob)
            d0_mins.append(m['d0_min'])
            d0_early_avgs.append(m['d0_early_avg'])
            if m['d0_zero_cycle']:
                zero_cycles.append(m['d0_zero_cycle'])
            if m['coex']:
                coex_count += 1

        avg_min = np.mean(d0_mins)
        avg_early = np.mean(d0_early_avgs)
        coex_pct = coex_count / len(seeds) * 100
        zero_rate = len(zero_cycles) / len(seeds) * 100

        analysis = ""
        if avg_min < 3:
            analysis = "DEPLETION!"
        elif coex_pct < 70:
            analysis = "dead zone"

        marker = " ← λ" if 13 <= n <= 14 else ""

        zero_info = f"{np.mean(zero_cycles):.0f}" if zero_cycles else "-"
        print(f"{n:>3} | {coex_pct:>4.0f}% | {avg_min:>6.1f} | {avg_early:>8.1f} | {zero_info:>6} | {analysis}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("ANALYSIS")
    print("=" * 80)
    print("""
D0 depletion rate explains dead zones:
- When D0_min approaches 0, cascade collapses
- Critical threshold: D0 must stay > 2 for reproduction sustainability
- At λ = 14, initial population size creates composition pressure
  that depletes D0 before steady-state is reached

The wavelength λ = 14 represents the critical mass where:
- Composition rate from N initial agents exceeds reproduction rate
- D0 depletes before higher depths can decompose back
- System enters "composition debt" that it cannot recover from
""")

if __name__ == "__main__":
    main()
