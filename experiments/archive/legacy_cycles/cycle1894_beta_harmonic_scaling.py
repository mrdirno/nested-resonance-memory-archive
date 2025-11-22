#!/usr/bin/env python3
"""
CYCLE 1894: SCALING EXPONENT HARMONIC DECAY

How does β scale with harmonic number k?
From C1881-1882:
  k=1: β_below=0.24, β_above=0.44
  k=2: β_below=0.18, β_above=0.35

Hypothesis: β(k) ~ β(1) × k^(-α) for some α > 0
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

def run_test(seed, n_initial, repro_prob):
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

def compute_beta(coex_data, nc):
    """Compute scaling exponents below and above Nc."""
    below = [(n, c) for n, c in coex_data if n < nc and c > 0]
    above = [(n, c) for n, c in coex_data if n > nc and c < 100]

    # Log-log fit: ln(coex) = β × ln|N - Nc|
    def fit_beta(data, nc):
        if len(data) < 2:
            return 0
        deltas = [abs(n - nc) for n, c in data]
        coex = [c/100 for n, c in data]
        ln_d = [math.log(d) for d in deltas if d > 0]
        ln_c = [math.log(c) for c in coex if c > 0]
        if len(ln_d) < 2:
            return 0
        slope, _ = np.polyfit(ln_d[:len(ln_c)], ln_c, 1)
        return abs(slope)

    beta_below = fit_beta(below, nc)
    beta_above = fit_beta(above, nc)
    return beta_below, beta_above

def main():
    print(f"CYCLE 1894: β Harmonic Scaling | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing β(k) ~ β(1) × k^(-α)")
    print("=" * 80)

    seeds = list(range(1894001, 1894041))  # 40 seeds
    prob = 0.10
    lam = 16 - 13 * prob

    harmonics = [1, 2]
    results = {}

    for k in harmonics:
        nc = int(round(k * lam))

        # Scan around critical point
        test_range = range(nc - 5, nc + 7)
        coex_data = []

        print(f"\nHarmonic k={k} (Nc={nc}):")
        print(f"{'N':>3} | {'Coex':>5}")
        print("-" * 15)

        for n in test_range:
            coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
            coex_data.append((n, coex))
            marker = "**" if n == nc else "  "
            print(f"{n:>3} | {coex:>4.0f}%{marker}")

        beta_below, beta_above = compute_beta(coex_data, nc)
        results[k] = {'below': beta_below, 'above': beta_above}

    # Analysis
    print("\n" + "=" * 80)
    print("HARMONIC SCALING ANALYSIS")
    print("=" * 80)

    print(f"\n{'k':>3} | {'β_below':>8} | {'β_above':>8} | {'Ratio':>6}")
    print("-" * 35)

    for k in harmonics:
        r = results[k]
        ratio = r['above'] / r['below'] if r['below'] > 0 else 0
        print(f"{k:>3} | {r['below']:>8.3f} | {r['above']:>8.3f} | {ratio:>6.2f}")

    # Fit decay
    if len(harmonics) >= 2:
        k_vals = [1, 2]
        beta_b = [results[k]['below'] for k in k_vals]
        beta_a = [results[k]['above'] for k in k_vals]

        # Compute decay exponent: β(k) = β(1) × k^(-α)
        # ln(β) = ln(β(1)) - α × ln(k)
        if beta_b[0] > 0 and beta_b[1] > 0:
            alpha_below = -math.log(beta_b[1]/beta_b[0]) / math.log(2)
        else:
            alpha_below = 0

        if beta_a[0] > 0 and beta_a[1] > 0:
            alpha_above = -math.log(beta_a[1]/beta_a[0]) / math.log(2)
        else:
            alpha_above = 0

        print(f"\nDecay exponent α:")
        print(f"  Below: α = {alpha_below:.2f}")
        print(f"  Above: α = {alpha_above:.2f}")

        if alpha_below > 0 and alpha_above > 0:
            print(f"""
HARMONIC DECAY CONFIRMED:

β(k) ~ β(1) × k^(-α)

Below Nc: α ≈ {alpha_below:.2f}
Above Nc: α ≈ {alpha_above:.2f}

Higher harmonics show weaker criticality.
The scaling exponents decay as a power law.
""")

if __name__ == "__main__":
    main()
