"""Minimal agent abstraction backed by the real transcendental bridge."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from bridge.transcendental_bridge import (
    ResonanceMatch,
    TranscendentalBridge,
    TranscendentalState,
)

from .reality import RealitySnapshot


@dataclass
class MinimalAgent:
    """Reality-grounded agent used by the runnable minimal package."""

    agent_id: str
    state: TranscendentalState
    anchor: RealitySnapshot
    resonance_history: List[float] = field(default_factory=list)

    @classmethod
    def from_snapshot(
        cls,
        snapshot: RealitySnapshot,
        bridge: TranscendentalBridge,
        agent_id: Optional[str] = None,
    ) -> "MinimalAgent":
        """Instantiate an agent anchored to a concrete ``snapshot``."""

        state = bridge.reality_to_phase(snapshot.as_dict())
        return cls(agent_id=agent_id or f"agent_{uuid.uuid4().hex[:8]}", state=state, anchor=snapshot)

    def update(self, snapshot: RealitySnapshot, bridge: TranscendentalBridge) -> None:
        """Refresh the agent state using a new snapshot captured from reality."""

        new_state = bridge.reality_to_phase(snapshot.as_dict())
        match = bridge.detect_resonance(self.state, new_state)
        self.resonance_history.append(match.similarity)
        self.state = new_state
        self.anchor = snapshot

    def resonance_with(self, other: "MinimalAgent", bridge: TranscendentalBridge) -> ResonanceMatch:
        """Compute resonance between this agent and ``other`` using the bridge."""

        return bridge.detect_resonance(self.state, other.state)

    @property
    def magnitude(self) -> float:
        """Expose the magnitude of the agent's current transcendental state."""

        return float(self.state.magnitude)


__all__ = ["MinimalAgent"]
