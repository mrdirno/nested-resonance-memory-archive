#!/usr/bin/env python3
"""
Debug script v2 for C263c H5 anomaly.
Runs H5 condition with EXACT experiment parameters.
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
CYCLES = 3000
INITIAL_POPULATION = 10
MAX_AGENTS = 50
INITIAL_ENERGY = 50.0
METABOLIC_RATE = 0.2
SPAWN_COST = 25.0
SPAWN_THRESHOLD = 40.0
DEPTH_LIMIT = 3
RECOVERY_BONUS = 15.0

def run_debug():
    print("Running H5 Debug V2...")
    reality = RealityInterface()
    bridge = TranscendentalBridge()
    
    agents = []
    for i in range(INITIAL_POPULATION):
        agent = FractalAgent(
            agent_id=f"root_{i}",
            depth=0,
            energy=INITIAL_ENERGY,
            phase=0.0
        )
        agents.append(agent)
        
    print(f"Cycle 0: Agents={len(agents)}")
    
    for cycle in range(CYCLES):
        # Evolve
        for agent in agents:
            agent.update_phase(delta_t=1.0)
            agent.energy -= METABOLIC_RATE
            
        # Spawn (H5 only)
        potential_parents = [a for a in agents if a.energy >= SPAWN_THRESHOLD and a.depth < DEPTH_LIMIT]
        
        if potential_parents and len(agents) < MAX_AGENTS:
            parent = random.choice(potential_parents)
            
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
            
        # Death
        agents = [a for a in agents if a.energy > 0]
        
        if cycle % 100 == 0 or not agents:
            depths = [a.depth for a in agents]
            avg_depth = sum(depths)/len(depths) if depths else 0
            print(f"Cycle {cycle}: Agents={len(agents)} AvgDepth={avg_depth:.1f}")
            
        if not agents:
            print(f"EXTINCTION REACHED at Cycle {cycle}.")
            break

if __name__ == "__main__":
    run_debug()
