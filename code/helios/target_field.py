import numpy as np
from PIL import Image

class TargetField:
    def __init__(self, resolution=(100, 100)):
        """
        Initialize the TargetField.
        
        Args:
            resolution (tuple): Grid size (height, width).
        """
        self.resolution = resolution
        self.field = np.zeros(resolution, dtype=float)

    def create_square(self, center, size):
        """
        Create a square target in the field.
        
        Args:
            center (tuple): (y, x) coordinates of the center.
            size (int): Side length of the square.
        """
        y_c, x_c = center
        half_size = size // 2
        
        y_min = max(0, int(y_c - half_size))
        y_max = min(self.resolution[0], int(y_c + half_size))
        x_min = max(0, int(x_c - half_size))
        x_max = min(self.resolution[1], int(x_c + half_size))
        
        self.field[y_min:y_max, x_min:x_max] = 1.0

    def create_circle(self, center, radius):
        """
        Create a circular target in the field.
        
        Args:
            center (tuple): (y, x) coordinates of the center.
            radius (float): Radius of the circle.
        """
        y_c, x_c = center
        y, x = np.ogrid[:self.resolution[0], :self.resolution[1]]
        mask = (y - y_c)**2 + (x - x_c)**2 <= radius**2
        self.field[mask] = 1.0

    def load_image(self, path):
        """
        Load a target from an image file.
        The image is resized to the field resolution and converted to grayscale.
        
        Args:
            path (str): Path to the image file.
        """
        try:
            img = Image.open(path).convert('L')
            img = img.resize((self.resolution[1], self.resolution[0])) # PIL uses (width, height)
            img_data = np.array(img)
            self.field = img_data / 255.0
        except Exception as e:
            print(f"Error loading image: {e}")

    def get_error(self, current_density):
        """
        Calculate the error between the current swarm density and the target field.
        
        Args:
            current_density (np.array): 2D array of the same shape as the field.
            
        Returns:
            float: Mean Squared Error (MSE).
        """
        if current_density.shape != self.resolution:
            raise ValueError(f"Density shape {current_density.shape} does not match field resolution {self.resolution}")
        
        return np.mean((self.field - current_density)**2)

    def visualize(self):
        """
        Return a string representation of the field for console visualization.
        """
        chars = " .:-=+*#%@"
        result = []
        step_y = max(1, self.resolution[0] // 20)
        step_x = max(1, self.resolution[1] // 40) # Aspect ratio correction
        
        for y in range(0, self.resolution[0], step_y):
            row = ""
            for x in range(0, self.resolution[1], step_x):
                val = self.field[y, x]
                char_idx = int(val * (len(chars) - 1))
                row += chars[char_idx]
            result.append(row)
        return "\n".join(result)
