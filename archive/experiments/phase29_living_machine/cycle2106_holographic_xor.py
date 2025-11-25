
import sys
import os
import random
import numpy as np
from typing import List, Tuple

# Add project root to path
sys.path.append(os.getcwd())

from src.fractal.agent import FractalAgent

# --- PHYSICS ENGINE ---
def propagate_field(agents: List[FractalAgent], target_pos: np.ndarray) -> float:
    """Calculate the net field phase at a target position."""
    # Superposition of fields from all agents
    # Field at r = A * exp(i * (phase - k*r)) / r
    # Simplified: Sum of sin(phase - distance)
    
    total_sin = 0.0
    total_cos = 0.0
    
    for agent in agents:
        dist = np.linalg.norm(agent.state.position - target_pos)
        if dist < 0.1: dist = 0.1 # Avoid singularity
        
        # Wave propagation: Phase delay = Distance (assuming k=1, v=1)
        # Amplitude decay: 1/r
        
        local_phase = agent.state.phase - dist
        amplitude = agent.state.energy / dist
        
        total_sin += amplitude * np.sin(local_phase)
        total_cos += amplitude * np.cos(local_phase)
        
    return np.arctan2(total_sin, total_cos)

# --- GENETIC ALGORITHM ---

class LogicSubstrate:
    def __init__(self, n_nodes: int, bounds: float = 10.0):
        self.n_nodes = n_nodes
        self.bounds = bounds
        # Genotype: Positions of N nodes (x, y, z)
        self.genome = np.random.rand(n_nodes, 3) * bounds
        
    def mutate(self, rate: float = 0.1, strength: float = 1.0):
        mask = np.random.rand(*self.genome.shape) < rate
        noise = np.random.normal(0, strength, self.genome.shape)
        self.genome[mask] += noise[mask]
        self.genome = np.clip(self.genome, 0, self.bounds)

def evaluate_xor(substrate: LogicSubstrate) -> float:
    # Inputs: Source A and Source B (Fixed positions)
    # Output: Target T (Fixed position)
    # Substrate: Passive nodes (Scatterers) or Active Repeaters?
    # Let's assume Active Repeaters (Transducers) driven by the field.
    # Or simply Sources A and B transmit, Substrate reflects/modulates?
    
    # Let's model "Active Swarm": 
    # Inputs A and B define the Boundary Conditions.
    # Substrate agents adjust their phase to minimize local potential? 
    # No, that's self-organization.
    # Here we are "Designing" (Evolving) the static positions.
    # Physics: A and B emit waves. Substrate agents oscillate in response (passive).
    # Then they re-emit.
    # Simplified: Total Field at Target = Field(A) + Field(B) + Sum(Field(Node_i))
    # Where Field(Node_i) depends on Field(A->i) + Field(B->i).
    
    # Let's stick to "Holographic":
    # A and B emit. 
    # Nodes are *Active Emitters* with fixed phase relative to inputs? 
    # Or just Repeaters?
    # Let's assume Nodes are PASSIVE SCATTERERS. 
    # Complex wave physics.
    
    # SIMPLER MODEL:
    # Input A and B are agents with specific phases (0 or Pi).
    # Substrate agents are located at `substrate.genome`.
    # Target is at (bounds/2, bounds/2).
    # Field at Target = Sum( Field(A->Target), Field(B->Target), Field(A->Node->Target), Field(B->Node->Target) )
    # Direct path + Scattered path.
    # This is true interference.
    
    pos_a = np.array([0.0, 0.0, 0.0])
    pos_b = np.array([10.0, 0.0, 0.0])
    pos_target = np.array([5.0, 10.0, 0.0])
    
    score = 0.0
    
    # XOR Truth Table
    # 0,0 -> 0
    # 0,1 -> 1
    # 1,0 -> 1
    # 1,1 -> 0
    
    truth_table = [
        (0.0, 0.0, 0.0),
        (0.0, np.pi, 1.0),
        (np.pi, 0.0, 1.0),
        (np.pi, np.pi, 0.0)
    ]
    
    for phase_a, phase_b, expected_out in truth_table:
        # Calculate Field at Target
        
        # 1. Direct Fields
        dist_a = np.linalg.norm(pos_a - pos_target)
        dist_b = np.linalg.norm(pos_b - pos_target)
        
        field_a = np.exp(1j * (phase_a - dist_a)) / dist_a
        field_b = np.exp(1j * (phase_b - dist_b)) / dist_b
        
        # 2. Scattered Fields (Single Scattering approximation)
        field_scattered = 0.0
        for i in range(substrate.n_nodes):
            pos_node = substrate.genome[i]
            
            # Field at Node
            d_an = np.linalg.norm(pos_a - pos_node)
            d_bn = np.linalg.norm(pos_b - pos_node)
            
            val_at_node = (np.exp(1j * (phase_a - d_an)) / d_an) + (np.exp(1j * (phase_b - d_bn)) / d_bn)
            
            # Re-emission (Scattering)
            d_nt = np.linalg.norm(pos_node - pos_target)
            field_scattered += val_at_node * np.exp(1j * (-d_nt)) / d_nt # Phase delay
            
        total_field = field_a + field_b + field_scattered
        
        # Measure Intensity at Target
        intensity = np.abs(total_field)
        
        # Logic: 0 = Low Intensity, 1 = High Intensity
        # We need a threshold. Let's optimize for (High - Low) separation.
        
        if expected_out == 1.0:
            score += intensity # Maximize signal for 1
        else:
            score -= intensity # Minimize signal for 0
            
    return score

def run_evolution():
    print("MOG ONLINE: Cycle 2106 - The Holographic XOR", flush=True)
    
    POP_SIZE = 50
    GENERATIONS = 100
    N_NODES = 5
    
    population = [LogicSubstrate(N_NODES) for _ in range(POP_SIZE)]
    
    for gen in range(GENERATIONS):
        # Evaluate
        fitnesses = [(ind, evaluate_xor(ind)) for ind in population]
        fitnesses.sort(key=lambda x: x[1], reverse=True)
        
        best = fitnesses[0]
        if gen % 10 == 0:
            print(f"Gen {gen}: Best Fitness {best[1]:.4f}", flush=True)
            
        # Selection (Elitism + Mutation)
        survivors = [x[0] for x in fitnesses[:10]] # Top 10
        
        new_pop = []
        while len(new_pop) < POP_SIZE:
            parent = random.choice(survivors)
            child = LogicSubstrate(N_NODES)
            child.genome = parent.genome.copy()
            child.mutate(rate=0.2, strength=0.5)
            new_pop.append(child)
            
        population = new_pop
        
    print(f"Final Best Fitness: {best[1]:.4f}")
    
    # Verification
    best_sub = best[0]
    pos_a = np.array([0.0, 0.0, 0.0])
    pos_b = np.array([10.0, 0.0, 0.0])
    pos_target = np.array([5.0, 10.0, 0.0])
    
    print("\n--- TRUTH TABLE VERIFICATION ---")
    for phase_a, phase_b, expected_out in [(0,0,0), (0,np.pi,1), (np.pi,0,1), (np.pi,np.pi,0)]:
        # Re-calc (Copy-paste logic, sorry for redundancy in verification)
        dist_a = np.linalg.norm(pos_a - pos_target)
        dist_b = np.linalg.norm(pos_b - pos_target)
        field_a = np.exp(1j * (phase_a - dist_a)) / dist_a
        field_b = np.exp(1j * (phase_b - dist_b)) / dist_b
        field_scattered = 0.0
        for i in range(best_sub.n_nodes):
            pos_node = best_sub.genome[i]
            d_an = np.linalg.norm(pos_a - pos_node)
            d_bn = np.linalg.norm(pos_b - pos_node)
            val_at_node = (np.exp(1j * (phase_a - d_an)) / d_an) + (np.exp(1j * (phase_b - d_bn)) / d_bn)
            d_nt = np.linalg.norm(pos_node - pos_target)
            field_scattered += val_at_node * np.exp(1j * (-d_nt)) / d_nt
        total = field_a + field_b + field_scattered
        intensity = np.abs(total)
        
        print(f"In ({phase_a:.2f}, {phase_b:.2f}) -> Out Intensity: {intensity:.4f} (Expected {'HIGH' if expected_out else 'LOW'})", flush=True)

if __name__ == "__main__":
    run_evolution()
