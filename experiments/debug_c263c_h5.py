#!/usr/bin/env python3
"""
Debug script for C263c H5 anomaly.
Runs H5 condition with verbose logging to trace depth and energy.
"""
import sys
import time
import random
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from code.bridge.transcendental_bridge import TranscendentalBridge
from code.fractal.agent import FractalAgent

# Config
CYCLES = 600  # Short run, enough to see extinction (expected ~400)
INITIAL_ENERGY = 50.0
METABOLIC_RATE = 0.2
SPAWN_COST = 25.0
SPAWN_THRESHOLD = 40.0
DEPTH_LIMIT = 3
RECOVERY_BONUS = 15.0

def run_debug():
    print("Running H5 Debug...")
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    
    agents = []
    for i in range(1): # Start with just 1 agent for clarity
        agent = FractalAgent(
            agent_id=f"root_{i}",
            depth=0,
            energy=INITIAL_ENERGY,
            phase=0.0
        )
        agents.append(agent)
        
    print(f"Cycle 0: Agents={len(agents)} {[f'D{a.depth}:E{a.energy:.1f}' for a in agents]}")
    
    for cycle in range(CYCLES):
        # Evolve
        for agent in agents:
            agent.update_phase(delta_t=1.0)
            agent.energy -= METABOLIC_RATE
            # No baseline recharge (Harsh)
            
        # Spawn (H5 only)
        potential_parents = [a for a in agents if a.energy >= SPAWN_THRESHOLD and a.depth < DEPTH_LIMIT]
        
        if potential_parents:
            parent = potential_parents[0] # Deterministic for debug
            
            # Spawn
            parent.energy -= SPAWN_COST
            parent.energy += RECOVERY_BONUS # H5
            
            child = FractalAgent(
                agent_id=f"child_{cycle}",
                depth=parent.depth + 1,
                energy=INITIAL_ENERGY,
                phase=0.0
            )
            agents.append(child)
            print(f"Cycle {cycle}: SPAWN! Parent D{parent.depth}->E{parent.energy:.1f}, Child D{child.depth}")
            
        # Death
        dead = [a for a in agents if a.energy <= 0]
        if dead:
            print(f"Cycle {cycle}: DIED {[f'D{a.depth}' for a in dead]}")
        agents = [a for a in agents if a.energy > 0]
        
        if cycle % 50 == 0 or not agents:
            print(f"Cycle {cycle}: Agents={len(agents)} {[f'D{a.depth}:E{a.energy:.1f}' for a in agents]}")
            
        if not agents:
            print("EXTINCTION REACHED.")
            break

if __name__ == "__main__":
    run_debug()
