"""
CYCLE 322: Shape Holding Test
Objective: Validate if the Inverse Cymatics Solver can converge to and HOLD a target shape (Square, Circle).
Hypothesis: The Genetic Algorithm will find a stable emitter configuration that minimizes error for specific geometries.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from experiments.cycle319_target_field import TargetField
from experiments.cycle320_forward_cymatics_2d import Emitter, CymaticSimulation
from experiments.cycle321_inverse_cymatics_ga import InverseCymaticsGA

def run_shape_test(shape_name: str, width: int, height: int, population_size: int, generations: int):
    print(f"\n--- Testing Shape: {shape_name} ---")
    
    target_field = TargetField(width, height)
    
    if shape_name == "Square":
        target_field.set_square(x_center=width//2, y_center=height//2, size=min(width, height)//2, density=1.0)
    elif shape_name == "Circle":
        target_field.set_circle(x_center=width//2, y_center=height//2, radius=min(width, height)//4, density=1.0)
    else:
        raise ValueError("Unknown shape")

    print("Target Field:")
    target_field.display(scale=1)

    solver = InverseCymaticsGA(target_field, population_size=population_size, mutation_rate=0.1, num_emitters=6)
    best_individual = solver.evolve(generations=generations)
    
    print(f"Best Error ({shape_name}): {best_individual['error']:.4f}")
    
    # Verify the result
    best_emitters = [Emitter(**p) for p in best_individual['genome']]
    sim = CymaticSimulation(width, height, best_emitters)
    generated_field = sim.calculate_density_field()
    
    print(f"Generated Field ({shape_name}):")
    # Use TargetField for display convenience
    display_field = TargetField(width, height)
    display_field.field = generated_field
    display_field.display(scale=1)
    
    return best_individual['error'], generated_field

def main():
    print("CYCLE 322: SHAPE HOLDING TEST")
    print("=============================")

    width, height = 40, 20
    pop_size = 50
    generations = 50

    # 1. Test Square
    square_error, square_field = run_shape_test("Square", width, height, pop_size, generations)

    # 2. Test Circle
    circle_error, circle_field = run_shape_test("Circle", width, height, pop_size, generations)

    # Save results
    results = {
        "cycle": 322,
        "square_error": square_error,
        "circle_error": circle_error,
        "parameters": {
            "width": width,
            "height": height,
            "population": pop_size,
            "generations": generations
        },
        "status": "Shape Holding Test Complete"
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c322_shape_holding.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n--- C322 Complete ---")
    if square_error < 0.2 and circle_error < 0.2:
        print(">>")
        print("SUCCESS: Solver effectively holds shapes.")
    else:
        print(">>")
        print("PARTIAL/FAILURE: Convergence errors remain high. Higher resolution or more emitters may be needed.")

if __name__ == "__main__":
    main()
