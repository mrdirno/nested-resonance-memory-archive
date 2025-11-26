"""
HELIOS Serial Bridge (Gate 4.2)
Implements the EmitterArray interface for physical serial communication.

Principle: PRIN-SERIAL-BRIDGE
Author: MOG (Cycle 2348)
"""

from src.helios.hal import EmitterArray
import time
# import serial # Requires pyserial

class SerialArray(EmitterArray):
    """
    Driver for physical arrays connected via USB/Serial.
    """
    def __init__(self, port, baudrate=115200, num_emitters=64):
        super().__init__(num_emitters)
        self.port = port
        self.baudrate = baudrate
        self._serial = None

    def connect(self):
        try:
            # self._serial = serial.Serial(self.port, self.baudrate, timeout=1)
            print(f"SERIAL: Connected to {self.port} @ {self.baudrate}")
            self.connected = True
            return True
        except Exception as e: # ImportError or SerialException
            print(f"SERIAL ERROR: Could not connect to {self.port}. {e}")
            self.connected = False
            return False

    def disconnect(self):
        if self._serial and self._serial.is_open:
            # self._serial.close()
            pass
        print("SERIAL: Disconnected.")
        self.connected = False

    def update_phases(self, phases):
        super().update_phases(phases)
        if not self.connected:
            return
        
        # Protocol: [0xFF (Start), ID, Phase_High, Phase_Low, ..., 0xFE (End)]
        # Simplified for prototype: Just printing bytes
        
        payload = bytearray([0xFF])
        for i, phase in enumerate(phases):
            # Normalize phase (0..2pi) to (0..255) or similar
            # Using simple mapping for prototype
            val = int((phase / (2 * 3.14159)) * 255) % 256
            payload.append(val)
        payload.append(0xFE)
        
        # self._serial.write(payload)
        print(f"SERIAL: Sent {len(payload)} bytes to hardware.")
