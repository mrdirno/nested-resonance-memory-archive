"""
Cycle 2589: The Sensorium (Gate 58.2)
Role: Visual Processing Unit
Responsibility: Process raw camera frames into semantic data.
"""

import random

class Camera:
    def __init__(self, resolution=(640, 480)):
        self.resolution = resolution
        
    def capture(self):
        """
        Simulate capturing an image.
        Returns a mock frame (matrix of pixel values).
        """
        # Mock: Just return noise or a simple pattern
        return [[random.randint(0, 255) for _ in range(10)] for _ in range(10)]

class VisionProcessor:
    def process(self, frame):
        """
        Simulate object detection.
        Returns a list of detected objects.
        """
        # Mock Logic: Randomly detect "Red Ball" or "Wall"
        detected = []
        if random.random() > 0.5:
            detected.append({'label': 'RED_BALL', 'confidence': 0.95, 'bbox': [10, 10, 50, 50]})
        
        if random.random() > 0.7:
             detected.append({'label': 'WALL', 'confidence': 0.88, 'bbox': [100, 100, 200, 200]})
             
        return detected
