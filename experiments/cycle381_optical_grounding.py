import numpy as np
import time
import random
import math

# Try importing OpenCV, fallback to mock if necessary (but we really need it)
try:
    import cv2
except ImportError:
    print("OpenCV not found. Please install: pip install opencv-python")
    sys.exit(1)

class VirtualCamera:
    """
    Simulates a camera feed looking at the levitation trap.
    Generates synthetic images of particles.
    """
    def __init__(self, width=640, height=480, noise_level=0.0):
        self.width = width
        self.height = height
        self.noise_level = noise_level
        self.particles = [] # List of (x, y, radius)

    def update_particles(self, particles):
        self.particles = particles

    def capture(self):
        """
        Returns a numpy array (image) representing the current view.
        """
        # Black background
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Draw particles
        for p in self.particles:
            x, y, r = p
            # Draw white circle with some blur to simulate glow
            cv2.circle(img, (int(x), int(y)), int(r), (255, 255, 255), -1)
            
        # Add blur (glow effect)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        
        # Add noise
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, img.shape).astype(np.uint8)
            img = cv2.add(img, noise)
            
        return img

class ParticleDetector:
    """
    Computer Vision pipeline to detect particles in the image.
    """
    def __init__(self):
        self.threshold = 50
        
    def detect(self, image):
        """
        Returns list of (x, y) coordinates of detected particles.
        """
        # 1. Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 2. Threshold
        _, thresh = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY)
        
        # 3. Find Contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        detected_positions = []
        
        for c in contours:
            # Calculate Moments
            M = cv2.moments(c)
            if M["m00"] != 0:
                cX = M["m10"] / M["m00"]
                cY = M["m01"] / M["m00"]
                detected_positions.append((cX, cY))
                
        return detected_positions

def run_experiment():
    print("Cycle 381: Optical Grounding Research")
    print("=====================================")
    
    cam = VirtualCamera(width=640, height=480, noise_level=5.0)
    detector = ParticleDetector()
    
    # Test Trajectory: Circle
    center_x, center_y = 320, 240
    radius = 100
    steps = 20
    
    total_error = 0.0
    
    print(f"{'Step':<5} | {'True Pos':<20} | {'Detected Pos':<20} | {'Error':<10}")
    print("-" * 65)
    
    for i in range(steps):
        angle = 2 * math.pi * i / steps
        true_x = center_x + radius * math.cos(angle)
        true_y = center_y + radius * math.sin(angle)
        
        # Update Camera
        cam.update_particles([(true_x, true_y, 5)]) # Radius 5px
        
        # Capture
        frame = cam.capture()
        
        # Detect
        detections = detector.detect(frame)
        
        if not detections:
            print(f"{i:<5} | {f'({true_x:.1f}, {true_y:.1f})':<20} | {'NONE':<20} | {'FAIL':<10}")
            continue
            
        # Assume single particle, take closest
        det_x, det_y = detections[0]
        
        # Calculate Error
        error = math.sqrt((true_x - det_x)**2 + (true_y - det_y)**2)
        total_error += error
        
        print(f"{i:<5} | {f'({true_x:.1f}, {true_y:.1f})':<20} | {f'({det_x:.1f}, {det_y:.1f})':<20} | {error:.4f}")
        
    avg_error = total_error / steps
    print("-" * 65)
    print(f"Average Error: {avg_error:.4f} pixels")
    
    if avg_error < 1.0:
        print("SUCCESS: Optical Grounding Verified.")
    else:
        print("FAIL: Error too high.")

if __name__ == "__main__":
    run_experiment()
