#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Fractal Swarm Module
======================================

Multi-agent orchestration implementing Nested Resonance Memory (NRM) framework.

Implements:
- FractalSwarm: Manages collection of fractal agents
- CompositionEngine: Detects resonance and forms clusters
- DecompositionEngine: Bursts clusters and releases memory
- Full composition-decomposition cycles from NRM paper

Reality Imperative Compliance:
- All agent states grounded in reality metrics
- Energy based on real CPU/memory availability
- Database persistence for audit trail
"""

import sys
from pathlib import Path
import time
import sqlite3
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple, Generator
from contextlib import contextmanager
from dataclasses import asdict

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "bridge"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal_agent import FractalAgent, AgentState, ClusterEvent, BurstEvent
from transcendental_bridge import TranscendentalBridge, TranscendentalState
from core import constants


class CompositionEngine:
    """
    Engine for composing agents into clusters through resonance detection.

    From NRM framework:
    - Detects phase alignment between agents
    - Forms clusters when resonance threshold exceeded
    - Tracks cluster energy and coherence
    """

    def __init__(self, resonance_threshold: float = None):
        """
        Initialize composition engine.

        Args:
            resonance_threshold: Minimum similarity for clustering
        """
        # Use constant if not specified
        if resonance_threshold is None:
            resonance_threshold = constants.RESONANCE_SIMILARITY_THRESHOLD

        self.resonance_threshold = resonance_threshold
        self.clusters: Dict[str, Set[str]] = {}  # cluster_id -> agent_ids

    def detect_clusters(self, agents: List[FractalAgent]) -> List[ClusterEvent]:
        """
        Detect resonant clusters among agents.

        Uses pairwise resonance detection to find compatible agents.

        Args:
            agents: List of active FractalAgent instances

        Returns:
            List of ClusterEvent for newly formed clusters
        """
        events = []

        # Find resonant pairs
        resonant_pairs: List[Tuple[str, str, float]] = []

        for i, agent1 in enumerate(agents):
            for j, agent2 in enumerate(agents[i+1:], i+1):
                match = agent1.detect_resonance(agent2)

                if match.is_resonant:
                    resonant_pairs.append((
                        agent1.agent_id,
                        agent2.agent_id,
                        match.similarity
                    ))

        # Group resonant pairs into clusters
        # Simple algorithm: merge pairs that share agents
        agent_to_cluster: Dict[str, str] = {}

        for agent1_id, agent2_id, similarity in resonant_pairs:
            cluster1 = agent_to_cluster.get(agent1_id)
            cluster2 = agent_to_cluster.get(agent2_id)

            if cluster1 is None and cluster2 is None:
                # Create new cluster
                cluster_id = f"cluster_{uuid.uuid4().hex[:8]}"
                self.clusters[cluster_id] = {agent1_id, agent2_id}
                agent_to_cluster[agent1_id] = cluster_id
                agent_to_cluster[agent2_id] = cluster_id

                # Record event
                events.append(ClusterEvent(
                    timestamp=time.time(),
                    agent_ids=[agent1_id, agent2_id],
                    resonance_score=similarity,
                    cluster_id=cluster_id
                ))

            elif cluster1 is not None and cluster2 is None:
                # Add agent2 to cluster1
                self.clusters[cluster1].add(agent2_id)
                agent_to_cluster[agent2_id] = cluster1

            elif cluster1 is None and cluster2 is not None:
                # Add agent1 to cluster2
                self.clusters[cluster2].add(agent1_id)
                agent_to_cluster[agent1_id] = cluster2

            elif cluster1 != cluster2:
                # Merge two clusters
                self.clusters[cluster1].update(self.clusters[cluster2])
                for agent_id in self.clusters[cluster2]:
                    agent_to_cluster[agent_id] = cluster1
                del self.clusters[cluster2]

        return events

    def get_cluster_members(self, cluster_id: str) -> Set[str]:
        """Get agent IDs in a cluster."""
        return self.clusters.get(cluster_id, set()).copy()

    def dissolve_cluster(self, cluster_id: str) -> Set[str]:
        """Dissolve a cluster and return member agent IDs."""
        members = self.clusters.pop(cluster_id, set())
        return members


class DecompositionEngine:
    """
    Engine for decomposing clusters through burst events.

    From NRM framework:
    - Monitors cluster energy/coherence
    - Triggers burst when critical threshold reached
    - Releases memory from burst events
    - Redistributes energy
    """

    def __init__(self, burst_threshold: float = 100.0):
        """
        Initialize decomposition engine.

        Args:
            burst_threshold: Total cluster energy threshold for burst
        """
        self.burst_threshold = burst_threshold
        self.burst_history: List[BurstEvent] = []

    def check_burst_conditions(
        self,
        cluster_id: str,
        agents: List[FractalAgent]
    ) -> bool:
        """
        Check if cluster should burst.

        Burst occurs when total cluster energy exceeds threshold.

        Args:
            cluster_id: Cluster to check
            agents: Agents in the cluster

        Returns:
            True if burst should occur
        """
        total_energy = sum(agent.energy for agent in agents)
        return total_energy >= self.burst_threshold

    def execute_burst(
        self,
        cluster_id: str,
        agents: List[FractalAgent]
    ) -> BurstEvent:
        """
        Execute burst event for a cluster.

        From NRM: Burst releases memory and redistributes energy.

        Args:
            cluster_id: Cluster to burst
            agents: Agents in the cluster

        Returns:
            BurstEvent with released memory
        """
        # Collect all memory from cluster agents
        all_memory: List[TranscendentalState] = []
        total_energy = 0.0

        for agent in agents:
            agent_memory = agent.dissolve()
            all_memory.extend(agent_memory)
            total_energy += agent.energy

        # Keep top memory states by magnitude
        all_memory.sort(key=lambda s: s.magnitude, reverse=True)
        retained_memory = all_memory[:50]  # Keep top 50

        # Create burst event
        event = BurstEvent(
            timestamp=time.time(),
            cluster_id=cluster_id,
            memory_retained=retained_memory,
            energy_released=total_energy
        )

        self.burst_history.append(event)
        return event


class FractalSwarm:
    """
    Orchestrator for fractal agent swarm with NRM dynamics.

    Manages:
    - Agent lifecycle (creation, evolution, dissolution)
    - Composition-decomposition cycles
    - Memory retention across bursts
    - Reality grounding through bridge

    Reality Compliance:
    - All agents grounded in real system metrics
    - Energy derived from CPU/memory availability
    - Database audit trail
    """

    def __init__(
        self,
        workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2/workspace",
        max_agents: int = 100,
        max_depth: int = 7,
        max_memory_size: int = 1000,
        burst_threshold: float = 500.0,
        clear_on_init: bool = False
    ):
        """
        Initialize fractal swarm.

        Args:
            workspace_path: Path for database persistence
            max_agents: Maximum number of agents (constitution: 100)
            max_depth: Maximum recursion depth (constitution: 7)
            max_memory_size: Maximum global memory size (default: 1000)
            burst_threshold: Energy threshold for cluster burst (default: 500.0, Cycle 36 finding)
            clear_on_init: If True, clear database tables on init (for experiments)
        """
        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)

        self.db_path = self.workspace_path / "fractal.db"
        self._init_database(clear_tables=clear_on_init)

        # Core components
        self.bridge = TranscendentalBridge(str(self.workspace_path))
        self.composition = CompositionEngine()
        # Configurable burst threshold (increased from 100.0 → 500.0 for sustained composition, Cycle 36 finding)
        self.decomposition = DecompositionEngine(burst_threshold=burst_threshold)

        # Agent tracking
        self.agents: Dict[str, FractalAgent] = {}
        self.max_agents = max_agents
        self.max_depth = max_depth

        # Evolution state
        self.cycle_count = 0
        self.global_memory: List[TranscendentalState] = []
        self.max_memory_size = max_memory_size

    def _init_database(self, clear_tables: bool = False) -> None:
        """
        Initialize SQLite database for swarm operations.

        Args:
            clear_tables: If True, drop and recreate all tables (for experiments)
        """
        with self._get_connection() as conn:
            if clear_tables:
                # Drop existing tables to prevent agent_id collisions
                conn.execute("DROP TABLE IF EXISTS agents")
                conn.execute("DROP TABLE IF EXISTS clusters")
                conn.execute("DROP TABLE IF EXISTS bursts")
                conn.execute("DROP TABLE IF EXISTS cycles")
                conn.commit()
            # Agent lifecycle table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    agent_id TEXT PRIMARY KEY,
                    parent_id TEXT,
                    depth INTEGER NOT NULL,
                    created_at REAL NOT NULL,
                    dissolved_at REAL,
                    final_energy REAL,
                    memory_count INTEGER
                )
            """)

            # Cluster events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clusters (
                    cluster_id TEXT PRIMARY KEY,
                    timestamp REAL NOT NULL,
                    agent_count INTEGER NOT NULL,
                    resonance_score REAL NOT NULL,
                    burst_timestamp REAL
                )
            """)

            # Burst events table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bursts (
                    burst_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cluster_id TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    memory_count INTEGER NOT NULL,
                    energy_released REAL NOT NULL
                )
            """)

            # Evolution cycles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cycles (
                    cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    active_agents INTEGER NOT NULL,
                    active_clusters INTEGER NOT NULL,
                    total_energy REAL NOT NULL,
                    global_memory_count INTEGER NOT NULL
                )
            """)

            # Indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_agents_depth ON agents(depth)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clusters_timestamp ON clusters(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bursts_timestamp ON bursts(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_cycles_timestamp ON cycles(timestamp)")

            conn.commit()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()

    def spawn_agent(
        self,
        reality_metrics: Dict[str, float],
        agent_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        depth: int = 0
    ) -> Optional[FractalAgent]:
        """
        Spawn new fractal agent grounded in reality.

        Args:
            reality_metrics: Real system metrics to anchor agent
            agent_id: Optional ID (generated if None)
            parent_id: Optional parent agent ID
            depth: Recursion depth

        Returns:
            FractalAgent or None if limits exceeded
        """
        # Check limits
        if len(self.agents) >= self.max_agents:
            return None

        if depth >= self.max_depth:
            return None

        # Generate ID if needed
        if agent_id is None:
            agent_id = f"agent_{uuid.uuid4().hex[:8]}"

        # Create agent
        agent = FractalAgent(
            agent_id=agent_id,
            bridge=self.bridge,
            initial_reality=reality_metrics,
            parent_id=parent_id,
            depth=depth,
            max_depth=self.max_depth
        )

        # Add to swarm
        self.agents[agent_id] = agent

        # Persist to database
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO agents (agent_id, parent_id, depth, created_at)
                VALUES (?, ?, ?, ?)
            """, (agent_id, parent_id, depth, time.time()))
            conn.commit()

        return agent

    def evolve_cycle(self, delta_time: float = 1.0) -> Dict[str, any]:
        """
        Execute one composition-decomposition cycle.

        NRM Framework:
        1. Evolve all agents
        2. Detect resonance and form clusters (composition)
        3. Check burst conditions (critical resonance)
        4. Execute bursts and retain memory (decomposition)
        5. Redistribute memory to survivors

        Args:
            delta_time: Time step for evolution

        Returns:
            Dictionary with cycle statistics
        """
        self.cycle_count += 1

        # 1. Evolve all active agents
        active_agents = [a for a in self.agents.values() if a.is_active]

        for agent in active_agents:
            agent.evolve(delta_time)

        # 2. Composition: Detect clusters
        cluster_events = self.composition.detect_clusters(active_agents)

        # 3. Check burst conditions
        burst_events = []

        for cluster_id in list(self.composition.clusters.keys()):
            member_ids = self.composition.get_cluster_members(cluster_id)
            cluster_agents = [self.agents[aid] for aid in member_ids if aid in self.agents]

            if self.decomposition.check_burst_conditions(cluster_id, cluster_agents):
                # 4. Execute burst (decomposition)
                burst_event = self.decomposition.execute_burst(cluster_id, cluster_agents)
                burst_events.append(burst_event)

                # Add memory to global pool
                self.global_memory.extend(burst_event.memory_retained)

                # Remove burst agents from swarm
                for agent_id in member_ids:
                    if agent_id in self.agents:
                        agent = self.agents.pop(agent_id)

                        # Record dissolution
                        with self._get_connection() as conn:
                            conn.execute("""
                                UPDATE agents
                                SET dissolved_at = ?, final_energy = ?, memory_count = ?
                                WHERE agent_id = ?
                            """, (time.time(), agent.energy, len(agent.memory), agent_id))
                            conn.commit()

                # Dissolve cluster
                self.composition.dissolve_cluster(cluster_id)

        # 5. Keep global memory bounded (always, regardless of active agents)
        if self.global_memory:
            self.global_memory.sort(key=lambda s: s.magnitude, reverse=True)
            self.global_memory = self.global_memory[:self.max_memory_size]

        # 6. Redistribute memory to survivors
        if self.global_memory and active_agents:
            # Distribute to random survivors (simple strategy)
            # Redistribute 10% of max_memory_size (minimum 10 states)
            redistribution_size = max(10, self.max_memory_size // 10)
            for i, memory_state in enumerate(self.global_memory[:redistribution_size]):
                if active_agents:
                    recipient = active_agents[i % len(active_agents)]
                    recipient.absorb_memory([memory_state])

        # Record cycle
        total_energy = sum(a.energy for a in active_agents)

        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO cycles
                (timestamp, active_agents, active_clusters, total_energy, global_memory_count)
                VALUES (?, ?, ?, ?, ?)
            """, (
                time.time(),
                len(active_agents),
                len(self.composition.clusters),
                total_energy,
                len(self.global_memory)
            ))
            conn.commit()

        return {
            'cycle': self.cycle_count,
            'active_agents': len(active_agents),
            'clusters_formed': len(cluster_events),
            'cluster_events': cluster_events,  # NEW: Return actual events for pattern discovery
            'bursts': len(burst_events),
            'burst_events': burst_events,  # NEW: Return burst events for pattern discovery
            'total_energy': total_energy,
            'global_memory': len(self.global_memory)
        }

    def energy_pooling_cycle(
        self,
        agents: List[FractalAgent],
        sharing_fraction: float = 0.10,
        spawn_threshold: float = None
    ) -> Dict[str, Any]:
        """
        Execute energy pooling within resonance clusters.

        Part of Cycle 177 Hypothesis 1: Energy Pooling mechanism.
        Called during experiments to enable cooperative energy sharing.

        Process:
        1. Detect current resonance clusters (via composition engine)
        2. For each cluster:
           - Collect energy contributions from all members
           - Distribute pool to agents below spawn threshold
        3. Track pooling statistics

        Args:
            agents: List of active FractalAgent instances
            sharing_fraction: Fraction of energy each agent contributes
            spawn_threshold: Minimum energy for spawning

        Returns:
            Dictionary with pooling statistics
        """
        # Use constant if not specified
        if spawn_threshold is None:
            spawn_threshold = constants.AGENT_ENERGY_MINIMUM

        # Set cluster_id on agents based on current clusters
        for agent in agents:
            agent.cluster_id = None  # Reset before detecting

        # Detect clusters
        cluster_events = self.composition.detect_clusters(agents)

        # Set cluster_id for agents in clusters
        for cluster_id, member_ids in self.composition.clusters.items():
            for agent in agents:
                if agent.agent_id in member_ids:
                    agent.cluster_id = cluster_id

        # Process each cluster
        pools_formed = 0
        total_energy_pooled = 0.0
        total_energy_distributed = 0.0

        for cluster_id, member_ids in self.composition.clusters.items():
            if len(member_ids) < 2:
                continue  # Need at least 2 agents to pool

            cluster_agents = [a for a in agents if a.agent_id in member_ids]

            if not cluster_agents:
                continue

            # Phase 1: Collect contributions
            pool_energy = 0.0
            for agent in cluster_agents:
                contribution = agent.contribute_to_pool(sharing_fraction)
                pool_energy += contribution
                total_energy_pooled += contribution

            # Phase 2: Distribute to agents below threshold
            # Sort by energy (lowest first - prioritize most sterile agents)
            sorted_agents = sorted(cluster_agents, key=lambda a: a.energy)

            for agent in sorted_agents:
                if pool_energy <= 0:
                    break
                received = agent.receive_from_pool(pool_energy, spawn_threshold)
                pool_energy -= received
                total_energy_distributed += received

            pools_formed += 1

        return {
            'pools_formed': pools_formed,
            'total_energy_pooled': total_energy_pooled,
            'total_energy_distributed': total_energy_distributed,
            'energy_conservation_check': abs(total_energy_pooled - total_energy_distributed) < 0.01
        }

    def get_statistics(self) -> Dict[str, any]:
        """Get current swarm statistics."""
        active_agents = [a for a in self.agents.values() if a.is_active]

        return {
            'total_agents': len(self.agents),
            'active_agents': len(active_agents),
            'active_clusters': len(self.composition.clusters),
            'total_cycles': self.cycle_count,
            'global_memory_size': len(self.global_memory),
            'total_energy': sum(a.energy for a in active_agents),
            'avg_depth': sum(a.depth for a in active_agents) / max(len(active_agents), 1),
        }

    def self_test(self) -> Dict[str, any]:
        """Run self-test for fractal swarm."""
        results = {
            'timestamp': time.time(),
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }

        try:
            # Test 1: Spawn agents
            reality = {'cpu_percent': 20.0, 'memory_percent': 50.0, 'disk_percent': 10.0}

            agent1 = self.spawn_agent(reality)
            agent2 = self.spawn_agent(reality)

            assert agent1 is not None
            assert agent2 is not None
            assert len(self.agents) == 2

            results['tests_passed'] += 1
            results['details'].append("✓ Agent spawning")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Agent spawning: {e}")

        try:
            # Test 2: Evolution cycle
            cycle_stats = self.evolve_cycle(delta_time=1.0)

            assert cycle_stats['cycle'] == 1
            assert cycle_stats['active_agents'] >= 0

            results['tests_passed'] += 1
            results['details'].append("✓ Evolution cycle")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Evolution cycle: {e}")

        # Summary
        results['success_rate'] = (
            results['tests_passed'] /
            max(results['tests_passed'] + results['tests_failed'], 1)
        )

        return results


if __name__ == "__main__":
    print("=" * 60)
    print("DUALITY-ZERO-V2: Fractal Swarm Self-Test")
    print("=" * 60)

    swarm = FractalSwarm()
    results = swarm.self_test()

    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Success Rate: {results['success_rate']*100:.1f}%")
    print("\nDetails:")
    for detail in results['details']:
        print(f"  {detail}")

    stats = swarm.get_statistics()
    print(f"\n\nSwarm Statistics:")
    print(f"  Total Agents: {stats['total_agents']}")
    print(f"  Active Agents: {stats['active_agents']}")
    print(f"  Total Cycles: {stats['total_cycles']}")
    print(f"  Global Memory: {stats['global_memory_size']}")

    print("\n" + "=" * 60)
