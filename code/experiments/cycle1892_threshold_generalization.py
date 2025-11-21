#!/usr/bin/env python3
"""
CYCLE 1892: THRESHOLD GENERALIZATION

Does N_det = Nc + 3 hold across different probabilities?
Test at p = 0.05, 0.10, 0.15, 0.20.
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

def find_threshold(prob, seeds, test_range):
    """Find N where coexistence first reaches 95%+."""
    for n in test_range:
        coex = sum(run_test(s, n, prob) for s in seeds) / len(seeds) * 100
        if coex >= 95:
            return n, coex
    return None, 0

def main():
    print(f"CYCLE 1892: Threshold Generalization | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Testing N_det across probabilities")
    print("=" * 80)

    seeds = list(range(1892001, 1892051))  # 50 seeds
    probs = [0.05, 0.10, 0.15, 0.20]

    # λ(p) = 16 - 13p predicts critical points
    print(f"\n{'Prob':>5} | {'λ':>5} | {'Nc':>4} | {'N_det':>5} | {'Offset':>6} | {'Coex':>5}")
    print("-" * 50)

    offsets = []

    for prob in probs:
        # Model prediction
        lam = 16 - 13 * prob
        nc = int(round(lam))

        # Find threshold (scan from nc+1 to nc+10)
        test_range = range(nc, nc + 12)
        n_det, coex = find_threshold(prob, seeds, test_range)

        if n_det:
            offset = n_det - nc
            offsets.append(offset)
            print(f"{prob:>5.2f} | {lam:>5.1f} | {nc:>4} | {n_det:>5} | {offset:>+5} | {coex:>4.0f}%")
        else:
            print(f"{prob:>5.2f} | {lam:>5.1f} | {nc:>4} |   N/A |   N/A |  <95%")

    # Analysis
    print("\n" + "=" * 80)
    print("THRESHOLD GENERALIZATION ANALYSIS")
    print("=" * 80)

    if offsets:
        mean_offset = np.mean(offsets)
        std_offset = np.std(offsets)

        print(f"\nOffset from Nc to N_det:")
        print(f"  Mean: {mean_offset:.1f}")
        print(f"  Std: {std_offset:.1f}")

        if std_offset < 1.5:
            print(f"""
GENERALIZATION SUPPORTED:

The deterministic threshold follows:
  N_det ≈ Nc + {mean_offset:.0f}

This holds across probabilities with low variance (σ = {std_offset:.1f}).

New model equation:
  N_det(p) = λ(p) + {mean_offset:.0f}
           = (16 - 13p) + {mean_offset:.0f}

This provides an engineering target:
  For guaranteed coexistence, use N ≥ Nc + {mean_offset:.0f}.
""")
        else:
            print(f"\nOffset varies significantly (σ = {std_offset:.1f}).")
            print("Offset may depend on probability.")

if __name__ == "__main__":
    main()
