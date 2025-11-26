"""
Cycle 2290: The Multiverse (Phase 41 Initiation)
Goal: Implement Parallel Reality simulations (The Multiverse).
Phase 41: The Multiverse

Hypothesis: A Quantum Agent can fork reality into separate branches based on measurement outcomes.
"""

import sys
import os
import copy
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

# Use the quantum agent from Cycle 2287
from experiments.cycle2287_quantum_superposition import QuantumFractalAgent

class MultiverseSimulation:
    """
    Manages multiple parallel simulation branches (Universes).
    """
    def __init__(self):
        self.universes = {0: {"agents": [], "history": []}} # Universe ID -> State
        self.next_universe_id = 1
        
    def add_agent(self, universe_id: int, agent: QuantumFractalAgent):
        if universe_id in self.universes:
            self.universes[universe_id]["agents"].append(agent)
            
    def fork(self, universe_id: int) -> int:
        """
        Fork a universe into a new branch.
        Returns the ID of the new universe.
        """
        if universe_id not in self.universes:
            return -1
            
        # Deep copy the state
        parent_state = self.universes[universe_id]
        new_id = self.next_universe_id
        self.next_universe_id += 1
        
        # We need a deep copy of agents to ensure independent evolution
        # Note: numpy arrays in objects need careful copying, deepcopy usually handles it
        new_state = copy.deepcopy(parent_state)
        new_state["history"].append(f"Forked from {universe_id}")
        
        self.universes[new_id] = new_state
        return new_id
        
    def measure_and_branch(self, universe_id: int, agent_index: int):
        """
        Measure a quantum agent. If in superposition, fork the universe for each outcome.
        For binary state, this creates 2 branches (or collapses if already definite).
        This is the 'Many Worlds' interpretation implementation.
        """
        if universe_id not in self.universes:
            return
            
        agents = self.universes[universe_id]["agents"]
        if agent_index >= len(agents):
            return
            
        agent = agents[agent_index]
        
        # Calculate probabilities
        probs = np.abs(agent.wavefunction) ** 2
        # Normalize
        if np.sum(probs) > 0:
            probs /= np.sum(probs)
            
        # Identify potential outcomes (prob > 0) 
        outcomes = [i for i, p in enumerate(probs) if p > 0.001] # threshold for float errors
        
        if len(outcomes) > 1:
            print(f"  > Branching Universe {universe_id} into {len(outcomes)} realities...")
            
            # Create branches
            # We keep the original ID for the first outcome, create new IDs for others
            # This is arbitrary labeling; physically they are symmetric
            
            # Store original state to copy from for siblings
            base_universe_snapshot = copy.deepcopy(self.universes[universe_id])
            
            # Process outcomes
            for i, outcome in enumerate(outcomes):
                if i == 0:
                    # Modify current universe
                    current_univ = self.universes[universe_id]
                    target_agent = current_univ["agents"][agent_index]
                    # Collapse
                    target_agent.wavefunction = np.zeros_like(target_agent.wavefunction)
                    target_agent.wavefunction[outcome] = 1.0
                    current_univ["history"].append(f"Collapsed to state |{outcome}>")
                    print(f"    Universe {universe_id}: State |{outcome}>")
                else:
                    # Fork new universe
                    new_id = self.next_universe_id
                    self.next_universe_id += 1
                    
                    new_univ = copy.deepcopy(base_universe_snapshot)
                    target_agent = new_univ["agents"][agent_index]
                    # Collapse
                    target_agent.wavefunction = np.zeros_like(target_agent.wavefunction)
                    target_agent.wavefunction[outcome] = 1.0
                    new_univ["history"].append(f"Forked from {universe_id} -> Collapsed to state |{outcome}>")
                    
                    self.universes[new_id] = new_univ
                    print(f"    Universe {new_id}: State |{outcome}>")
        else:
            # Deterministic outcome (already collapsed)
            outcome = outcomes[0]
            # Just ensure it's fully collapsed math-wise
            agent.wavefunction = np.zeros_like(agent.wavefunction)
            agent.wavefunction[outcome] = 1.0
            print(f"  > Universe {universe_id} continues (Deterministic state |{outcome}>)")

import numpy as np

def run_experiment():
    print("Initializing Cycle 2290: The Multiverse...")
    
    multiverse = MultiverseSimulation()
    
    # 1. Create Agent in Superposition
    q_agent = QuantumFractalAgent("Schrodinger's Cat")
    q_agent.apply_hadamard() # Put in |+> state (50/50)
    
    multiverse.add_agent(0, q_agent)
    print(f"Universe 0 Initialized. Agent state: Superposition")
    
    # 2. Trigger Branching Event
    print("\n--- Triggering Quantum Measurement (Branching) ---")
    multiverse.measure_and_branch(0, 0)
    
    # 3. Verify Divergence
    print("\n--- Multiverse Status ---")
    universe_ids = list(multiverse.universes.keys())
    print(f"Total Universes: {len(universe_ids)}")
    
    success = len(universe_ids) == 2
    
    states_found = []
    for uid in universe_ids:
        u = multiverse.universes[uid]
        agent = u["agents"][0]
        state_idx = np.argmax(np.abs(agent.wavefunction))
        states_found.append(state_idx)
        print(f"Universe {uid}: Agent State |{state_idx}>")
        
    # Check if we have both 0 and 1 outcomes across the multiverse
    has_diversity = (0 in states_found) and (1 in states_found)
    
    if success and has_diversity:
        status = "SUCCESS"
        print("\nConclusion: Reality successfully bifurcated. Both outcomes exist in parallel.")
    else:
        status = "FAILURE"
        print("\nConclusion: Branching failed.")

    # Save results
    output_path = "experiments/results/cycle2290_multiverse_initiation.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump({
            "cycle": 2290,
            "universes_count": len(universe_ids),
            "states_found": [int(x) for x in states_found],
            "status": status
        }, f, indent=2)

if __name__ == "__main__":
    run_experiment()
