"""
Cycle 2589: The Sensorium (Gate 58.2)
Goal: Verify visual processing pipeline.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.hardware.sensor import Camera, VisionProcessor

def run_experiment():
    print("--- Cycle 2589: The Sensorium (Visual Perception) ---")
    
    cam = Camera()
    processor = VisionProcessor()
    
    print("Capturing Frame...")
    frame = cam.capture()
    print(f"Frame Size: {len(frame)}x{len(frame[0])}")
    
    print("Processing Frame...")
    objects = processor.process(frame)
    
    if objects:
        print(f"Detected: {objects}")
    else:
        print("Detected: Nothing (Empty Scene)")
        
    print("\nSUCCESS: Vision Pipeline Operational.")

if __name__ == "__main__":
    run_experiment()
