"""
CYCLE 307: Phase Transition Hunt Around Optimal Cohesion
Objective: Fine-grained sweep around C306's optimal (0.173) to detect phase transitions
Hypothesis: There may be a critical point or phase transition at optimal cohesion
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

class SwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0,
                 metabolic_rate=0.01, cohesion_factor=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor

    def update(self, world_size, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False, 0, 0

        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)
        neighbors = 0

        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors += 1

        # Cohesion behavior
        if neighbors > 0:
            avg_neighbor_pos /= neighbors
            avg_neighbor_vel /= neighbors
            cohesion_vec = (avg_neighbor_pos - self.pos) * self.cohesion_factor
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vec)
            self.vel = self.vel.clip(-self.move_speed, self.move_speed)

        # Resource seeking
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
        return True, flock_size, neighbors

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

def run_sim(cohesion, n_agents=50, steps=100):
    """Run single simulation, return detailed metrics for phase transition detection"""
    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion) for i in range(n_agents)]

    flock_sizes = []
    neighbor_counts = []
    energy_history = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        step_energy = 0
        step_neighbors = 0
        for agent in alive:
            survived, flock_size, neighbors = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                step_energy += agent.energy
                step_neighbors += neighbors
                if flock_size > 0:
                    flock_sizes.append(flock_size)
                    neighbor_counts.append(neighbors)
        alive = new_alive
        if not alive: break

        energy_history.append(step_energy / len(alive) if alive else 0)

        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    # Calculate variance (indicator of phase transitions)
    flock_size_var = np.var(flock_sizes) if flock_sizes else 0

    return {
        "agents_survived": len(alive),
        "flock_count": len(flock_sizes),
        "avg_flock_size": round(np.mean(flock_sizes), 3) if flock_sizes else 0,
        "flock_size_variance": round(flock_size_var, 3),
        "max_flock_size": max(flock_sizes) if flock_sizes else 0,
        "avg_energy": round(np.mean(energy_history), 3) if energy_history else 0,
        "energy_variance": round(np.var(energy_history), 4) if energy_history else 0
    }

def main():
    print("CYCLE 307: PHASE TRANSITION HUNT")
    print("=" * 50)
    print("Fine-grained sweep around optimal cohesion (0.173)")
    print("Looking for phase transition indicators")

    # Fine sweep: 20 points from 0.10 to 0.25 (around optimal 0.173)
    cohesion_values = np.linspace(0.10, 0.25, 20)
    n_seeds = 10  # More seeds for variance detection

    results = []

    for cf in cohesion_values:
        seed_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 100 + int(cf * 10000))
            r = run_sim(cf)
            seed_results.append(r)

        # Calculate susceptibility (variance across seeds - phase transition indicator)
        flock_sizes_across_seeds = [r["avg_flock_size"] for r in seed_results]
        susceptibility = np.var(flock_sizes_across_seeds)

        avg_result = {
            "cohesion_factor": round(cf, 4),
            "avg_flock_size": round(np.mean([r["avg_flock_size"] for r in seed_results]), 3),
            "flock_size_std": round(np.std([r["avg_flock_size"] for r in seed_results]), 3),
            "avg_flock_count": round(np.mean([r["flock_count"] for r in seed_results]), 0),
            "survival_rate": round(np.mean([r["agents_survived"] for r in seed_results]) / 50 * 100, 1),
            "susceptibility": round(susceptibility, 4),  # High at phase transitions
            "avg_variance": round(np.mean([r["flock_size_variance"] for r in seed_results]), 3),
            "avg_energy": round(np.mean([r["avg_energy"] for r in seed_results]), 3)
        }
        results.append(avg_result)

        print(f"Cohesion {cf:.4f}: Size={avg_result['avg_flock_size']:.2f}, "
              f"Suscept={avg_result['susceptibility']:.4f}, "
              f"Survival={avg_result['survival_rate']}%")

    # Phase transition analysis
    print("\n" + "=" * 50)
    print("PHASE TRANSITION ANALYSIS")
    print("=" * 50)

    # Find peak susceptibility (indicator of critical point)
    max_suscept = max(results, key=lambda x: x["susceptibility"])
    max_size = max(results, key=lambda x: x["avg_flock_size"])

    print(f"\nPeak susceptibility at cohesion={max_suscept['cohesion_factor']}")
    print(f"  → Susceptibility = {max_suscept['susceptibility']:.4f}")
    print(f"  → This may indicate a phase transition")

    print(f"\nMaximum flock size at cohesion={max_size['cohesion_factor']}")
    print(f"  → Avg size = {max_size['avg_flock_size']:.2f}")

    # Calculate derivative of flock size (look for inflection points)
    cfs = [r["cohesion_factor"] for r in results]
    sizes = [r["avg_flock_size"] for r in results]

    # Numerical derivative
    derivatives = np.gradient(sizes, cfs)
    max_deriv_idx = np.argmax(np.abs(derivatives))

    print(f"\nSteepest change at cohesion={cfs[max_deriv_idx]:.4f}")
    print(f"  → Derivative = {derivatives[max_deriv_idx]:.3f}")

    # Determine if there's a clear phase transition
    suscept_values = [r["susceptibility"] for r in results]
    suscept_peak_prominence = max(suscept_values) / (np.mean(suscept_values) + 0.001)

    if suscept_peak_prominence > 2.0:
        print(f"\n** PHASE TRANSITION DETECTED **")
        print(f"   Susceptibility peak prominence: {suscept_peak_prominence:.2f}x")
        print(f"   Critical cohesion: ~{max_suscept['cohesion_factor']:.4f}")
    else:
        print(f"\nNo clear phase transition (peak prominence: {suscept_peak_prominence:.2f}x)")
        print("This appears to be a smooth crossover region")

    # Save results
    output = {
        "experiment": "C307_phase_transition_hunt",
        "parameters": {
            "n_agents": 50, "steps": 100, "seeds": 10,
            "cohesion_range": [0.10, 0.25], "n_points": 20
        },
        "results": results,
        "analysis": {
            "peak_susceptibility": {
                "cohesion": max_suscept["cohesion_factor"],
                "value": max_suscept["susceptibility"]
            },
            "max_flock_size": {
                "cohesion": max_size["cohesion_factor"],
                "value": max_size["avg_flock_size"]
            },
            "steepest_change": {
                "cohesion": round(cfs[max_deriv_idx], 4),
                "derivative": round(derivatives[max_deriv_idx], 3)
            },
            "susceptibility_peak_prominence": round(suscept_peak_prominence, 3),
            "phase_transition_detected": bool(suscept_peak_prominence > 2.0)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c307_phase_transition.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c307_phase_transition.json")
    print("\n--- C307 Complete ---")

if __name__ == "__main__":
    main()
