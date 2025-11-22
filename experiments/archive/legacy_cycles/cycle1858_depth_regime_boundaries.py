#!/usr/bin/env python3
"""
CYCLE 1858: DEPTH REGIME BOUNDARIES

How do regime transitions scale with N_DEPTHS?
Hypothesis: λ scales with 2^(N_DEPTHS-1) since each depth doubles composition requirement.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 500
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

def run_test(seed, n_initial, repro_prob, n_depths):
    reality = RealityInterface(n_populations=n_depths, mode="SEARCH")
    np.random.seed(seed)

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(n_depths)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(n_depths):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        for d in range(n_depths - 1):
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

        for d in range(1, n_depths):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(n_depths):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    final_pops = [len(reality.get_population_agents(d)) for d in range(n_depths)]
    return sum(1 for p in final_pops if p > 0) >= 2

def find_transition_zone(n_depths, seeds, prob):
    """Find the N range where transition occurs."""
    results = []
    for n in range(4, 35):
        coex = sum(run_test(seed, n, prob, n_depths) for seed in seeds) / len(seeds) * 100
        results.append((n, coex))

    # Find first dead zone after minimum viable
    transition_start = None
    for n, coex in results:
        if coex >= 60 and transition_start is None:
            # Found minimum viable
            pass
        elif coex < 60 and transition_start is None:
            # Check if there was a safe zone before
            prev_safe = any(c >= 70 for nn, c in results if nn < n and nn > 6)
            if prev_safe:
                transition_start = n
                break

    # Find where it recovers
    transition_end = None
    if transition_start:
        for n, coex in results:
            if n > transition_start + 1 and coex >= 80:
                consecutive_safe = True
                for nn, c in results:
                    if nn > n and nn <= n + 2 and c < 70:
                        consecutive_safe = False
                        break
                if consecutive_safe:
                    transition_end = n
                    break

    return results, transition_start, transition_end

def main():
    print(f"CYCLE 1858: Depth Regime Boundaries | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("How do regime transitions scale with N_DEPTHS?")
    print("=" * 80)

    seeds = list(range(1858001, 1858016))
    prob = 0.10

    # Test different depths
    depth_configs = [3, 4, 5, 6]

    results_by_depth = {}

    for n_depths in depth_configs:
        print(f"\n{'='*80}")
        print(f"N_DEPTHS = {n_depths}")
        print("=" * 80)

        results, trans_start, trans_end = find_transition_zone(n_depths, seeds, prob)
        results_by_depth[n_depths] = {
            'results': results,
            'trans_start': trans_start,
            'trans_end': trans_end
        }

        # Show results
        print(f"\nCoexistence by N:")
        print("-" * 50)
        for n, coex in results:
            marker = ""
            if trans_start and n == trans_start:
                marker = " ← TRANS START"
            elif trans_end and n == trans_end:
                marker = " ← TRANS END"
            status = "DEAD" if coex < 70 else "safe"
            if n % 5 == 0 or marker:
                print(f"N={n:>2}: {coex:>4.0f}% ({status}){marker}")

        print(f"\nTransition zone: N = {trans_start} to {trans_end}")

        # Theoretical prediction
        predicted_min = 2 ** (n_depths - 1)
        predicted_lambda = round(predicted_min * PHI)
        print(f"Predicted: N_min = 2^{n_depths-1} = {predicted_min}, λ = {predicted_lambda}")

    # Summary analysis
    print("\n" + "=" * 80)
    print("SCALING ANALYSIS")
    print("=" * 80)

    print(f"\n{'Depths':>6} | {'Trans_Start':>11} | {'Trans_End':>9} | {'Predicted λ':>11}")
    print("-" * 45)

    for n_depths in depth_configs:
        r = results_by_depth[n_depths]
        predicted = round(2**(n_depths-1) * PHI)
        ts = r['trans_start'] if r['trans_start'] else "?"
        te = r['trans_end'] if r['trans_end'] else "?"
        print(f"{n_depths:>6} | {ts:>11} | {te:>9} | {predicted:>11}")

    print("""
Scaling Law:
  λ(d) = 2^(d-1) × φ

For d=5 (standard): λ = 2^4 × 1.618 = 16 × 1.618 = 25.9 ≈ 26
But empirically λ ≈ 14, so scaling is different.

Alternative: λ(d) = F_d × φ where F_d is d-th Fibonacci
  d=3: λ = 2 × 1.618 ≈ 3
  d=4: λ = 3 × 1.618 ≈ 5
  d=5: λ = 5 × 1.618 ≈ 8 (but we observe ~14)

Need more data to determine scaling law.
""")

if __name__ == "__main__":
    main()
