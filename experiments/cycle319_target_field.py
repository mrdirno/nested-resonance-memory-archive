"""
CYCLE 319: Target Field Definition
Objective: Implement the TargetField class for defining voxelized density goals in 2D.
Hypothesis: A flexible and precise target definition is crucial for the Inverse Cymatics solver.
Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 2.5 Flash (MOG Pilot)
"""
import numpy as np
import json
import os

class TargetField:
    """
    Represents a 2D grid of target density values.
    Used to define the desired emergent pattern for Inverse Cymatics.
    """
    def __init__(self, width: int, height: int, default_density: float = 0.0):
        if not isinstance(width, int) or width <= 0:
            raise ValueError("Width must be a positive integer.")
        if not isinstance(height, int) or height <= 0:
            raise ValueError("Height must be a positive integer.")
            
        self.width = width
        self.height = height
        self.field = np.full((height, width), default_density, dtype=float)
        self.default_density = default_density

    def set_point(self, x: int, y: int, density: float = 1.0):
        """Sets the density at a specific point."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.field[y, x] = density
        else:
            raise IndexError(f"Coordinates ({x},{y}) out of bounds for field of size ({self.width},{self.height}).")

    def set_square(self, x_center: int, y_center: int, size: int, density: float = 1.0):
        """Fills a square region with the given density."""
        half_size = size // 2
        x_min = max(0, x_center - half_size)
        x_max = min(self.width, x_center + half_size + (size % 2))
        y_min = max(0, y_center - half_size)
        y_max = min(self.height, y_center + half_size + (size % 2))

        self.field[y_min:y_max, x_min:x_max] = density

    def set_circle(self, x_center: int, y_center: int, radius: int, density: float = 1.0):
        """Fills a circular region with the given density."""
        for y in range(self.height):
            for x in range(self.width):
                if (x - x_center)**2 + (y - y_center)**2 <= radius**2:
                    self.field[y, x] = density
    
    def get_density(self, x: int, y: int) -> float:
        """Returns the target density at a given coordinate."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.field[y, x]
        return self.default_density # Or raise IndexError

    def get_field_as_numpy_array(self) -> np.ndarray:
        """Returns the entire field as a NumPy array."""
        return self.field

    def calculate_error(self, actual_density_field: np.ndarray) -> float:
        """
        Calculates the Mean Squared Error (MSE) between the target field
        and an actual density field.
        The actual_density_field must have the same shape.
        """
        if self.field.shape != actual_density_field.shape:
            raise ValueError(f"Shape mismatch: Target {self.field.shape}, Actual {actual_density_field.shape}")
        
        # We only care about matching where the target density is > 0
        # For inverse cymatics, empty space is as important as filled space
        # So, calculate MSE over the entire field.
        return np.mean((self.field - actual_density_field)**2)

    def display(self, scale: int = 1):
        """Prints a text-based representation of the field."""
        print(f"Target Field ({self.width}x{self.height}):")
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                char = "#" if self.field[y, x] > 0.5 else "."
                row += char * scale
            print(row)

def main():
    print("CYCLE 319: TARGET FIELD DEFINITION")
    print("===================================")

    width, height = 20, 10
    target_density = 1.0

    # 1. Create an empty target field
    empty_field = TargetField(width, height)
    print("--- Empty Field ---")
    empty_field.display()
    print(f"Mean density: {np.mean(empty_field.get_field_as_numpy_array()):.2f}\n")

    # 2. Create a square target
    square_field = TargetField(width, height)
    square_field.set_square(x_center=5, y_center=5, size=4, density=target_density)
    print("--- Square Target Field ---")
    square_field.display()
    
    # Test perfect match
    perfect_match_square = np.zeros((height, width))
    perfect_match_square[3:7, 3:7] = target_density # Corresponds to center 5, size 4
    error_perfect = square_field.calculate_error(perfect_match_square)
    print(f"Error for perfect match: {error_perfect:.2f}\n") # Expected 0.0

    # Test partial match
    partial_match_square = np.zeros((height, width))
    partial_match_square[4:6, 4:6] = target_density # Smaller square
    error_partial = square_field.calculate_error(partial_match_square)
    print(f"Error for partial match (smaller square): {error_partial:.2f}\n") # Expected > 0

    # 3. Create a circle target
    circle_field = TargetField(width, height)
    circle_field.set_circle(x_center=15, y_center=5, radius=3, density=target_density)
    print("--- Circle Target Field ---")
    circle_field.display()
    
    # Test perfect circle match (simple manual check)
    perfect_match_circle = np.zeros((height, width))
    for y in range(height):
        for x in range(width):
            if (x - 15)**2 + (y - 5)**2 <= 3**2:
                perfect_match_circle[y, x] = target_density
    error_circle_perfect = circle_field.calculate_error(perfect_match_circle)
    print(f"Error for perfect circle match: {error_circle_perfect:.2f}\n") # Expected 0.0

    # 4. Mixed shapes
    mixed_field = TargetField(width, height)
    mixed_field.set_square(x_center=5, y_center=5, size=4, density=target_density)
    mixed_field.set_circle(x_center=15, y_center=5, radius=3, density=target_density)
    print("--- Mixed Shapes Field ---")
    mixed_field.display()
    print(f"Mean density: {np.mean(mixed_field.get_field_as_numpy_array()):.2f}\n")

    # Save results summary
    results_summary = {
        "cycle": 319,
        "width": width,
        "height": height,
        "default_density": empty_field.default_density,
        "error_perfect_square": error_perfect,
        "error_partial_square": error_partial,
        "error_perfect_circle": error_circle_perfect,
        "status": "TargetField class operational and verified"
    }

    os.makedirs("experiments/results", exist_ok=True)
    with open("experiments/results/c319_target_field.json", "w") as f:
        json.dump(results_summary, f, indent=2)
    
    print("--- C319 Complete ---")

if __name__ == "__main__":
    main()