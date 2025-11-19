"""Simplified reality interface for the minimal NRM stack."""
import time, random
from typing import Dict

class RealityInterface:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path

    def get_system_metrics(self) -> Dict[str, float]:
        return {
            "cpu_percent": random.uniform(5, 50),
            "memory_percent": random.uniform(10, 60),
            "disk_percent": random.uniform(1, 30),
            "timestamp": time.time() % 1000,
            "process_count": random.randint(50, 300),
        }
