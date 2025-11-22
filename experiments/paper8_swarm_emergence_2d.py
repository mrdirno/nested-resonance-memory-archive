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

class SwarmAgent(FractalAgent):
    def __init__(self, agent_id, pos, energy=1.0, sight_range=15.0, move_speed=1.0, metabolic_rate=0.01):
        super().__init__(agent_id, energy=energy)
        self.pos = np.array(pos, dtype=float)
        self.vel = np.random.uniform(-move_speed, move_speed, 2) # Random initial velocity
        self.sight_range = sight_range
        self.move_speed = move_speed
        self.metabolic_rate = metabolic_rate
        self.last_pattern_id = None # For causal linking

    def update(self, sim, all_agents, resources):
        # Consume energy
        self.energy -= self.metabolic_rate
        if self.energy <= 0:
            return False # Agent dies

        # Flocking behavior: cohesion + alignment
        avg_neighbor_pos = np.zeros(2)
        avg_neighbor_vel = np.zeros(2)
        neighbors_in_sight = 0
        
        local_patterns = [] # Patterns discovered in this step, potential parents

        # Find nearby agents
        for other in all_agents:
            if other == self: continue
            dist = np.linalg.norm(self.pos - other.pos)
            if dist < self.sight_range:
                avg_neighbor_pos += other.pos
                avg_neighbor_vel += other.vel
                neighbors_in_sight += 1
                
                # Low-level Interaction Pattern
                interaction_obs = {
                    "type": "interaction",
                    "agent1": self.agent_id,
                    "agent2": other.agent_id,
                    "distance": round(dist, 2),
                    "context_pos": list(self.pos.round(1))
                }
                # Link to self-awareness or previous action
                if self.last_pattern_id:
                    self_pattern_id = self.discover_pattern(interaction_obs, parent_pattern_id=self.last_pattern_id)
                else:
                     self_pattern_id = self.discover_pattern(interaction_obs)
                local_patterns.append(self_pattern_id)
                
        # Flocking movement
        cohesion_vector = np.zeros(2)
        if neighbors_in_sight > 0:
            avg_neighbor_pos /= neighbors_in_sight
            avg_neighbor_vel /= neighbors_in_sight
            cohesion_vector = (avg_neighbor_pos - self.pos) * 0.05 # Move towards center of mass
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vector).clip(-self.move_speed, self.move_speed)
        
        # Resource seeking
        closest_resource = None
        min_res_dist = float('inf')
        
        for res in resources:
            if res.amount > 0:
                dist = np.linalg.norm(self.pos - res.pos)
                if dist < min_res_dist:
                    min_res_dist = dist
                    closest_resource = res
        
        if closest_resource and min_res_dist < self.sight_range * 2: # Attract to resources
            attract_vector = (closest_resource.pos - self.pos) * 0.1
            self.vel = (self.vel + attract_vector).clip(-self.move_speed, self.move_speed)
            
            if min_res_dist < 2.0: # Consume resource
                consumed_amount = min(self.energy * 0.1, closest_resource.amount) # Consume up to 10% of current energy
                self.energy += consumed_amount
                closest_resource.amount -= consumed_amount
                
                resource_obs = {
                    "type": "resource_consumed",
                    "resource_id": closest_resource.id,
                    "amount": round(consumed_amount, 2),
                    "pos": list(self.pos.round(1))
                }
                # Link to previous state or resource found pattern
                if local_patterns:
                    self.last_pattern_id = self.discover_pattern(resource_obs, parent_pattern_id=local_patterns[-1])
                else:
                    self.last_pattern_id = self.discover_pattern(resource_obs, parent_pattern_id=self.last_pattern_id)
                local_patterns.append(self.last_pattern_id)

        self.pos += self.vel
        # Wrap around world boundaries
        self.pos %= sim.world_size
        
        
        # Flocking movement
        cohesion_vector = np.zeros(2)
        if neighbors_in_sight > 0:
            avg_neighbor_pos /= neighbors_in_sight
            avg_neighbor_vel /= neighbors_in_sight
            cohesion_vector = (avg_neighbor_pos - self.pos) * 0.1 # Increased cohesion
            self.vel = (self.vel + (avg_neighbor_vel - self.vel) * 0.1 + cohesion_vector).clip(-self.move_speed, self.move_speed)
        
        # Resource seeking
        closest_resource = None
        min_res_dist = float('inf')
        
        for res in resources:
            if res.amount > 0:
                dist = np.linalg.norm(self.pos - res.pos)
                if dist < min_res_dist:
                    min_res_dist = dist
                    closest_resource = res
        
        if closest_resource and min_res_dist < self.sight_range * 2: # Attract to resources
            attract_vector = (closest_resource.pos - self.pos) * 0.1
            self.vel = (self.vel + attract_vector).clip(-self.move_speed, self.move_speed)
            
            if min_res_dist < 2.0: # Consume resource
                consumed_amount = min(self.energy * 0.1, closest_resource.amount) # Consume up to 10% of current energy
                self.energy += consumed_amount
                closest_resource.amount -= consumed_amount
                
                resource_obs = {
                    "type": "resource_consumed",
                    "resource_id": closest_resource.id,
                    "amount": round(consumed_amount, 2),
                    "pos": list(self.pos.round(1))
                }
                # Link to previous state or resource found pattern
                if local_patterns:
                    self.last_pattern_id = self.discover_pattern(resource_obs, parent_pattern_id=local_patterns[-1])
                else:
                    self.last_pattern_id = self.discover_pattern(resource_obs, parent_pattern_id=self.last_pattern_id)
                local_patterns.append(self.last_pattern_id)
                print(f"  {self.agent_id} consumed {round(consumed_amount,2)} from {closest_resource.id}. Pattern: {self.last_pattern_id}")

        self.pos += self.vel
        # Wrap around world boundaries
        self.pos %= sim.world_size
        
        # Discover emergent patterns (simplified for demo)
        if neighbors_in_sight > 2: # Emergent flock (lowered threshold)
            flock_obs = {
                "type": "flock_formed",
                "size": neighbors_in_sight + 1,
                "center": list(avg_neighbor_pos.round(1)),
                "agent_id": self.agent_id
            }
            # Link to the interaction patterns that define it
            # For simplicity, link to the most recent interaction for now
            if local_patterns:
                 self.last_pattern_id = self.discover_pattern(flock_obs, parent_pattern_id=local_patterns[-1])
            else: # If no local interactions, link to current self-pattern
                 self.last_pattern_id = self.discover_pattern(flock_obs, parent_pattern_id=self.last_pattern_id)
            print(f"  {self.agent_id} discovered FLOCK: {self.last_pattern_id}. Size: {neighbors_in_sight + 1}")
            local_patterns.append(self.last_pattern_id)
            
        return True # Agent is alive

class WorldSim(SimulationInterface):
    def __init__(self, world_size=(100,100), db_path=None, n_resources=5):
        super().__init__(db_path=db_path, n_populations=1)
        self.world_size = np.array(world_size)
        self.resources = []
        for i in range(n_resources):
            self.resources.append(Resource(f"Res_{i}", np.random.uniform(0, self.world_size, 2)))

    def get_agents(self):
        return self.populations[0]

def main():
    print("CYCLE 296: PAPER 8 - 2D SWARM EMERGENCE DATA GENERATION")
    print("======================================================")
    
    # 0. Setup Environment
    memory = PatternMemory()
    sim = WorldSim(world_size=(100,100), n_resources=5)
    
    N_AGENTS = 50
    SIM_STEPS = 200
    
    # Initialize agents
    initial_agents = []
    for i in range(N_AGENTS):
        agent = SwarmAgent(f"Agent_{i}", np.random.uniform(0, sim.world_size, 2), energy=np.random.uniform(0.5, 1.5), move_speed=2.0) # Increased move_speed
        initial_agents.append(agent)
        sim.add_agent(agent, 0)
    
    print(f"Simulation setup: {N_AGENTS} agents in {sim.world_size} world, {len(sim.resources)} resources.")
    
    # 1. Run Simulation
    alive_agents = initial_agents
    for step in range(SIM_STEPS):
        print(f"Step {step}/{SIM_STEPS}. Alive: {len(alive_agents)}", end='\r')
        new_alive_agents = []
        for agent in alive_agents:
            if agent.update(sim, alive_agents, sim.resources):
                new_alive_agents.append(agent)
        alive_agents = new_alive_agents
        
        if not alive_agents:
            print("\nAll agents died.")
            break
            
        # Optional: replenish some resources
        for res in sim.resources:
            if res.amount < res.initial_amount / 2:
                res.amount += 0.1 # Slow replenishment
    print("\nSimulation complete.")
    
    # 2. Analyze Data (Identify "Hero" Patterns)
    print("\n--- Analyzing Emergent Patterns ---")
    archaeologist = PatternArchaeologist(workspace_path=memory.workspace_path)
    
    # DEBUG: Inspect what patterns are actually being saved
    print("\nDEBUG: Inspecting top 10 most recent patterns:")
    recent_patterns_raw = archaeologist.memory.search_patterns(limit=10, sort_by='last_seen')
    for p in recent_patterns_raw:
        print(f"  ID: {p.pattern_id[:8]}... | Name: {p.name} | Type: {p.pattern_type.value} | Data: {p.data}")

    # Find a significant flock pattern
    # Manual filter for now to bypass potential data_query issues
    all_patterns = archaeologist.memory.search_patterns(limit=5000, sort_by='last_seen', sort_order='DESC')
    flock_patterns = [p for p in all_patterns if p.data.get("type") == "flock_formed"]

    if flock_patterns:
        hero_flock = flock_patterns[0]
        print(f"\nFound Hero Flock Pattern: {hero_flock.name} (ID: {hero_flock.pattern_id})")
        
        # Trace and store its lineage
        flock_lineage = archaeologist.trace_ancestry(hero_flock.pattern_id, max_depth=15) # Deeper trace
        
        # archaeologist.get_depth is a helper method, let's use it from the instance
        print(f"  Lineage Depth: {archaeologist.get_depth(flock_lineage)}")
        
        os.makedirs("experiments/results", exist_ok=True)
        with open("experiments/results/paper8_hero_flock_lineage.json", "w") as f:
            json.dump(flock_lineage, f, indent=2)
        print(f"  Hero Flock Lineage saved to experiments/results/paper8_hero_flock_lineage.json")
    else:
        print("No significant flock patterns found.")
    
    # Find a significant resource consumption pattern
    resource_patterns = [p for p in all_patterns if p.data.get("type") == "resource_consumed"]
    if resource_patterns:
        hero_res_event = resource_patterns[0]
        print(f"\nFound Hero Resource Event: {hero_res_event.name} (ID: {hero_res_event.pattern_id})")
        
        res_lineage = archaeologist.trace_ancestry(hero_res_event.pattern_id, max_depth=15)
        print(f"  Lineage Depth: {archaeologist.get_depth(res_lineage)}")
        
        os.makedirs("experiments/results", exist_ok=True)
        with open("experiments/results/paper8_hero_resource_lineage.json", "w") as f:
            json.dump(res_lineage, f, indent=2)
        print(f"  Hero Resource Lineage saved to experiments/results/paper8_hero_resource_lineage.json")
    else:
        print("No significant resource consumption patterns found.")
        
    print("\n--- Paper 8 Data Generation Complete ---")

if __name__ == "__main__":
    main()
