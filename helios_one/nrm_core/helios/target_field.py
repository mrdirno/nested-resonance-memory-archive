import numpy as np
from PIL import Image

import numpy as np
from PIL import Image

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

    def load_image(self, path):
        """
        Load a target from an image file.
        The image is resized to the field resolution and converted to grayscale.
        """
        try:
            img = Image.open(path).convert('L')
            img = img.resize((self.width, self.height)) # PIL uses (width, height)
            img_data = np.array(img)
            self.field = img_data / 255.0
        except Exception as e:
            print(f"Error loading image: {e}")
