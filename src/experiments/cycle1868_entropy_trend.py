#!/usr/bin/env python3
"""
CYCLE 1868: ENTROPY TREND AS PREDICTOR

Can entropy TREND (change from cycle 5-10) improve specificity?
Hypothesis: Dead zones show entropy decline, safe zones show increase
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
    total = sum(pop_counts)
    if total == 0:
        return 0
    probs = [p / total for p in pop_counts if p > 0]
    return -sum(p * np.log2(p) for p in probs if p > 0)

def run_test(seed, n_initial, repro_prob):
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    early_entropy = {}

    for i in range(n_initial):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        pop_counts = [len(p) for p in pops]
        total = sum(pop_counts)

        if cycle in [5, 10, 15]:
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

    e5 = early_entropy.get(5, 0)
    e10 = early_entropy.get(10, 0)
    e15 = early_entropy.get(15, 0)

    return {
        'coex': coex,
        'entropy_5': e5,
        'entropy_10': e10,
        'entropy_15': e15,
        'trend_5_10': e10 - e5,
        'trend_10_15': e15 - e10
    }

def main():
    print(f"CYCLE 1868: Entropy Trend | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("Can entropy trend improve specificity?")
    print("=" * 80)

    seeds = list(range(1868001, 1868051))
    prob = 0.10
    test_n = list(range(10, 45))

    all_results = []
    for n in test_n:
        for seed in seeds:
            result = run_test(seed, n, prob)
            result['n'] = n
            all_results.append(result)

    # Analyze trend
    print("\nEntropy Trend Analysis")
    print("=" * 80)

    coex_results = [r for r in all_results if r['coex']]
    fail_results = [r for r in all_results if not r['coex']]

    # Trend statistics
    coex_trend = [r['trend_5_10'] for r in coex_results]
    fail_trend = [r['trend_5_10'] for r in fail_results]

    print(f"\nTrend (cycle 5→10):")
    print(f"  Coex: {np.mean(coex_trend):.3f} ± {np.std(coex_trend):.3f}")
    print(f"  Fail: {np.mean(fail_trend):.3f} ± {np.std(fail_trend):.3f}")
    print(f"  Separation: {np.mean(coex_trend) - np.mean(fail_trend):.3f}")

    # Combined predictor: entropy_10 AND trend
    print("\n" + "=" * 80)
    print("COMBINED PREDICTOR: Entropy_10 + Trend")
    print("=" * 80)

    # Test combined thresholds
    best_acc = 0
    best_params = {}

    for ent_thresh in np.arange(0.5, 1.2, 0.1):
        for trend_thresh in np.arange(-0.2, 0.5, 0.1):
            correct = 0
            for r in all_results:
                predict_coex = r['entropy_10'] >= ent_thresh and r['trend_5_10'] >= trend_thresh
                actual_coex = r['coex']
                if predict_coex == actual_coex:
                    correct += 1
            acc = correct / len(all_results) * 100
            if acc > best_acc:
                best_acc = acc
                best_params = {'ent': ent_thresh, 'trend': trend_thresh}

    print(f"\nBest combined: entropy_10 >= {best_params['ent']:.1f} AND trend >= {best_params['trend']:.1f}")
    print(f"Accuracy: {best_acc:.1f}%")

    # Calculate confusion matrix for combined
    tp = tn = fp = fn = 0
    for r in all_results:
        predict_coex = r['entropy_10'] >= best_params['ent'] and r['trend_5_10'] >= best_params['trend']
        actual_coex = r['coex']
        if predict_coex and actual_coex: tp += 1
        elif not predict_coex and not actual_coex: tn += 1
        elif predict_coex and not actual_coex: fp += 1
        else: fn += 1

    print(f"\nConfusion matrix:")
    print(f"  TP: {tp}, TN: {tn}, FP: {fp}, FN: {fn}")

    sensitivity = tp / (tp + fn) * 100 if (tp + fn) > 0 else 0
    specificity = tn / (tn + fp) * 100 if (tn + fp) > 0 else 0
    print(f"  Sensitivity: {sensitivity:.1f}%")
    print(f"  Specificity: {specificity:.1f}%")

    # Compare to entropy-only
    print("\n" + "=" * 80)
    print("COMPARISON: Combined vs Entropy-Only")
    print("=" * 80)

    # Entropy-only (from C1867)
    tp_e = tn_e = fp_e = fn_e = 0
    for r in all_results:
        predict_coex = r['entropy_10'] >= 0.75
        actual_coex = r['coex']
        if predict_coex and actual_coex: tp_e += 1
        elif not predict_coex and not actual_coex: tn_e += 1
        elif predict_coex and not actual_coex: fp_e += 1
        else: fn_e += 1

    acc_e = (tp_e + tn_e) / len(all_results) * 100
    sens_e = tp_e / (tp_e + fn_e) * 100 if (tp_e + fn_e) > 0 else 0
    spec_e = tn_e / (tn_e + fp_e) * 100 if (tn_e + fp_e) > 0 else 0

    print(f"\nEntropy-only (threshold = 0.75):")
    print(f"  Accuracy: {acc_e:.1f}%")
    print(f"  Sensitivity: {sens_e:.1f}%")
    print(f"  Specificity: {spec_e:.1f}%")

    print(f"\nCombined (entropy + trend):")
    print(f"  Accuracy: {best_acc:.1f}%")
    print(f"  Sensitivity: {sensitivity:.1f}%")
    print(f"  Specificity: {specificity:.1f}%")

    spec_improvement = specificity - spec_e
    print(f"\nSpecificity improvement: {spec_improvement:+.1f}%")

    # Conclusion
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    if specificity > spec_e + 5:
        print(f"""
Trend IMPROVES specificity by {spec_improvement:.0f}%!

Combined diagnostic rule:
  if entropy_10 >= {best_params['ent']:.1f} AND trend_5_10 >= {best_params['trend']:.1f}:
      SAFE
  else:
      WARNING: Collapse risk
""")
    else:
        print(f"""
Trend provides minimal improvement ({spec_improvement:.1f}%).

Entropy-only diagnostic remains preferred for simplicity:
  if entropy_10 < 0.75:
      WARNING: Collapse risk
""")

if __name__ == "__main__":
    main()
