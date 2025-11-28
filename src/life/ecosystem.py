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

    def update(self):
        """
        Perform one simulation tick.
        - Update all agents.
        - Handle reproduction.
        - Remove dead agents.
        - Propagate signals.
        """
        self.tick_count += 1
        # print(f"--- Tick {self.tick_count} | Population: {len(self.agents)} ---")

        new_agents = []
        dead_agents = []
        
        # Collect signals from previous tick (or current if synchronous)
        # For now, we'll collect signals emitted during this tick and make them available next tick?
        # Or just immediate propagation. Let's do immediate for simplicity in this loop, 
        # but ideally it should be: Sense(T-1) -> Act(T) -> Emit(T).
        
        # We need a 2-pass approach or just use signals from last frame.
        # Let's use a list of signals generated in this frame to pass to next frame.
        # But wait, the plan said "Collect signals returned by agent.act()".
        
        current_signals = getattr(self, 'active_signals', [])
        next_signals = []

        for agent in self.agents:
            # 0. Sense Environment (Signals)
            agent.sense(current_signals)

            # 1. Metabolize & Act
            agent.metabolize()
            signal = agent.act() # act() now returns a Signal or None
            if signal:
                next_signals.append(signal)

            # 2. Check Survival
            if not agent.alive or agent.energy <= 0:
                agent.die()
                dead_agents.append(agent)
                continue

            # 3. Reproduce (if possible and space available)
            if len(self.agents) + len(new_agents) < self.capacity:
                child = agent.reproduce()
                if child:
                    new_agents.append(child)

        # Update active signals for next tick
        self.active_signals = next_signals

        # Cleanup
        for dead in dead_agents:
            if dead in self.agents:
                self.agents.remove(dead)

        # Add new life
        for child in new_agents:
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