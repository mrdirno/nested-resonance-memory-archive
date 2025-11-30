#!/usr/bin/env python3
"""
Experiment: Cycle 2615 - The Prompt
Goal: Generate natural language context from agent state for LLM consumption.
"""

import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def generate_context_prompt(agent: HiveAgent, neighbors: list, target_dist: float) -> str:
    """
    Constructs a prompt describing the agent's situation.
    """
    state_desc = "searching"
    if agent.known_target:
        state_desc = "converging on target"
    
    neighbor_count = len(neighbors)
    
    prompt = f"""
You are Agent {agent.agent_id}.
Current Status: {state_desc}.
Position: ({agent.position.x:.1f}, {agent.position.y:.1f}).
Nearby Allies: {neighbor_count}.
Distance to Objective: {target_dist:.1f} units.

Based on this sensor data, what should be your immediate strategic priority?
Options: [CONTINUE, REGROUP, PANIC, SIGNAL]
"""
    return prompt.strip()

def run_test():
    print("Cycle 2615: The Prompt - Generation Test")
    
    agent = HiveAgent("Alpha-1", Vector2(10, 10))
    agent.known_target = Vector2(50, 50)
    
    # Sim neighbors
    neighbors = ["Beta-2", "Gamma-3"]
    
    dist = 56.5 # approx sqrt(40^2 + 40^2)
    
    prompt = generate_context_prompt(agent, neighbors, dist)
    
    print("\n--- GENERATED PROMPT ---")
    print(prompt)
    print("------------------------")
    
    if "Agent Alpha-1" in prompt and "converging" in prompt:
        print("SUCCESS: Prompt contains key state information.")
    else:
        print("FAILURE: Prompt missing information.")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
