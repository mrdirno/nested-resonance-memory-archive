"""Resonance helpers that delegate to :mod:`code.bridge.transcendental_bridge`."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List

from bridge.transcendental_bridge import ResonanceMatch, TranscendentalBridge

from .agent import MinimalAgent


@dataclass
class ResonantCluster:
    """Grouping of agents whose mutual resonance exceeds a threshold."""

    member_ids: List[str]
    average_similarity: float
    matches: List[ResonanceMatch]

    def as_dict(self) -> dict:
        return {
            "member_ids": self.member_ids,
            "average_similarity": self.average_similarity,
            "matches": [match.similarity for match in self.matches],
        }


def find_resonant_clusters(
    agents: Iterable[MinimalAgent],
    bridge: TranscendentalBridge,
    *,
    resonance_threshold: float | None = None,
) -> List[ResonantCluster]:
    """Return disjoint clusters whose pairwise similarity clears ``threshold``."""

    agents = list(agents)
    if resonance_threshold is None:
        resonance_threshold = bridge.resonance_threshold

    clusters: List[ResonantCluster] = []
    assigned: set[str] = set()

    for pivot in agents:
        if pivot.agent_id in assigned:
            continue

        members = [pivot]
        matches: List[ResonanceMatch] = []

        for candidate in agents:
            if candidate.agent_id == pivot.agent_id or candidate.agent_id in assigned:
                continue

            match = pivot.resonance_with(candidate, bridge)
            if match.similarity >= resonance_threshold:
                members.append(candidate)
                matches.append(match)

        if len(members) > 1:
            clusters.append(
                ResonantCluster(
                    member_ids=[agent.agent_id for agent in members],
                    average_similarity=mean(match.similarity for match in matches) if matches else 1.0,
                    matches=matches,
                )
            )
            assigned.update(agent.agent_id for agent in members)

    return clusters


__all__ = ["ResonantCluster", "find_resonant_clusters"]
