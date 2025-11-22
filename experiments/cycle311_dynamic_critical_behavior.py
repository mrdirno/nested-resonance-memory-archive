"""
CYCLE 311: Dynamic Critical Behavior (Relaxation Times)
Objective: Measure how relaxation time diverges near critical point
Hypothesis: τ ~ |c - c_crit|^(-νz) (critical slowing down)
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

def run_sim_with_perturbation(n_agents, cohesion, steps=150):
    """
    Run simulation with initial perturbation, measure relaxation time.
    Perturbation: Start agents clustered, measure time to equilibrium.
    """
    sim = WorldSim()

    # Initial perturbation: all agents start clustered in center
    center = sim.world_size / 2
    agents = [SwarmAgent(f"A{i}", center + np.random.uniform(-5, 5, 2),
                        energy=np.random.uniform(0.5, 1.5), move_speed=2.0,
                        cohesion_factor=cohesion, metabolic_rate=0.01)
              for i in range(n_agents)]

    flock_history = []
    alive = agents[:]

    for step in range(steps):
        new_alive = []
        step_flocks = 0
        for agent in alive:
            survived, flock_size = agent.update(sim.world_size, alive, sim.resources)
            if survived:
                new_alive.append(agent)
                if flock_size > 0:
                    step_flocks += 1
        alive = new_alive
        if not alive: break

        # Track flock formation rate
        flock_rate = step_flocks / len(alive) if alive else 0
        flock_history.append(flock_rate)

        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    # Measure relaxation time: time to reach 90% of final value
    if len(flock_history) < 20:
        return None

    final_value = np.mean(flock_history[-20:])
    target = 0.9 * final_value

    relaxation_time = None
    for t, val in enumerate(flock_history):
        if val >= target:
            relaxation_time = t
            break

    if relaxation_time is None:
        relaxation_time = len(flock_history)  # Never reached

    # Also measure fluctuation decay (autocorrelation time)
    fluctuations = np.array(flock_history) - final_value
    autocorr = np.correlate(fluctuations, fluctuations, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    autocorr = autocorr / autocorr[0] if autocorr[0] > 0 else autocorr

    # Find 1/e decay time
    decay_time = len(autocorr)
    for t, val in enumerate(autocorr):
        if val < 1/np.e:
            decay_time = t
            break

    return {
        "relaxation_time": relaxation_time,
        "decay_time": decay_time,
        "final_flock_rate": round(final_value, 3),
        "survived": len(alive)
    }

def main():
    print("CYCLE 311: DYNAMIC CRITICAL BEHAVIOR")
    print("=" * 50)
    print("Measuring relaxation time divergence near critical point")

    n_agents = 50
    n_seeds = 8
    critical = 0.195  # From C307

    # Sample points around critical
    cohesion_values = np.concatenate([
        np.linspace(0.10, 0.18, 5),  # Below critical
        [critical],  # At critical
        np.linspace(0.21, 0.30, 5)   # Above critical
    ])

    results = []

    for cf in cohesion_values:
        seed_results = []
        for seed in range(n_seeds):
            np.random.seed(seed * 1000 + int(cf * 10000))
            r = run_sim_with_perturbation(n_agents, cf)
            if r:
                seed_results.append(r)

        if not seed_results:
            continue

        avg_relax = np.mean([r["relaxation_time"] for r in seed_results])
        avg_decay = np.mean([r["decay_time"] for r in seed_results])
        relax_std = np.std([r["relaxation_time"] for r in seed_results])

        distance = abs(cf - critical)

        result = {
            "cohesion": round(cf, 4),
            "distance_from_critical": round(distance, 4),
            "relaxation_time": round(avg_relax, 2),
            "relaxation_std": round(relax_std, 2),
            "decay_time": round(avg_decay, 2)
        }
        results.append(result)

        print(f"c={cf:.3f}, Δc={distance:.3f}: τ_relax={avg_relax:.1f}, τ_decay={avg_decay:.1f}")

    # Analysis
    print("\n" + "=" * 50)
    print("CRITICAL SLOWING DOWN ANALYSIS")
    print("=" * 50)

    # Find peak relaxation time (should be at or near critical)
    peak = max(results, key=lambda x: x["relaxation_time"])
    print(f"\nPeak relaxation time at c={peak['cohesion']}")
    print(f"  τ = {peak['relaxation_time']:.1f} steps")

    # Fit power law: τ ~ |Δc|^(-νz)
    # Exclude exact critical point for fitting
    fit_data = [(r["distance_from_critical"], r["relaxation_time"])
                for r in results if r["distance_from_critical"] > 0.01]

    if len(fit_data) > 3:
        distances = np.array([d[0] for d in fit_data])
        times = np.array([d[1] for d in fit_data])

        # Fit log(τ) vs log(Δc)
        log_d = np.log(distances)
        log_t = np.log(times)
        slope, intercept = np.polyfit(log_d, log_t, 1)

        print(f"\nPower law fit: τ ~ Δc^{slope:.3f}")
        print(f"Dynamic exponent: νz ≈ {-slope:.3f}")

        # Check for critical slowing down
        if slope < -0.3:
            print("\n** CRITICAL SLOWING DOWN CONFIRMED **")
            print(f"   Relaxation time diverges near critical point")
            print(f"   Exponent νz = {-slope:.2f}")
        else:
            print("\nWeak or no critical slowing down detected")
    else:
        slope = 0
        print("\nInsufficient data for power law fit")

    # Compare to other exponents
    print(f"\n--- Exponent Summary ---")
    print(f"γ/ν = 1.63 (susceptibility)")
    print(f"β = 0.01 (order parameter)")
    print(f"νz = {-slope:.2f} (dynamic)")

    # Save results
    output = {
        "experiment": "C311_dynamic_critical_behavior",
        "parameters": {
            "n_agents": n_agents,
            "seeds": n_seeds,
            "critical_cohesion": critical,
            "steps": 150
        },
        "results": results,
        "analysis": {
            "peak_relaxation": {
                "cohesion": peak["cohesion"],
                "time": peak["relaxation_time"]
            },
            "dynamic_exponent_nuz": round(-slope, 4) if slope else None,
            "critical_slowing_down": bool(slope < -0.3)
        }
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c311_dynamic_critical.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to experiments/results/c311_dynamic_critical.json")
    print("\n--- C311 Complete ---")

if __name__ == "__main__":
    main()
