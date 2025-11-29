"""
Cycle 2588: The Interface (Gate 58.1)
Goal: Verify the Hardware Abstraction Layer with a Mock Robot.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.hardware.interface import MockRobot

def run_experiment():
    print("--- Cycle 2588: The Interface (HAL Verification) ---")
    
    # Initialize
    robot = MockRobot()
    robot.initialize()
    
    # Test Actuation
    print("\n[Testing Motors]")
    robot.move_motor(1, 0.5)
    robot.move_motor(2, 1.2) # Should clamp to 1.0
    
    # Test Sensing
    print("\n[Testing Sensors]")
    robot.read_sensor(0)
    
    # Test Vision
    print("\n[Testing Camera]")
    img = robot.capture_image()
    
    # Shutdown
    print("\n[Shutting Down]")
    robot.shutdown()
    
    if robot.motors[1] == 0.5 and robot.motors[2] == 1.0:
        print("\nSUCCESS: HAL Logic Verified.")
    else:
        print("\nFAILURE: Motor state incorrect.")

if __name__ == "__main__":
    run_experiment()
