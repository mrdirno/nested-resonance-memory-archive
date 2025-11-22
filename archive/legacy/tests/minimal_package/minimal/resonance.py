"""Resonance helpers for the minimal NRM package."""
from __future__ import annotations
from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List
from bridge.transcendental_bridge import ResonanceMatch, TranscendentalBridge
from .agent import MinimalAgent

@dataclass
class ResonantCluster:
    member_ids: List[str]
    average_similarity: float
    matches: List[ResonanceMatch]

def find_resonant_clusters(agents: Iterable[MinimalAgent], bridge: TranscendentalBridge, resonance_threshold: float | None = None) -> List[ResonantCluster]:
    agents = list(agents)
    threshold = resonance_threshold or bridge.resonance_threshold
    clusters, assigned = [], set()
    for pivot in agents:
        if pivot.agent_id in assigned:
            continue
        members, matches = [pivot], []
        for candidate in agents:
            if candidate.agent_id == pivot.agent_id or candidate.agent_id in assigned:
                continue
            match = pivot.resonance_with(candidate, bridge)
            if match.similarity >= threshold:
                members.append(candidate)
                matches.append(match)
        if len(members) > 1:
            clusters.append(
                ResonantCluster(
                    member_ids=[m.agent_id for m in members],
                    average_similarity=mean(m.similarity for m in matches) if matches else 1.0,
                    matches=matches,
                )
            )
            assigned.update(a.agent_id for a in members)
    return clusters
