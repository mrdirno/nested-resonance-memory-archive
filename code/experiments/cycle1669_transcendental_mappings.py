#!/usr/bin/env python3
"""
CYCLE 1669: ALTERNATIVE TRANSCENDENTAL MAPPINGS
Test different mathematical constants for phase resonance.
Current: π, e, φ. Test: √2, √3, √5, ln2, simple energy diff.
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1669"
CYCLES = 30000
N_DEPTHS = 5

# Constants
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2
SQRT2 = math.sqrt(2)
SQRT3 = math.sqrt(3)
SQRT5 = math.sqrt(5)
LN2 = math.log(2)

def compute_resonance_peφ(e1, d1, e2, d2):
    """Original π, e, φ mapping."""
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

def compute_resonance_roots(e1, d1, e2, d2):
    """√2, √3, √5 mapping (algebraic irrationals)."""
    r2_1 = (e1 * SQRT2 * 2) % (2 * PI)
    r3_1 = (d1 * SQRT3 / 4) % (2 * PI)
    r5_1 = (e1 * SQRT5) % (2 * PI)
    r2_2 = (e2 * SQRT2 * 2) % (2 * PI)
    r3_2 = (d2 * SQRT3 / 4) % (2 * PI)
    r5_2 = (e2 * SQRT5) % (2 * PI)
    v1 = [r2_1, r3_1, r5_1]
    v2 = [r2_2, r3_2, r5_2]
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a**2 for a in v1))
    mag2 = math.sqrt(sum(a**2 for a in v2))
    if mag1 == 0 or mag2 == 0: return 0.0
    return dot / (mag1 * mag2)

def compute_resonance_simple(e1, d1, e2, d2):
    """Simple energy difference (non-transcendental)."""
    diff = abs(e1 - e2)
    # Map to 0-1 where small diff = high resonance
    return max(0, 1 - diff)

def compute_resonance_pi_only(e1, d1, e2, d2):
    """Single π oscillator."""
    pi1 = (e1 * PI * 2) % (2 * PI)
    pi2 = (e2 * PI * 2) % (2 * PI)
    # Cosine similarity in 1D
    return math.cos(pi1 - pi2)

def run_experiment(seed, mapping='peφ'):
    """Run experiment with different resonance mapping."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    # Select resonance function
    if mapping == 'peφ':
        compute_resonance = compute_resonance_peφ
    elif mapping == 'roots':
        compute_resonance = compute_resonance_roots
    elif mapping == 'simple':
        compute_resonance = compute_resonance_simple
    elif mapping == 'pi_only':
        compute_resonance = compute_resonance_pi_only
    else:
        compute_resonance = compute_resonance_peφ

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition
        for d in range(N_DEPTHS - 1):
            agents = list(reality.get_population_agents(d))
            if len(agents) < 2: continue
            np.random.shuffle(agents)
            i = 0
            while i < len(agents) - 1:
                sim = compute_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    return {
        "seed": seed,
        "mapping": mapping,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "coexist": depths_alive >= 3
    }

def main():
    print(f"CYCLE 1669: Transcendental Mappings | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1669001, 1669051))  # 50 seeds

    mappings = ['peφ', 'roots', 'simple', 'pi_only']
    all_results = []

    for mapping in mappings:
        print(f"\nmapping={mapping}")
        results = [run_experiment(seed, mapping) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        avg_depths = np.mean([r["depths_alive"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({coexist_count/len(results)*100:.0f}%)")
        print(f"    avg depths: {avg_depths:.1f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("TRANSCENDENTAL MAPPING RESULTS")
    print("=" * 70)

    for mapping in mappings:
        subset = [r for r in all_results if r["mapping"] == mapping]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"{mapping:10s}: {rate*100:.0f}% coexist, {avg_depths:.1f} depths")

if __name__ == "__main__":
    main()
