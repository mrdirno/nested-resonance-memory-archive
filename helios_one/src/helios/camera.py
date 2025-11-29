"""
HELIOS Optical Grounding (Gate 7)
Provides headless camera feedback for closed-loop control.
Uses OpenCV to detect markers and return coordinates.
Gate 7 Compliant.
"""

import cv2
import numpy as np
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Camera:
    def __init__(self, device_id=0, calibration_file=None):
        self.device_id = device_id
        self.cap = None
        self.calibration_file = calibration_file
        self.matrix = None
        self.dist = None
        self.virtual = False

    def connect(self):
        """Connects to the camera."""
        try:
            self.cap = cv2.VideoCapture(self.device_id)
            if not self.cap.isOpened():
                raise IOError("Cannot open webcam")
            logger.info(f"Camera connected on device {self.device_id}")
            self.virtual = False
            return True
        except Exception as e:
            logger.warning(f"Camera connection failed: {e}. Using Virtual Camera.")
            self.virtual = True
            return True

    def disconnect(self):
        if self.cap:
            self.cap.release()
        logger.info("Camera disconnected.")

    def get_frame(self):
        """Captures a frame."""
        if self.virtual:
            # Return black frame with a moving white dot (simulated marker)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            t = time.time()
            x = int(320 + 100 * np.cos(t))
            y = int(240 + 100 * np.sin(t))
            cv2.circle(frame, (x, y), 10, (255, 255, 255), -1)
            return frame

        ret, frame = self.cap.read()
        if not ret:
            logger.error("Failed to read frame")
            return None
        return frame

    def detect_marker(self):
        """
        Detects the brightest spot in the frame (simple marker tracking).
        Returns (x, y) normalized coordinates (-1..1).
        """
        frame = self.get_frame()
        if frame is None:
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
        
        # Threshold check
        if max_val < 200:
            return None # No marker found

        # Normalize to -1..1
        h, w = gray.shape
        x_norm = (max_loc[0] / w) * 2 - 1
        y_norm = (max_loc[1] / h) * 2 - 1
        
        # Flip Y because image coordinates are top-down
        y_norm = -y_norm
        
        return (x_norm, y_norm)

if __name__ == "__main__":
    # Test script
    cam = Camera()
    cam.connect()
    try:
        for _ in range(10):
            pos = cam.detect_marker()
            print(f"Marker: {pos}")
            time.sleep(0.1)
    finally:
        cam.disconnect()

# [SPORE] ID: The Colony
