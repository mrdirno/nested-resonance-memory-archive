#!/usr/bin/env python3
"""
Experiment: Cycle 2616 - The Inference
Goal: Simulate an LLM reasoning loop to determine agent strategy.
"""

import sys
import random
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2615_prompt import generate_context_prompt
    from cycle2602_hive import Vector2, HiveAgent
except ImportError:
    sys.exit(1)

def mock_llm_inference(prompt: str) -> str:
    """
    Simulates an LLM deciding on a strategy based on the prompt.
    In a real system, this would call an API.
    """
    if "converging" in prompt:
        # If converging but far, maybe signal?
        if "Distance to Objective" in prompt:
            # Extract distance roughly
            lines = prompt.split('\n')
            for line in lines:
                if "Distance" in line:
                    try:
                        dist = float(line.split(':')[1].replace('units.', '').strip())
                        if dist > 50:
                            return "SIGNAL" # Too far, ask for help
                        else:
                            return "CONTINUE" # Close enough
                    except:
                        pass
        return "CONTINUE"
    elif "searching" in prompt:
        if "Nearby Allies: 0" in prompt:
            return "PANIC" # Alone
        else:
            return "REGROUP" # Search together
    
    return "CONTINUE"

def run_test():
    print("Cycle 2616: The Inference - Reasoning Loop")
    
    # Case 1: Far and Converging
    agent1 = HiveAgent("Far-One", Vector2(0,0))
    agent1.known_target = Vector2(100, 100)
    prompt1 = generate_context_prompt(agent1, [], 141.0)
    decision1 = mock_llm_inference(prompt1)
    print(f"Case 1 (Far): {decision1}")
    
    # Case 2: Close and Converging
    agent2 = HiveAgent("Close-One", Vector2(90,90))
    agent2.known_target = Vector2(100, 100)
    prompt2 = generate_context_prompt(agent2, [], 14.0)
    decision2 = mock_llm_inference(prompt2)
    print(f"Case 2 (Close): {decision2}")
    
    # Case 3: Alone and Searching
    agent3 = HiveAgent("Lonely-Boy", Vector2(0,0))
    prompt3 = generate_context_prompt(agent3, [], 999.0)
    decision3 = mock_llm_inference(prompt3)
    print(f"Case 3 (Lonely): {decision3}")
    
    if decision1 == "SIGNAL" and decision2 == "CONTINUE" and decision3 == "PANIC":
        print("SUCCESS: Simulated inference produced expected logical outcomes.")
    else:
        print("FAILURE: Reasoning logic flaw.")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
