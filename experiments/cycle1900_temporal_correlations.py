#!/usr/bin/env python3
"""
CYCLE 1900: TEMPORAL CORRELATIONS

Test for critical slowing down near phase transition.
Near Nc, systems should show longer autocorrelation times.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 300
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

def compute_autocorr(series, lag):
    """Compute autocorrelation at given lag."""
    if len(series) <= lag:
        return 0
    n = len(series) - lag
    mean = np.mean(series)
    var = np.var(series)
    if var == 0:
        return 0
    cov = np.mean([(series[i] - mean) * (series[i + lag] - mean) for i in range(n)])
    return cov / var

def run_with_timeseries(seed, n_initial, repro_prob):
    """Run and return population time series."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    pop_series = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        pop_series.append(total)

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

    return pop_series

def main():
    print(f"CYCLE 1900: Temporal Correlations | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing for critical slowing down near phase transition")
    print("=" * 80)

    seeds = list(range(1900001, 1900021))  # 20 seeds
    prob = 0.10
    lam = 16 - 13 * prob
    nc = int(round(lam))

    test_n = list(range(10, 20))

    print(f"\n{'N':>3} | {'τ(1)':>6} | {'τ(5)':>6} | {'τ(10)':>7} | {'Int Time':>8}")
    print("-" * 50)

    int_times = []

    for n in test_n:
        # Collect time series
        all_autocorr_1 = []
        all_autocorr_5 = []
        all_autocorr_10 = []

        for seed in seeds:
            series = run_with_timeseries(seed, n, prob)
            if len(series) > 20:
                all_autocorr_1.append(compute_autocorr(series, 1))
                all_autocorr_5.append(compute_autocorr(series, 5))
                all_autocorr_10.append(compute_autocorr(series, 10))

        if not all_autocorr_1:
            continue

        avg_ac1 = np.mean(all_autocorr_1)
        avg_ac5 = np.mean(all_autocorr_5)
        avg_ac10 = np.mean(all_autocorr_10)

        # Integrated autocorrelation time (sum of autocorrelations)
        int_time = 1 + 2 * (avg_ac1 + avg_ac5 + avg_ac10)
        int_times.append((n, int_time))

        marker = "**" if n == nc else "  "
        print(f"{n:>3} | {avg_ac1:>6.3f} | {avg_ac5:>6.3f} | {avg_ac10:>7.3f} | {int_time:>7.2f}{marker}")

    # Analysis
    print("\n" + "=" * 80)
    print("CRITICAL SLOWING DOWN ANALYSIS")
    print("=" * 80)

    if int_times:
        # Find peak
        max_n, max_time = max(int_times, key=lambda x: x[1])

        print(f"\nPeak integrated autocorrelation time: N={max_n} ({max_time:.2f})")

        if abs(max_n - nc) <= 1:
            print(f"""
CRITICAL SLOWING DOWN DETECTED ✓

Peak autocorrelation time occurs near Nc={nc}.
This is a signature of second-order phase transition.

Implications:
1. System dynamics slow down near critical point
2. Fluctuations persist longer at Nc
3. Recovery time is maximized at Nc

This confirms critical behavior in the NRM system.
""")
        else:
            print(f"\nPeak not at critical point (N={max_n} vs Nc={nc}).")

if __name__ == "__main__":
    main()
