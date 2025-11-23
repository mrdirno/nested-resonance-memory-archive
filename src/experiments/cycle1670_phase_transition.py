#!/usr/bin/env python3
"""
CYCLE 1670: PHASE TRANSITION ANALYSIS
Investigate the ~20% failure rate by analyzing early dynamics.
Question: What happens in cycles 0-50 that determines success/failure?
"""
import sys, json, numpy as np, math
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1670"
CYCLES = 30000
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

def run_experiment(seed):
    """Run experiment with detailed early-cycle tracking."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    # Track early dynamics in detail
    early_comps = []  # Compositions per cycle for first 50
    early_decomps = []
    early_total = []
    early_d1 = []  # Depth 1 population

    first_d1_cycle = None  # When depth 1 first appears
    first_d2_cycle = None  # When depth 2 first appears
    max_d1_early = 0  # Max D1 in first 50 cycles

    n_comps = n_decomps = 0

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        cycle_comps = 0
        cycle_decomps = 0

        # Track early D1 population
        if cycle < 50:
            d1_pop = len(pops[1])
            early_d1.append(d1_pop)
            if d1_pop > max_d1_early:
                max_d1_early = d1_pop
            early_total.append(total)

        # Track first appearances
        if first_d1_cycle is None and len(pops[1]) > 0:
            first_d1_cycle = cycle
        if first_d2_cycle is None and len(pops[2]) > 0:
            first_d2_cycle = cycle

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
                sim = compute_phase_resonance(agents[i].energy, d, agents[i+1].energy, d)
                if sim >= RESONANCE_THRESHOLD:
                    new_e = (agents[i].energy + agents[i+1].energy) * 0.85
                    reality.remove_agent(agents[i].agent_id, d)
                    reality.remove_agent(agents[i+1].agent_id, d)
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}_{n_comps}", d+1, new_e, depth=d+1), d+1)
                    n_comps += 1
                    cycle_comps += 1
                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{n_decomps}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)
                    n_decomps += 1
                    cycle_decomps += 1

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        # Track early cycle metrics
        if cycle < 50:
            early_comps.append(cycle_comps)
            early_decomps.append(cycle_decomps)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    depths_alive = sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5)

    # Calculate early metrics
    comps_10 = sum(early_comps[:10]) if len(early_comps) >= 10 else 0
    comps_50 = sum(early_comps) if early_comps else 0
    decomps_50 = sum(early_decomps) if early_decomps else 0
    min_total_50 = min(early_total) if early_total else 0
    avg_d1_50 = np.mean(early_d1) if early_d1 else 0

    return {
        "seed": seed,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        # Early dynamics
        "comps_10": comps_10,
        "comps_50": comps_50,
        "decomps_50": decomps_50,
        "min_total_50": min_total_50,
        "avg_d1_50": round(avg_d1_50, 1),
        "max_d1_50": max_d1_early,
        "first_d1": first_d1_cycle if first_d1_cycle else 999,
        "first_d2": first_d2_cycle if first_d2_cycle else 999
    }

def main():
    print(f"CYCLE 1670: Phase Transition | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    seeds = list(range(1670001, 1670201))  # 200 seeds for statistical power
    results = [run_experiment(seed) for seed in seeds]

    # Separate success and failure
    success = [r for r in results if r["coexist"]]
    failure = [r for r in results if not r["coexist"]]

    rate = len(success) / len(results)
    print(f"\nOverall: {len(success)}/{len(results)} coexist ({rate*100:.0f}%)")

    # Compare early metrics
    print("\n" + "=" * 70)
    print("EARLY DYNAMICS COMPARISON (First 50 cycles)")
    print("=" * 70)

    metrics = [
        ("comps_10", "Compositions (cycles 0-10)"),
        ("comps_50", "Compositions (cycles 0-50)"),
        ("decomps_50", "Decompositions (cycles 0-50)"),
        ("min_total_50", "Minimum total population"),
        ("avg_d1_50", "Average D1 population"),
        ("max_d1_50", "Maximum D1 population"),
        ("first_d1", "First D1 appearance (cycle)"),
        ("first_d2", "First D2 appearance (cycle)")
    ]

    print(f"\n{'Metric':<35s} {'Success':>10s} {'Failure':>10s} {'Diff':>10s}")
    print("-" * 70)

    for key, name in metrics:
        if success and failure:
            s_val = np.mean([r[key] for r in success])
            f_val = np.mean([r[key] for r in failure])
            diff = s_val - f_val
            print(f"{name:<35s} {s_val:>10.1f} {f_val:>10.1f} {diff:>+10.1f}")

    # Find critical thresholds
    print("\n" + "=" * 70)
    print("CRITICAL THRESHOLDS")
    print("=" * 70)

    # Test different thresholds for comps_10
    for threshold in [20, 25, 30, 35, 40]:
        above = [r for r in results if r["comps_10"] >= threshold]
        below = [r for r in results if r["comps_10"] < threshold]
        if above and below:
            above_rate = sum(1 for r in above if r["coexist"]) / len(above)
            below_rate = sum(1 for r in below if r["coexist"]) / len(below)
            print(f"comps_10 >= {threshold}: {above_rate*100:.0f}% success ({len(above)} runs)")
            print(f"comps_10 <  {threshold}: {below_rate*100:.0f}% success ({len(below)} runs)")
            print()

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1670_phase_transition_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": results}, f, indent=2)

if __name__ == "__main__":
    main()
