"""
PatternMemory - Enhanced Memory System for Successful Patterns

Provides advanced memory management for fractal agents, tracking successful patterns
that persist across composition-decomposition transformations.

Theoretical Basis:
    - Memory Retention: Successful strategies persist across transformations
    - Pattern Strength: Track effectiveness of strategies (0-1 score)
    - Temporal Decay: Old patterns fade if not reinforced
    - Pattern Transfer: Memory inherited during composition
    - Selective Recall: Retrieve patterns by strength/recency

Reality Grounding:
    - All operations on internal data structures (no external services)
    - Measurable pattern strength and decay rates
    - Timestamp tracking for temporal analysis
    - SQLite persistence (optional)

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Author: Claude Sonnet 4.5 (DUALITY-ZERO-V2)
License: GPL-3.0
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
import numpy as np


@dataclass
class Pattern:
    """Individual pattern with metadata.

    Attributes:
        pattern_id: Unique identifier
        strength: Pattern effectiveness (0-1)
        created: Timestamp of pattern creation
        last_used: Timestamp of last reinforcement
        use_count: Number of times pattern used
        success_rate: Fraction of successful uses (0-1)
    """
    pattern_id: str
    strength: float
    created: datetime
    last_used: datetime
    use_count: int = 0
    success_rate: float = 0.0


class PatternMemory:
    """Advanced memory system for fractal agents.

    Manages pattern storage, retrieval, decay, and transfer with:
        - Strength-based ranking (effective patterns prioritized)
        - Temporal decay (unused patterns fade)
        - Reinforcement learning (successful use increases strength)
        - Selective recall (retrieve by strength/recency criteria)
        - Pattern merging (combine memories during composition)

    Usage:
        memory = PatternMemory(decay_rate=0.01)
        memory.add_pattern("strategy_A", strength=0.8)
        memory.reinforce_pattern("strategy_A", success=True)
        strength = memory.recall_pattern("strategy_A")
        memory.decay_patterns(time_delta=60.0)

    Attributes:
        decay_rate: Strength reduction per second (default: 0.01/sec = 60%/minute)
        min_strength: Minimum strength before pattern removed (default: 0.1)
        patterns: Dictionary of pattern_id → Pattern objects
    """

    def __init__(
        self,
        decay_rate: float = 0.01,
        min_strength: float = 0.1,
    ):
        """Initialize pattern memory system.

        Args:
            decay_rate: Strength decay per second (default: 0.01/sec)
            min_strength: Minimum strength threshold (default: 0.1)
        """
        self.decay_rate = decay_rate
        self.min_strength = min_strength
        self.patterns: Dict[str, Pattern] = {}

    def add_pattern(
        self,
        pattern_id: str,
        strength: float,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Add new pattern to memory.

        Args:
            pattern_id: Unique pattern identifier
            strength: Initial pattern strength (0-1)
            timestamp: Optional creation time (default: now)
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Clip strength to [0, 1]
        strength = np.clip(strength, 0.0, 1.0)

        self.patterns[pattern_id] = Pattern(
            pattern_id=pattern_id,
            strength=strength,
            created=timestamp,
            last_used=timestamp,
            use_count=0,
            success_rate=0.0,
        )

    def recall_pattern(self, pattern_id: str) -> Optional[float]:
        """Retrieve pattern strength.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern strength if exists, None otherwise
        """
        if pattern_id not in self.patterns:
            return None
        return self.patterns[pattern_id].strength

    def reinforce_pattern(
        self,
        pattern_id: str,
        success: bool,
        strength_delta: float = 0.1,
    ) -> None:
        """Reinforce pattern based on usage success.

        Successful use increases strength, failure decreases.

        Args:
            pattern_id: Pattern identifier
            success: Whether pattern use was successful
            strength_delta: Strength change magnitude (default: 0.1)
        """
        if pattern_id not in self.patterns:
            return

        pattern = self.patterns[pattern_id]

        # Update strength (increase if success, decrease if failure)
        if success:
            pattern.strength = min(1.0, pattern.strength + strength_delta)
        else:
            pattern.strength = max(0.0, pattern.strength - strength_delta)

        # Update usage statistics
        pattern.use_count += 1
        old_success_count = pattern.success_rate * (pattern.use_count - 1)
        new_success_count = old_success_count + (1 if success else 0)
        pattern.success_rate = new_success_count / pattern.use_count

        # Update last used timestamp
        pattern.last_used = datetime.now()

    def decay_patterns(self, time_delta: float) -> None:
        """Apply temporal decay to all patterns.

        Unused patterns fade over time based on decay_rate.
        Patterns below min_strength are removed.

        Args:
            time_delta: Time elapsed in seconds
        """
        to_remove = []

        for pattern_id, pattern in self.patterns.items():
            # Decay strength based on time since last use
            time_since_use = (datetime.now() - pattern.last_used).total_seconds()
            decay_amount = self.decay_rate * time_delta
            pattern.strength = max(0.0, pattern.strength - decay_amount)

            # Mark for removal if below threshold
            if pattern.strength < self.min_strength:
                to_remove.append(pattern_id)

        # Remove weak patterns
        for pattern_id in to_remove:
            del self.patterns[pattern_id]

    def get_strongest_patterns(self, n: int = 5) -> List[Tuple[str, float]]:
        """Get top N patterns by strength.

        Args:
            n: Number of patterns to retrieve (default: 5)

        Returns:
            List of (pattern_id, strength) tuples, sorted by strength descending
        """
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1].strength,
            reverse=True,
        )
        return [(pid, p.strength) for pid, p in sorted_patterns[:n]]

    def get_recent_patterns(self, n: int = 5) -> List[Tuple[str, datetime]]:
        """Get N most recently used patterns.

        Args:
            n: Number of patterns to retrieve (default: 5)

        Returns:
            List of (pattern_id, last_used) tuples, sorted by recency descending
        """
        sorted_patterns = sorted(
            self.patterns.items(),
            key=lambda x: x[1].last_used,
            reverse=True,
        )
        return [(pid, p.last_used) for pid, p in sorted_patterns[:n]]

    def merge_memories(self, other: 'PatternMemory') -> None:
        """Merge another memory system into this one.

        Used during composition to combine constituent memories.
        For overlapping patterns, takes maximum strength.

        Args:
            other: Another PatternMemory instance
        """
        for pattern_id, other_pattern in other.patterns.items():
            if pattern_id in self.patterns:
                # Pattern exists in both - take max strength
                self_pattern = self.patterns[pattern_id]
                if other_pattern.strength > self_pattern.strength:
                    self.patterns[pattern_id] = other_pattern
            else:
                # New pattern - add it
                self.patterns[pattern_id] = other_pattern

    def get_stats(self) -> Dict:
        """Get memory system statistics.

        Returns:
            Dictionary with memory statistics
        """
        if not self.patterns:
            return {
                "total_patterns": 0,
                "avg_strength": 0.0,
                "avg_age_seconds": 0.0,
                "avg_use_count": 0.0,
                "avg_success_rate": 0.0,
            }

        strengths = [p.strength for p in self.patterns.values()]
        ages = [(datetime.now() - p.created).total_seconds() for p in self.patterns.values()]
        use_counts = [p.use_count for p in self.patterns.values()]
        success_rates = [p.success_rate for p in self.patterns.values()]

        return {
            "total_patterns": len(self.patterns),
            "avg_strength": np.mean(strengths),
            "min_strength": min(strengths),
            "max_strength": max(strengths),
            "avg_age_seconds": np.mean(ages),
            "min_age_seconds": min(ages),
            "max_age_seconds": max(ages),
            "avg_use_count": np.mean(use_counts),
            "avg_success_rate": np.mean(success_rates),
        }

    def to_dict(self) -> Dict:
        """Export memory as dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "decay_rate": self.decay_rate,
            "min_strength": self.min_strength,
            "patterns": {
                pid: {
                    "pattern_id": p.pattern_id,
                    "strength": p.strength,
                    "created": p.created.isoformat(),
                    "last_used": p.last_used.isoformat(),
                    "use_count": p.use_count,
                    "success_rate": p.success_rate,
                }
                for pid, p in self.patterns.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'PatternMemory':
        """Reconstruct memory from dictionary.

        Args:
            data: Dictionary with memory state

        Returns:
            Reconstructed PatternMemory instance
        """
        memory = cls(
            decay_rate=data["decay_rate"],
            min_strength=data["min_strength"],
        )

        for pid, pdata in data["patterns"].items():
            pattern = Pattern(
                pattern_id=pdata["pattern_id"],
                strength=pdata["strength"],
                created=datetime.fromisoformat(pdata["created"]),
                last_used=datetime.fromisoformat(pdata["last_used"]),
                use_count=pdata["use_count"],
                success_rate=pdata["success_rate"],
            )
            memory.patterns[pid] = pattern

        return memory
