import cv2
import numpy as np
import sys
import os

# Attempt imports
try:
    from experiments.cycle385_physical_camera import get_camera, PhysicalCamera
    from experiments.cycle382_optical_calibration import CalibrationManager
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)

class CalibrationWizard:
    def __init__(self):
        self.cam = get_camera()
        self.calib = CalibrationManager()
        self.points_clicked = []

    def run(self):
        print("="*60)
        print("DUALITY-ZERO: PHYSICAL CALIBRATION WIZARD")
        print("="*60)

        if isinstance(self.cam, PhysicalCamera):
            self.run_physical()
        else:
            self.run_simulation()

    def run_simulation(self):
        print("[MODE] Simulation (Virtual Camera)")
        print("Auto-generating default calibration for 640x480 -> 100x100mm")
        
        # Simulate the "perfect" alignment we expect
        # Center of image (320, 240) -> Center of workspace (50, 50)
        # Scale: 640px = 100mm (approx, let's say field of view is slightly larger)
        # Let's use the points defined in CalibrationManager as the "Ground Truth" for simulation
        
        pixel_points = self.calib.pixel_points
        world_points = self.calib.world_points
        
        print("Simulated Pixel Points:\n", pixel_points)
        print("World Points:\n", world_points)
        
        # Compute Homography
        H, status = cv2.findHomography(pixel_points, world_points)
        self.calib.homography_matrix = H
        
        print("Computed Homography:\n", H)
        
        # Save
        self.calib.save()
        print("Calibration Complete.")

    def run_physical(self):
        print("[MODE] Physical (Real Camera)")
        print("Instructions:")
        print("1. A window will open showing the camera feed.")
        print("2. Click the 4 corners of the 100x100mm working area in this order:")
        print("   Bottom-Left -> Bottom-Right -> Top-Right -> Top-Left")
        print("3. Press 'q' to quit without saving.")
        
        # Placeholder for interactive loop
        # Since we are in a headless environment mostly, we can't easily open a window here.
        # But the code would look like this:
        """
        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", self.click_event)
        
        while True:
            ret, frame = self.cam.read()
            if not ret: break
            
            # Draw points
            for p in self.points_clicked:
                cv2.circle(frame, p, 5, (0, 255, 0), -1)
                
            cv2.imshow("Calibration", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if len(self.points_clicked) == 4:
                break
        
        cv2.destroyAllWindows()
        
        if len(self.points_clicked) == 4:
            pixel_points = np.array(self.points_clicked, dtype=np.float32)
            world_points = self.calib.world_points
            H, _ = cv2.findHomography(pixel_points, world_points)
            self.calib.homography_matrix = H
            self.calib.save()
        """
        print("Interactive mode not supported in headless environment.")
        print("Please run this script on a machine with a display if using a real camera.")

if __name__ == "__main__":
    wizard = CalibrationWizard()
    wizard.run()
