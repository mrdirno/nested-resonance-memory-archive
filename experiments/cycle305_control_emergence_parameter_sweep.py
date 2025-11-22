import sys
import os
import time
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.fractal_agent import FractalAgent, SimulationInterface
from analysis.pattern_archaeologist import PatternArchaeologist
from memory.pattern_memory import PatternMemory, PatternType

# --- Helper Classes / Functions ---

class Resource:
    def __init__(self, id, pos, amount=10.0):
        self.id = id
        self.pos = np.array(pos, dtype=float)
        self.amount = amount
        self.initial_amount = amount

class ControlledSwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0, metabolic_rate=0.01, cohesion_factor=0.05):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2)
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.cohesion_factor = cohesion_factor # Control parameter
        self.last_pattern_id = None

    def update(self, sim, all_agents, resources):
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False

        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)
        neighbors_in_sight = 0
        local_patterns = []

        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors_in_sight += 1
                
                interaction_obs = {
                    "type": "interaction",
                    "agent1": self.agent_id,
                    "agent2": other.agent_id,
                    "distance": round(dist, 2),
                    "context_pos": list(self.pos.round(1))
                }
                if self.last_pattern_id:
                    self.last_pattern_id = self.discover_pattern(interaction_obs, parent_pattern_id=self.last_pattern_id)
                else:
                    self.last_pattern_id = self.discover_pattern(interaction_obs)
                local_patterns.append(self.last_pattern_id)
                
        cohesion_vector = np.zeros(2)
        if neighbors_in_sight > 0:
            avg_neighbor_pos /= neighbors_in_sight
            avg_neighbor_vel /= neighbors_in_sight
            cohesion_vector = (avg_neighbor_pos - self.pos) * self.cohesion_factor # Use control parameter
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vector).clip(-self.move_speed, self.move_speed)
        
        closest_resource = None
        min_res_dist = float('inf')
        
        for res in resources:
            if res.amount > 0:
                dist = np.linalg.norm(self.pos - res.pos)
                if dist < min_res_dist:
                    min_res_dist = dist
                    closest_resource = res
        
        if closest_resource and min_res_dist < self.sight_range * 2:
            attract_vector = (closest_resource.pos - self.pos) * 0.1
            self.vel = (self.vel + attract_vector).clip(-self.move_speed, self.move_speed)
            
            if min_res_dist < 2.0:
                consumed_amount = min(self.energy * 0.1, closest_resource.amount)
                self.energy += consumed_amount
                closest_resource.amount -= consumed_amount
                
                resource_obs = {
                    "type": "resource_consumed",
                    "resource_id": closest_resource.id,
                    "amount": round(consumed_amount, 2),
                    "pos": list(self.pos.round(1))
                }
                if local_patterns:
                    self.last_pattern_id = self.discover_pattern(resource_obs, parent_pattern_id=local_patterns[-1])
                else:
                    self.last_pattern_id = self.discover_pattern(resource_obs, parent_pattern_id=self.last_pattern_id)
                local_patterns.append(self.last_pattern_id)

        self.pos += self.vel
        self.pos %= sim.world_size
        
        if neighbors_in_sight > 2:
            flock_obs = {
                "type": "flock_formed",
                "size": neighbors_in_sight + 1,
                "center": list(avg_neighbor_pos.round(1)),
                "agent_id": self.agent_id
            }
            if local_patterns:
                 self.last_pattern_id = self.discover_pattern(flock_obs, parent_pattern_id=local_patterns[-1])
            else:
                 self.last_pattern_id = self.discover_pattern(flock_obs, parent_pattern_id=self.last_pattern_id)
            local_patterns.append(self.last_pattern_id)
            
        return True

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), db_path=None, n_resources=5):
        super().__init__(db_path=db_path, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = []
        for i in range(n_resources):
            self.resources.append(Resource(f"Res_{i}", np.random.uniform(0, self.world_size, 2)))

    def get_agents(self):
        return self.populations[0]

def run_single_simulation(simulation_id, N_AGENTS, SIM_STEPS, cohesion_factor_val):
    memory = PatternMemory()
    # Clear patterns for each run to avoid contamination between parameter settings
    memory.clear_patterns()
    memory.clear_relationships()
    
    sim = WorldSim(world_size=(100,100), n_resources=5)
    
    initial_agents = []
    for i in range(N_AGENTS):
        agent = ControlledSwarmAgent(f"Agent_{i}_{simulation_id}", np.random.uniform(0, sim.world_size, 2), energy=np.random.uniform(0.5, 1.5), move_speed=2.0, cohesion_factor=cohesion_factor_val)
        initial_agents.append(agent)
        sim.add_agent(agent, 0)
    
    alive_agents = initial_agents
    for step in range(SIM_STEPS):
        new_alive_agents = []
        for agent in alive_agents:
            if agent.update(sim, alive_agents, sim.resources): # Pass all_agents, not new_alive_agents
                new_alive_agents.append(agent)
        alive_agents = new_alive_agents
        
        if not alive_agents:
            break
            
        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1

    archaeologist = PatternArchaeologist(workspace_path=memory.workspace_path)
    
    flock_patterns = [p for p in archaeologist.memory.search_patterns(limit=100000, sort_by='last_seen', sort_order='DESC') if p.data.get("type") == "flock_formed"]
    
    avg_flock_size = 0
    if flock_patterns:
        avg_flock_size = np.mean([p.data.get("size", 0) for p in flock_patterns])

    # Calculate average lineage depth for flock patterns
    avg_lineage_depth = 0
    if flock_patterns:
        total_depth = 0
        for fp in flock_patterns:
            lineage = archaeologist.trace_ancestry(fp.pattern_id, max_depth=20) # Max depth for calculation
            total_depth += archaeologist.get_depth(lineage)
        avg_lineage_depth = total_depth / len(flock_patterns)

    return {
        "simulation_id": simulation_id,
        "cohesion_factor": cohesion_factor_val,
        "agents_at_end": len(alive_agents),
        "total_flock_patterns": len(flock_patterns),
        "avg_flock_size": round(float(avg_flock_size), 2),
        "avg_flock_lineage_depth": round(float(avg_lineage_depth), 2)
    }


def main():
    print("CYCLE 305: MAPPING CONTROL-EMERGENCE RELATIONSHIP")
    print("======================================================")
    print("Objective: Systematically map the relationship between micro-level control signals and macro-level emergent properties.")
    
    N_AGENTS = 50
    SIM_STEPS = 100 # Increased steps for better emergent behavior
    NUM_SEEDS = 3 # Number of seeds per cohesion factor to average out stochasticity

    # Cohesion factors to sweep
    cohesion_factors = np.linspace(0.01, 0.50, 10) # 10 steps from very low to high cohesion

    all_results = []

    for cf in cohesion_factors:
        cf_results = []
        for seed in range(NUM_SEEDS):
            sim_id = f"cohesion_{cf:.2f}_seed_{seed}"
            print(f"Running sim: {sim_id}, Cohesion: {cf:.2f} (Seed {seed+1}/{NUM_SEEDS})...", end='\r')
            result = run_single_simulation(sim_id, N_AGENTS, SIM_STEPS, cf)
            cf_results.append(result)
        
        # Average results for this cohesion factor
        avg_flock_size_list = [r["avg_flock_size"] for r in cf_results]
        avg_flock_lineage_depth_list = [r["avg_flock_lineage_depth"] for r in cf_results]
        
        avg_result = {
            "cohesion_factor": cf,
            "avg_flock_size": round(np.mean(avg_flock_size_list), 2),
            "avg_flock_lineage_depth": round(np.mean(avg_flock_lineage_depth_list), 2),
            "raw_results": cf_results # Keep raw results for deeper analysis if needed
        }
        all_results.append(avg_result)
        print(f"Cohesion {cf:.2f}: Avg Flock Size = {avg_result['avg_flock_size']}, Avg Lineage Depth = {avg_result['avg_flock_lineage_depth']}")
    
    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/cycle305_cohesion_sweep_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\n--- Mapping Control-Emergence Relationship Complete ---")

if __name__ == "__main__":
    main()
