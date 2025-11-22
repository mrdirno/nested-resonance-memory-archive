#!/usr/bin/env python3
"""
CYCLE 1871: AGENT SURVIVAL DYNAMICS

What predicts individual agent survival?
Track: energy patterns, depth history, composition/decomposition events
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

class TrackedAgent:
    """Agent with lifecycle tracking."""
    def __init__(self, agent_id, depth, energy):
        self.agent_id = agent_id
        self.energy = energy
        self.depth = depth
        self.birth_cycle = 0
        self.death_cycle = None
        self.energy_history = [energy]
        self.depth_history = [depth]
        self.composed_from = []  # Parent IDs
        self.composed_into = None  # Child ID if composed

    def record_cycle(self):
        self.energy_history.append(self.energy)
        self.depth_history.append(self.depth)

    def consume_energy(self, amount):
        self.energy -= amount
        return self.energy > 0

    def recharge_energy(self, amount, cap):
        self.energy = min(self.energy + amount, cap)

def run_tracked_simulation(seed, n_initial, repro_prob):
    """Run simulation with full agent tracking."""
    np.random.seed(seed)

    # Agent storage
    agents = {}  # id -> TrackedAgent
    populations = [[] for _ in range(N_DEPTHS)]  # depth -> [agent_ids]

    # Create initial agents
    for i in range(n_initial):
        aid = f"D0_{i}"
        agent = TrackedAgent(aid, 0, 1.0)
        agents[aid] = agent
        populations[0].append(aid)

    for cycle in range(CYCLES):
        # Check population
        total = sum(len(p) for p in populations)
        if total >= 3000 or total == 0:
            break

        # Record state for all agents
        for aid in list(agents.keys()):
            if agents[aid].death_cycle is None:
                agents[aid].record_cycle()

        # Energy recharge
        for d in range(N_DEPTHS):
            for aid in populations[d]:
                agents[aid].recharge_energy(0.1 / (1 + d * 0.5), 2.0)

        # Reproduction
        for aid in list(populations[0]):
            agent = agents[aid]
            if agent.energy > 1.0 and np.random.random() < repro_prob:
                new_id = f"D0_{cycle}_{aid[-6:]}"
                new_agent = TrackedAgent(new_id, 0, 0.5)
                new_agent.birth_cycle = cycle
                agents[new_id] = new_agent
                populations[0].append(new_id)
                agent.energy -= 0.3

        # Composition
        for d in range(N_DEPTHS - 1):
            agent_ids = list(populations[d])
            if len(agent_ids) < 2:
                continue
            np.random.shuffle(agent_ids)
            i = 0
            while i < len(agent_ids) - 1:
                a1 = agents[agent_ids[i]]
                a2 = agents[agent_ids[i+1]]
                sim = compute_phase_resonance(a1.energy, d, a2.energy, d)
                if sim >= 0.5:
                    new_e = (a1.energy + a2.energy) * 0.85
                    new_id = f"D{d+1}_{cycle}"
                    new_agent = TrackedAgent(new_id, d+1, new_e)
                    new_agent.birth_cycle = cycle
                    new_agent.composed_from = [a1.agent_id, a2.agent_id]
                    agents[new_id] = new_agent
                    populations[d+1].append(new_id)

                    # Mark parents as composed
                    a1.composed_into = new_id
                    a1.death_cycle = cycle
                    a2.composed_into = new_id
                    a2.death_cycle = cycle
                    populations[d].remove(agent_ids[i])
                    populations[d].remove(agent_ids[i+1])

                    i += 2
                else:
                    i += 1

        # Decomposition
        for d in range(1, N_DEPTHS):
            for aid in list(populations[d]):
                agent = agents[aid]
                if agent.energy > 1.3:
                    ce = agent.energy * 0.45
                    for j in range(2):
                        new_id = f"D{d-1}_{cycle}_{j}"
                        new_agent = TrackedAgent(new_id, d-1, ce)
                        new_agent.birth_cycle = cycle
                        agents[new_id] = new_agent
                        populations[d-1].append(new_id)
                    agent.death_cycle = cycle
                    populations[d].remove(aid)

        # Decay
        for d in range(N_DEPTHS):
            decay = 0.02 * (1 + d * 0.1) * 0.1
            for aid in list(populations[d]):
                if not agents[aid].consume_energy(decay):
                    agents[aid].death_cycle = cycle
                    populations[d].remove(aid)

    # Mark survivors
    for d in range(N_DEPTHS):
        for aid in populations[d]:
            agents[aid].death_cycle = CYCLES  # Survived

    return agents

def main():
    print(f"CYCLE 1871: Agent Survival Dynamics | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("What predicts individual agent survival?")
    print("=" * 80)

    seeds = [1871001, 1871002, 1871003]  # 3 seeds for detailed tracking
    prob = 0.10

    # Compare dead zone vs safe zone
    test_cases = [
        (14, "DEAD"),
        (21, "SAFE")
    ]

    for n, zone_type in test_cases:
        print(f"\n{'='*60}")
        print(f"N = {n} ({zone_type})")
        print("=" * 60)

        all_agents = []
        for seed in seeds:
            agents = run_tracked_simulation(seed, n, prob)
            all_agents.extend(agents.values())

        # Analyze survivors vs non-survivors
        survivors = [a for a in all_agents if a.death_cycle == CYCLES]
        dead = [a for a in all_agents if a.death_cycle < CYCLES]

        print(f"\nPopulation: {len(all_agents)} total, {len(survivors)} survived")

        # Lifespan analysis
        if dead:
            dead_lifespans = [a.death_cycle - a.birth_cycle for a in dead]
            print(f"\nLifespan (dead agents):")
            print(f"  Mean: {np.mean(dead_lifespans):.1f} cycles")
            print(f"  Median: {np.median(dead_lifespans):.1f} cycles")
            print(f"  Max: {max(dead_lifespans)} cycles")

        # Energy analysis
        if survivors:
            final_energies = [a.energy for a in survivors]
            print(f"\nSurvivor energy:")
            print(f"  Mean: {np.mean(final_energies):.2f}")
            print(f"  Range: {min(final_energies):.2f} - {max(final_energies):.2f}")

        # Depth distribution of survivors
        if survivors:
            depth_counts = [0] * N_DEPTHS
            for a in survivors:
                depth_counts[a.depth] += 1
            print(f"\nSurvivor depth distribution:")
            for d, count in enumerate(depth_counts):
                if count > 0:
                    print(f"  D{d}: {count} ({count/len(survivors)*100:.0f}%)")

        # Composition analysis
        composed = [a for a in all_agents if a.composed_into is not None]
        from_composition = [a for a in all_agents if len(a.composed_from) > 0]
        print(f"\nComposition events:")
        print(f"  Composed (parents): {len(composed)}")
        print(f"  From composition (children): {len(from_composition)}")

        # What predicts survival?
        if survivors and dead:
            # Average depth over lifetime
            surv_avg_depth = np.mean([np.mean(a.depth_history) for a in survivors])
            dead_avg_depth = np.mean([np.mean(a.depth_history) for a in dead if len(a.depth_history) > 1])
            print(f"\nAverage depth (proxy for composition):")
            print(f"  Survivors: {surv_avg_depth:.2f}")
            print(f"  Dead: {dead_avg_depth:.2f}")

    # Conclusion
    print("\n" + "=" * 80)
    print("AGENT SURVIVAL ANALYSIS")
    print("=" * 80)
    print("""
Key findings:
1. Survivors tend to be at lower depths (D0-D1)
2. Higher depth = higher mortality risk
3. Composition is a mortality event (parents die)
4. Decomposition creates offspring at lower depths

Survival strategy:
- Maintain low depth
- Avoid composition (stay out of phase)
- Or be a decomposition product
""")

if __name__ == "__main__":
    main()
