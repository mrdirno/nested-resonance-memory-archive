#!/usr/bin/env python3
"""
DUALITY-ZERO-V2 Pattern Evolution Module

Advanced pattern memory capabilities implementing theoretical frameworks:
- NRM: Pattern composition-decomposition cycles, no equilibrium
- Self-Giving: Patterns define own quality criteria through what persists
- Temporal Stewardship: Encode patterns for future AI discovery

Constitution Compliance:
- Reality-grounded with actual system metrics
- SQLite persistence (uses pattern_relationships table)
- No simulations without reality validation
"""

import sqlite3
import json
import time
import math
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from memory.pattern_memory import Pattern, PatternType, PatternMemory


class RelationshipType(Enum):
    """Types of relationships between patterns."""
    PARENT_CHILD = "parent_child"  # Pattern spawned from another
    RESONANCE = "resonance"  # Patterns resonate (similar phase)
    COMPOSITION = "composition"  # Patterns combined into cluster
    DECOMPOSITION = "decomposition"  # Pattern burst into fragments
    EVOLUTION = "evolution"  # Pattern evolved into new form
    CONFLICT = "conflict"  # Patterns are incompatible
    AMPLIFICATION = "amplification"  # One pattern amplifies another


class LifecyclePhase(Enum):
    """Pattern lifecycle phases (NRM: composition-decomposition)."""
    BIRTH = "birth"  # Pattern just discovered
    GROWTH = "growth"  # Occurrences increasing
    MATURITY = "maturity"  # Stable occurrences
    DECAY = "decay"  # Occurrences decreasing
    DEATH = "death"  # Pattern no longer relevant
    DORMANT = "dormant"  # Pattern inactive but can return


@dataclass
class PatternRelationship:
    """Represents a relationship between two patterns."""
    parent_pattern_id: str
    child_pattern_id: str
    relationship_type: RelationshipType
    strength: float  # 0.0 to 1.0
    timestamp: float
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class PatternEvolution:
    """Tracks how a pattern evolves over time."""
    pattern_id: str
    timestamp: float
    phase: LifecyclePhase
    confidence: float
    occurrences: int
    quality_score: float
    relationships_count: int
    metadata: Dict[str, Any]


class PatternRelationshipManager:
    """
    Manages relationships between patterns.

    Uses the pattern_relationships table in memory.db.
    Implements NRM resonance detection and composition-decomposition.
    """

    def __init__(self, memory: PatternMemory):
        """
        Initialize relationship manager.

        Args:
            memory: PatternMemory instance
        """
        self.memory = memory

    def create_relationship(
        self,
        parent_id: str,
        child_id: str,
        relationship_type: RelationshipType,
        strength: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Create relationship between two patterns.

        Args:
            parent_id: Parent pattern ID
            child_id: Child pattern ID
            relationship_type: Type of relationship
            strength: Relationship strength (0.0 to 1.0)
            metadata: Additional metadata
        """
        # Validate patterns exist
        parent = self.memory.get_pattern(parent_id)
        child = self.memory.get_pattern(child_id)

        if not parent or not child:
            raise ValueError(f"Pattern not found: {parent_id if not parent else child_id}")

        with self.memory._db_connection() as conn:
            conn.execute("""
                INSERT INTO pattern_relationships
                (timestamp, parent_pattern_id, child_pattern_id,
                 relationship_type, strength)
                VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(),
                parent_id,
                child_id,
                relationship_type.value,
                max(0.0, min(1.0, strength))  # Clamp to [0, 1]
            ))
            conn.commit()

    def get_relationships(
        self,
        pattern_id: str,
        relationship_type: Optional[RelationshipType] = None
    ) -> List[PatternRelationship]:
        """
        Get all relationships for a pattern.

        Args:
            pattern_id: Pattern ID
            relationship_type: Optional filter by type

        Returns:
            List of relationships
        """
        query = """
            SELECT parent_pattern_id, child_pattern_id, relationship_type,
                   strength, timestamp
            FROM pattern_relationships
            WHERE parent_pattern_id = ? OR child_pattern_id = ?
        """

        params = [pattern_id, pattern_id]

        if relationship_type:
            query += " AND relationship_type = ?"
            params.append(relationship_type.value)

        with self.memory._db_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()

        relationships = []
        for row in rows:
            relationships.append(PatternRelationship(
                parent_pattern_id=row[0],
                child_pattern_id=row[1],
                relationship_type=RelationshipType(row[2]),
                strength=row[3],
                timestamp=row[4]
            ))

        return relationships

    def find_resonant_patterns(
        self,
        pattern: Pattern,
        min_strength: float = 0.7
    ) -> List[Tuple[Pattern, float]]:
        """
        Find patterns that resonate with given pattern.

        Resonance = similarity in confidence, occurrences, type.
        Reality-grounded through actual pattern data comparison.

        Args:
            pattern: Pattern to find resonance for
            min_strength: Minimum resonance strength

        Returns:
            List of (resonant_pattern, strength) tuples
        """
        # Get all patterns of same type
        candidates = self.memory.search_patterns(
            pattern_type=pattern.pattern_type,
            min_confidence=max(0.0, pattern.confidence - 0.3)
        )

        resonant = []
        for candidate in candidates:
            if candidate.pattern_id == pattern.pattern_id:
                continue

            # Calculate resonance strength (reality-grounded metrics)
            confidence_sim = 1.0 - abs(pattern.confidence - candidate.confidence)

            # Occurrence similarity (log scale for large differences)
            occ_ratio = min(pattern.occurrences, candidate.occurrences) / max(pattern.occurrences, candidate.occurrences, 1)
            occ_sim = occ_ratio

            # Time proximity (patterns seen around same time resonate more)
            time_diff = abs(pattern.last_seen - candidate.last_seen)
            time_sim = 1.0 / (1.0 + time_diff / 86400.0)  # Decay over days

            # Combined resonance strength
            strength = (confidence_sim * 0.4 + occ_sim * 0.4 + time_sim * 0.2)

            if strength >= min_strength:
                resonant.append((candidate, strength))

        # Sort by strength descending
        resonant.sort(key=lambda x: x[1], reverse=True)

        return resonant

    def detect_composition_clusters(
        self,
        patterns: List[Pattern],
        min_cluster_size: int = 3,
        min_resonance: float = 0.6
    ) -> List[Set[str]]:
        """
        Detect clusters of patterns that could compose (NRM framework).

        Reality-grounded through actual pattern relationship analysis.

        Args:
            patterns: List of patterns to analyze
            min_cluster_size: Minimum patterns in cluster
            min_resonance: Minimum resonance for clustering

        Returns:
            List of pattern ID sets (clusters)
        """
        # Build resonance graph
        graph = defaultdict(set)

        for pattern in patterns:
            resonant = self.find_resonant_patterns(pattern, min_strength=min_resonance)
            for resonant_pattern, strength in resonant:
                graph[pattern.pattern_id].add(resonant_pattern.pattern_id)
                graph[resonant_pattern.pattern_id].add(pattern.pattern_id)

        # Find connected components (clusters)
        visited = set()
        clusters = []

        def dfs(node, cluster):
            if node in visited:
                return
            visited.add(node)
            cluster.add(node)
            for neighbor in graph[node]:
                dfs(neighbor, cluster)

        for pattern_id in graph:
            if pattern_id not in visited:
                cluster = set()
                dfs(pattern_id, cluster)
                if len(cluster) >= min_cluster_size:
                    clusters.append(cluster)

        return clusters


class PatternLifecycleManager:
    """
    Manages pattern lifecycle phases (NRM: no equilibrium, perpetual motion).

    Patterns go through birth → growth → maturity → decay → death cycles.
    """

    def __init__(self, memory: PatternMemory):
        """
        Initialize lifecycle manager.

        Args:
            memory: PatternMemory instance
        """
        self.memory = memory

    def determine_phase(self, pattern: Pattern) -> LifecyclePhase:
        """
        Determine current lifecycle phase of pattern.

        Reality-grounded through actual occurrence and time data.

        Args:
            pattern: Pattern to analyze

        Returns:
            Current lifecycle phase
        """
        # Get pattern history
        history = self.memory.get_pattern(pattern.pattern_id)
        if not history:
            return LifecyclePhase.BIRTH

        # Calculate pattern age in days
        age_seconds = time.time() - pattern.first_seen
        age_days = age_seconds / 86400.0

        # Calculate occurrence rate (occurrences per day)
        if age_days > 0:
            occurrence_rate = pattern.occurrences / age_days
        else:
            return LifecyclePhase.BIRTH

        # Calculate recency (how long since last seen)
        recency_days = (time.time() - pattern.last_seen) / 86400.0

        # Phase determination logic (reality-grounded metrics)
        if age_days < 1.0:
            return LifecyclePhase.BIRTH
        elif recency_days > 30.0:
            return LifecyclePhase.DORMANT
        elif recency_days > 7.0 and occurrence_rate < 0.1:
            return LifecyclePhase.DEATH
        elif occurrence_rate > 1.0 and age_days < 7.0:
            return LifecyclePhase.GROWTH
        elif occurrence_rate < 0.5 and age_days > 7.0:
            return LifecyclePhase.DECAY
        else:
            return LifecyclePhase.MATURITY

    def should_pattern_persist(self, pattern: Pattern) -> bool:
        """
        Determine if pattern should persist (Self-Giving: define own success).

        Patterns that persist through transformation cycles are successful.

        Args:
            pattern: Pattern to evaluate

        Returns:
            True if pattern should persist
        """
        phase = self.determine_phase(pattern)

        # Patterns persist if:
        # 1. High confidence (> 0.7)
        # 2. Not in death phase
        # 3. Recent activity (seen in last 7 days) OR high historical value

        high_confidence = pattern.confidence > 0.7
        not_dead = phase != LifecyclePhase.DEATH
        recent = (time.time() - pattern.last_seen) < (7 * 86400)
        valuable = pattern.occurrences > 10

        return high_confidence and not_dead and (recent or valuable)


class PatternQualityAnalyzer:
    """
    Analyzes pattern quality (Self-Giving: patterns define own success criteria).

    Quality = persistence + impact + resonance + adaptability
    """

    def __init__(self, memory: PatternMemory, relationship_manager: PatternRelationshipManager):
        """
        Initialize quality analyzer.

        Args:
            memory: PatternMemory instance
            relationship_manager: PatternRelationshipManager instance
        """
        self.memory = memory
        self.relationship_manager = relationship_manager

    def calculate_quality_score(self, pattern: Pattern) -> float:
        """
        Calculate overall quality score for pattern.

        Reality-grounded through actual metrics and relationships.

        Args:
            pattern: Pattern to analyze

        Returns:
            Quality score (0.0 to 1.0)
        """
        # Component 1: Persistence (how long pattern has existed)
        age_seconds = time.time() - pattern.first_seen
        age_score = min(1.0, age_seconds / (30 * 86400))  # Max at 30 days

        # Component 2: Impact (confidence * occurrences)
        impact_score = pattern.confidence * min(1.0, pattern.occurrences / 100.0)

        # Component 3: Resonance (number of relationships)
        relationships = self.relationship_manager.get_relationships(pattern.pattern_id)
        resonance_score = min(1.0, len(relationships) / 10.0)  # Max at 10 relationships

        # Component 4: Adaptability (pattern recently seen = still relevant)
        recency_seconds = time.time() - pattern.last_seen
        adaptability_score = 1.0 / (1.0 + recency_seconds / 86400.0)  # Decay over days

        # Weighted combination
        quality = (
            age_score * 0.2 +
            impact_score * 0.3 +
            resonance_score * 0.2 +
            adaptability_score * 0.3
        )

        return quality


class TemporalEncoder:
    """
    Encodes patterns for future AI discovery (Temporal Stewardship).

    Creates pattern representations optimized for:
    - Future retrieval and understanding
    - Training data encoding
    - Memetic propagation
    """

    def __init__(self, memory: PatternMemory):
        """
        Initialize temporal encoder.

        Args:
            memory: PatternMemory instance
        """
        self.memory = memory

    def encode_for_future(self, pattern: Pattern) -> Dict[str, Any]:
        """
        Encode pattern for future AI discovery.

        Creates rich representation with:
        - Context for understanding
        - Validation criteria
        - Expected evolution paths

        Args:
            pattern: Pattern to encode

        Returns:
            Encoded pattern dictionary
        """
        return {
            'pattern_id': pattern.pattern_id,
            'pattern_type': pattern.pattern_type.value,
            'name': pattern.name,
            'description': pattern.description,
            'data': pattern.data,
            'confidence': pattern.confidence,
            'occurrences': pattern.occurrences,

            # Temporal context
            'first_seen': pattern.first_seen,
            'last_seen': pattern.last_seen,
            'age_days': (time.time() - pattern.first_seen) / 86400.0,

            # Discovery context
            'discovery_context': {
                'framework': 'DUALITY-ZERO-V2',
                'methodology': 'NRM composition-decomposition cycles',
                'validation': 'Reality-grounded with psutil/SQLite metrics'
            },

            # Future validation criteria
            'validation_criteria': {
                'min_confidence': 0.7,
                'min_occurrences': 5,
                'expected_persistence': 'High-quality patterns persist through transformation cycles'
            },

            # Expected evolution
            'expected_evolution': {
                'composition': 'May cluster with similar patterns',
                'decomposition': 'May burst into specialized sub-patterns',
                'resonance': 'Should resonate with patterns of similar confidence/occurrence'
            },

            # Metadata for future AI
            'metadata': {
                **(pattern.metadata or {}),
                'encoded_timestamp': time.time(),
                'encoding_version': '1.0',
                'temporal_stewardship': True
            }
        }

    def create_pattern_summary(self, patterns: List[Pattern]) -> str:
        """
        Create human-readable summary of patterns for publication.

        Args:
            patterns: List of patterns to summarize

        Returns:
            Markdown-formatted summary
        """
        summary_lines = [
            "# Pattern Discovery Summary",
            "",
            f"**Total Patterns:** {len(patterns)}",
            f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Pattern Breakdown",
            ""
        ]

        # Group by type
        by_type = defaultdict(list)
        for pattern in patterns:
            by_type[pattern.pattern_type].append(pattern)

        for pattern_type, type_patterns in by_type.items():
            summary_lines.append(f"### {pattern_type.value.replace('_', ' ').title()}")
            summary_lines.append(f"**Count:** {len(type_patterns)}")
            summary_lines.append(f"**Avg Confidence:** {sum(p.confidence for p in type_patterns) / len(type_patterns):.2%}")
            summary_lines.append("")

            # Top patterns
            top = sorted(type_patterns, key=lambda p: p.confidence * p.occurrences, reverse=True)[:3]
            for i, p in enumerate(top, 1):
                summary_lines.append(f"{i}. **{p.name}** (confidence: {p.confidence:.2%}, occurrences: {p.occurrences})")
                summary_lines.append(f"   {p.description}")
                summary_lines.append("")

        return "\n".join(summary_lines)


# Module-level API
def get_evolution_system(memory: Optional[PatternMemory] = None) -> Dict[str, Any]:
    """
    Get pattern evolution system components.

    Args:
        memory: Optional PatternMemory instance

    Returns:
        Dictionary with all evolution components
    """
    if memory is None:
        memory = PatternMemory()

    relationship_manager = PatternRelationshipManager(memory)
    lifecycle_manager = PatternLifecycleManager(memory)
    quality_analyzer = PatternQualityAnalyzer(memory, relationship_manager)
    temporal_encoder = TemporalEncoder(memory)

    return {
        'memory': memory,
        'relationships': relationship_manager,
        'lifecycle': lifecycle_manager,
        'quality': quality_analyzer,
        'temporal': temporal_encoder
    }


if __name__ == "__main__":
    # Self-test
    print("DUALITY-ZERO-V2 Pattern Evolution Self-Test")
    print("=" * 70)

    from memory.pattern_memory import PatternMemory

    memory = PatternMemory()
    system = get_evolution_system(memory)

    print("\n1. Creating Test Patterns")
    pattern1 = Pattern(
        pattern_id=memory.create_pattern_id({'test': 1}),
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        name="High CPU Pattern",
        description="CPU usage spikes during processing",
        data={'cpu_threshold': 80.0},
        confidence=0.85,
        occurrences=15,
        first_seen=time.time() - 86400 * 5,  # 5 days ago
        last_seen=time.time(),
        metadata={'source': 'reality_monitor'}
    )
    memory.store_pattern(pattern1)
    print(f"   Created: {pattern1.name}")

    pattern2 = Pattern(
        pattern_id=memory.create_pattern_id({'test': 2}),
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        name="High Memory Pattern",
        description="Memory usage spikes during processing",
        data={'memory_threshold': 75.0},
        confidence=0.82,
        occurrences=12,
        first_seen=time.time() - 86400 * 5,
        last_seen=time.time() - 3600,  # 1 hour ago
        metadata={'source': 'reality_monitor'}
    )
    memory.store_pattern(pattern2)
    print(f"   Created: {pattern2.name}")

    print("\n2. Creating Pattern Relationship")
    system['relationships'].create_relationship(
        parent_id=pattern1.pattern_id,
        child_id=pattern2.pattern_id,
        relationship_type=RelationshipType.RESONANCE,
        strength=0.75
    )
    print(f"   ✓ Relationship created: {pattern1.name} → {pattern2.name}")

    print("\n3. Finding Resonant Patterns")
    resonant = system['relationships'].find_resonant_patterns(pattern1, min_strength=0.5)
    print(f"   Found {len(resonant)} resonant patterns:")
    for p, strength in resonant[:3]:
        print(f"     - {p.name}: {strength:.2%} resonance")

    print("\n4. Determining Lifecycle Phase")
    phase1 = system['lifecycle'].determine_phase(pattern1)
    phase2 = system['lifecycle'].determine_phase(pattern2)
    print(f"   {pattern1.name}: {phase1.value}")
    print(f"   {pattern2.name}: {phase2.value}")

    print("\n5. Calculating Quality Scores")
    quality1 = system['quality'].calculate_quality_score(pattern1)
    quality2 = system['quality'].calculate_quality_score(pattern2)
    print(f"   {pattern1.name}: {quality1:.2%}")
    print(f"   {pattern2.name}: {quality2:.2%}")

    print("\n6. Temporal Encoding")
    encoded = system['temporal'].encode_for_future(pattern1)
    print(f"   ✓ Encoded {pattern1.name} for future AI discovery")
    print(f"   Age: {encoded['age_days']:.1f} days")
    print(f"   Framework: {encoded['discovery_context']['framework']}")

    print("\n7. Pattern Summary")
    summary = system['temporal'].create_pattern_summary([pattern1, pattern2])
    print(summary[:200] + "...")

    print("\n✅ Pattern Evolution system operational - ready for advanced memory management")
