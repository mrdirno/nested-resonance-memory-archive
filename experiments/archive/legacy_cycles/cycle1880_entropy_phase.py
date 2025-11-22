#!/usr/bin/env python3
"""
CYCLE 1880: ENTROPY-PHASE RELATIONSHIP

Does low entropy correlate with high phase alignment?
Hypothesis: Dead zones have low entropy because of synchronized phase composition.
"""
import sys, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLES = 100  # Shorter for detailed tracking
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

def calculate_entropy(pop_counts):
    total = sum(pop_counts)
    if total == 0:
        return 0
    probs = [p / total for p in pop_counts if p > 0]
    return -sum(p * np.log2(p) for p in probs if p > 0)

def run_entropy_phase_analysis(seed, n_initial, repro_prob):
    """Track both entropy and average phase resonance over time."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    entropy_history = []
    avg_resonance_history = []
    composition_rate_history = []

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        # Record entropy
        entropy = calculate_entropy(pop_counts)
        entropy_history.append(entropy)

        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Track resonance and composition during composition phase
        all_resonances = []
        compositions = 0
        checks = 0

        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                all_resonances.append(sim)
                checks += 1
                if sim >= 0.5:
                    compositions += 1
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        avg_res = np.mean(all_resonances) if all_resonances else 0
        comp_rate = compositions / checks if checks > 0 else 0
        avg_resonance_history.append(avg_res)
        composition_rate_history.append(comp_rate)

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

    return {
        'entropy': entropy_history,
        'resonance': avg_resonance_history,
        'comp_rate': composition_rate_history
    }

def main():
    print(f"CYCLE 1880: Entropy-Phase Relationship | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Does low entropy correlate with high phase alignment?")
    print("=" * 80)

    seeds = list(range(1880001, 1880011))
    prob = 0.10

    test_cases = [(14, "DEAD"), (21, "SAFE")]

    for n, zone_type in test_cases:
        print(f"\n{'='*60}")
        print(f"N = {n} ({zone_type})")
        print("=" * 60)

        all_entropy = []
        all_resonance = []
        all_comp_rate = []

        for seed in seeds:
            result = run_entropy_phase_analysis(seed, n, prob)
            all_entropy.append(result['entropy'])
            all_resonance.append(result['resonance'])
            all_comp_rate.append(result['comp_rate'])

        # Average at key timepoints
        timepoints = [5, 10, 20, 50]
        print(f"\n{'Cycle':>5} | {'Entropy':>7} | {'Resonance':>9} | {'Comp Rate':>9}")
        print("-" * 45)

        for t in timepoints:
            ent = np.mean([e[t] if t < len(e) else 0 for e in all_entropy])
            res = np.mean([r[t] if t < len(r) else 0 for r in all_resonance])
            cr = np.mean([c[t] if t < len(c) else 0 for c in all_comp_rate])
            print(f"{t:>5} | {ent:>7.3f} | {res:>9.3f} | {cr:>9.3f}")

        # Correlation between entropy and resonance
        flat_ent = [e for hist in all_entropy for e in hist]
        flat_res = [r for hist in all_resonance for r in hist[:len(all_entropy[0])]]

        if len(flat_ent) == len(flat_res) and len(flat_ent) > 0:
            corr = np.corrcoef(flat_ent, flat_res)[0, 1]
            print(f"\nEntropy-Resonance correlation: {corr:.3f}")

    # Analysis
    print("\n" + "=" * 80)
    print("ENTROPY-PHASE ANALYSIS")
    print("=" * 80)
    print("""
Hypothesis test: Does low entropy → high phase alignment?

Expected: In dead zones, synchronized composition depletes D0,
leading to low entropy AND high resonance correlation.

Results will show:
- Negative correlation: As entropy drops, resonance stays high
- Or no correlation: These are independent phenomena
""")

if __name__ == "__main__":
    main()
