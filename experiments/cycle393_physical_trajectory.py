import numpy as np
import time
import math
from experiments.cycle391_physical_levitation import PhysicalLevitationController

class TrajectoryGenerator:
    """
    Generates target coordinates (x, y, z) as a function of time t.
    """
    @staticmethod
    def circle(t, center, radius, speed):
        """
        Circular trajectory in XY plane.
        """
        angle = speed * t
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        z = center[2]
        return np.array([x, y, z])

    @staticmethod
    def figure_eight(t, center, width, height, speed):
        """
        Figure-8 trajectory (Lemniscate of Bernoulli approximation).
        """
        angle = speed * t
        # Parametric equations for a lemniscate-like figure 8
        scale = width / 2.0
        x = center[0] + scale * math.sin(angle)
        y = center[1] + (height / 2.0) * math.sin(angle) * math.cos(angle)
        z = center[2]
        return np.array([x, y, z])

    @staticmethod
    def spiral(t, center, r_start, r_end, duration, speed):
        """
        Spiral trajectory (Archimedean).
        """
        progress = min(t / duration, 1.0)
        current_radius = r_start + (r_end - r_start) * progress
        angle = speed * t
        x = center[0] + current_radius * math.cos(angle)
        y = center[1] + current_radius * math.sin(angle)
        z = center[2]
        return np.array([x, y, z])

class TrajectoryController(PhysicalLevitationController):
    def __init__(self):
        super().__init__()
        self.start_time = 0
        self.trajectory_type = "circle"
        
    def run_trajectory(self, type="circle", duration=20):
        print(f"[TRAJECTORY] Starting {type} trajectory for {duration}s...")
        self.trajectory_type = type
        self.is_running = True
        self.start_time = time.time()
        
        # Enable Traps
        self.serial.send_command("ENABLE")
        self.serial.send_command("HOME")
        time.sleep(1)
        
        center = np.array([50.0, 50.0, 20.0])
        
        try:
            while self.is_running:
                t = time.time() - self.start_time
                if t > duration:
                    print("[TRAJECTORY] Duration complete.")
                    break
                
                # 1. UPDATE TARGET
                if type == "circle":
                    self.target_pos = TrajectoryGenerator.circle(t, center, radius=20, speed=1.0)
                elif type == "figure8":
                    self.target_pos = TrajectoryGenerator.figure_eight(t, center, width=40, height=20, speed=1.0)
                elif type == "spiral":
                    self.target_pos = TrajectoryGenerator.spiral(t, center, r_start=5, r_end=30, duration=duration, speed=2.0)
                
                # 2. SENSE
                ret, frame = self.cam.read()
                if not ret:
                    print("[ERROR] Camera read failed.")
                    break
                
                self.frame_count += 1
                
                # 3. MAP
                detections = self.detector.detect(frame)
                world_pos = None
                if detections:
                    pixel_pos = detections[0]
                    world_pos_2d = self.calib.pixel_to_world(pixel_pos[0], pixel_pos[1])
                    world_pos = np.array([world_pos_2d[0], world_pos_2d[1], self.current_pos[2]])
                    self.current_pos = world_pos
                
                # 4. SAFETY
                if not self.safety_check(world_pos):
                    self.serial.send_command("DISABLE")
                    break
                
                # 5. PLAN & ACT
                if world_pos is not None:
                    error = self.target_pos - world_pos
                    dt = 0.05
                    correction = self.pid.update(error, dt)
                    trap_pos = self.target_pos + correction
                    
                    cmd = f"MOVE {trap_pos[0]:.2f} {trap_pos[1]:.2f} {trap_pos[2]:.2f}"
                    self.serial.send_command(cmd)
                    
                    # Log Tracking Error
                    tracking_error = np.linalg.norm(error)
                    print(f"[{t:.1f}s] Tgt: {self.target_pos[:2]} | Act: {world_pos[:2]} | Err: {tracking_error:.2f}mm")
                else:
                    print(f"[{t:.1f}s] Searching...")
                    # If lost, move to target anyway (feedforward)
                    cmd = f"MOVE {self.target_pos[0]:.2f} {self.target_pos[1]:.2f} {self.target_pos[2]:.2f}"
                    self.serial.send_command(cmd)
                
                # Simulation Limit
                if self.frame_count >= 200: # Allow longer run for trajectory
                     print("[STOP] Simulation limit reached.")
                     break

                time.sleep(0.05)
                
        except KeyboardInterrupt:
            print("[STOP] Interrupted by user.")
        finally:
            print("[SHUTDOWN] Disabling Traps.")
            self.serial.send_command("DISABLE")
            self.cam.release()
            self.serial.close()

if __name__ == "__main__":
    controller = TrajectoryController()
    # Test Circle
    controller.run_trajectory(type="circle", duration=10)
