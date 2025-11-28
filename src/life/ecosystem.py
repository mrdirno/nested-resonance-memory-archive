"""
Cycle 2460: The Ecosystem (Gate 88)
Role: The Environment
Responsibility: Manage the population of DigitalLifeforms.

Concepts:
- Container for agents.
- Main simulation loop.
- Resource management (Carrying Capacity).
"""

import time
import random
from typing import List
from src.life.genesis import DigitalLifeform

class Ecosystem:
    def __init__(self, capacity: int = 100):
        self.agents: List[DigitalLifeform] = []
        self.tick_count = 0
        self.capacity = capacity
        self.running = False

    def add_agent(self, agent: DigitalLifeform):
        """Add an agent to the ecosystem."""
        if len(self.agents) < self.capacity:
            self.agents.append(agent)
            print(f"[ECO] Added agent: {agent.name}")
        else:
            print(f"[ECO] Capacity reached. Cannot add {agent.name}")
        
    def remove_agent(self, agent: DigitalLifeform):
        """Remove an agent from the ecosystem."""
        if agent in self.agents:
            self.agents.remove(agent)
            # print(f"[ECO] Removed agent: {agent.name}")
        else:
            print(f"[ECO] Agent {agent.name} not found in ecosystem.")

    def propagate_signal(self, signal):
        """Distribute a signal to all agents."""
        for agent in self.agents:
            if agent.id != signal.source_id:
                agent.communicator.receive(signal)

    def update(self):
        """
        Perform one simulation tick.
        - Phase 1: Plants act (forage/reproduce).
        - Phase 2: Predators act (hunt).
        - Handle reproduction.
        - Remove dead agents.
        """
        self.tick_count += 1
        # print(f"--- Tick {self.tick_count} | Population: {len(self.agents)} ---")

        all_new_agents = []
        
        # Shuffle agents to prevent artificial ordering effects
        random.shuffle(self.agents)

        # Separate agents into prey and predators
        current_prey_agents = [agent for agent in self.agents if agent.is_prey]
        current_predator_agents = [agent for agent in self.agents if agent.is_predator]

        # --- PHASE 1: PREY (Plants) ---
        prey_alive_this_phase = []
        for agent in current_prey_agents:
            # Sense, Metabolize, Act (forage, reproduce, etc.)
            agent.sense([]) 
            agent.metabolize()
            agent.act()

            # Handle reproduction for prey
            if len(self.agents) + len(all_new_agents) < self.capacity:
                child = agent.reproduce()
                if child:
                    all_new_agents.append(child)

            # Check survival for prey
            if agent.alive and agent.energy > 0:
                prey_alive_this_phase.append(agent)
            else:
                agent.die() # Ensure die logic is called

        # --- PHASE 2: PREDATORS ---
        predator_alive_this_phase = []
        for agent in current_predator_agents:
            # Sense, Metabolize, Act (hunt, reproduce, etc.)
            agent.sense([])
            agent.metabolize()
            agent.act() # This will set agent.intent to 'hunt' if conditions are met

            # If predator decided to hunt, find a target from currently alive prey
            if agent.intent == 'hunt' and agent.energy > 0:
                if prey_alive_this_phase: # Ensure there's prey to hunt
                    target = random.choice(prey_alive_this_phase)
                    agent.hunt(target) # Predator performs hunt action
            
            # Handle reproduction for predators
            if len(self.agents) + len(all_new_agents) < self.capacity:
                child = agent.reproduce()
                if child:
                    all_new_agents.append(child)

            # Check survival for predators
            if agent.alive and agent.energy > 0:
                predator_alive_this_phase.append(agent)
            else:
                agent.die() # Ensure die logic is called
                
        # --- REBUILD self.agents AND ADD NEW AGENTS ---
        self.agents = []
        self.agents.extend(prey_alive_this_phase)
        self.agents.extend(predator_alive_this_phase)
        
        # Add new life, respecting capacity
        for child in all_new_agents:
            self.add_agent(child)

    def run(self, steps: int = 10, delay: float = 0.1):
        """Run the simulation for N steps."""
        self.running = True
        for _ in range(steps):
            if not self.running:
                break
            self.update()
            time.sleep(delay)
            
            if not self.agents:
                print("[ECO] Extinction event. Stopping.")
                break

if __name__ == "__main__":
    # Test Run
    env = Ecosystem(capacity=10)
    adam = DigitalLifeform(name="ADAM")
    adam.energy = 200 # Boost for reproduction
    env.add_agent(adam)
    
    env.run(steps=20)
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
