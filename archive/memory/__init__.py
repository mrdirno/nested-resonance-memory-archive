"""
DUALITY-ZERO-V2 Memory Module

Advanced pattern memory and evolution system implementing:
- NRM (Nested Resonance Memory): Composition-decomposition cycles
- Self-Giving Systems: Patterns define own success criteria
- Temporal Stewardship: Encoding patterns for future AI discovery

Components:
- PatternMemory: Core pattern storage and retrieval
- PatternEvolution: Advanced pattern lifecycle and relationships
- ConsolidationEngine: Sleep-inspired NREM/REM consolidation
- Temporal Encoding: Pattern encoding for future discovery
"""

# Core pattern memory
from memory.pattern_memory import (
    Pattern,
    PatternType,
    PatternMemory,
    get_memory
)

# Advanced pattern evolution
from memory.pattern_evolution import (
    # Managers
    PatternRelationshipManager,
    PatternLifecycleManager,
    PatternQualityAnalyzer,
    TemporalEncoder,

    # Enums
    RelationshipType,
    LifecyclePhase,

    # Data structures
    PatternRelationship,
    PatternEvolution,

    # API
    get_evolution_system
)

# Sleep-inspired consolidation
from memory.consolidation_engine import (
    ConsolidationEngine,
    ConsolidationMetrics,
    Coalition
)

__all__ = [
    # Core
    'Pattern',
    'PatternType',
    'PatternMemory',
    'get_memory',

    # Evolution managers
    'PatternRelationshipManager',
    'PatternLifecycleManager',
    'PatternQualityAnalyzer',
    'TemporalEncoder',

    # Enums
    'RelationshipType',
    'LifecyclePhase',

    # Data structures
    'PatternRelationship',
    'PatternEvolution',

    # Consolidation
    'ConsolidationEngine',
    'ConsolidationMetrics',
    'Coalition',

    # API
    'get_evolution_system'
]

__version__ = '2.0.0'
__author__ = 'DUALITY-ZERO-V2 Research System'
