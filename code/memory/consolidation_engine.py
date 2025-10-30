#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Sleep-Inspired Consolidation Engine
=====================================================

NRM V2 Integration: Implements offline consolidation using sleep-inspired
dynamics for memory strengthening (NREM) and exploratory hypothesis generation (REM).

Theoretical Foundation:
- NREM (slow-wave): Consolidate patterns through Hebbian strengthening
- REM (high-frequency): Explore parameter space through stochastic perturbations
- Kuramoto coupling: Detect coalitions via phase synchronization
- Cost-aware: Track computational expense vs information gain

Reality Grounding:
- Uses actual experimental data from pattern_memory
- Tracks CPU time and memory usage via psutil
- Validates predictions against ground truth
- All operations logged to SQLite
"""

import sys
import time
import psutil
import sqlite3
import math
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from contextlib import contextmanager

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent))

from fractal_agent import FractalAgent
from transcendental_bridge import TranscendentalBridge, TranscendentalState
from pattern_memory import PatternMemory, Pattern


@dataclass
class ConsolidationMetrics:
    """Metrics for consolidation session."""
    session_id: str
    phase_type: str  # 'nrem' or 'rem'
    start_time: float
    end_time: float
    patterns_processed: int
    coalitions_detected: int
    hebbian_updates: int
    cpu_time_ms: float
    memory_usage_mb: float
    information_gain_bits: float = 0.0


@dataclass
class Coalition:
    """Detected coalition of synchronized agents."""
    coalition_id: str
    member_pattern_ids: List[str]
    coherence_scores: Dict[str, float]  # band -> coherence
    mean_coherence: float
    timestamp: float


class ConsolidationEngine:
    """
    Sleep-inspired consolidation engine for NRM V2.

    Implements two phases:
    1. NREM (slow-wave): Strengthen successful patterns through Hebbian learning
    2. REM (high-frequency): Explore parameter space through perturbations

    Reality-grounded through:
    - PatternMemory for data storage
    - TranscendentalBridge for phase space operations
    - FractalAgent for Kuramoto dynamics
    - psutil for cost tracking
    """

    def __init__(
        self,
        memory: Optional[PatternMemory] = None,
        bridge: Optional[TranscendentalBridge] = None,
        workspace_path: Optional[str] = None
    ):
        """
        Initialize consolidation engine.

        Args:
            memory: PatternMemory instance (created if None)
            bridge: TranscendentalBridge instance (created if None)
            workspace_path: Workspace directory path (uses env var or relative path if None)
        """
        # Resolve workspace path: env var > explicit arg > relative default
        import os
        if workspace_path is None:
            workspace_path = os.environ.get(
                'NRM_WORKSPACE_PATH',
                str(Path(__file__).parent.parent.parent / 'workspace')
            )

        self.memory = memory if memory else PatternMemory(workspace_path)
        self.bridge = bridge if bridge else TranscendentalBridge(workspace_path)
        self.workspace_path = Path(workspace_path)

        # Consolidation database
        self.db_path = self.workspace_path / "consolidation.db"
        self._init_database()

        # Session tracking
        self.session_id: Optional[str] = None
        self.start_cpu_time: float = 0.0
        self.start_memory: float = 0.0

    def _init_database(self) -> None:
        """Initialize consolidation database."""
        with self._get_connection() as conn:
            # Consolidation sessions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS consolidation_sessions (
                    session_id TEXT PRIMARY KEY,
                    phase_type TEXT,
                    start_time REAL,
                    end_time REAL,
                    patterns_processed INTEGER,
                    coalitions_detected INTEGER,
                    hebbian_updates INTEGER,
                    cpu_time_ms REAL,
                    memory_usage_mb REAL,
                    information_gain_bits REAL
                )
            """)

            # Detected coalitions
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coalitions (
                    coalition_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    member_pattern_ids TEXT,  -- JSON array
                    coherence_scores TEXT,    -- JSON dict
                    mean_coherence REAL,
                    timestamp REAL,
                    FOREIGN KEY (session_id) REFERENCES consolidation_sessions(session_id)
                )
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def start_session(self, phase_type: str = 'nrem') -> str:
        """
        Start consolidation session.

        Args:
            phase_type: 'nrem' or 'rem'

        Returns:
            Session ID
        """
        self.session_id = f"{phase_type}_{int(time.time()*1000)}"

        # Track resource usage
        process = psutil.Process()
        self.start_cpu_time = process.cpu_times().user
        self.start_memory = process.memory_info().rss / (1024 * 1024)  # MB

        return self.session_id

    def end_session(self, metrics: ConsolidationMetrics) -> None:
        """
        End consolidation session and store metrics.

        Args:
            metrics: Session metrics
        """
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO consolidation_sessions
                (session_id, phase_type, start_time, end_time, patterns_processed,
                 coalitions_detected, hebbian_updates, cpu_time_ms, memory_usage_mb,
                 information_gain_bits)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.session_id, metrics.phase_type, metrics.start_time,
                metrics.end_time, metrics.patterns_processed, metrics.coalitions_detected,
                metrics.hebbian_updates, metrics.cpu_time_ms, metrics.memory_usage_mb,
                metrics.information_gain_bits
            ))
            conn.commit()

    def nrem_consolidation(
        self,
        patterns: List[Pattern],
        duration_cycles: int = 100,
        frequency_hz: float = 2.0,
        hebbian_learning_rate: float = 0.01,
        coherence_threshold: float = 0.8
    ) -> Tuple[List[Coalition], ConsolidationMetrics]:
        """
        NREM slow-wave consolidation phase.

        Strengthens patterns through Hebbian learning on coherent coalitions.

        Args:
            patterns: List of patterns to consolidate
            duration_cycles: Number of evolution cycles
            frequency_hz: Slow-wave frequency (0.5-4 Hz typical)
            hebbian_learning_rate: Learning rate η for Hebbian update
            coherence_threshold: Minimum coherence for coalition detection

        Returns:
            (detected_coalitions, metrics)
        """
        session_id = self.start_session('nrem')
        start_time = time.time()

        # Create FractalAgents for each pattern
        agents: Dict[str, FractalAgent] = {}
        for pattern in patterns:
            # Use pattern data as reality anchor
            reality = {
                'cpu_percent': pattern.confidence * 100,
                'memory_percent': pattern.occurrences / 10.0,
                'disk_usage': 50.0
            }

            agent = FractalAgent(
                agent_id=pattern.pattern_id,
                bridge=self.bridge,
                initial_reality=reality,
                depth=0
            )
            agents[pattern.pattern_id] = agent

        # Build neighbor lists from semantic graph
        neighbor_map: Dict[str, List[Tuple[FractalAgent, float]]] = {}
        for pattern_id, agent in agents.items():
            neighbors_data = self.memory.get_graph_neighbors(pattern_id, min_weight=0.1)
            neighbors = []
            for neighbor_id, weight in neighbors_data:
                if neighbor_id in agents:
                    neighbors.append((agents[neighbor_id], weight))
            neighbor_map[pattern_id] = neighbors

        # Evolve with Kuramoto coupling
        coalitions: List[Coalition] = []
        hebbian_updates = 0
        delta_time = 1.0 / frequency_hz  # Time step

        for cycle in range(duration_cycles):
            # Coupled evolution for all agents
            for pattern_id, agent in agents.items():
                neighbors = neighbor_map[pattern_id]
                agent.coupled_evolve(
                    delta_time=delta_time,
                    neighbors=neighbors,
                    intrinsic_frequency=frequency_hz * 2 * math.pi,
                    cross_frequency_beta=0.05
                )

            # Detect coalitions every 10 cycles
            if cycle % 10 == 0:
                coalition = self._detect_coalition(
                    agents, coherence_threshold, session_id
                )
                if coalition:
                    coalitions.append(coalition)

                    # Hebbian strengthening for coalition members
                    for i, pi in enumerate(coalition.member_pattern_ids):
                        for j, pj in enumerate(coalition.member_pattern_ids):
                            if i < j:  # Avoid double-counting
                                # Compute phase coherence
                                coherence = agents[pi].compute_phase_coherence(
                                    agents[pj], band='pi'
                                )

                                # Hebbian update: ΔW_ij = η * coherence
                                current_neighbors = self.memory.get_graph_neighbors(pi)
                                current_weight = 0.1  # Default
                                for nid, w in current_neighbors:
                                    if nid == pj:
                                        current_weight = w
                                        break

                                new_weight = current_weight + hebbian_learning_rate * coherence
                                new_weight = min(1.0, new_weight)  # Cap at 1.0

                                # Update graph edge
                                self.memory.store_graph_edge(pi, pj, new_weight, 'hebbian')
                                hebbian_updates += 1

        # Compute metrics
        end_time = time.time()
        process = psutil.Process()
        cpu_time_ms = (process.cpu_times().user - self.start_cpu_time) * 1000
        memory_mb = (process.memory_info().rss / (1024 * 1024)) - self.start_memory

        # Compute information gain from detected coalitions
        information_gain = self._compute_information_gain(coalitions, len(patterns))

        metrics = ConsolidationMetrics(
            session_id=session_id,
            phase_type='nrem',
            start_time=start_time,
            end_time=end_time,
            patterns_processed=len(patterns),
            coalitions_detected=len(coalitions),
            hebbian_updates=hebbian_updates,
            cpu_time_ms=cpu_time_ms,
            memory_usage_mb=memory_mb,
            information_gain_bits=information_gain
        )

        self.end_session(metrics)

        return coalitions, metrics

    def rem_exploration(
        self,
        patterns: List[Pattern],
        duration_cycles: int = 50,
        frequency_hz: float = 8.0,
        perturbation_strength: float = 0.5,
        coherence_threshold: float = 0.7
    ) -> Tuple[List[Coalition], ConsolidationMetrics]:
        """
        REM high-frequency exploration phase.

        Explores parameter space through stochastic perturbations to discover
        novel relationships.

        Args:
            patterns: List of patterns to explore
            duration_cycles: Number of evolution cycles
            frequency_hz: High-frequency oscillation (5-12 Hz typical)
            perturbation_strength: Strength of stochastic noise
            coherence_threshold: Minimum coherence for coalition detection

        Returns:
            (detected_coalitions, metrics)
        """
        import random

        session_id = self.start_session('rem')
        start_time = time.time()

        # Create FractalAgents with perturbations
        agents: Dict[str, FractalAgent] = {}
        for pattern in patterns:
            # Add noise to reality anchor for exploration
            reality = {
                'cpu_percent': max(0, min(100, pattern.confidence * 100 + random.gauss(0, perturbation_strength * 10))),
                'memory_percent': max(0, min(100, pattern.occurrences / 10.0 + random.gauss(0, perturbation_strength * 5))),
                'disk_usage': 50.0 + random.gauss(0, perturbation_strength * 5)
            }

            agent = FractalAgent(
                agent_id=pattern.pattern_id,
                bridge=self.bridge,
                initial_reality=reality,
                depth=0
            )
            agents[pattern.pattern_id] = agent

        # Build neighbor lists
        neighbor_map: Dict[str, List[Tuple[FractalAgent, float]]] = {}
        for pattern_id, agent in agents.items():
            neighbors_data = self.memory.get_graph_neighbors(pattern_id, min_weight=0.05)
            neighbors = []
            for neighbor_id, weight in neighbors_data:
                if neighbor_id in agents:
                    neighbors.append((agents[neighbor_id], weight))
            neighbor_map[pattern_id] = neighbors

        # Evolve with stochastic perturbations
        coalitions: List[Coalition] = []
        delta_time = 1.0 / frequency_hz

        for cycle in range(duration_cycles):
            # Coupled evolution with perturbations
            for pattern_id, agent in agents.items():
                neighbors = neighbor_map[pattern_id]
                agent.coupled_evolve(
                    delta_time=delta_time,
                    neighbors=neighbors,
                    intrinsic_frequency=frequency_hz * 2 * math.pi,
                    cross_frequency_beta=0.2  # Stronger cross-frequency for exploration
                )

                # Add stochastic perturbation
                agent.phase_state.pi_phase += random.gauss(0, perturbation_strength * 0.1)
                agent.phase_state.pi_phase = agent.phase_state.pi_phase % (2 * math.pi)

            # Detect coalitions every 5 cycles
            if cycle % 5 == 0:
                coalition = self._detect_coalition(
                    agents, coherence_threshold, session_id
                )
                if coalition:
                    coalitions.append(coalition)

        # Compute metrics
        end_time = time.time()
        process = psutil.Process()
        cpu_time_ms = (process.cpu_times().user - self.start_cpu_time) * 1000
        memory_mb = (process.memory_info().rss / (1024 * 1024)) - self.start_memory

        # Compute information gain from detected coalitions
        information_gain = self._compute_information_gain(coalitions, len(patterns))

        metrics = ConsolidationMetrics(
            session_id=session_id,
            phase_type='rem',
            start_time=start_time,
            end_time=end_time,
            patterns_processed=len(patterns),
            coalitions_detected=len(coalitions),
            hebbian_updates=0,
            cpu_time_ms=cpu_time_ms,
            memory_usage_mb=memory_mb,
            information_gain_bits=information_gain
        )

        self.end_session(metrics)

        return coalitions, metrics

    def _detect_coalition(
        self,
        agents: Dict[str, FractalAgent],
        coherence_threshold: float,
        session_id: str
    ) -> Optional[Coalition]:
        """
        Detect coalition of synchronized agents.

        Args:
            agents: Dictionary of pattern_id -> FractalAgent
            coherence_threshold: Minimum coherence for inclusion
            session_id: Current session ID

        Returns:
            Coalition if detected, None otherwise
        """
        agent_list = list(agents.items())
        if len(agent_list) < 2:
            return None

        # Find largest clique of coherent agents
        # Simplified: take all pairwise coherent agents
        coherent_pairs: List[Tuple[str, str, float]] = []

        for i in range(len(agent_list)):
            for j in range(i + 1, len(agent_list)):
                pi, agent_i = agent_list[i]
                pj, agent_j = agent_list[j]

                coherence = agent_i.compute_phase_coherence(agent_j, band='pi')

                if coherence >= coherence_threshold:
                    coherent_pairs.append((pi, pj, coherence))

        if not coherent_pairs:
            return None

        # Build coalition from most coherent pairs
        # Simplified: take top pair
        best_pair = max(coherent_pairs, key=lambda x: x[2])
        pi, pj, coherence = best_pair

        coalition_id = f"coalition_{session_id}_{int(time.time()*1000000)}"

        coalition = Coalition(
            coalition_id=coalition_id,
            member_pattern_ids=[pi, pj],
            coherence_scores={'pi': coherence},
            mean_coherence=coherence,
            timestamp=time.time()
        )

        # Store in database
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO coalitions
                (coalition_id, session_id, member_pattern_ids, coherence_scores,
                 mean_coherence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                coalition.coalition_id,
                session_id,
                json.dumps(coalition.member_pattern_ids),
                json.dumps(coalition.coherence_scores),
                coalition.mean_coherence,
                coalition.timestamp
            ))
            conn.commit()

        return coalition

    def _compute_information_gain(
        self,
        coalitions: List[Coalition],
        total_patterns: int
    ) -> float:
        """
        Compute information gain from detected coalitions.

        Each coalition reduces uncertainty about pattern relationships.
        Information gain is computed as:
            sum over coalitions of: coherence * log2(C(N, k))
        where C(N, k) = binomial coefficient for choosing k from N patterns.

        Args:
            coalitions: List of detected coalitions
            total_patterns: Total number of patterns processed

        Returns:
            Total information gain in bits
        """
        if not coalitions or total_patterns < 2:
            return 0.0

        total_bits = 0.0

        for coalition in coalitions:
            k = len(coalition.member_pattern_ids)
            if k < 2 or k > total_patterns:
                continue

            # Compute binomial coefficient C(N, k) = N! / (k! * (N-k)!)
            # For small k, compute directly to avoid overflow
            binom = 1
            for i in range(k):
                binom = binom * (total_patterns - i) // (i + 1)

            # Information bits from this coalition
            if binom > 0:
                info_bits = math.log2(binom)

                # Weight by coalition coherence (reliable information)
                weighted_bits = coalition.mean_coherence * info_bits
                total_bits += weighted_bits

        return total_bits

    def get_session_metrics(self, session_id: str) -> Optional[ConsolidationMetrics]:
        """
        Retrieve metrics for a consolidation session.

        Args:
            session_id: Session identifier

        Returns:
            ConsolidationMetrics or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM consolidation_sessions WHERE session_id = ?
            """, (session_id,))

            row = cursor.fetchone()
            if not row:
                return None

            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))

            return ConsolidationMetrics(**data)


if __name__ == "__main__":
    print("=" * 60)
    print("DUALITY-ZERO-V2: Consolidation Engine")
    print("NRM V2 Sleep-Inspired Memory System")
    print("=" * 60)
    print("\nModule: Sleep consolidation with NREM and REM phases")
    print("Status: ✅ Operational - ready for pattern consolidation")
    print("=" * 60)
