"""Minimal orchestrator wiring snapshots, agents, and resonance."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List, Optional
from bridge.transcendental_bridge import TranscendentalBridge
from .agent import MinimalAgent
from .reality import MinimalRealityGateway, RealitySnapshot
from .resonance import find_resonant_clusters

CaptureFn = Callable[[], RealitySnapshot]

@dataclass
class CycleSummary:
    cycle: int
    total_magnitude: float
    cluster_count: int

class MinimalSwarm:
    def __init__(self, capture: Optional[CaptureFn] = None, *, bridge: Optional[TranscendentalBridge] = None, gateway: Optional[MinimalRealityGateway] = None):
        self._gateway = gateway or MinimalRealityGateway()
        self._bridge = bridge or TranscendentalBridge(workspace_path=str(self._gateway._workspace / "bridge"))
        self._capture = capture or self._gateway.capture_snapshot
        self._agents: List[MinimalAgent] = []
        self._cycle = 0

    def spawn_agent(self, snapshot: Optional[RealitySnapshot] = None) -> MinimalAgent:
        snapshot = snapshot or self._capture()
        agent = MinimalAgent.from_snapshot(snapshot, self._bridge)
        self._agents.append(agent)
        return agent

    def run_cycle(self) -> CycleSummary:
        snapshot = self._capture()
        for a in self._agents:
            a.update(snapshot, self._bridge)
        clusters = find_resonant_clusters(self._agents, self._bridge)
        self._cycle += 1
        return CycleSummary(self._cycle, sum(a.magnitude for a in self._agents), len(clusters))
