"""
NRM Core: Consolidation Engine
Sleep-inspired memory consolidation.
"""
import time
import math
import json
import sqlite3
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False

from ..fractal import FractalAgent
from .pattern_memory import PatternMemory, Pattern

@dataclass
class ConsolidationMetrics:
    """Metrics for consolidation session."""
    session_id: str
    phase_type: str
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
    coherence_scores: Dict[str, float]
    mean_coherence: float
    timestamp: float

class ConsolidationEngine:
    """
    Sleep-inspired consolidation engine.
    """
    def __init__(self, memory: Optional[PatternMemory] = None, db_path: str = "consolidation.db"):
        self.memory = memory if memory else PatternMemory()
        self.db_path = db_path
        self._init_database()
        self.session_id: Optional[str] = None
        self.start_cpu_time: float = 0.0
        self.start_memory: float = 0.0

    def _init_database(self) -> None:
        with self._get_connection() as conn:
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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS coalitions (
                    coalition_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    member_pattern_ids TEXT,
                    coherence_scores TEXT,
                    mean_coherence REAL,
                    timestamp REAL,
                    FOREIGN KEY (session_id) REFERENCES consolidation_sessions(session_id)
                )
            """)
            conn.commit()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def start_session(self, phase_type: str = 'nrem') -> str:
        self.session_id = f"{phase_type}_{int(time.time()*1000)}"
        if _HAS_PSUTIL:
            process = psutil.Process()
            self.start_cpu_time = process.cpu_times().user
            self.start_memory = process.memory_info().rss / (1024 * 1024)
        return self.session_id

    def end_session(self, metrics: ConsolidationMetrics) -> None:
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
        
        session_id = self.start_session('nrem')
        start_time = time.time()

        agents: Dict[str, FractalAgent] = {}
        for pattern in patterns:
            agent = FractalAgent(agent_id=pattern.pattern_id)
            agents[pattern.pattern_id] = agent

        # Neighbor map (mocked for now, should come from memory)
        # For now, assume fully connected or random?
        # Or fetch from memory if edges exist.
        # We'll fetch from memory.
        neighbor_map: Dict[str, List[FractalAgent]] = {}
        for pattern_id, agent in agents.items():
            neighbors_data = self.memory.get_graph_neighbors(pattern_id, min_weight=0.1)
            neighbors = []
            for neighbor_id, weight in neighbors_data:
                if neighbor_id in agents:
                    neighbors.append(agents[neighbor_id]) # Weight ignored in FractalAgent for now
            neighbor_map[pattern_id] = neighbors

        coalitions: List[Coalition] = []
        hebbian_updates = 0
        delta_time = 1.0 / frequency_hz

        for cycle in range(duration_cycles):
            for pattern_id, agent in agents.items():
                neighbors = neighbor_map.get(pattern_id, [])
                agent.coupled_evolve(delta_time, neighbors)

            if cycle % 10 == 0:
                coalition = self._detect_coalition(agents, coherence_threshold, session_id)
                if coalition:
                    coalitions.append(coalition)
                    # Hebbian update logic would go here, updating PatternMemory edges

        end_time = time.time()
        cpu_time_ms = 0.0
        memory_mb = 0.0
        if _HAS_PSUTIL:
            process = psutil.Process()
            cpu_time_ms = (process.cpu_times().user - self.start_cpu_time) * 1000
            memory_mb = (process.memory_info().rss / (1024 * 1024)) - self.start_memory

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
            information_gain_bits=0.0 # Simplified
        )
        self.end_session(metrics)
        return coalitions, metrics

    def _detect_coalition(
        self,
        agents: Dict[str, FractalAgent],
        coherence_threshold: float,
        session_id: str
    ) -> Optional[Coalition]:
        
        agent_list = list(agents.items())
        if len(agent_list) < 2:
            return None

        best_pair = None
        best_score = 0.0

        for i in range(len(agent_list)):
            for j in range(i + 1, len(agent_list)):
                pi, agent_i = agent_list[i]
                pj, agent_j = agent_list[j]
                coherence = agent_i.compute_coherence(agent_j)
                if coherence > best_score:
                    best_score = coherence
                    best_pair = (pi, pj)

        if best_score >= coherence_threshold and best_pair:
            coalition_id = f"coalition_{session_id}_{int(time.time()*1000000)}"
            coalition = Coalition(
                coalition_id=coalition_id,
                member_pattern_ids=list(best_pair),
                coherence_scores={'pi': best_score},
                mean_coherence=best_score,
                timestamp=time.time()
            )
            # Store
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
        return None