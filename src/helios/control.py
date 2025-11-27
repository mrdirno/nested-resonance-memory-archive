"""
HELIOS Control Module (Gate 8)
The Brain of the Physical Loop.
Integrates Fabricator (Output) and Camera (Input) into a cohesive controller.
Gate 8 Compliant.
"""

import time
import numpy as np
from src.helios.fabricator import Fabricator
from src.helios.camera import Camera

class ClosedLoopController:
    def __init__(self, target_pos=None, kp=0.1, virtual=True):
        """
        Initialize the Closed Loop Controller.
        :param target_pos: Target (x, y) position in normalized coordinates (-1..1).
        :param kp: Proportional gain for the control loop.
        :param virtual: Whether to run in virtual mode (mock hardware).
        """
        self.target = np.array(target_pos) if target_pos is not None else np.array([0.0, 0.0])
        self.kp = kp
        self.fabricator = Fabricator(virtual=virtual)
        self.camera = Camera()
        self.running = False

    def connect(self):
        """Connect to both Camera and Fabricator."""
        print("[CONTROLLER] Connecting to hardware...")
        cam_ok = self.camera.connect()
        fab_ok = self.fabricator.connect()
        
        if cam_ok and fab_ok:
            print("[CONTROLLER] All systems online.")
            return True
        else:
            print(f"[CONTROLLER] Connection failed. Cam: {cam_ok}, Fab: {fab_ok}")
            return False

    def disconnect(self):
        """Disconnect from hardware."""
        self.camera.disconnect()
        self.fabricator.disconnect()
        print("[CONTROLLER] Systems offline.")

    def run_loop(self, duration=10, interval=0.1):
        """
        Execute the control loop.
        :param duration: Total runtime in seconds.
        :param interval: Loop interval in seconds.
        """
        if not self.fabricator.array.connected:
            print("[CONTROLLER] Hardware not connected.")
            return

        self.running = True
        start_time = time.time()
        
        print(f"[CONTROLLER] Starting Control Loop (Duration: {duration}s)...")
        try:
            while self.running and (time.time() - start_time < duration):
                # 1. SENSE
                marker_pos = self.camera.detect_marker()
                
                if marker_pos:
                    current_pos = np.array(marker_pos)
                    
                    # 2. THINK (Error Calculation)
                    error = self.target - current_pos
                    
                    # 3. ACT (Compute Correction)
                    # In a real acoustic levitator, we would adjust the focal point 
                    # of the trap. For this prototype, we compute the 'shift' required.
                    correction = error * self.kp
                    
                    # Apply correction to the fabricator (Conceptual)
                    # self.fabricator.shift_field(correction) 
                    
                    # For validation, we just log the telemetry
                    status_str = f"Pos: {current_pos.round(2)} | Err: {error.round(2)} | Correction: {correction.round(3)}"
                    print(f"[LOOP] {status_str}")
                else:
                    print("[LOOP] No marker detected.")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n[CONTROLLER] Loop interrupted.")
        finally:
            self.running = False
            print("[CONTROLLER] Loop terminated.")

if __name__ == "__main__":
    # Quick Test
    ctrl = ClosedLoopController(virtual=True)
    if ctrl.connect():
        ctrl.run_loop(duration=2)
        ctrl.disconnect()
