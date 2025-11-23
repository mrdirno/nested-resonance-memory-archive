import time
import numpy as np
import cv2
import sys

# Attempt imports from previous cycles
try:
    from experiments.cycle385_physical_camera import get_camera
    from experiments.cycle386_serial_integration import get_serial
    from experiments.cycle381_optical_grounding import ParticleDetector
    from experiments.cycle382_optical_calibration import CalibrationManager
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running from the repo root: python3 -m experiments.cycle387_closed_loop_levitation")
    sys.exit(1)

class PIDController:
    def __init__(self, kp=1.0, ki=0.0, kd=0.0):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = np.array([0.0, 0.0, 0.0])
        self.integral = np.array([0.0, 0.0, 0.0])

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output

class LevitationController:
    def __init__(self, target_pos):
        self.target_pos = np.array(target_pos)
        
        # Initialize Hardware (with fallbacks)
        self.cam = get_camera()
        self.ser = get_serial()
        
        # Initialize Logic
        self.detector = ParticleDetector()
        self.calib = CalibrationManager() # Assumes z=50mm plane
        # Initialize default calibration for simulation
        # In a real scenario, we would load from file or run calibration routine.
        # Here we set a 1:1 mapping centered at 320,240 -> 50,50
        # 640px = 100mm -> 1px = 0.156mm
        scale = 100.0 / 640.0
        # H = [[scale, 0, -320*scale + 50], [0, scale, -240*scale + 50], [0, 0, 1]]
        H = np.array([
            [scale, 0, -320*scale + 50],
            [0, scale, -240*scale + 50],
            [0, 0, 1]
        ])
        self.calib.homography_matrix = H
        # self.calib.is_calibrated = True # Not used by class
        
        self.pid = PIDController(kp=0.5, ki=0.0, kd=0.1)
        
        self.running = True
        self.dt = 0.1 # Loop time estimate

    def run(self, steps=100):
        print(f"Starting Levitation Loop. Target: {self.target_pos}")
        print("-" * 80)
        print(f"{'Step':<5} | {'Observed (mm)':<20} | {'Error (mm)':<20} | {'Command':<20}")
        print("-" * 80)

        for i in range(steps):
            start_time = time.time()
            
            # 1. SENSE
            ret, frame = self.cam.read()
            if not ret:
                print("Camera failed to read frame.")
                break
                
            detections = self.detector.detect(frame)
            
            if not detections:
                print(f"{i:<5} | {'NO DETECTION':<20} | {'N/A':<20} | {'HOLD':<20}")
                continue
                
            # Use first detection
            u, v = detections[0]
            
            # 2. MAP (Pixel -> World)
            # CalibrationManager returns (x, y, z)
            obs_x, obs_y, obs_z = self.calib.pixel_to_world(u, v)
            obs_pos = np.array([obs_x, obs_y, obs_z])
            
            # 3. PLAN (Error Calculation)
            error = self.target_pos - obs_pos
            
            # 4. ACT (PID -> Serial)
            # In a real trap, we move the trap *towards* the error to pull the particle?
            # Or if error is (Target - Current), we want to move particle by +Error.
            # So we move Trap to Current + Correction?
            # Let's assume Trap Position = Current Position + PID Output
            correction = self.pid.update(error, self.dt)
            new_trap_pos = obs_pos + correction
            
            # Clamp to workspace (0-100mm)
            new_trap_pos = np.clip(new_trap_pos, 0, 100)
            
            cmd = f"MOVE {new_trap_pos[0]:.2f} {new_trap_pos[1]:.2f} {new_trap_pos[2]:.2f}"
            self.ser.write(f"{cmd}\n".encode('utf-8'))
            
            # Log
            error_mag = np.linalg.norm(error)
            obs_str = f"({obs_x:.1f}, {obs_y:.1f})"
            err_str = f"{error_mag:.2f}"
            print(f"{i:<5} | {obs_str:<20} | {err_str:<20} | {cmd:<20}")
            
            # Timing
            elapsed = time.time() - start_time
            sleep_time = max(0, self.dt - elapsed)
            time.sleep(sleep_time)

        self.shutdown()

    def shutdown(self):
        print("Shutting down...")
        self.ser.write(b"DISABLE\n")
        self.cam.release()
        self.ser.close()

if __name__ == "__main__":
    # Target center of workspace
    target = [50.0, 50.0, 50.0]
    controller = LevitationController(target)
    controller.run(steps=50)
