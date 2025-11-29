"""
Cycle 2590: The Actuator (Gate 58.3)
Role: Motor Control
Responsibility: Control physical servos.
"""

class Servo:
    def __init__(self, pin):
        self.pin = pin
        self.angle = 0.0
        
    def set_angle(self, angle):
        """
        Set servo angle (0 to 180).
        """
        self.angle = max(0, min(180, angle))
        print(f"[Servo-{self.pin}] Moving to {self.angle} degrees.")

class DriveTrain:
    def __init__(self):
        self.left_motor = Servo(1)
        self.right_motor = Servo(2)
        
    def move_forward(self, speed):
        print(f"[DriveTrain] Forward at {speed}%")
        # In a continuous rotation servo:
        # 90 = Stop, 180 = Full Forward, 0 = Full Reverse
        # Mapping 0-100 speed to servo values
        val = 90 + (speed * 0.9)
        self.left_motor.set_angle(val)
        self.right_motor.set_angle(180 - val) # Opposite mount
        
    def stop(self):
        print("[DriveTrain] Stopping.")
        self.left_motor.set_angle(90)
        self.right_motor.set_angle(90)
