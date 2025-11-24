"""
Hello Resonance: A Basic NRM Example
"""
from nrm_core.resonance import ResonantField
from nrm_core.vector import Vector

def main():
    print("Initializing Resonant Field...")
    field = ResonantField()
    
    # Define some simple vectors (orthogonality simulation)
    # [Animal, Machine, Pet]
    v_cat = Vector([1.0, 0.0, 1.0])
    v_dog = Vector([1.0, 0.0, 1.0])
    v_car = Vector([0.0, 1.0, 0.0])
    
    field.add_node("Cat", v_cat)
    field.add_node("Dog", v_dog)
    field.add_node("Car", v_car)
    
    print("Nodes added: Cat, Dog, Car")
    
    # Stimulate with 'Cat-like' features
    stimulus = Vector([1.0, 0.0, 0.0]) # 'Animal' feature
    print(f"Stimulating with {stimulus}...")
    
    field.stimulate(stimulus)
    
    active = field.get_active_nodes(threshold=0.1)
    print("\nActive Nodes:")
    for node_id, energy in active.items():
        print(f"  - {node_id}: {energy:.4f}")
        
    if "Cat" in active and "Dog" in active and "Car" not in active:
        print("\nSUCCESS: Resonance detected correctly (Animals resonated, Car did not).")
    else:
        print("\nFAILURE: Resonance logic error.")

if __name__ == "__main__":
    main()
