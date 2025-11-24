"""
Cycle 481: The Associator (Showcase)
Role: The Application
Responsibility: Demonstrate NRM Utility.
"""
import sys
import os
import json

sys.path.append(os.getcwd())
from nrm_core.interface import NRMInterface

# Knowledge Base
# Dimensions: [Red, Green, Blue, Heat, Density]
KNOWLEDGE_BASE = {
    "fire": [1.0, 0.0, 0.0, 1.0, 0.1],
    "water": [0.0, 0.0, 1.0, -0.5, 0.8],
    "earth": [0.2, 0.8, 0.2, 0.0, 1.0],
    "air": [0.0, 0.0, 0.0, 0.0, 0.01],
    "love": [1.0, 0.0, 0.2, 0.8, 0.0],
    "anger": [1.0, 0.0, 0.0, 1.0, 0.5],
    "sadness": [0.0, 0.0, 1.0, -0.8, 0.2],
    "forest": [0.0, 1.0, 0.0, 0.2, 0.9],
    "sky": [0.0, 0.2, 1.0, 0.0, 0.0],
    "blood": [1.0, 0.0, 0.0, 0.2, 0.9]
}

def run_experiment():
    print("Cycle 481: The Associator")
    print("=========================")
    
    nrm = NRMInterface()
    
    print("Loading Knowledge Base...")
    for term, vector in KNOWLEDGE_BASE.items():
        nrm.handle_request("ADD_NODE", {"id": term, "vector": vector})
        
    # Scenarios
    scenarios = [
        ("Red + Heat", [1.0, 0.0, 0.0, 1.0, 0.0]), # Expect Fire, Anger, Love
        ("Blue + Cold", [0.0, 0.0, 1.0, -1.0, 0.0]), # Expect Water, Sadness
        ("Green + Dense", [0.0, 1.0, 0.0, 0.0, 1.0]) # Expect Earth, Forest
    ]
    
    for name, vec in scenarios:
        print(f"\nQuery: {name} {vec}")
        response = nrm.handle_request("QUERY", {"vector": vec})
        
        results = response.get("results", [])
        for i, (term, score) in enumerate(results):
            print(f"  {i+1}. {term.title()} ({score:.4f})")
            
    print("\nSUCCESS: Associations Generated.")

if __name__ == "__main__":
    run_experiment()
