#!/usr/bin/env python3
"""
CYCLE 1675: EARLY TERMINATION AT SCALE
Test the early termination strategy from C1674 at larger scale.
Run 500 seeds to cycle 100, terminate based on entropy, continue survivors.
"""
import sys, json, numpy as np, math, time
from datetime import datetime
sys.path.insert(0, '/Volumes/dual/DUALITY-ZERO-V2')
from core.fractal_agent import FractalAgent, RealityInterface

CYCLE_ID = "C1675"
N_DEPTHS = 5
ENTROPY_THRESHOLD = 0.3

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

def compute_entropy(populations):
    total = sum(populations)
    if total == 0:
        return 0.0
    probs = [p / total for p in populations if p > 0]
    return -sum(p * math.log2(p) for p in probs if p > 0)

def run_to_checkpoint(seed, cycles=100):
    """Run to checkpoint and return entropy."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    for cycle in range(cycles):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

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
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

    pop_counts = [len(reality.get_population_agents(d)) for d in range(N_DEPTHS)]
    return compute_entropy(pop_counts)

def run_full(seed, cycles=30000):
    """Run full experiment."""
    reality = RealityInterface(n_populations=N_DEPTHS, mode="SEARCH")
    np.random.seed(seed)

    DECAY_MULT = 0.1
    BASE_REPRO = 0.1
    DECOMP_THRESHOLD = 1.3
    RESONANCE_THRESHOLD = 0.5

    for i in range(100):
        reality.add_agent(FractalAgent(f"D0_{i}", 0, 1.0, depth=0), 0)

    histories = {d: [] for d in range(N_DEPTHS)}

    for cycle in range(cycles):
        pops = [reality.get_population_agents(d) for d in range(N_DEPTHS)]
        total = sum(len(p) for p in pops)
        if total >= 3000 or total == 0: break

        for d in range(N_DEPTHS):
            for agent in pops[d]:
                agent.recharge_energy(0.1 / (1 + d * 0.5), cap=2.0)

        for agent in list(reality.get_population_agents(0)):
            if agent.energy > 1.0 and np.random.random() < BASE_REPRO:
                reality.add_agent(FractalAgent(f"D0_{cycle}_{agent.agent_id[-6:]}", 0, 0.5, depth=0), 0)
                agent.energy -= 0.3

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
                    reality.add_agent(FractalAgent(f"D{d+1}_{cycle}", d+1, new_e, depth=d+1), d+1)
                    i += 2
                else:
                    i += 1

        for d in range(1, N_DEPTHS):
            for agent in list(reality.get_population_agents(d)):
                if agent.energy > DECOMP_THRESHOLD:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        reality.add_agent(FractalAgent(f"D{d-1}_{cycle}_{j}", d-1, ce, depth=d-1), d-1)
                    reality.remove_agent(agent.agent_id, d)

        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * DECAY_MULT
            for agent in list(reality.get_population_agents(d)):
                if not agent.consume_energy(decay):
                    reality.remove_agent(agent.agent_id, d)

        if cycle % 100 == 0:
            for d in range(N_DEPTHS):
                histories[d].append(len(reality.get_population_agents(d)))

    finals = {d: np.mean(histories[d][-10:]) if len(histories[d]) > 10 else 0 for d in range(N_DEPTHS)}
    return sum(1 for d in range(N_DEPTHS) if finals[d] >= 0.5) >= 3

def main():
    print(f"CYCLE 1675: Early Termination at Scale | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    n_seeds = 300
    seeds = list(range(1675001, 1675001 + n_seeds))

    # Phase 1: Screen all seeds to cycle 100
    print(f"\nPhase 1: Screening {n_seeds} seeds to cycle 100...")
    start = time.time()

    entropies = [(seed, run_to_checkpoint(seed, 100)) for seed in seeds]
    screen_time = time.time() - start

    survivors = [seed for seed, ent in entropies if ent >= ENTROPY_THRESHOLD]
    terminated = [seed for seed, ent in entropies if ent < ENTROPY_THRESHOLD]

    print(f"  Screening time: {screen_time:.1f}s")
    print(f"  Survivors: {len(survivors)} ({len(survivors)/n_seeds*100:.0f}%)")
    print(f"  Terminated: {len(terminated)} ({len(terminated)/n_seeds*100:.0f}%)")

    # Phase 2: Run survivors to completion
    print(f"\nPhase 2: Running {len(survivors)} survivors to completion...")
    start = time.time()

    results = [run_full(seed) for seed in survivors]
    run_time = time.time() - start

    successful = sum(results)
    print(f"  Run time: {run_time:.1f}s")
    print(f"  Successful: {successful}/{len(survivors)} ({successful/len(survivors)*100:.0f}% of survivors)")

    # Phase 3: Check false negatives (sample terminated seeds)
    n_check = min(50, len(terminated))
    print(f"\nPhase 3: Checking {n_check} terminated seeds for false negatives...")

    false_neg_results = [run_full(seed) for seed in terminated[:n_check]]
    false_negatives = sum(false_neg_results)

    print(f"  False negatives: {false_negatives}/{n_check} ({false_negatives/n_check*100:.0f}%)")

    # Summary
    print("\n" + "=" * 70)
    print("EARLY TERMINATION SUMMARY")
    print("=" * 70)

    total_time = screen_time + run_time
    hypothetical_full = n_seeds * (run_time / len(survivors)) if survivors else n_seeds * 10

    print(f"\nTotal seeds: {n_seeds}")
    print(f"Survivors: {len(survivors)} ({len(survivors)/n_seeds*100:.0f}%)")
    print(f"Successful runs: {successful}")
    print(f"Success rate: {successful/n_seeds*100:.1f}% (estimated actual)")
    print(f"\nTime analysis:")
    print(f"  Screening: {screen_time:.1f}s")
    print(f"  Full runs: {run_time:.1f}s")
    print(f"  Total: {total_time:.1f}s")
    print(f"  Hypothetical full (no termination): ~{hypothetical_full:.0f}s")
    print(f"  Speedup: {hypothetical_full/total_time:.1f}×")

if __name__ == "__main__":
    main()
