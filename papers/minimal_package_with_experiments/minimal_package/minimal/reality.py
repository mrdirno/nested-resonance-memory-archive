"""Reality gateway used by the minimal NRM package."""

from __future__ import annotations
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional
from core.reality_interface import RealityInterface

@dataclass(frozen=True)
class RealitySnapshot:
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: float
    process_count: int

    def as_dict(self) -> Dict[str, float]:
        return asdict(self)

class MinimalRealityGateway:
    def __init__(self, workspace_path: Optional[Path] = None):
        base = workspace_path or Path("workspace/minimal")
        self._workspace = Path(base)
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._interface = RealityInterface(str(self._workspace))

    def capture_snapshot(self) -> RealitySnapshot:
        m = self._interface.get_system_metrics()
        return RealitySnapshot(**m)
