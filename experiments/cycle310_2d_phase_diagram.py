"""
CYCLE 310: 2D Phase Diagram (Cohesion × Metabolic Rate)
Objective: Map emergence transition across 2D parameter space
Hypothesis: Critical line exists in (cohesion, metabolic) space
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
            return False, 0

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
        return True, flock_size

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), n_resources=5):
        super().__init__(db_path=None, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = [Resource(f"R{i}", np.random.uniform(0, world_size, 2))
                        for i in range(n_resources)]

def run_sim(n_agents, cohesion, metabolic, steps=80):
    """Run simulation with cohesion and metabolic parameters"""
    sim = WorldSim()
    agents = [SwarmAgent(f"A{i}", np.random.uniform(0, sim.world_size, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion, metabolic_rate=metabolic)
              for i in range(n_agents)]

    flock_sizes = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        for agent in alive:
            survived, flock_size = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                if flock_size > 0:
                    flock_sizes.append(flock_size)
        alive = new_alive
        if not alive: break

        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    return {
        "survival_rate": len(alive) / n_agents,
        "avg_flock_size": np.mean(flock_sizes) if flock_sizes else 0
    }

def main():
    print("CYCLE 310: 2D PHASE DIAGRAM")
    print("=" * 50)
    print("Mapping emergence across (cohesion × metabolic) space")

    n_agents = 50
    n_seeds = 5

    # Grid: 8×8 = 64 points
    cohesion_values = np.linspace(0.05, 0.35, 8)
    metabolic_values = np.linspace(0.005, 0.025, 8)

    phase_map = []

    total = len(cohesion_values) * len(metabolic_values)
    count = 0

    for cf in cohesion_values:
        for meta in metabolic_values:
            seed_results = []
            for seed in range(n_seeds):
                np.random.seed(seed * 1000 + int(cf * 1000) + int(meta * 100000))
                r = run_sim(n_agents, cf, meta)
                seed_results.append(r)

            # Average
            avg_size = np.mean([r["avg_flock_size"] for r in seed_results])
            avg_survival = np.mean([r["survival_rate"] for r in seed_results])

            # Susceptibility (variance)
            suscept = np.var([r["avg_flock_size"] for r in seed_results])

            point = {
                "cohesion": round(cf, 3),
                "metabolic": round(meta, 4),
                "avg_flock_size": round(avg_size, 2),
                "survival_rate": round(avg_survival * 100, 1),
                "susceptibility": round(suscept, 2)
            }
            phase_map.append(point)

            count += 1
            print(f"[{count}/{total}] c={cf:.2f}, m={meta:.3f}: size={avg_size:.1f}, surv={avg_survival*100:.0f}%")

    # Analysis
    print("\n" + "=" * 50)
    print("PHASE DIAGRAM ANALYSIS")
    print("=" * 50)

    # Find critical line (points with high susceptibility)
    critical_threshold = np.percentile([p["susceptibility"] for p in phase_map], 75)
    critical_points = [p for p in phase_map if p["susceptibility"] > critical_threshold]

    print(f"\nCritical line (top 25% susceptibility):")
    for p in sorted(critical_points, key=lambda x: x["metabolic"]):
        print(f"  c={p['cohesion']:.2f}, m={p['metabolic']:.3f}, suscept={p['susceptibility']:.1f}")

    # Find best operating point (high size, good survival)
    viable = [p for p in phase_map if p["survival_rate"] > 50]
    if viable:
        best = max(viable, key=lambda x: x["avg_flock_size"])
        print(f"\nOptimal operating point:")
        print(f"  c={best['cohesion']:.3f}, m={best['metabolic']:.4f}")
        print(f"  Size={best['avg_flock_size']:.1f}, Survival={best['survival_rate']:.0f}%")

    # Identify phase regions
    low_meta = [p for p in phase_map if p["metabolic"] < 0.012]
    high_meta = [p for p in phase_map if p["metabolic"] > 0.018]

    avg_size_low = np.mean([p["avg_flock_size"] for p in low_meta]) if low_meta else 0
    avg_size_high = np.mean([p["avg_flock_size"] for p in high_meta]) if high_meta else 0

    print(f"\nPhase regions:")
    print(f"  Low metabolic (<0.012): avg size = {avg_size_low:.1f}")
    print(f"  High metabolic (>0.018): avg size = {avg_size_high:.1f}")

    # Save results
    output = {
        "experiment": "C310_2d_phase_diagram",
        "parameters": {
            "n_agents": n_agents,
            "seeds": n_seeds,
            "cohesion_range": [0.05, 0.35],
            "metabolic_range": [0.005, 0.025],
            "grid_size": "8x8"
        },
        "phase_map": phase_map,
        "analysis": {
            "critical_line": critical_points,
            "optimal_point": best if viable else None,
            "low_metabolic_avg_size": round(avg_size_low, 2),
            "high_metabolic_avg_size": round(avg_size_high, 2)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c310_2d_phase_diagram.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c310_2d_phase_diagram.json")
    print("\n--- C310 Complete ---")

if __name__ == "__main__":
    main()
