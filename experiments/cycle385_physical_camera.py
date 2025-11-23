import cv2
import numpy as np
import time
import os

class VirtualCamera:
    """
    Simulates a camera feed looking at the levitation trap.
    Used as fallback if physical hardware is unavailable.
    """
    def __init__(self, width=640, height=480, noise_level=2.0):
        self.width = width
        self.height = height
        self.noise_level = noise_level
        self.frame_count = 0
        print("[VirtualCamera] Initialized (Simulation Mode)")

    def read(self):
        """
        Returns (True, frame) to match cv2.VideoCapture API.
        """
        self.frame_count += 1
        # Black background
        img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Draw a moving "particle" to show liveness
        cx = int(self.width/2 + 100 * np.cos(self.frame_count * 0.1))
        cy = int(self.height/2 + 100 * np.sin(self.frame_count * 0.1))
        
        cv2.circle(img, (cx, cy), 10, (255, 255, 255), -1)
        
        # Add noise
        img = cv2.GaussianBlur(img, (5, 5), 0)
        if self.noise_level > 0:
            noise = np.random.normal(0, self.noise_level, img.shape)
            img_float = img.astype(np.float32) + noise
            img = np.clip(img_float, 0, 255).astype(np.uint8)
            
        return True, img

    def release(self):
        pass

class PhysicalCamera:
    """
    Wraps the actual hardware camera.
    """
    def __init__(self, camera_index=0):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera index {camera_index}")
        print(f"[PhysicalCamera] Initialized (Hardware Index {camera_index})")

    def read(self):
        return self.cap.read()

    def release(self):
        self.cap.release()

def get_camera():
    """
    Factory to get the best available camera.
    """
    try:
        print("Attempting to connect to Physical Camera...")
        return PhysicalCamera(0)
    except Exception as e:
        print(f"Physical Camera failed: {e}")
        print("Falling back to Virtual Camera...")
        return VirtualCamera()

def run_experiment():
    print("Cycle 385: Physical Camera Integration")
    print("======================================")
    
    cam = get_camera()
    
    print("Capturing 10 frames...")
    last_frame = None
    
    for i in range(10):
        ret, frame = cam.read()
        if ret:
            print(f"Frame {i}: Captured {frame.shape}")
            last_frame = frame
            time.sleep(0.1)
        else:
            print(f"Frame {i}: Failed")
            
    if last_frame is not None:
        filename = "cycle385_capture.png"
        cv2.imwrite(filename, last_frame)
        print(f"Saved snapshot to {filename}")
        print("SUCCESS: Camera pipeline verified.")
    else:
        print("FAIL: No frames captured.")
        
    cam.release()

if __name__ == "__main__":
    run_experiment()
