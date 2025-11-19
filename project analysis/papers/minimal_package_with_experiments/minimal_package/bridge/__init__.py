"""Stub bridge package used by the minimal NRM tests."""

# Exposes TranscendentalBridge + helpers for minimal validation
from .transcendental_bridge import (
    TranscendentalBridge,
    ResonanceMatch,
    TranscendentalState,
)

__all__ = ["TranscendentalBridge", "ResonanceMatch", "TranscendentalState"]
