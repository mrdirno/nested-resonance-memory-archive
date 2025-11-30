#!/usr/bin/env python3
"""
Experiment: Cycle 2617 - The Agency
Goal: Agents modify their internal goal state based on high-level reasoning.
"""

import sys
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2602_hive import Vector2, HiveAgent
    from cycle2615_prompt import generate_context_prompt
    from cycle2616_inference import mock_llm_inference
except ImportError:
    sys.exit(1)

class SmartAgent(HiveAgent):
    def think(self):
        """
        Generate prompt, run inference, and update state.
        """
        # Dummy context for test
        dist = 100.0
        if self.known_target:
            dist = ((self.position.x - self.known_target.x)**2 + 
                    (self.position.y - self.known_target.y)**2)**0.5
            
        prompt = generate_context_prompt(self, [], dist)
        decision = mock_llm_inference(prompt)
        
        print(f"[{self.agent_id}] Thought: {decision}")
        
        if decision == "PANIC":
            # Change behavior: Move randomly fast
            self.speed *= 2.0
            print(f"[{self.agent_id}] ACTION: Panic! Speed increased to {self.speed}")
        elif decision == "SIGNAL":
            # In a real app, broadcast. Here, we just flag.
            print(f"[{self.agent_id}] ACTION: Broadcasting distress signal.")

def run_agency_test():
    print("Cycle 2617: The Agency - Autonomous Goal Modification")
    
    agent = SmartAgent("Smart-1", Vector2(0,0))
    
    # Scenario: Alone and searching -> Should PANIC
    print("\n--- Scenario 1: Isolation ---")
    agent.think()
    
    if agent.speed > 4.0: # Base is 4.0
        print("SUCCESS: Agent modified its own parameters based on reasoning.")
    else:
        print("FAILURE: Agent did not react.")
        sys.exit(1)

if __name__ == "__main__":
    run_agency_test()
