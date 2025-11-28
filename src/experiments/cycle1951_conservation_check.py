
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

def run_experiment():
    print("MOG ONLINE: Cycle 1951 - Conservation of Mass Check")
    
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 10
    VELOCITY_MAGNITUDE = 5.0
    
    RECHARGE_RATE = 0.02
    COST_SINGLE = 0.10
    COST_CLUSTER = 0.02
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

    print(f"Initialized {len(agents)} agents.")
    
    # Initial Count Check
    initial_ids = set(a.agent_id for a in agents)
    assert len(initial_ids) == N_AGENTS

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    for cycle in range(CYCLES):
        print(f"\n--- Cycle {cycle} ---")
        
        # 1. Movement
        for agent in agents:
            theta = random.uniform(0, 2*np.pi)
            dx = VELOCITY_MAGNITUDE * np.cos(theta)
            dy = VELOCITY_MAGNITUDE * np.sin(theta)
            agent.move(np.array([dx, dy, 0.0]))
            agent.state.position = agent.state.position % WORLD_SIZE

        # 2. Metabolism & Recharge & Decomp
        active_agents = []
        newly_released = []

        for agent in agents:
            cost = COST_CLUSTER if agent.state.depth > 0 else COST_SINGLE
            agent.update_phase(delta_t=1.0)
            agent.update_energy(RECHARGE_RATE - cost)
            
            decomposed = False
            if agent.state.depth > 0:
                if agent.state.energy < DECOMP_LOW_ENERGY:
                    decomposed = True
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    if constituents:
                        print(f"Cluster {agent.agent_id[:6]} starved. Releasing {len(constituents)}.")
                        for child in constituents:
                            child.state.energy = agent.state.energy / len(constituents)
                            child.state.position = agent.state.position.copy()
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)
                
                elif agent.state.energy > DECOMP_HIGH_ENERGY:
                    decomposed = True
                    constituents = cluster_registry.pop(agent.agent_id, [])
                    if constituents:
                        print(f"Cluster {agent.agent_id[:6]} burst. Releasing {len(constituents)}.")
                        for child in constituents:
                            child.state.energy = agent.state.energy / len(constituents)
                            child.state.position = agent.state.position.copy()
                            child.move(np.random.rand(3) * 2.0 - 1.0)
                            newly_released.append(child)

            if not decomposed:
                if agent.is_alive(energy_threshold=0.0):
                    active_agents.append(agent)
                else:
                    print(f"Agent {agent.agent_id[:6]} died (Energy {agent.state.energy:.2f}).")
        
        agents = active_agents + newly_released
        
        # Pre-Composition Check
        active_ids = set(a.agent_id for a in agents)
        dormant_ids = set(a.agent_id for sublist in cluster_registry.values() for a in sublist)
        overlap = active_ids.intersection(dormant_ids)
        if overlap:
            print(f"ERROR: Overlap detected BEFORE composition: {overlap}")
        
        total_mass = len(active_ids) + len(dormant_ids)
        print(f"Mass Check 1 (Pre-Comp): Active {len(active_ids)} + Dormant {len(dormant_ids)} = {total_mass}")

        # 3. Composition
        new_clusters = comp_engine.compose_all(agents)
        
        if new_clusters:
            print(f"Formed {len(new_clusters)} new clusters.")
        
        for cluster in new_clusters:
            constituents = []
            for child_id in cluster.state.children_ids:
                found = next((a for a in agents if a.agent_id == child_id), None)
                if found:
                    constituents.append(found)
                else:
                    print(f"ERROR: Constituent {child_id[:6]} not found in active list!")
            cluster_registry[cluster.agent_id] = constituents
            
        clustered_ids = set()
        for cluster in new_clusters:
            for child_id in cluster.state.children_ids:
                clustered_ids.add(child_id)
        
        surviving_agents = [a for a in agents if a.agent_id not in clustered_ids]
        agents = surviving_agents + new_clusters
        
        # Post-Composition Check
        active_ids = set(a.agent_id for a in agents)
        dormant_ids = set(a.agent_id for sublist in cluster_registry.values() for a in sublist)
        
        # Check for Cluster Duplication
        # Are new clusters in 'agents'? Yes.
        # Are constituents removed from 'agents'? Yes.
        # Are constituents added to 'dormant'? Yes.
        
        overlap = active_ids.intersection(dormant_ids)
        if overlap:
            print(f"ERROR: Overlap detected AFTER composition: {overlap}")
            # This is the likely bug source. If we failed to remove a constituent, it is both Active and Dormant.
            
        total_mass = len(active_ids) + len(dormant_ids)
        
        # Clusters themselves are agents, so they are in 'active_ids'.
        # But they are emergent entities. Mass conservation applies to *Base Agents*.
        # We need to count Base Agents.
        
        # Count Base Agents
        base_active = sum(1 for a in agents if a.state.depth == 0)
        base_dormant = len(dormant_ids) # Assuming depth 0 constituents
        total_base = base_active + base_dormant
        
        print(f"Mass Check 2 (Post-Comp): Base Active {base_active} + Base Dormant {base_dormant} = {total_base}")
        print(f"Total Entities (including clusters): {len(active_ids)}")

        if total_base > N_AGENTS:
            print("VIOLATION: MATTER CREATED.")
            break
            
    if total_base <= N_AGENTS:
        print("CONSERVATION CONFIRMED.")
    else:
        print("CONSERVATION FAILED.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
