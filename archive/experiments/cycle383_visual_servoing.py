import numpy as np
import cv2
import math
import time

# --- Components from Previous Cycles ---

class VirtualCamera:
    def __init__(self, width=640, height=480, noise_level=0.0):
        self.width = width
        self.height = height
        self.noise_level = noise_level
        self.particles = [] 
        # Intrinsic Matrix (Approximate for 640x480)
        self.K = np.array([[600, 0, 320], [0, 600, 240], [0, 0, 1]], dtype=np.float32)

    def update_particles(self, particles):
        self.particles = particles

    def project_point(self, x, y, z):
        # Simple projection for simulation: u = fx * x/z + cx, v = fy * y/z + cy
        # We assume camera is at some height looking down.
        # But for this simulation, we'll use the inverse of the CalibrationManager's logic
        # to ensure consistency. 
        # Let's just use the CalibrationManager's pixel_points interpolation for simplicity
        # since we defined a linear mapping in C382.
        # u = 120 + 4*x
        # v = 440 - 4*y
        u = 120.0 + 4.0 * x
        v = 440.0 - 4.0 * y
        return int(u), int(v)

    def capture(self):
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        for p in self.particles:
            x, y, z = p
            u, v = self.project_point(x, y, z)
            # Draw particle
            cv2.circle(img, (u, v), 5, (255, 255, 255), -1)
        
        img = cv2.GaussianBlur(img, (5, 5), 0)
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, img.shape)
            img_float = img.astype(np.float32) + noise
            img = np.clip(img_float, 0, 255).astype(np.uint8)
        return img

class ParticleDetector:
    def detect(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detected_positions = []
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = M["m10"] / M["m00"]
                cY = M["m01"] / M["m00"]
                detected_positions.append((cX, cY))
        return detected_positions

class CalibrationManager:
    def __init__(self, plane_z=50.0):
        self.plane_z = plane_z
        # Hardcoded Homography from C382 for stability
        # H maps Pixel -> World
        # Based on: (120,440)->(0,0), (520,440)->(100,0), (520,40)->(100,100), (120,40)->(0,100)
        pts_src = np.array([[120, 440], [520, 440], [520, 40], [120, 40]], dtype=np.float32)
        pts_dst = np.array([[0, 0], [100, 0], [100, 100], [0, 100]], dtype=np.float32)
        self.H, _ = cv2.findHomography(pts_src, pts_dst)

    def pixel_to_world(self, u, v):
        p = np.array([u, v, 1.0])
        w = np.dot(self.H, p)
        x = w[0] / w[2]
        y = w[1] / w[2]
        return (x, y, self.plane_z)

# --- New Simulation Components ---

class PhysicsEngine:
    def __init__(self, dt=0.1):
        self.particle_pos = np.array([10.0, 10.0, 50.0]) # Start off-center
        self.trap_pos = np.array([10.0, 10.0, 50.0])
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.dt = dt
        self.stiffness = 0.5
        self.damping = 0.8

    def update(self):
        # F = -k(x - x_trap) - c*v
        force = -self.stiffness * (self.particle_pos - self.trap_pos) - self.damping * self.velocity
        accel = force # Mass = 1
        self.velocity += accel * self.dt
        self.particle_pos += self.velocity * self.dt
        return self.particle_pos

class VisualServoController:
    def __init__(self, target_pos):
        self.target_pos = np.array(target_pos)
        self.kp = 0.5 # Proportional Gain
        
    def update(self, current_pos):
        # Error = Target - Current
        error = self.target_pos - current_pos
        # Control Output (Trap Position)
        # In a real trap, we move the trap towards the target, dragging the particle.
        # Or we place the trap *at* the target + offset?
        # Simple P-Control: Move trap in direction of error
        # Actually, if we want particle at Target, we should put Trap at Target + PID correction?
        # Simplest: Trap = Target. 
        # But Visual Servoing usually means: Trap += Gain * Error
        # Let's try: Trap = Current_Particle + Gain * Error + Integral...
        # For this simulation, let's just move the trap towards the target based on error.
        
        # Strategy: The Trap *is* the actuator. 
        # If we want particle at T, and it's at C.
        # We pull it. Trap = C + Gain * (T - C).
        # If Gain is high, Trap jumps to T.
        # If Gain is low, Trap leads the particle.
        
        control_signal = current_pos + self.kp * error
        return control_signal

def run_simulation():
    print("Cycle 383: Closed Loop Control / Visual Servoing")
    print("================================================")
    
    # Init
    cam = VirtualCamera(noise_level=2.0)
    detector = ParticleDetector()
    calib = CalibrationManager()
    physics = PhysicsEngine()
    
    target = np.array([80.0, 80.0, 50.0])
    controller = VisualServoController(target)
    
    print(f"Target: {target}")
    print(f"Start:  {physics.particle_pos}")
    print("-" * 80)
    print(f"{'Step':<5} | {'Particle (x, y)':<20} | {'Trap (x, y)':<20} | {'Error':<10} | {'True Pos':<20}")
    print("-" * 80)
    
    for i in range(200):
        # 1. Physics Step
        true_pos = physics.update()
        
        # 2. Sensing (Camera -> Detector -> Calibration)
        cam.update_particles([true_pos])
        frame = cam.capture()
        detections = detector.detect(frame)
        
        if not detections:
            print(f"{i:<5} | LOST TRACKING")
            continue
            
        u, v = detections[0]
        obs_x, obs_y, _ = calib.pixel_to_world(u, v)
        obs_pos = np.array([obs_x, obs_y, 50.0])
        
        # 3. Control
        new_trap_pos = controller.update(obs_pos)
        physics.trap_pos = new_trap_pos
        
        # 4. Log
        error = np.linalg.norm(target - obs_pos)
        print(f"{i:<5} | {f'({obs_x:.1f}, {obs_y:.1f})':<20} | {f'({new_trap_pos[0]:.1f}, {new_trap_pos[1]:.1f})':<20} | {error:.4f} | True: ({true_pos[0]:.1f}, {true_pos[1]:.1f})")
        
        if error < 1.0:
            print("-" * 60)
            print(f"Converged in {i} steps.")
            print("SUCCESS: Visual Servoing Verified.")
            return

    print("FAIL: Did not converge.")

if __name__ == "__main__":
    run_simulation()
