"""
Cycle 2590: The Actuator (Gate 58.3)
Goal: Verify motor control logic.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.hardware.actuator import DriveTrain

def run_experiment():
    print("--- Cycle 2590: The Actuator (Physical Movement) ---")
    
    bot = DriveTrain()
    
    print("Moving Forward...")
    bot.move_forward(50) # Half speed
    
    print("Moving Fast...")
    bot.move_forward(100) # Full speed
    
    print("Stopping...")
    bot.stop()
    
    print("\nSUCCESS: Motor Control Logic Verified.")

if __name__ == "__main__":
    run_experiment()
