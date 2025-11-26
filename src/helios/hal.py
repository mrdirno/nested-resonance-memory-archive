"""
HELIOS Hardware Abstraction Layer (Gate 4.1)
Generic interface for controlling physical emitter arrays.

Principle: PRIN-HARDWARE-ABSTRACTION
Author: MOG (Cycle 2347)
"""

from abc import ABC, abstractmethod
import time
import numpy as np

class EmitterArray(ABC):
    """
    Abstract Base Class for Physical Emitter Arrays.
    """
    
    def __init__(self, num_emitters=64):
        self.num_emitters = num_emitters
        self.phases = [0.0] * num_emitters
        self.connected = False

    @abstractmethod
    def connect(self, port=None):
        """Establish connection to hardware."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close connection."""
        pass

    @abstractmethod
    def update_phases(self, phases):
        """
        Send phase data to hardware.
        :param phases: List or Array of phase values (0..2pi).
        """
        if len(phases) != self.num_emitters:
            raise ValueError(f"Phase count {len(phases)} does not match emitter count {self.num_emitters}")
        self.phases = phases

class MockArray(EmitterArray):
    """
    Virtual array for testing without hardware.
    """
    def connect(self, port=None):
        print("MOCK: Connected to Virtual Array.")
        self.connected = True
        return True

    def disconnect(self):
        print("MOCK: Disconnected.")
        self.connected = False

    def update_phases(self, phases):
        super().update_phases(phases)
        # Simulate latency
        time.sleep(0.001) 
        print(f"MOCK: Updated {len(phases)} emitters. Sample: {phases[:3]}...")

# Factory
def get_driver(driver_type="MOCK", num_emitters=64, port=None):
    if driver_type == "MOCK":
        return MockArray(num_emitters)
    # Future: Add SERIAL, GPIO drivers
    else:
        raise ValueError(f"Unknown driver type: {driver_type}")