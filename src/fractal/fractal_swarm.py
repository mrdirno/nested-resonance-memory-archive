"""
Fractal Swarm - Collection Management for Fractal Agents
"""

import random
from typing import Dict, List, Optional, Any
from .agent import FractalAgent
from .composition import CompositionEngine

class FractalSwarm:
    def __init__(self, max_agents: int = 100, burst_threshold: float = 1000.0):
        self.agents: Dict[str, FractalAgent] = {}
        self.max_agents = max_agents
        self.burst_threshold = burst_threshold
        self.composition_engine = CompositionEngine()
        self.cycle_count = 0

    def spawn_agent(self, reality_metrics: Dict[str, Any], initial_energy: float = 100.0, parent_id: Optional[str] = None, depth: int = 0, phase: float = 0.0, repulsive_fraction: float = 0.3) -> Optional[FractalAgent]:
        if len(self.agents) >= self.max_agents:
            return None
            
        agent_id = f"agent_{self.cycle_count}_{len(self.agents)}"
        
        # Determine coupling sign (Asymmetric Mixed Coupling)
        # Default: 70% Attractive (1.0), 30% Repulsive (-1.0)
        is_repulsive = random.random() < repulsive_fraction
        coupling_sign = -1.0 if is_repulsive else 1.0
        
        agent = FractalAgent(
            agent_id=agent_id,
            energy=initial_energy,
            depth=depth,
            phase=phase,
            coupling_sign=coupling_sign
        )
        if parent_id:
            agent.state.parent_id = parent_id
            
        self.agents[agent_id] = agent
        return agent

    def evolve_cycle(self, coupling_strength: float = 0.0) -> Dict[str, Any]:
        self.cycle_count += 1
        active_agents = [a for a in self.agents.values() if a.is_active]
        
        # Pre-calculate phases for vectorized operations if possible, 
        # but for now we'll do it iteratively or use numpy if available in this scope.
        # Assuming numpy is available as it's used in agent.py, but let's check imports.
        # It's not imported in this file. Let's add it or use pure python.
        # Given the project structure, numpy is standard.
        
        import numpy as np
        
        if active_agents:
            n = len(active_agents)
            phases = np.array([a.state.phase for a in active_agents])
            
            # Calculate Kuramoto Forces with Mixed Coupling
            # F_i = (K_i / N) * sum(sin(phi_j - phi_i))
            # where K_i = coupling_strength * agent.coupling_sign
            
            # If coupling_strength is 0 (default), we might want a base coupling for the "Complex Regime"
            # But the signature defaults to 0.0. Let's assume the caller provides K, 
            # OR we set a default K for internal physics if K=0 is passed but we want self-organization.
            # For now, we respect the passed K.
            
            for i, agent in enumerate(active_agents):
                delta_phases = phases - agent.state.phase
                interactions = np.sin(delta_phases)
                
                # Effective coupling for this agent
                k_effective = coupling_strength * agent.state.coupling_sign
                
                force = (k_effective / n) * np.sum(interactions)
                
                # Apply to velocity (Intrinsic freq 0.1 + Force)
                agent.state.velocity = 0.1 + force

        # Evolve each agent
        for agent in active_agents:
            # 1. Harvest Energy (Resonance Gain)
            # Simulating energy intake from the field based on coupling
            harvest = coupling_strength * 10.0 
            agent.update_energy(harvest)
            
            # 2. Evolve State
            agent.evolve(delta_time=1.0)
            
            # 3. Check for Reproduction (Burst/Mitosis)
            if agent.state.energy > self.burst_threshold:
                # Split energy
                child_energy = agent.state.energy / 2.0
                agent.state.energy = child_energy
                
                # Spawn child
                self.spawn_agent(
                    reality_metrics={}, 
                    initial_energy=child_energy, 
                    parent_id=agent.agent_id, 
                    depth=agent.depth
                )
        
        # Cleanup dead agents
        self.agents = {aid: a for aid, a in self.agents.items() if a.is_active and a.state.energy > 0}
        
        return {
            "cycle": self.cycle_count,
            "active_agents": len(self.agents),
            "total_energy": sum(a.state.energy for a in self.agents.values())
        }

    def energy_pooling_cycle(self, participants: List[FractalAgent], sharing_fraction: float = 0.1):
        """
        Implements PRIN-COOPERATION: Agents share a fraction of energy.
        """
        if not participants:
            return
            
        # print("DEBUG: Entering energy_pooling_cycle", flush=True)
        pool = 0.0
        for agent in participants:
            contribution = agent.state.energy * sharing_fraction
            agent.state.energy -= contribution
            pool += contribution
            
        # Distribute evenly (or could be weighted)
        share = pool / len(participants)
        # print(f"DEBUG: Pool={pool:.2f}, Share={share:.2f}, Agents={len(participants)}", flush=True)
        for agent in participants:
            agent.state.energy += share
