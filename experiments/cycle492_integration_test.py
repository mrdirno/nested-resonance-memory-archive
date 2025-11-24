"""
Cycle 492: Integration Test
Role: The Integration Engineer
Responsibility: Ensure the Vector class works within the Field.
"""
import sys
import os

sys.path.append(os.getcwd())
from nrm_core.resonance import ResonantField
from nrm_core.vector import Vector

def run_experiment():
    print("Cycle 492: Integration Test")
    print("===========================")
    
    field = ResonantField()
    
    # Mixing Lists and Vectors to test auto-conversion
    field.add_node("A", [1, 0, 0])
    field.add_node("B", Vector([0, 1, 0]))
    
    print("Stimulating with [1, 0, 0]...")
    field.stimulate([1, 0, 0])
    
    active = field.get_active_nodes(threshold=0.1)
    print(f"Active: {active}")
    
    if "A" in active and "B" not in active:
        print("SUCCESS: Vector integration successful.")
    else:
        print("FAIL: Resonance logic broken.")

if __name__ == "__main__":
    run_experiment()
