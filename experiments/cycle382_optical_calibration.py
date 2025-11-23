import numpy as np
import cv2
import random

class CalibrationManager:
    """
    Manages the mapping between 2D pixel coordinates and 3D world coordinates.
    Assumes particles are on a fixed plane (e.g., z=constant).
    """
    def __init__(self, plane_z=50.0):
        self.plane_z = plane_z
        self.homography_matrix = None
        
        # Define 4 known calibration points in World Coordinates (x, y, z)
        # We assume a working area of 100x100 mm centered at (50, 50)
        self.world_points = np.array([
            [0.0, 0.0],      # Bottom-Left
            [100.0, 0.0],    # Bottom-Right
            [100.0, 100.0],  # Top-Right
            [0.0, 100.0]     # Top-Left
        ], dtype=np.float32)
        
        # Corresponding Pixel Coordinates (Simulated)
        # We simulate a camera looking down at the center
        # Image: 640x480. Center: 320, 240.
        # Scale: 1 mm = 4 pixels (approx)
        self.pixel_points = np.array([
            [120.0, 440.0],  # Bottom-Left
            [520.0, 440.0],  # Bottom-Right
            [520.0, 40.0],   # Top-Right
            [120.0, 40.0]    # Top-Left
        ], dtype=np.float32)

    def calibrate(self):
        """
        Computes the Homography Matrix.
        """
        self.homography_matrix, status = cv2.findHomography(self.pixel_points, self.world_points)
        print("Calibration Complete.")
        print("Homography Matrix:\n", self.homography_matrix)

    def pixel_to_world(self, u, v):
        """
        Maps pixel (u, v) to world (x, y) on the calibrated plane.
        """
        if self.homography_matrix is None:
            raise ValueError("Not calibrated!")
            
        # Homogeneous coordinates
        p = np.array([u, v, 1.0])
        
        # Map
        w = np.dot(self.homography_matrix, p)
        
        # Normalize
        x = w[0] / w[2]
        y = w[1] / w[2]
        
        return (x, y, self.plane_z)

def run_experiment():
    print("Cycle 382: Optical Calibration Research")
    print("=======================================")
    
    calib = CalibrationManager(plane_z=50.0)
    calib.calibrate()
    
    print("\nVerifying Accuracy...")
    print(f"{'Pixel (u, v)':<20} | {'Recovered World (x, y)':<25} | {'Expected World':<20} | {'Error (mm)':<10}")
    print("-" * 85)
    
    # Test Points (Interpolated from the known mapping)
    # Center (320, 240) should be (50, 50)
    test_pixels = [
        (320.0, 240.0), # Center
        (120.0, 440.0), # Bottom-Left (Calibration Point)
        (220.0, 340.0), # Mid-Left-ish
        (420.0, 140.0)  # Mid-Right-ish
    ]
    
    # Expected values based on the linear mapping we defined implicitly
    # u = 120 + 4*x  => x = (u - 120) / 4
    # v = 440 - 4*y  => y = (440 - v) / 4
    
    total_error = 0.0
    
    for u, v in test_pixels:
        # Calculate Ground Truth based on our simulation logic
        true_x = (u - 120.0) / 4.0
        true_y = (440.0 - v) / 4.0
        
        # Recover using Homography
        rec_x, rec_y, rec_z = calib.pixel_to_world(u, v)
        
        # Error
        error = np.sqrt((true_x - rec_x)**2 + (true_y - rec_y)**2)
        total_error += error
        
        print(f"({u:.1f}, {v:.1f}){'':<8} | ({rec_x:.2f}, {rec_y:.2f}){'':<13} | ({true_x:.1f}, {true_y:.1f}){'':<8} | {error:.4f}")
        
    avg_error = total_error / len(test_pixels)
    print("-" * 85)
    print(f"Average Reconstruction Error: {avg_error:.4f} mm")
    
    if avg_error < 1.0:
        print("SUCCESS: Calibration Verified.")
    else:
        print("FAIL: Error too high.")

if __name__ == "__main__":
    run_experiment()
