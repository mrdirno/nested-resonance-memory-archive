"""
CYCLE 313: Self-Organized Criticality Test
Objective: Test if system naturally evolves toward critical point
Hypothesis: SOC = system self-tunes without external parameter tuning
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Claude <noreply@anthropic.com>
"""
import sys
import os
import json
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface

class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class AdaptiveSwarmAgent(FractalAgent):
    """Agent with adaptive cohesion that evolves based on local conditions"""
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0,
                 metabolic_rate=0.01, cohesion_factor=0.20):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor
        self.adaptation_rate = 0.01  # How fast cohesion adapts

    def update(self, world_size, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False, 0, self.cohesion_factor

        neighbors = 0
        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)

        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors += 1

        # Adaptive cohesion: increase when isolated, decrease when crowded
        if neighbors < 2:
            # Lonely → increase cohesion to find group
            self.cohesion_factor = min(0.5, self.cohesion_factor + self.adaptation_rate)
        elif neighbors > 6:
            # Crowded → decrease cohesion for mobility
            self.cohesion_factor = max(0.01, self.cohesion_factor - self.adaptation_rate)

        if neighbors > 0:
            avg_neighbor_pos /= neighbors
            avg_neighbor_vel /= neighbors
            cohesion_vec = (avg_neighbor_pos - self.pos) * self.cohesion_factor
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vec)
            self.vel = self.vel.clip(-self.move_speed, self.move_speed)

        closest_res = None
        min_dist = float('inf')
        for res in resources:
            if res.amount > 0:
                dist = np.linalg.norm(self.pos - res.pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_res = res

        if closest_res and min_dist < self.sight_range * 2:
            attract = (closest_res.pos - self.pos) * 0.1
            self.vel = (self.vel + attract).clip(-self.move_speed, self.move_speed)
            if min_dist < 2.0:
                consumed = min(self.energy * 0.1, closest_res.amount)
                self.energy += consumed
                closest_res.amount -= consumed

        self.pos = (self.pos + self.vel) % world_size
        flock_size = neighbors + 1 if neighbors > 2 else 0
        return True, flock_size, self.cohesion_factor

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

def run_adaptive_sim(n_agents, initial_cohesion, steps=200):
    """Run simulation with adaptive cohesion, track evolution"""
    sim = WorldSim()
    agents = [AdaptiveSwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                                 energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                                 cohesion_factor=initial_cohesion)
              for i in range(n_agents)]

    cohesion_history = []
    flock_history = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        step_cohesions = []
        step_flocks = 0

        for agent in alive:
            survived, flock_size, cohesion = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                step_cohesions.append(cohesion)
                if flock_size > 0:
                    step_flocks += 1

        alive = new_alive
        if not alive: break

        avg_cohesion = np.mean(step_cohesions)
        flock_rate = step_flocks / len(alive) if alive else 0

        cohesion_history.append(avg_cohesion)
        flock_history.append(flock_rate)

        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    return {
        "initial_cohesion": initial_cohesion,
        "final_cohesion": cohesion_history[-1] if cohesion_history else 0,
        "cohesion_history": cohesion_history,
        "final_flock_rate": flock_history[-1] if flock_history else 0,
        "survived": len(alive),
        "converged_to": round(np.mean(cohesion_history[-20:]) if len(cohesion_history) >= 20 else cohesion_history[-1] if cohesion_history else 0, 4)
    }

def main():
    print("CYCLE 313: SELF-ORGANIZED CRITICALITY TEST")
    print("=" * 50)
    print("Testing if adaptive cohesion self-tunes to critical point")

    n_agents = 50
    n_seeds = 8
    critical = 0.195  # Known critical point from C307

    # Start from various initial conditions
    initial_cohesions = [0.05, 0.10, 0.20, 0.30, 0.40]

    results = []

    for init_c in initial_cohesions:
        seed_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000 + int(init_c * 10000))
            r = run_adaptive_sim(n_agents, init_c)
            seed_results.append(r)

        # Average final cohesion across seeds
        final_cohesions = [r["converged_to"] for r in seed_results]
        avg_final = np.mean(final_cohesions)
        std_final = np.std(final_cohesions)

        result = {
            "initial_cohesion": init_c,
            "final_cohesion_mean": round(avg_final, 4),
            "final_cohesion_std": round(std_final, 4),
            "distance_to_critical": round(abs(avg_final - critical), 4)
        }
        results.append(result)

        print(f"Init={init_c:.2f} → Final={avg_final:.3f}±{std_final:.3f} (Δ to crit={abs(avg_final-critical):.3f})")

    # Analysis
    print("\n" + "=" * 50)
    print("SELF-ORGANIZED CRITICALITY ANALYSIS")
    print("=" * 50)

    # Check if all initial conditions converge to same point
    final_cohesions = [r["final_cohesion_mean"] for r in results]
    convergence_point = np.mean(final_cohesions)
    convergence_std = np.std(final_cohesions)

    print(f"\nConvergence point: {convergence_point:.4f}")
    print(f"Convergence spread: {convergence_std:.4f}")
    print(f"Known critical point: {critical}")
    print(f"Distance to critical: {abs(convergence_point - critical):.4f}")

    # SOC test: convergence should be near critical
    soc_supported = abs(convergence_point - critical) < 0.05 and convergence_std < 0.05

    if soc_supported:
        print("\n** SELF-ORGANIZED CRITICALITY SUPPORTED **")
        print("   System self-tunes to near critical point")
        print("   From any initial condition → convergence to c_crit")
    else:
        # Alternative: convergence to different attractor
        print(f"\nSelf-organization detected but NOT to critical point")
        print(f"   Attractor: {convergence_point:.3f}")
        print(f"   Critical: {critical}")

    # Check convergence uniformity
    if convergence_std < 0.03:
        print("\n   Strong convergence (low spread)")
    else:
        print("\n   Weak convergence (high spread)")

    # Save results
    output = {
        "experiment": "C313_self_organized_criticality",
        "parameters": {
            "n_agents": n_agents,
            "seeds": n_seeds,
            "steps": 200,
            "known_critical": critical
        },
        "results": results,
        "analysis": {
            "convergence_point": round(convergence_point, 4),
            "convergence_std": round(convergence_std, 4),
            "distance_to_critical": round(abs(convergence_point - critical), 4),
            "soc_supported": bool(soc_supported)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c313_self_organized_criticality.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c313_self_organized_criticality.json")
    print("\n--- C313 Complete ---")

if __name__ == "__main__":
    main()
