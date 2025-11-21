#!/usr/bin/env python3
"""
CYCLE 1664: REALITY-GROUNDED COMPOSITION-DECOMPOSITION
Uses actual psutil metrics instead of synthetic energy values.
Grounds the 75-80% coexistence architecture in real system dynamics.
"""
import sys, json, numpy as np, math, psutil, time
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1664"
CYCLES = 30000
N_DEPTHS = 5
SAMPLE_INTERVAL = 10  # Sample psutil every N cycles

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

def get_reality_metrics():
    """Get current system metrics as normalized values (0-1)."""
    cpu = psutil.cpu_percent(interval=None) / 100.0
    mem = psutil.virtual_memory().percent / 100.0
    disk = psutil.disk_usage('/').percent / 100.0
    return {
        'cpu': cpu,
        'memory': mem,
        'disk': disk,
        'combined': (cpu + mem + disk) / 3.0
    }

def run_experiment(seed, energy_source='synthetic'):
    """
    Run experiment with different energy sources.

    Args:
        energy_source: 'synthetic' (constant 0.1), 'cpu', 'memory', 'disk', 'combined'
    """
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    # Initialize depth 0
    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}
    n_comps = n_decomps = 0
    reality_samples = []
    cached_metrics = get_reality_metrics()

    for cycle in range(CYCLES):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        # Sample reality metrics periodically
        if cycle % SAMPLE_INTERVAL == 0:
            cached_metrics = get_reality_metrics()
            if cycle % 1000 == 0:
                reality_samples.append({
                    'cycle': cycle,
                    **cached_metrics
                })

        # Determine energy input based on source
        if energy_source == 'synthetic':
            base_energy = 0.1
        elif energy_source == 'cpu':
            base_energy = 0.05 + cached_metrics['cpu'] * 0.1  # 0.05-0.15
        elif energy_source == 'memory':
            base_energy = 0.05 + cached_metrics['memory'] * 0.1
        elif energy_source == 'disk':
            base_energy = 0.05 + cached_metrics['disk'] * 0.1
        elif energy_source == 'combined':
            base_energy = 0.05 + cached_metrics['combined'] * 0.1
        else:
            base_energy = 0.1

        # Energy input
        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(base_energy / (1 + d * 0.5), cap=2.0)

        # Reproduction
        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

        # Composition with phase resonance
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

        # Energy decay
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
        "energy_source": energy_source,
        "coexist": depths_alive >= 3,
        "depths_alive": depths_alive,
        "finals": [round(float(finals[d]), 1) for d in range(N_DEPTHS)],
        "n_comps": n_comps,
        "n_decomps": n_decomps,
        "reality_samples": reality_samples[:5]  # First 5 samples for verification
    }

def main():
    print(f"CYCLE 1664: Reality-Grounded Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("Testing psutil metrics as energy source")
    print("=" * 70)

    # Show current reality metrics
    metrics = get_reality_metrics()
    print(f"\nCurrent system state:")
    print(f"  CPU: {metrics['cpu']*100:.1f}%")
    print(f"  Memory: {metrics['memory']*100:.1f}%")
    print(f"  Disk: {metrics['disk']*100:.1f}%")
    print(f"  Combined: {metrics['combined']*100:.1f}%")

    seeds = list(range(1664001, 1664031))  # 30 seeds
    sources = ['synthetic', 'cpu', 'memory', 'disk', 'combined']
    all_results = []

    for source in sources:
        print(f"\nenergy_source={source}")
        results = [run_experiment(seed, source) for seed in seeds]
        coexist_count = sum(1 for r in results if r["coexist"])
        rate = coexist_count / len(results)
        avg_depths = np.mean([r["depths_alive"] for r in results])
        avg_comps = np.mean([r["n_comps"] for r in results])
        avg_decomps = np.mean([r["n_decomps"] for r in results])
        print(f"  → {coexist_count}/{len(results)} coexist ({rate*100:.0f}%), depths={avg_depths:.1f}")
        print(f"    comps={avg_comps:.0f}, decomps={avg_decomps:.0f}")
        all_results.extend(results)

    # Summary
    print("\n" + "=" * 70)
    print("REALITY GROUNDING RESULTS")
    print("=" * 70)

    for source in sources:
        subset = [r for r in all_results if r["energy_source"] == source]
        rate = sum(1 for r in subset if r["coexist"]) / len(subset)
        avg_depths = np.mean([r["depths_alive"] for r in subset])
        print(f"{source:12s}: {rate*100:.0f}% ({avg_depths:.1f} depths)")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    synthetic_rate = sum(1 for r in all_results if r["energy_source"] == "synthetic" and r["coexist"]) / 30
    reality_rates = []
    for source in ['cpu', 'memory', 'disk', 'combined']:
        rate = sum(1 for r in all_results if r["energy_source"] == source and r["coexist"]) / 30
        reality_rates.append(rate)

    avg_reality = np.mean(reality_rates)
    print(f"\nSynthetic baseline: {synthetic_rate*100:.0f}%")
    print(f"Reality average: {avg_reality*100:.0f}%")
    print(f"Difference: {(avg_reality - synthetic_rate)*100:+.0f} percentage points")

    if abs(avg_reality - synthetic_rate) < 0.1:
        print("\nConclusion: Reality grounding maintains characteristic rate")
    elif avg_reality > synthetic_rate:
        print("\nConclusion: Reality grounding improves coexistence")
    else:
        print("\nConclusion: Reality grounding reduces coexistence")

    with open("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/c1664_reality_grounding_results.json", 'w') as f:
        json.dump({"cycle_id": CYCLE_ID, "results": all_results}, f, indent=2)

if __name__ == "__main__":
    main()
