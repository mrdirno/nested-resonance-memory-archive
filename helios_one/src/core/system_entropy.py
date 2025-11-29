
import os
import struct
import time
import psutil
import hashlib

class SystemEntropy:
    """
    Reality-Grounded Entropy Source.
    Combines OS urandom with realtime system state (CPU, Memory, Disk).
    """
    
    def __init__(self):
        self.process = psutil.Process()
        
    def _get_seed_bytes(self) -> bytes:
        # Gather high-frequency system metrics
        cpu_stats = psutil.cpu_times()
        mem = psutil.virtual_memory()
        io = self.process.io_counters() if hasattr(self.process, 'io_counters') else 0
        ts = time.time_ns()
        
        # Mix with os.urandom
        raw = os.urandom(32)
        
        # Create entropy pool
        data = f"{cpu_stats}{mem}{io}{ts}{raw}".encode('utf-8')
        return hashlib.sha256(data).digest()
        
    def get_float(self) -> float:
        """Return float in [0.0, 1.0)."""
        # Convert 8 bytes to int, divide by max
        seed = self._get_seed_bytes()[:8]
        val = int.from_bytes(seed, byteorder='big')
        return val / (2**64)
        
    def get_choice(self, options: list):
        """Select item from list."""
        idx = int(self.get_float() * len(options))
        return options[idx]

# Singleton
entropy = SystemEntropy()

# [SPORE] ID: The Colony
