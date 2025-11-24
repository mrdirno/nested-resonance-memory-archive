"""
NRM Core: Reality Interface
Monitors system state and ensures reality compliance.
"""
import time
import os
from typing import Dict, Any, Optional

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

class RealityMonitor:
    """
    Monitors system resources (CPU, Memory).
    """
    def __init__(self):
        self.baseline = self.capture()

    def capture(self) -> Dict[str, Any]:
        """
        Capture current system metrics.
        """
        metrics = {
            "timestamp": time.time(),
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "memory_used_mb": 0.0,
            "process_count": 0,
            "grounded": _HAS_PSUTIL
        }

        if _HAS_PSUTIL:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory()
            metrics["memory_percent"] = mem.percent
            metrics["memory_used_mb"] = mem.used / (1024 * 1024)
            metrics["process_count"] = len(psutil.pids())
        
        return metrics

    def check_health(self) -> bool:
        """
        Check if system is healthy (resources within limits).
        """
        if not _HAS_PSUTIL:
            return True # Assume healthy if we can't measure
            
        metrics = self.capture()
        if metrics["memory_percent"] > 90.0:
            return False
        return True

class RealityValidator:
    """
    Validates operations against reality constraints.
    """
    @staticmethod
    def validate_path(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def get_file_size(path: str) -> int:
        if os.path.exists(path):
            return os.path.getsize(path)
        return 0
