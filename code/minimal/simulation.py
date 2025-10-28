"""Minimal orchestrator wiring reality snapshots, agents, and resonance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from bridge.transcendental_bridge import TranscendentalBridge

from .agent import MinimalAgent
from .reality import MinimalRealityGateway, RealitySnapshot
from .resonance import ResonantCluster, find_resonant_clusters

CaptureFn = Callable[[], RealitySnapshot]


@dataclass
class CycleSummary:
    """Result returned from :meth:`MinimalSwarm.run_cycle`."""

    cycle: int
    total_magnitude: float
    cluster_count: int

    def as_dict(self) -> Dict[str, float]:
        return {
            "cycle": self.cycle,
            "total_magnitude": self.total_magnitude,
            "cluster_count": self.cluster_count,
        }


class MinimalSwarm:
    """Self-contained driver that keeps a small pool of agents active."""

    def __init__(
        self,
        capture: Optional[CaptureFn] = None,
        *,
        bridge: Optional[TranscendentalBridge] = None,
        gateway: Optional[MinimalRealityGateway] = None,
    ) -> None:
        self._gateway = gateway or MinimalRealityGateway()
        self._bridge = bridge or TranscendentalBridge(workspace_path=str(self._gateway.workspace / "bridge"))
        self._capture = capture or self._gateway.capture_snapshot
        self._agents: List[MinimalAgent] = []
        self._cycle = 0

    @property
    def agents(self) -> List[MinimalAgent]:
        return list(self._agents)

    @property
    def cycle(self) -> int:
        return self._cycle

    @property
    def bridge(self) -> TranscendentalBridge:
        return self._bridge

    def spawn_agent(self, snapshot: Optional[RealitySnapshot] = None) -> MinimalAgent:
        snapshot = snapshot or self._capture()
        agent = MinimalAgent.from_snapshot(snapshot, self._bridge)
        self._agents.append(agent)
        return agent

    def run_cycle(self) -> CycleSummary:
        snapshot = self._capture()
        for agent in self._agents:
            agent.update(snapshot, self._bridge)

        clusters = find_resonant_clusters(self._agents, self._bridge)
        self._cycle += 1
        total_magnitude = sum(agent.magnitude for agent in self._agents)

        return CycleSummary(
            cycle=self._cycle,
            total_magnitude=total_magnitude,
            cluster_count=len(clusters),
        )

    def describe_clusters(self, resonance_threshold: float | None = None) -> List[ResonantCluster]:
        return find_resonant_clusters(
            self._agents,
            self._bridge,
            resonance_threshold=resonance_threshold,
        )


__all__ = ["CycleSummary", "MinimalSwarm"]
