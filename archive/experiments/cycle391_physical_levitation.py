import cv2
import numpy as np
import sys
import time
import json
import os
from experiments.cycle385_physical_camera import get_camera, PhysicalCamera
from experiments.cycle386_serial_integration import get_serial, PhysicalSerial
from experiments.cycle382_optical_calibration import CalibrationManager
from experiments.cycle381_optical_grounding import ParticleDetector
from experiments.cycle387_closed_loop_levitation import PIDController

class PhysicalLevitationController:
    def __init__(self):
        print("[INIT] Initializing Physical Levitation Controller...")
        
        # 1. Initialize Hardware
        self.cam = get_camera()
        self.serial = get_serial()
        
        # 2. Initialize Perception & Calibration
        self.detector = ParticleDetector()
        self.calib = CalibrationManager() # Auto-loads calibration_matrix.npy
        
        # 3. Initialize Control
        self.pid = PIDController(kp=0.1, ki=0.0, kd=0.05)
        self.load_config()
        
        # 4. State
        self.target_pos = np.array([50.0, 50.0, 20.0]) # Center of 100x100mm workspace, 20mm height
        self.current_pos = np.array([50.0, 50.0, 20.0])
        self.is_running = False
        self.frame_count = 0
        
        # 5. Safety Watchdog
        self.frames_without_lock = 0
        self.MAX_LOSS_OF_LOCK = 10 # Frames
        self.SAFE_VOLUME = [[0, 100], [0, 100], [0, 50]] # mm [x_min, x_max], ...

    def safety_check(self, detected_pos):
        """
        Returns True if safe to proceed, False if emergency stop needed.
        """
        # Check 1: Loss of Lock
        if detected_pos is None:
            self.frames_without_lock += 1
            if self.frames_without_lock > self.MAX_LOSS_OF_LOCK:
                print(f"[EMERGENCY] LOSS OF LOCK for {self.frames_without_lock} frames!")
                return False
            return True # Tolerating temporary loss
        
        self.frames_without_lock = 0 # Reset counter
        
        # Check 2: Excursion Limit
        x, y, z = detected_pos
        if not (self.SAFE_VOLUME[0][0] <= x <= self.SAFE_VOLUME[0][1] and
                self.SAFE_VOLUME[1][0] <= y <= self.SAFE_VOLUME[1][1] and
                self.SAFE_VOLUME[2][0] <= z <= self.SAFE_VOLUME[2][1]):
            print(f"[EMERGENCY] EXCURSION LIMIT EXCEEDED: {detected_pos}")
            return False
            
        return True

    def load_config(self, filename="pid_config.json"):
        """Loads PID configuration from a JSON file."""
        if os.path.exists(filename):
            try:
                with open(filename, 'r') as f:
                    config = json.load(f)
                self.pid.kp = config.get("kp", self.pid.kp)
                self.pid.ki = config.get("ki", self.pid.ki)
                self.pid.kd = config.get("kd", self.pid.kd)
                print(f"[CONFIG] Loaded PID Config: Kp={self.pid.kp}, Ki={self.pid.ki}, Kd={self.pid.kd}")
            except Exception as e:
                print(f"[CONFIG] Error loading config: {e}")
        else:
            print("[CONFIG] No config file found. Using defaults.")

    def run(self):
        print("[START] Starting Control Loop...")
        self.is_running = True
        
        # Enable Traps
        self.serial.send_command("ENABLE")
        self.serial.send_command("HOME")
        time.sleep(1)
        
        try:
            while self.is_running:
                # 1. SENSE
                ret, frame = self.cam.read()
                if not ret:
                    print("[ERROR] Camera read failed.")
                    break
                
                self.frame_count += 1
                
                # 2. MAP
                # Detect particle in pixel space
                detections = self.detector.detect(frame)
                
                world_pos = None
                if detections:
                    pixel_pos = detections[0] # Take first detected particle
                    
                    # CalibrationManager.pixel_to_world expects (u, v)
                    world_pos_2d = self.calib.pixel_to_world(pixel_pos[0], pixel_pos[1])
                    # We assume Z is detected via focus or fixed. 
                    # For single camera, Z is unobservable without size change or focus.
                    # We will assume Z is at target height for control purposes (2D servoing).
                    world_pos = np.array([world_pos_2d[0], world_pos_2d[1], self.current_pos[2]])
                    self.current_pos = world_pos
                
                # 3. SAFETY
                if not self.safety_check(world_pos):
                    self.serial.send_command("DISABLE")
                    break
                
                # 4. PLAN
                if world_pos is not None:
                    error = self.target_pos - world_pos
                    dt = 0.05 # Approximate loop time
                    
                    # Compute Correction (Vector)
                    correction = self.pid.update(error, dt)
                    
                    # Apply Correction to Trap Position
                    trap_pos = self.target_pos + correction
                    
                    trap_x = trap_pos[0]
                    trap_y = trap_pos[1]
                    trap_z = trap_pos[2]
                    
                    # 5. ACT
                    cmd = f"MOVE {trap_x:.2f} {trap_y:.2f} {trap_z:.2f}"
                    self.serial.send_command(cmd)
                    
                    print(f"[{self.frame_count}] Pos: {world_pos[:2]} | Err: {error[:2]} | Cmd: {cmd}")
                else:
                    print(f"[{self.frame_count}] Searching...")
                
                # Simulation Limit
                if self.frame_count >= 50:
                    print("[STOP] Simulation limit reached.")
                    break
                    
                time.sleep(0.05) # 20Hz Loop
                
        except KeyboardInterrupt:
            print("[STOP] Interrupted by user.")
        finally:
            print("[SHUTDOWN] Disabling Traps.")
            self.serial.send_command("DISABLE")
            self.cam.release()
            self.serial.close()

if __name__ == "__main__":
    controller = PhysicalLevitationController()
    controller.run()
