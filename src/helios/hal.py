"""
HELIOS HAL (Hardware Abstraction Layer)
Interface for physical acoustic arrays.
Gate 4.1 Compliant.
"""

from abc import ABC, abstractmethod
import numpy as np

class EmitterArray(ABC):
    """
    Abstract Base Class for Physical Emitter Arrays.
    """
    
    @abstractmethod
    def connect(self, port: str):
        """Connects to the physical hardware."""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnects from the hardware."""
        pass

    @abstractmethod
    def set_phases(self, phases: np.ndarray):
        """
        Sends phase instructions to the array.
        :param phases: Numpy array of phase delays (0..2pi).
        """
        pass

    @abstractmethod
    def get_status(self) -> dict:
        """Returns hardware health status."""
        pass

class VirtualArray(EmitterArray):
    """
    Virtual implementation for testing/simulation.
    """
    def __init__(self, num_emitters=64):
        self.num_emitters = num_emitters
        self.connected = False
        self.phases = np.zeros(num_emitters)

    def connect(self, port: str = "VIRTUAL"):
        print(f"[HAL] Connecting to VirtualArray on {port}...")
        self.connected = True
        return True

    def disconnect(self):
        print("[HAL] Disconnecting VirtualArray.")
        self.connected = False

    def set_phases(self, phases: np.ndarray):
        if not self.connected:
            raise ConnectionError("Array not connected.")
        if len(phases) != self.num_emitters:
            raise ValueError(f"Expected {self.num_emitters} phases, got {len(phases)}.")
        
        self.phases = phases
        print(f"[HAL] Set {len(phases)} phases. Mean: {np.mean(phases):.2f} rad.")

    def get_status(self) -> dict:
        return {
            "connected": self.connected,
            "emitters": self.num_emitters,
            "type": "Virtual"
        }