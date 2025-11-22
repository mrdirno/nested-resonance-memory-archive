#!/usr/bin/env python3
"""
CYCLE 1867: ENTROPY AS EARLY WARNING DIAGNOSTIC

Can entropy at cycle 10-15 predict system fate?
Test: correlation between early entropy and final coexistence
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

def calculate_entropy(pop_counts):
    """Calculate depth entropy from population counts."""
    total = sum(pop_counts)
    if total == 0:
        return 0
    probs = [p / total for p in pop_counts if p > 0]
    return -sum(p * np.log2(p) for p in probs if p > 0)

def run_test_with_early_entropy(seed, n_initial, repro_prob):
    """Run test and return early entropy values + final outcome."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    early_entropy = {}  # cycle -> entropy

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        # Record entropy at key early cycles
        if cycle in [5, 10, 15, 20]:
            early_entropy[cycle] = calculate_entropy(pop_counts)

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
    coex = sum(1 for p in final_pops if p > 0) >= 2

    return {
        'coex': coex,
        'entropy_5': early_entropy.get(5, 0),
        'entropy_10': early_entropy.get(10, 0),
        'entropy_15': early_entropy.get(15, 0),
        'entropy_20': early_entropy.get(20, 0)
    }

def main():
    print(f"CYCLE 1867: Entropy Early Warning | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Can entropy at cycle 10-15 predict system fate?")
    print("=" * 80)

    seeds = list(range(1867001, 1867051))  # 50 seeds for statistics
    prob = 0.10

    # Test across N values (mix of dead and safe zones)
    test_n = list(range(10, 45))

    all_results = []

    for n in test_n:
        for seed in seeds:
            result = run_test_with_early_entropy(seed, n, prob)
            result['n'] = n
            result['seed'] = seed
            all_results.append(result)

    # Analyze predictive power of each timepoint
    print("\nPredictive Power Analysis")
    print("=" * 80)

    for cycle in [5, 10, 15, 20]:
        entropy_key = f'entropy_{cycle}'

        # Calculate correlation
        entropies = [r[entropy_key] for r in all_results]
        outcomes = [1 if r['coex'] else 0 for r in all_results]

        # Point-biserial correlation
        coex_ent = [e for e, o in zip(entropies, outcomes) if o == 1]
        fail_ent = [e for e, o in zip(entropies, outcomes) if o == 0]

        mean_coex = np.mean(coex_ent) if coex_ent else 0
        mean_fail = np.mean(fail_ent) if fail_ent else 0

        # Calculate prediction accuracy with threshold
        threshold = (mean_coex + mean_fail) / 2
        correct = sum(1 for e, o in zip(entropies, outcomes)
                      if (e >= threshold and o == 1) or (e < threshold and o == 0))
        accuracy = correct / len(all_results) * 100

        print(f"\nCycle {cycle}:")
        print(f"  Coex mean entropy: {mean_coex:.3f}")
        print(f"  Fail mean entropy: {mean_fail:.3f}")
        print(f"  Separation: {mean_coex - mean_fail:.3f}")
        print(f"  Threshold: {threshold:.3f}")
        print(f"  Prediction accuracy: {accuracy:.1f}%")

    # Best predictor analysis
    print("\n" + "=" * 80)
    print("OPTIMAL EARLY WARNING THRESHOLD")
    print("=" * 80)

    # Use cycle 10 entropy as primary predictor
    entropies_10 = [r['entropy_10'] for r in all_results]
    outcomes = [1 if r['coex'] else 0 for r in all_results]

    # Find optimal threshold
    best_acc = 0
    best_thresh = 0
    for thresh in np.arange(0.4, 1.4, 0.05):
        correct = sum(1 for e, o in zip(entropies_10, outcomes)
                      if (e >= thresh and o == 1) or (e < thresh and o == 0))
        acc = correct / len(all_results) * 100
        if acc > best_acc:
            best_acc = acc
            best_thresh = thresh

    print(f"\nOptimal threshold at cycle 10: {best_thresh:.2f}")
    print(f"Prediction accuracy: {best_acc:.1f}%")

    # False positive/negative rates
    fp = sum(1 for e, o in zip(entropies_10, outcomes) if e >= best_thresh and o == 0)
    fn = sum(1 for e, o in zip(entropies_10, outcomes) if e < best_thresh and o == 1)
    tp = sum(1 for e, o in zip(entropies_10, outcomes) if e >= best_thresh and o == 1)
    tn = sum(1 for e, o in zip(entropies_10, outcomes) if e < best_thresh and o == 0)

    print(f"\nConfusion matrix:")
    print(f"  True positive (coex predicted coex): {tp}")
    print(f"  True negative (fail predicted fail): {tn}")
    print(f"  False positive (fail predicted coex): {fp}")
    print(f"  False negative (coex predicted fail): {fn}")

    if tp + fn > 0:
        sensitivity = tp / (tp + fn) * 100
        print(f"\nSensitivity (detect coex): {sensitivity:.1f}%")
    if tn + fp > 0:
        specificity = tn / (tn + fp) * 100
        print(f"Specificity (detect fail): {specificity:.1f}%")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    print(f"""
Early Warning Diagnostic:

1. Entropy at cycle 10 predicts fate with {best_acc:.0f}% accuracy
2. Threshold: entropy < {best_thresh:.2f} → collapse risk
3. Can diagnose dead zone behavior 490 cycles before failure

Diagnostic Rule:
  if entropy_10 < {best_thresh:.2f}:
      WARNING: System likely in dead zone
      Action: Adjust N or prob parameters
""")

if __name__ == "__main__":
    main()
