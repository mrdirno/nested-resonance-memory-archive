"""
Cycle 2588: The Interface (Gate 58.1)
Role: Hardware Abstraction Layer (HAL)
Responsibility: Define standard interface for physical I/O.
"""

import abc

class HardwareInterface(abc.ABC):
    @abc.abstractmethod
    def initialize(self):
        """Startup sequence."""
        pass

    @abc.abstractmethod
    def shutdown(self):
        """Safety shutdown."""
        pass

class RobotInterface(HardwareInterface):
    """
    Abstract Base Class for a Physical Robot.
    """
    @abc.abstractmethod
    def move_motor(self, motor_id: int, position: float):
        """Move a servo to a specific angle (0.0 to 1.0)."""
        pass

    @abc.abstractmethod
    def read_sensor(self, sensor_id: int):
        """Read value from a sensor."""
        pass
        
    @abc.abstractmethod
    def capture_image(self):
        """Return a frame from the camera."""
        pass

class MockRobot(RobotInterface):
    """
    Virtual robot for simulation/testing.
    """
    def __init__(self):
        self.motors = {}
        self.sensors = {}
        self.camera_frame = "Virtual Image Data"
        
    def initialize(self):
        print("[HAL] MockRobot Initialized.")
        
    def shutdown(self):
        print("[HAL] MockRobot Shutdown.")
        
    def move_motor(self, motor_id, position):
        self.motors[motor_id] = max(0.0, min(1.0, position))
        print(f"[HAL] Motor {motor_id} moved to {position:.2f}")
        
    def read_sensor(self, sensor_id):
        val = self.sensors.get(sensor_id, 0.0)
        print(f"[HAL] Sensor {sensor_id} read: {val}")
        return val
        
    def capture_image(self):
        print(f"[HAL] Captured: {self.camera_frame}")
        return self.camera_frame
