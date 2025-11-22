#!/usr/bin/env python3
"""
CYCLE 1874: INFORMATION FLOW

How does information propagate through the composition/decomposition network?
Track lineage from initial agents to final survivors.
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

class LineageAgent:
    """Agent with lineage tracking."""
    def __init__(self, agent_id, depth, energy, ancestors=None):
        self.agent_id = agent_id
        self.energy = energy
        self.depth = depth
        # Set of ancestor IDs (initial agents that contributed)
        self.ancestors = ancestors if ancestors else {agent_id}

    def consume_energy(self, amount):
        self.energy -= amount
        return self.energy > 0

    def recharge_energy(self, amount, cap):
        self.energy = min(self.energy + amount, cap)

def run_lineage_analysis(seed, n_initial, repro_prob):
    """Run simulation tracking ancestor lineage."""
    np.random.seed(seed)

    # Storage
    agents = {}  # id -> LineageAgent
    populations = [[] for _ in range(N_DEPTHS)]

    # Create initial agents with unique ancestor
    for i in range(n_initial):
        aid = f"D0_init_{i}"
        agent = LineageAgent(aid, 0, 1.0, {i})  # Ancestor is initial index
        agents[aid] = agent
        populations[0].append(aid)

    for cycle in range(CYCLES):
        total = sum(len(p) for p in populations)
        if total >= 3000 or total == 0:
            break

        # Energy recharge
        for d in range(N_DEPTHS):
            for aid in populations[d]:
                agents[aid].recharge_energy(0.1 / (1 + d * 0.5), 2.0)

        # Reproduction (inherits ancestors)
        for aid in list(populations[0]):
            agent = agents[aid]
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                new_id = f"D0_{cycle}_{aid[-6:]}"
                new_agent = LineageAgent(new_id, 0, 0.5, agent.ancestors.copy())
                agents[new_id] = new_agent
                populations[0].append(new_id)
                agent.energy -= 0.3

        # Composition (merges ancestors)
        for d in range(N_DEPTHS - 1):
            agent_ids = list(populations[d])
            if len(agent_ids) < 2:
                continue
            np.random.shuffle(agent_ids)
            to_remove = []
            i = 0
            while i < len(agent_ids) - 1:
                aid1, aid2 = agent_ids[i], agent_ids[i+1]
                if aid1 in to_remove or aid2 in to_remove:
                    i += 1
                    continue
                a1 = agents[aid1]
                a2 = agents[aid2]
                sim = compute_phase_resonance(a1.energy, d, a2.energy, d)
                if sim >= 0.5:
                    new_e = (a1.energy + a2.energy) * 0.85
                    new_id = f"D{d+1}_{cycle}_{i}"
                    # Merge ancestors from both parents
                    merged_ancestors = a1.ancestors | a2.ancestors
                    new_agent = LineageAgent(new_id, d+1, new_e, merged_ancestors)
                    agents[new_id] = new_agent
                    populations[d+1].append(new_id)
                    to_remove.extend([aid1, aid2])
                    i += 2
                else:
                    i += 1
            # Remove after loop
            for aid in to_remove:
                if aid in populations[d]:
                    populations[d].remove(aid)
                if aid in agents:
                    del agents[aid]

        # Decomposition (inherits merged ancestors)
        for d in range(1, N_DEPTHS):
            for aid in list(populations[d]):
                if aid not in agents:
                    continue
                agent = agents[aid]
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        new_id = f"D{d-1}_{cycle}_dec_{j}"
                        new_agent = LineageAgent(new_id, d-1, ce, agent.ancestors.copy())
                        agents[new_id] = new_agent
                        populations[d-1].append(new_id)
                    if aid in populations[d]:
                        populations[d].remove(aid)
                    del agents[aid]

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for aid in list(populations[d]):
                if aid not in agents:
                    if aid in populations[d]:
                        populations[d].remove(aid)
                    continue
                if not agents[aid].consume_energy(decay):
                    if aid in populations[d]:
                        populations[d].remove(aid)
                    del agents[aid]

    # Analyze survivors
    survivors = []
    for d in range(N_DEPTHS):
        for aid in populations[d]:
            survivors.append(agents[aid])

    return {
        'n_initial': n_initial,
        'n_survivors': len(survivors),
        'survivor_ancestors': [len(a.ancestors) for a in survivors],
        'unique_ancestors': set().union(*[a.ancestors for a in survivors]) if survivors else set()
    }

def main():
    print(f"CYCLE 1874: Information Flow | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("How does information propagate through composition/decomposition?")
    print("=" * 80)

    seeds = list(range(1874001, 1874011))
    prob = 0.10

    test_cases = [(14, "DEAD"), (21, "SAFE"), (28, "DEAD"), (35, "SAFE")]

    for n, zone_type in test_cases:
        print(f"\n{'='*60}")
        print(f"N = {n} ({zone_type})")
        print("=" * 60)

        all_survivor_ancestors = []
        all_unique = []
        all_survivors = []

        for seed in seeds:
            result = run_lineage_analysis(seed, n, prob)
            all_survivor_ancestors.extend(result['survivor_ancestors'])
            all_unique.append(len(result['unique_ancestors']))
            all_survivors.append(result['n_survivors'])

        print(f"\nSurvivors: {np.mean(all_survivors):.1f} ± {np.std(all_survivors):.1f}")

        if all_survivor_ancestors:
            print(f"\nAncestors per survivor:")
            print(f"  Mean: {np.mean(all_survivor_ancestors):.1f}")
            print(f"  Max: {max(all_survivor_ancestors)}")
            print(f"  Min: {min(all_survivor_ancestors)}")

        print(f"\nUnique initial ancestors in survivors:")
        print(f"  Mean: {np.mean(all_unique):.1f} / {n}")
        print(f"  Coverage: {np.mean(all_unique)/n*100:.0f}%")

    # Analysis
    print("\n" + "=" * 80)
    print("INFORMATION FLOW ANALYSIS")
    print("=" * 80)
    print("""
Key findings:

1. Ancestors per survivor = information mixing
   - Higher = more composition history
   - Lower = direct lineage preservation

2. Unique ancestors = information preservation
   - High % = initial conditions preserved
   - Low % = information loss

3. Dead vs Safe zones:
   - Compare ancestor mixing and preservation
   - May reveal why safe zones persist
""")

if __name__ == "__main__":
    main()
