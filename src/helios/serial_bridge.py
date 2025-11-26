"""
HELIOS Serial Bridge (Gate 4.2)
High-performance serial communication protocol for driving physical emitter arrays.
Gate 4.2 Compliant.
"""

import serial
import time
import struct
import numpy as np
from src.helios.hal import EmitterArray

class SerialArray(EmitterArray):
    """
    Physical implementation of EmitterArray using Serial/USB.
    Protocol:
    [HEADER: 0xAA 0xBB] [CMD: 1 byte] [PAYLOAD_LEN: 2 bytes] [PAYLOAD] [CHECKSUM: 1 byte]
    """
    
    CMD_SET_PHASES = 0x01
    CMD_GET_STATUS = 0x02
    CMD_PING = 0x03

    def __init__(self, port=None, baudrate=115200, num_emitters=64):
        self.port = port
        self.baudrate = baudrate
        self.num_emitters = num_emitters
        self.serial = None
        self.connected = False

    def connect(self, port: str = None):
        target_port = port if port else self.port
        if not target_port:
            raise ValueError("No serial port specified.")
            
        print(f"[HAL] Connecting to SerialArray on {target_port} at {self.baudrate} baud...")
        try:
            self.serial = serial.Serial(target_port, self.baudrate, timeout=1)
            time.sleep(2) # Wait for Arduino reset
            self.connected = True
            print("[HAL] Connected.")
            return True
        except serial.SerialException as e:
            print(f"[HAL] Connection Failed: {e}")
            return False

    def disconnect(self):
        if self.serial and self.serial.is_open:
            self.serial.close()
            print("[HAL] Disconnected.")
        self.connected = False

    def _send_packet(self, cmd, payload=b''):
        if not self.connected:
            raise ConnectionError("Serial port not connected.")
            
        header = bytes([0xAA, 0xBB])
        length = struct.pack('<H', len(payload))
        packet = header + bytes([cmd]) + length + payload
        
        checksum = sum(packet) % 256
        packet += bytes([checksum])
        
        self.serial.write(packet)

    def set_phases(self, phases: np.ndarray):
        """
        Sends 8-bit phase data to the hardware.
        Phases 0..2pi are mapped to 0..255.
        """
        if len(phases) != self.num_emitters:
            raise ValueError(f"Expected {self.num_emitters} phases.")
            
        # Quantize phases to 8-bit
        quantized = (phases / (2*np.pi) * 255).astype(np.uint8)
        payload = quantized.tobytes()
        
        self._send_packet(self.CMD_SET_PHASES, payload)
        # print(f"[HAL] Sent {len(phases)} phases.")

    def get_status(self) -> dict:
        if not self.connected:
            return {"connected": False}
            
        self._send_packet(self.CMD_GET_STATUS)
        # Basic mock response handling for prototype
        # In real hardware, read back bytes here
        return {"connected": True, "type": "Serial", "port": self.port}

if __name__ == "__main__":
    # Mock test
    # Requires virtual serial port or Arduino
    print("Serial Bridge Module Loaded.")