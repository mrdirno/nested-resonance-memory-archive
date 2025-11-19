#!/usr/bin/env python3
"""
DUALITY-ZERO-V2 Pattern Memory Module

This module implements the memory persistence layer for storing discovered
patterns, agent states, and historical data for learning and evolution.

Constitution Compliance:
- Reality-grounded pattern storage
- SQLite-backed persistence
- Efficient retrieval for decision-making
- Pattern emergence tracking
"""

import sqlite3
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Generator
from contextlib import contextmanager
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class PatternType(Enum):
    """Types of patterns that can be stored."""
    SYSTEM_BEHAVIOR = "system_behavior"
    TASK_EXECUTION = "task_execution"
    RESOURCE_USAGE = "resource_usage"
    ERROR_RECOVERY = "error_recovery"
    OPTIMIZATION = "optimization"
    FRACTAL_STATE = "fractal_state"
    EMERGENCE = "emergence"


@dataclass
class Pattern:
    """Represents a discovered pattern."""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    data: Dict[str, Any]
    confidence: float  # 0.0 to 1.0
    occurrences: int
    first_seen: float
    last_seen: float
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary."""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'name': self.name,
            'description': self.description,
            'data': self.data,
            'confidence': self.confidence,
            'occurrences': self.occurrences,
            'first_seen': self.first_seen,
            'last_seen': self.last_seen,
            'metadata': self.metadata or {}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create pattern from dictionary."""
        return cls(
            pattern_id=data['pattern_id'],
            pattern_type=PatternType(data['pattern_type']),
            name=data['name'],
            description=data['description'],
            data=data['data'],
            confidence=data['confidence'],
            occurrences=data['occurrences'],
            first_seen=data['first_seen'],
            last_seen=data['last_seen'],
            metadata=data.get('metadata')
        )


class PatternMemory:
    """
    Pattern memory system for storing and retrieving discovered patterns.

    Uses SQLite for efficient persistence and querying.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        """
        Initialize pattern memory.

        Args:
            workspace_path: Path to workspace directory
        """
        if workspace_path is None:
            workspace_path = Path(__file__).parent.parent / "workspace"

        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)

        self.db_path = self.workspace_path / "memory.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialize memory database schema."""
        with self._db_connection() as conn:
            # Patterns table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS patterns (
                    pattern_id TEXT PRIMARY KEY,
                    pattern_type TEXT,
                    name TEXT,
                    description TEXT,
                    data TEXT,
                    confidence REAL,
                    occurrences INTEGER,
                    first_seen REAL,
                    last_seen REAL,
                    metadata TEXT
                )
            """)

            # Agent states table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_states (
                    state_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    agent_id TEXT,
                    agent_type TEXT,
                    state_data TEXT,
                    metrics TEXT,
                    parent_agent_id TEXT,
                    recursion_depth INTEGER
                )
            """)

            # Metrics history table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics_history (
                    timestamp REAL PRIMARY KEY,
                    metric_type TEXT,
                    metric_name TEXT,
                    value REAL,
                    context TEXT
                )
            """)

            # Learning episodes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_episodes (
                    episode_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    episode_type TEXT,
                    initial_state TEXT,
                    actions_taken TEXT,
                    outcome TEXT,
                    reward REAL,
                    patterns_discovered TEXT
                )
            """)

            # Pattern relationships table (for tracking pattern emergence)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_relationships (
                    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    parent_pattern_id TEXT,
                    child_pattern_id TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    FOREIGN KEY (parent_pattern_id) REFERENCES patterns(pattern_id),
                    FOREIGN KEY (child_pattern_id) REFERENCES patterns(pattern_id)
                )
            """)

            # Memetic embeddings table (NRM V2 integration)
            # Stores vector representations of patterns for semantic similarity
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pattern_embeddings (
                    embedding_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE,
                    embedding_vector TEXT,  -- JSON array of floats
                    embedding_model TEXT,   -- Model name (e.g., "all-mpnet-base-v2")
                    embedding_dim INTEGER,  -- Vector dimensionality
                    timestamp REAL,
                    FOREIGN KEY (pattern_id) REFERENCES patterns(pattern_id)
                )
            """)

            # Semantic graph weights (sparse adjacency matrix W)
            # Encodes semantic similarity and co-occurrence relationships
            conn.execute("""
                CREATE TABLE IF NOT EXISTS semantic_graph (
                    edge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id_i TEXT,
                    pattern_id_j TEXT,
                    weight REAL,           -- Edge weight W_ij
                    weight_type TEXT,      -- 'semantic', 'cooccurrence', 'composite'
                    last_updated REAL,
                    FOREIGN KEY (pattern_id_i) REFERENCES patterns(pattern_id),
                    FOREIGN KEY (pattern_id_j) REFERENCES patterns(pattern_id)
                )
            """)

            # Indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_patterns_type
                ON patterns(pattern_type, confidence DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_agent_states_agent_id
                ON agent_states(agent_id, timestamp DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_history_type
                ON metrics_history(metric_type, timestamp DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_learning_episodes_type
                ON learning_episodes(episode_type, timestamp DESC)
            """)

            conn.commit()

    @contextmanager
    def _db_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def store_pattern(self, pattern: Pattern) -> None:
        """
        Store or update a pattern in memory.

        Args:
            pattern: Pattern to store
        """
        with self._db_connection() as conn:
            # Check if pattern exists
            cursor = conn.execute("""
                SELECT occurrences FROM patterns WHERE pattern_id = ?
            """, (pattern.pattern_id,))
            existing = cursor.fetchone()

            if existing:
                # Update existing pattern
                pattern.occurrences = existing[0] + 1
                pattern.last_seen = time.time()

            conn.execute("""
                INSERT OR REPLACE INTO patterns
                (pattern_id, pattern_type, name, description, data,
                 confidence, occurrences, first_seen, last_seen, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id, pattern.pattern_type.value,
                pattern.name, pattern.description,
                json.dumps(pattern.data), pattern.confidence,
                pattern.occurrences, pattern.first_seen,
                pattern.last_seen, json.dumps(pattern.metadata or {})
            ))
            conn.commit()

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """
        Retrieve a pattern by ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern object or None if not found
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM patterns WHERE pattern_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))
            data['data'] = json.loads(data['data'])
            data['metadata'] = json.loads(data['metadata'])

            return Pattern.from_dict(data)

    def search_patterns(
        self,
        pattern_type: Optional[PatternType] = None,
        name_like: Optional[str] = None,
        data_query: Optional[Dict[str, Any]] = None,
        metadata_query: Optional[Dict[str, Any]] = None,
        min_confidence: float = 0.0,
        sort_by: str = 'confidence',
        sort_order: str = 'DESC',
        limit: int = 100
    ) -> List[Pattern]:
        """
        Search for patterns matching criteria with advanced filtering and sorting.

        Args:
            pattern_type: Optional pattern type filter.
            name_like: Optional pattern name filter (case-insensitive LIKE).
            data_query: Optional dictionary to query JSON 'data' field.
            metadata_query: Optional dictionary to query JSON 'metadata' field.
            min_confidence: Minimum confidence threshold.
            sort_by: Field to sort by (e.g., 'confidence', 'last_seen', 'occurrences').
            sort_order: 'ASC' or 'DESC'.
            limit: Maximum number of results.

        Returns:
            List of matching patterns.
        """
        query = "SELECT * FROM patterns WHERE confidence >= ?"
        params = [min_confidence]

        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type.value)
        
        if name_like:
            query += " AND name LIKE ?"
            params.append(f"%{name_like}%")

        # The rest of the implementation will require iterating through the results
        # and filtering in Python, as direct JSON querying can be complex with pure SQL
        # across different SQLite versions.

        if sort_by not in ['confidence', 'last_seen', 'occurrences', 'first_seen', 'name']:
            sort_by = 'confidence'
        
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'

        query += f" ORDER BY {sort_by} {sort_order}, last_seen DESC"
        query += " LIMIT ?"
        params.append(limit)
        
        patterns = []
        with self._db_connection() as conn:
            cursor = conn.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                data['data'] = json.loads(data['data'])
                data['metadata'] = json.loads(data['metadata'])
                
                # In-memory filtering for JSON fields
                match = True
                if data_query:
                    for key, value in data_query.items():
                        if data['data'].get(key) != value:
                            match = False
                            break
                if not match: continue

                if metadata_query:
                    for key, value in metadata_query.items():
                        if data['metadata'].get(key) != value:
                            match = False
                            break
                if not match: continue
                
                patterns.append(Pattern.from_dict(data))
                
            return patterns

    def save_agent_state(
        self,
        agent_id: str,
        agent_type: str,
        state_data: Dict[str, Any],
        metrics: Optional[Dict[str, Any]] = None,
        parent_agent_id: Optional[str] = None,
        recursion_depth: int = 0
    ) -> None:
        """
        Save agent state snapshot.

        Args:
            agent_id: Agent identifier
            agent_type: Type of agent
            state_data: Agent state dictionary
            metrics: Optional metrics dictionary
            parent_agent_id: Optional parent agent ID for nested agents
            recursion_depth: Current recursion depth
        """
        with self._db_connection() as conn:
            conn.execute("""
                INSERT INTO agent_states
                (timestamp, agent_id, agent_type, state_data, metrics,
                 parent_agent_id, recursion_depth)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(), agent_id, agent_type,
                json.dumps(state_data),
                json.dumps(metrics or {}),
                parent_agent_id, recursion_depth
            ))
            conn.commit()

    def get_agent_history(
        self,
        agent_id: str,
        hours: float = 24.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve agent state history.

        Args:
            agent_id: Agent identifier
            hours: Number of hours of history to retrieve

        Returns:
            List of agent state snapshots
        """
        cutoff = time.time() - (hours * 3600)

        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM agent_states
                WHERE agent_id = ? AND timestamp >= ?
                ORDER BY timestamp DESC
            """, (agent_id, cutoff))

            columns = [desc[0] for desc in cursor.description]
            states = []

            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                data['state_data'] = json.loads(data['state_data'])
                data['metrics'] = json.loads(data['metrics'])
                states.append(data)

            return states

    def record_metric(
        self,
        metric_type: str,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Record a metric value.

        Args:
            metric_type: Type of metric (e.g., 'performance', 'resource')
            metric_name: Name of metric
            value: Metric value
            context: Optional context dictionary
        """
        with self._db_connection() as conn:
            conn.execute("""
                INSERT INTO metrics_history
                (timestamp, metric_type, metric_name, value, context)
                VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(), metric_type, metric_name, value,
                json.dumps(context or {})
            ))
            conn.commit()

    def get_metric_history(
        self,
        metric_type: str,
        metric_name: str,
        hours: float = 24.0
    ) -> List[Tuple[float, float]]:
        """
        Retrieve metric history.

        Args:
            metric_type: Type of metric
            metric_name: Name of metric
            hours: Number of hours of history

        Returns:
            List of (timestamp, value) tuples
        """
        cutoff = time.time() - (hours * 3600)

        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT timestamp, value FROM metrics_history
                WHERE metric_type = ? AND metric_name = ? AND timestamp >= ?
                ORDER BY timestamp ASC
            """, (metric_type, metric_name, cutoff))

            return cursor.fetchall()

    def record_learning_episode(
        self,
        episode_type: str,
        initial_state: Dict[str, Any],
        actions_taken: List[str],
        outcome: Dict[str, Any],
        reward: float,
        patterns_discovered: Optional[List[str]] = None
    ) -> None:
        """
        Record a learning episode for future analysis.

        Args:
            episode_type: Type of learning episode
            initial_state: Initial state dictionary
            actions_taken: List of actions
            outcome: Outcome dictionary
            reward: Reward value (positive or negative)
            patterns_discovered: Optional list of pattern IDs discovered
        """
        with self._db_connection() as conn:
            conn.execute("""
                INSERT INTO learning_episodes
                (timestamp, episode_type, initial_state, actions_taken,
                 outcome, reward, patterns_discovered)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(), episode_type,
                json.dumps(initial_state),
                json.dumps(actions_taken),
                json.dumps(outcome),
                reward,
                json.dumps(patterns_discovered or [])
            ))
            conn.commit()

    def create_pattern_id(self, pattern_data: Dict[str, Any]) -> str:
        """
        Create a unique pattern ID based on pattern data.

        Args:
            pattern_data: Pattern data dictionary

        Returns:
            Unique pattern ID hash
        """
        # Create deterministic hash of pattern data
        data_str = json.dumps(pattern_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory system statistics.

        Returns:
            Statistics dictionary
        """
        with self._db_connection() as conn:
            # Pattern counts
            cursor = conn.execute("""
                SELECT pattern_type, COUNT(*) FROM patterns
                GROUP BY pattern_type
            """)
            pattern_counts = dict(cursor.fetchall())

            # Total patterns
            cursor = conn.execute("SELECT COUNT(*) FROM patterns")
            total_patterns = cursor.fetchone()[0]

            # Agent state count
            cursor = conn.execute("SELECT COUNT(*) FROM agent_states")
            agent_states = cursor.fetchone()[0]

            # Metrics count
            cursor = conn.execute("SELECT COUNT(*) FROM metrics_history")
            metrics_count = cursor.fetchone()[0]

            # Learning episodes
            cursor = conn.execute("SELECT COUNT(*) FROM learning_episodes")
            episodes = cursor.fetchone()[0]

            # Average pattern confidence
            cursor = conn.execute("SELECT AVG(confidence) FROM patterns")
            avg_confidence = cursor.fetchone()[0] or 0.0

        return {
            'total_patterns': total_patterns,
            'patterns_by_type': pattern_counts,
            'agent_states_stored': agent_states,
            'metrics_recorded': metrics_count,
            'learning_episodes': episodes,
            'average_pattern_confidence': avg_confidence,
            'database_path': str(self.db_path)
        }

    # ============================================================================
    # NRM V2: Memetic Embedding Support
    # ============================================================================

    def store_embedding(
        self,
        pattern_id: str,
        embedding_vector: List[float],
        embedding_model: str = "local",
        embedding_dim: Optional[int] = None
    ) -> None:
        """
        Store embedding vector for a pattern.

        Part of NRM V2 integration: enables semantic similarity computation
        and Kuramoto-style coalition detection in embedding space.

        Args:
            pattern_id: Pattern identifier
            embedding_vector: Vector representation (list of floats)
            embedding_model: Model name used for embedding
            embedding_dim: Optional dimensionality (auto-detected if None)
        """
        if embedding_dim is None:
            embedding_dim = len(embedding_vector)

        with self._db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO pattern_embeddings
                (pattern_id, embedding_vector, embedding_model, embedding_dim, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pattern_id,
                json.dumps(embedding_vector),
                embedding_model,
                embedding_dim,
                time.time()
            ))
            conn.commit()

    def get_embedding(self, pattern_id: str) -> Optional[List[float]]:
        """
        Retrieve embedding vector for a pattern.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Embedding vector or None if not found
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT embedding_vector FROM pattern_embeddings
                WHERE pattern_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            return json.loads(row[0])

    def store_graph_edge(
        self,
        pattern_id_i: str,
        pattern_id_j: str,
        weight: float,
        weight_type: str = 'composite'
    ) -> None:
        """
        Store or update edge in semantic graph (adjacency matrix W).

        Part of NRM V2 integration: builds sparse weighted graph connecting
        related patterns for Kuramoto coupling dynamics.

        Args:
            pattern_id_i: First pattern ID
            pattern_id_j: Second pattern ID
            weight: Edge weight W_ij (>= 0.0)
            weight_type: Type of weight ('semantic', 'cooccurrence', 'composite')
        """
        with self._db_connection() as conn:
            # Ensure symmetric storage (W_ij = W_ji)
            for (pi, pj) in [(pattern_id_i, pattern_id_j), (pattern_id_j, pattern_id_i)]:
                conn.execute("""
                    INSERT OR REPLACE INTO semantic_graph
                    (pattern_id_i, pattern_id_j, weight, weight_type, last_updated)
                    VALUES (?, ?, ?, ?, ?)
                """, (pi, pj, weight, weight_type, time.time()))
            conn.commit()

    def get_graph_neighbors(
        self,
        pattern_id: str,
        min_weight: float = 0.1,
        limit: int = 50
    ) -> List[Tuple[str, float]]:
        """
        Get neighbors of a pattern in semantic graph.

        Args:
            pattern_id: Pattern identifier
            min_weight: Minimum edge weight threshold
            limit: Maximum number of neighbors

        Returns:
            List of (neighbor_pattern_id, weight) tuples
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT pattern_id_j, weight FROM semantic_graph
                WHERE pattern_id_i = ? AND weight >= ?
                ORDER BY weight DESC
                LIMIT ?
            """, (pattern_id, min_weight, limit))

            return cursor.fetchall()

    def compute_semantic_similarity(
        self,
        embedding_i: List[float],
        embedding_j: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embedding vectors.

        Part of NRM V2: used for building semantic graph edges.

        Args:
            embedding_i: First embedding vector
            embedding_j: Second embedding vector

        Returns:
            Cosine similarity (0.0 to 1.0, where 1.0 = identical)
        """
        import math

        # Dot product
        dot_product = sum(a * b for a, b in zip(embedding_i, embedding_j))

        # Magnitudes
        mag_i = math.sqrt(sum(a * a for a in embedding_i))
        mag_j = math.sqrt(sum(b * b for b in embedding_j))

        # Cosine similarity
        if mag_i == 0.0 or mag_j == 0.0:
            return 0.0

        similarity = dot_product / (mag_i * mag_j)

        # Clamp to [0, 1] (convert from [-1, 1])
        return max(0.0, (similarity + 1.0) / 2.0)


# Module-level API
_memory = None

def get_memory() -> PatternMemory:
    """Get singleton pattern memory instance."""
    global _memory
    if _memory is None:
        _memory = PatternMemory()
    return _memory


if __name__ == "__main__":
    # Self-test
    print("DUALITY-ZERO-V2 Pattern Memory Self-Test")
    print("=" * 50)

    memory = PatternMemory()

    print("\n1. Storing Test Pattern")
    test_pattern = Pattern(
        pattern_id=memory.create_pattern_id({'test': 'data', 'value': 42}),
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        name="High Memory Usage Pattern",
        description="System exhibits high memory usage during peak hours",
        data={
            'average_memory': 75.3,
            'peak_hours': [9, 10, 14, 15],
            'process_contributors': ['python', 'node']
        },
        confidence=0.92,
        occurrences=1,
        first_seen=time.time(),
        last_seen=time.time(),
        metadata={'source': 'reality_monitor', 'version': 'v2.0'}
    )
    memory.store_pattern(test_pattern)
    print(f"   Stored: {test_pattern.name}")
    print(f"   Confidence: {test_pattern.confidence:.2%}")

    print("\n2. Retrieving Pattern")
    retrieved = memory.get_pattern(test_pattern.pattern_id)
    if retrieved:
        print(f"   Retrieved: {retrieved.name}")
        print(f"   Occurrences: {retrieved.occurrences}")
    else:
        print("   ❌ Pattern not found")

    print("\n3. Searching Patterns")
    patterns = memory.search_patterns(
        pattern_type=PatternType.SYSTEM_BEHAVIOR,
        min_confidence=0.8
    )
    print(f"   Found {len(patterns)} patterns with confidence >= 80%")
    for p in patterns[:3]:
        print(f"     - {p.name}: {p.confidence:.2%}")

    print("\n4. Saving Agent State")
    memory.save_agent_state(
        agent_id="agent_001",
        agent_type="fractal_optimizer",
        state_data={
            'iteration': 1,
            'energy': 0.95,
            'parameters': {'learning_rate': 0.01}
        },
        metrics={'accuracy': 0.87, 'loss': 0.13},
        recursion_depth=0
    )
    print("   ✅ Agent state saved")

    print("\n5. Recording Metric")
    memory.record_metric(
        metric_type="performance",
        metric_name="task_completion_rate",
        value=0.98,
        context={'cycle': 7, 'tasks': 6}
    )
    print("   ✅ Metric recorded")

    print("\n6. Recording Learning Episode")
    memory.record_learning_episode(
        episode_type="optimization",
        initial_state={'memory_usage': 80.0},
        actions_taken=['garbage_collection', 'cache_clear'],
        outcome={'memory_usage': 65.0},
        reward=15.0,
        patterns_discovered=[test_pattern.pattern_id]
    )
    print("   ✅ Learning episode recorded")

    print("\n7. Memory Statistics")
    stats = memory.get_statistics()
    print(f"   Total Patterns: {stats['total_patterns']}")
    print(f"   Agent States: {stats['agent_states_stored']}")
    print(f"   Metrics: {stats['metrics_recorded']}")
    print(f"   Learning Episodes: {stats['learning_episodes']}")
    print(f"   Avg Pattern Confidence: {stats['average_pattern_confidence']:.2%}")

    print("\n✅ Pattern Memory operational - ready for pattern learning")
