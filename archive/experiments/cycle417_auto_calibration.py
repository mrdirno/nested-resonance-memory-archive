"""
Cycle 417: The Self-Correcting Laboratory
Role: The Technician
Responsibility: Detect sensor drift and execute automated calibration routines to maintain system integrity.
"""
import random
import time
import numpy as np

class CalibrationModule:
    def __init__(self):
        self.bias_x = 0.0
        self.bias_y = 0.0
        self.drift_rate = 0.2
        self.calibration_threshold = 0.5
        self.is_calibrating = False

    def apply_drift(self):
        # Simulates environmental drift (e.g. thermal expansion, sensor slip)
        self.bias_x += random.gauss(0, self.drift_rate)
        self.bias_y += random.gauss(0, self.drift_rate)

    def read_sensor(self, true_x, true_y):
        # Returns drifting sensor data
        return true_x + self.bias_x, true_y + self.bias_y

    def check_calibration(self):
        # In a real system, this would involve moving to a known "Home" position
        # and checking the sensor reading.
        # Here, we simulate a "Home Check" at (0,0).
        reading_x, reading_y = self.read_sensor(0, 0)
        error = np.sqrt(reading_x**2 + reading_y**2)
        
        print(f"[DIAGNOSTIC] Home Check Error: {error:.4f}")
        
        if error > self.calibration_threshold:
            return False # Needs calibration
        return True # Healthy

    def recalibrate(self):
        print("[MAINTENANCE] Initiating Auto-Calibration Sequence...")
        self.is_calibrating = True
        
        # Simulate the time cost of calibration
        time.sleep(0.1) 
        
        # "Zero" the sensors (Correct the bias)
        # In reality, this would update an offset variable.
        # Here, we just reset the bias to simulate a successful fix.
        self.bias_x = 0.0
        self.bias_y = 0.0
        
        self.is_calibrating = False
        print("[MAINTENANCE] Calibration Complete. System Nominal.")

def run_experiment():
    print("Cycle 417: Auto-Calibration Test")
    print("===============================")
    
    calibrator = CalibrationModule()
    
    # Simulation Loop
    target_x, target_y = 10.0, 10.0
    
    print("\n--- Phase 1: Normal Operation (With Drift) ---")
    for i in range(15):
        calibrator.apply_drift()
        
        # Perform task
        s_x, s_y = calibrator.read_sensor(target_x, target_y)
        accuracy = np.sqrt((s_x - target_x)**2 + (s_y - target_y)**2)
        
        print(f"Cycle {i}: Sensor Error {accuracy:.4f}")
        
        # Check Health
        if not calibrator.check_calibration():
            print(f"[ALERT] Drift detected at Cycle {i}!")
            calibrator.recalibrate()
            
            # Verify Fix
            s_x_new, s_y_new = calibrator.read_sensor(target_x, target_y)
            new_error = np.sqrt((s_x_new - target_x)**2 + (s_y_new - target_y)**2)
            
            if new_error < 0.1:
                print(f"SUCCESS: Error reduced from {accuracy:.4f} to {new_error:.4f}")
                return
            else:
                print("FAIL: Calibration failed to fix error.")
                return

    print("FAIL: Drift never triggered threshold (Drift rate might be too low).")

if __name__ == "__main__":
    run_experiment()