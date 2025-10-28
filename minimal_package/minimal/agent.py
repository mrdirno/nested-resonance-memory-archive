"""Minimal agent abstraction using the simplified transcendental bridge."""

from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import List, Optional
from bridge.transcendental_bridge import ResonanceMatch, TranscendentalBridge, TranscendentalState
from .reality import RealitySnapshot

@dataclass
class MinimalAgent:
    agent_id: str
    state: TranscendentalState
    anchor: RealitySnapshot
    resonance_history: List[float] = field(default_factory=list)

    @classmethod
    def from_snapshot(cls, snapshot: RealitySnapshot, bridge: TranscendentalBridge, agent_id: Optional[str] = None):
        state = bridge.reality_to_phase(snapshot.as_dict())
        return cls(agent_id or f"agent_{uuid.uuid4().hex[:8]}", state, snapshot)

    def update(self, snapshot: RealitySnapshot, bridge: TranscendentalBridge):
        new_state = bridge.reality_to_phase(snapshot.as_dict())
        match = bridge.detect_resonance(self.state, new_state)
        self.resonance_history.append(match.similarity)
        self.state = new_state
        self.anchor = snapshot

    def resonance_with(self, other: MinimalAgent, bridge: TranscendentalBridge) -> ResonanceMatch:
        return bridge.detect_resonance(self.state, other.state)

    @property
    def magnitude(self) -> float:
        return float(self.state.magnitude)
