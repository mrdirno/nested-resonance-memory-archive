"""
Cycle 478: Library Test
Role: The Quality Assurance
Responsibility: Verify the new NRM Core library.
"""
import sys
import os

# Add root to path so we can import nrm_core
sys.path.append(os.getcwd())

from nrm_core.resonance import ResonantField

def run_experiment():
    print("Cycle 478: NRM Core Library Test")
    print("================================")
    
    field = ResonantField()
    
    # Define concepts as vectors (simplified)
    # [IsAnimal, IsMachine, IsBig]
    cat = [1.0, 0.0, 0.0]
    robot = [0.0, 1.0, 0.0]
    tiger = [1.0, 0.0, 1.0]
    tank = [0.0, 1.0, 1.0]
    
    field.add_node("cat", cat)
    field.add_node("robot", robot)
    field.add_node("tiger", tiger)
    field.add_node("tank", tank)
    
    print("Stimulating with [IsAnimal, IsBig] (Big Animal)...")
    query = [1.0, 0.0, 1.0]
    field.stimulate(query)
    
    active = field.get_active_nodes(threshold=0.1)
    # Sort by energy desc
    sorted_active = sorted(active.items(), key=lambda x: x[1], reverse=True)
    
    for nid, energy in sorted_active:
        print(f"Node: {nid} | Energy: {energy:.4f}")
        
    # Tiger should be top (Perfect match 1.0 + magnitude stuff)
    # Actually similarity: dot(A, A) / (mag*mag) = 1.0
    
    top_match = sorted_active[0][0]
    if top_match == "tiger":
        print("SUCCESS: 'Tiger' resonated most strongly.")
    else:
        print(f"FAIL: Expected 'tiger', got '{top_match}'")

if __name__ == "__main__":
    run_experiment()
