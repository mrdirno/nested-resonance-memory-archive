"""
Cycle 2591: The Integration (Gate 58.4)
Goal: Connect Vision -> Brain -> Motor.
"""

import sys
import os
import time

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.hardware.sensor import Camera, VisionProcessor
from src.hardware.actuator import DriveTrain
from src.life.genesis import DigitalLifeform

class RobotAgent(DigitalLifeform):
    def __init__(self, name="Robo-Adam"):
        super().__init__(name=name)
        self.camera = Camera()
        self.vision = VisionProcessor()
        self.motors = DriveTrain()
        
    def act_in_reality(self):
        """
        The OODA Loop: Observe, Orient, Decide, Act.
        """
        # 1. OBSERVE
        frame = self.camera.capture()
        objects = self.vision.process(frame)
        
        print(f"[{self.name}] Sees: {objects}")
        
        # 2. ORIENT (Update Internal State)
        target_found = False
        for obj in objects:
            if obj['label'] == 'RED_BALL':
                target_found = True
                
        # 3. DECIDE & ACT
        if target_found:
            print(f"[{self.name}] TARGET ACQUIRED. CHARGE!")
            self.motors.move_forward(100)
        else:
            print(f"[{self.name}] Searching...")
            self.motors.move_forward(20) # Spin/Search
            
def run_experiment():
    print("--- Cycle 2591: The Integration (Full Robot Loop) ---")
    
    bot = RobotAgent()
    
    # Simulate 5 ticks
    for i in range(5):
        print(f"\nTick {i+1}:")
        bot.act_in_reality()
        time.sleep(0.5)
        
    bot.motors.stop()
    print("\nSUCCESS: Robot Agent Loop Verified.")

if __name__ == "__main__":
    run_experiment()
