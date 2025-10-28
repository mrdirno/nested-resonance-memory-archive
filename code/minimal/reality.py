"""Reality gateway used by the minimal NRM package.

The original Nested Resonance Memory stack relies on the
:class:`code.core.reality_interface.RealityInterface` to ground all
observations in verifiable system state.  For the lightweight package we
wrap that interface so experiments can capture compact ``RealitySnapshot``
objects without needing to understand the full workspace layout.

The gateway intentionally keeps a tiny footprint while still persisting
measurements to the same SQLite databases as the main project.  When a
custom workspace path is provided (for instance in tests) the databases
are created inside that directory, ensuring isolation from the primary
research artefacts.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional

from core.reality_interface import RealityInterface


@dataclass(frozen=True)
class RealitySnapshot:
    """Minimal projection of the full metric payload captured from reality."""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    timestamp: float
    process_count: int

    def as_dict(self) -> Dict[str, float]:
        """Return a serialisable representation of the snapshot."""

        return asdict(self)


class MinimalRealityGateway:
    """Thin wrapper around :class:`RealityInterface` for minimal experiments."""

    def __init__(self, workspace_path: Optional[Path] = None) -> None:
        base_path = workspace_path or Path(__file__).resolve().parents[1] / "workspace" / "minimal"
        self._workspace = Path(base_path)
        # ``RealityInterface`` expects a ``workspace`` directory underneath the
        # provided root.  Using ``mkdir`` with ``parents=True`` keeps the helper
        # robust when called with temporary directories in tests.
        self._workspace.mkdir(parents=True, exist_ok=True)
        self._interface = RealityInterface(workspace_path=str(self._workspace))

    @property
    def workspace(self) -> Path:
        return self._workspace

    def capture_snapshot(self) -> RealitySnapshot:
        metrics = self._interface.get_system_metrics()
        return RealitySnapshot(
            cpu_percent=float(metrics["cpu_percent"]),
            memory_percent=float(metrics["memory_percent"]),
            disk_percent=float(metrics["disk_percent"]),
            timestamp=float(metrics["timestamp"]),
            process_count=int(metrics["process_count"]),
        )


__all__ = ["MinimalRealityGateway", "RealitySnapshot"]
