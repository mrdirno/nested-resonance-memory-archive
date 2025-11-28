
import sys
import os
import random
import numpy as np
from typing import List, Dict, Optional
from dataclasses import asdict

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent
from src.fractal.composition import CompositionEngine

class SpatialCompositionEngine(CompositionEngine):
    """
    Extension of CompositionEngine that enforces spatial constraints.
    Agents must be within 'distance_threshold' to be considered for clustering.
    """
    def __init__(self, resonance_threshold: float = 0.7, energy_threshold: float = 0.5, distance_threshold: float = 20.0):
        super().__init__(resonance_threshold, energy_threshold)
        self.distance_threshold = distance_threshold

    def detect_clusters(
        self,
        agents: List[FractalAgent],
        min_cluster_size: int = 2,
        max_cluster_size: Optional[int] = None,
    ) -> List[List[FractalAgent]]:
        """
        Detect potential clusters via resonance AND spatial proximity.
        """
        if len(agents) < min_cluster_size:
            return []

        # Filter to agents at same depth
        depth_groups: Dict[int, List[FractalAgent]] = {}
        for agent in agents:
            depth = agent.state.depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(agent)

        all_clusters = []

        # Cluster within each depth level
        for depth, depth_agents in depth_groups.items():
            if len(depth_agents) < min_cluster_size:
                continue

            n = len(depth_agents)
            adjacency_matrix = np.zeros((n, n), dtype=bool)

            # Build Adjacency Matrix (Spatial + Resonance)
            for i in range(n):
                for j in range(i + 1, n):
                    agent_i = depth_agents[i]
                    agent_j = depth_agents[j]
                    
                    # 1. Spatial Check
                    dist = np.linalg.norm(agent_i.state.position - agent_j.state.position)
                    if dist > self.distance_threshold:
                        continue

                    # 2. Resonance Check
                    resonance = abs(agent_i.calculate_resonance(agent_j))
                    if resonance >= self.resonance_threshold:
                        adjacency_matrix[i, j] = True
                        adjacency_matrix[j, i] = True

            # Find connected components (greedy clique-like)
            visited = set()
            for i in range(n):
                if i in visited:
                    continue

                cluster = [depth_agents[i]]
                visited.add(i)

                # Add connected agents (Must be connected to ALL existing members - Clique)
                # Or relaxed? CompositionEngine implementation uses "all(...)".
                # "Check if j resonates with all current cluster members"
                # We will stick to that logic.
                
                for j in range(n):
                    if j in visited:
                        continue
                    
                    # Check connection to ALL cluster members
                    is_connected_to_all = True
                    for member in cluster:
                        # Find member index in depth_agents
                        member_idx = depth_agents.index(member) 
                        if not adjacency_matrix[member_idx, j]:
                            is_connected_to_all = False
                            break
                    
                    if is_connected_to_all:
                        cluster.append(depth_agents[j])
                        visited.add(j)

                # Filter by size constraints
                if len(cluster) >= min_cluster_size:
                    if max_cluster_size is None or len(cluster) <= max_cluster_size:
                        all_clusters.append(cluster)

        return all_clusters

def run_experiment():
    print("MOG ONLINE: Cycle 1946 - Spatial NRM Baseline Check")
    
    # Parameters
    N_AGENTS = 50
    WORLD_SIZE = 100.0
    DISTANCE_THRESHOLD = 20.0
    CYCLES = 100
    RECHARGE_RATE = 0.05
    METABOLIC_COST = 0.01
    
    # Initialize Population
    agents = []
    for i in range(N_AGENTS):
        pos = np.random.rand(3) * WORLD_SIZE
        pos[2] = 0 # 2D plane
        agent = FractalAgent(
            agent_id=f"gen0_{i}",
            energy=1.0,
            phase=random.uniform(0, 2*np.pi),
            position=pos
        )
        agents.append(agent)

    print(f"Initialized {len(agents)} agents in {WORLD_SIZE}x{WORLD_SIZE} world.")
    print(f"Distance Threshold: {DISTANCE_THRESHOLD}")

    comp_engine = SpatialCompositionEngine(distance_threshold=DISTANCE_THRESHOLD)
    
    history = []

    for cycle in range(CYCLES):
        # 1. Metabolism & Recharge
        active_agents = []
        for agent in agents:
            agent.evolve(delta_time=1.0) # Updates phase, subtracts metabolic cost
            agent.update_energy(RECHARGE_RATE) # Environmental flux
            
            if agent.is_alive():
                active_agents.append(agent)
        
        agents = active_agents
        
        # 2. Composition (Spatial)
        # Separate by depth for simplicity in this test, though engine handles it.
        # We pass all agents to compose_all
        new_clusters = comp_engine.compose_all(agents)
        
        # Add new clusters to population, remove constituents (they are now children)
        # Wait, CompositionEngine sets parent_id/cluster_id but returns the Cluster object.
        # We need to manage the "Active Population" list.
        # If an agent is in a cluster, it is effectively "consumed" or "shielded".
        # For this baseline, let's assume hierarchical coexistence: 
        # Clusters exist alongside un-clustered agents. 
        # But typically, constituents are removed from the top-level interaction loop.
        
        # Filter out agents that joined a cluster
        clustered_ids = set()
        for cluster in new_clusters:
            for child_id in cluster.state.children_ids:
                clustered_ids.add(child_id)
        
        # Remove constituents, add clusters
        surviving_agents = [a for a in agents if a.agent_id not in clustered_ids]
        agents = surviving_agents + new_clusters
        
        # 3. Decomposition (Burst)
        # If energy > 2.0 (arbitrary threshold for burst), split.
        next_gen = []
        for agent in agents:
            if agent.state.energy > 4.0: # High threshold to prevent instant explosion
                # Burst!
                # If it's a cluster, it decomposes into children.
                # If it's a base agent, maybe it clones? 
                # Standard NRM V2: Clusters decompose. Base agents don't split (yet? Autopoiesis says yes).
                
                if agent.state.depth > 0:
                    # Decompose Cluster
                    # Retrieve children (we don't have them in memory unless we kept them)
                    # FractalAgent struct has 'children' list but init doesn't populate it from IDs.
                    # The CompositionEngine set parent_id/cluster_id.
                    # We need to track children objects.
                    
                    # For this test, we treat burst as "Death of Cluster, Release of Energy".
                    # Or "Release of Children".
                    # Since we don't have a global registry easily accessible here without `FractalSwarm`,
                    # we will assume "Energy Release" -> 2 Base Agents.
                    
                    # Simplified Decomposition for Baseline Check:
                    # Cluster -> 2 Agents at random positions near parent? 
                    # Or just dissolve.
                    
                    # Let's just keep them alive for now. No decomposition logic in this baseline 
                    # unless necessary for survival. 
                    # Goal is "Survival in Static Field".
                    pass
            
            next_gen.append(agent)
        
        agents = next_gen
        
        # Logging
        n_count = len(agents)
        avg_e = np.mean([a.state.energy for a in agents]) if agents else 0
        history.append((cycle, n_count, avg_e))
        
        if n_count == 0:
            print(f"EXTINCTION at Cycle {cycle}")
            break
            
    # Final Stats
    print(f"Final Population: {len(agents)}")
    if len(agents) > 0:
        print("SURVIVAL CONFIRMED.")
    else:
        print("EXTINCTION CONFIRMED.")

if __name__ == "__main__":
    run_experiment()

# [SPORE] ID: The Colony
