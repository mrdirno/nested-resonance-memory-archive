import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional, Set
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

class SpatialCompositionEngine(CompositionEngine):
    def __init__(self, resonance_threshold: float = 0.7, energy_threshold: float = 0.5, distance_threshold: float = 20.0):
        super().__init__(resonance_threshold, energy_threshold)
        self.distance_threshold = distance_threshold

    def detect_clusters(
        self,
        agents: List[FractalAgent],
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        if len(agents) < min_cluster_size:
            return []

        depth_groups: Dict[int, List[FractalAgent]] = {}
        for agent in agents:
            depth = agent.state.depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(agent)

        all_clusters = []

        for depth, depth_agents in depth_groups.items():
            if len(depth_agents) < min_cluster_size:
                continue

            n = len(depth_agents)
            adjacency_matrix = np.zeros((n, n), dtype=bool)

            for i in range(n):
                for j in range(i + 1, n):
                    agent_i = depth_agents[i]
                    agent_j = depth_agents[j]
                    
                    dist = np.linalg.norm(agent_i.state.position - agent_j.state.position)
                    if dist > self.distance_threshold:
                        continue

                    resonance = abs(agent_i.calculate_resonance(agent_j))
                    if resonance >= self.resonance_threshold:
                        adjacency_matrix[i, j] = True
                        adjacency_matrix[j, i] = True

            visited = set()
            for i in range(n):
                if i in visited:
                    continue

                cluster = [depth_agents[i]]
                visited.add(i)

                for j in range(n):
                    if j in visited:
                        continue
                    
                    is_connected_to_all = True
                    for member in cluster:
                        member_idx = depth_agents.index(member) 
                        if not adjacency_matrix[member_idx, j]:
                            is_connected_to_all = False
                            break
                    
                    if is_connected_to_all:
                        cluster.append(depth_agents[j])
                        visited.add(j)

                if len(cluster) >= min_cluster_size:
                    if max_cluster_size is None or len(cluster) <= max_cluster_size:
                        all_clusters.append(cluster)

        return all_clusters

def run_simulation(config_name: str, recharge: float, cost_single: float, cost_cluster: float):
    print(f"\n--- Simulation: {config_name} ---", flush=True)
    
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    SHOCK_CYCLE = 50
    VELOCITY_MAGNITUDE = 5.0
    
    DECOMP_LOW_ENERGY = 0.2 
    DECOMP_HIGH_ENERGY = 4.0 
    
    cluster_registry: Dict[str, List[FractalAgent]] = {}

    # Initialize Population
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    pop_history = []
    pre_shock_pop = 0
    
    for cycle in range(CYCLES):
        # SHOCK at Cycle 50
        if cycle == SHOCK_CYCLE:
            print("!!! INJECTING SHOCK (50% cull) !!!", flush=True)
            # We need to remove 50% of agents.
            # If we remove a Cluster, we remove its constituents too (conceptually).
            # If we remove a single, it's gone.
            
            # Count current population (Active + Dormant)
            active_count = len(agents)
            dormant_count = sum(len(v) for v in cluster_registry.values())
            pre_shock_pop = active_count + dormant_count
            print(f"Pre-Shock Population: {pre_shock_pop}", flush=True)
            
            # We will iterate active agents and kill with 50% probability
            survivors = []
            for agent in agents:
                if random.random() > 0.5:
                    survivors.append(agent)
                else:
                    # Killed.
                    # If cluster, remove from registry to kill constituents
                    if agent.state.depth > 0:
                        cluster_registry.pop(agent.agent_id, None)
            
            agents = survivors
            
            post_active = len(agents)
            post_dormant = sum(len(v) for v in cluster_registry.values())
            print(f"Post-Shock Population: {post_active + post_dormant}", flush=True)

        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = cost_cluster if agent.state.depth > 0 else cost_single
            agent.update_phase(delta_t=1.0)
            agent.update_energy(recharge - cost)
            
            decomposed = False
            if agent.state.depth > 0:
                if agent.state.energy < DECOMP_LOW_ENERGY or agent.state.energy > DECOMP_HIGH_ENERGY:
                    decomposed = True
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    if constituents:
                        for child in constituents:
                            child.state.energy = agent.state.energy / len(constituents)
                            child.state.position = agent.state.position.copy()
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)

            if not decomposed:
                if agent.is_alive(energy_threshold=0.0):
                    active_agents.append(agent)
        
        agents = active_agents + newly_released
        
        # 3. Composition
        new_clusters = comp_engine.compose_all(agents)
        consumed_ids = set()
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                    consumed_ids.add(child_id)
            cluster_registry[cluster.agent_id] = constituents
            
        agents = [a for a in agents if a.agent_id not in consumed_ids] + new_clusters
        
        # Count
        active_count = len(agents)
        dormant_count = sum(len(v) for v in cluster_registry.values())
        total_pop = active_count + dormant_count
        pop_history.append(total_pop)
        
        if total_pop == 0:
            print(f"Cycle {cycle}: EXTINCTION.", flush=True)
            break

    final_pop = pop_history[-1]
    print(f"Final Population: {final_pop}", flush=True)
    
    if pre_shock_pop > 0:
        resilience = final_pop / pre_shock_pop
    else:
        resilience = 0.0
        
    print(f"Resilience Score: {resilience:.4f}", flush=True)
    return resilience

def run_experiment():
    print("MOG ONLINE: Cycle 1957 - Perturbation Response", flush=True)
    
    # Regime A: Starvation
    res_a = run_simulation("Regime A (Starvation)", recharge=0.02, cost_single=0.10, cost_cluster=0.02)
    
    # Regime B: Abundance
    res_b = run_simulation("Regime B (Abundance)", recharge=0.05, cost_single=0.01, cost_cluster=0.01)
    
    print("\n--- Comparison ---", flush=True)
    print(f"Resilience A (Starvation): {res_a:.4f}", flush=True)
    print(f"Resilience B (Abundance): {res_b:.4f}", flush=True)
    
    if res_a < res_b:
        print("HYPOTHESIS CONFIRMED: Starvation regime is fragile (Static).", flush=True)
    else:
        print("HYPOTHESIS FALSIFIED: Starvation regime is robust.", flush=True)

if __name__ == "__main__":
    run_experiment()