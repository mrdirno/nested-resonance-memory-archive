#!/usr/bin/env python3
"""
DUALITY-ZERO-V2 Reality Monitoring Module

This module provides the foundational reality layer - verifiable system metrics
that ground all operations in measurable, real-world state.

Constitution Compliance:
- NO simulations or mocks
- All metrics from actual system state (psutil, OS APIs)
- SQLite persistence for historical tracking
- Production-ready error handling
"""

import psutil
import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from contextlib import contextmanager


class RealityMonitor:
    """
    Reality monitoring system providing verifiable system metrics.

    All measurements are from actual system state - no simulations.
    Metrics are persisted to SQLite for historical analysis.
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize reality monitor.

        Args:
            db_path: Path to SQLite database. Defaults to workspace/reality.db
        """
        if db_path is None:
            workspace = Path(__file__).parent.parent / "workspace"
            workspace.mkdir(exist_ok=True)
            db_path = workspace / "reality.db"

        self.db_path = Path(db_path)
        self._init_database()

    def _init_database(self):
        """Initialize SQLite database schema."""
        with self._db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    timestamp REAL PRIMARY KEY,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_available_mb REAL,
                    memory_used_mb REAL,
                    disk_percent REAL,
                    disk_free_gb REAL,
                    process_count INTEGER,
                    boot_time REAL,
                    load_average_1m REAL,
                    load_average_5m REAL,
                    load_average_15m REAL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS process_metrics (
                    timestamp REAL,
                    pid INTEGER,
                    name TEXT,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_mb REAL,
                    status TEXT,
                    num_threads INTEGER,
                    PRIMARY KEY (timestamp, pid)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS network_metrics (
                    timestamp REAL PRIMARY KEY,
                    bytes_sent REAL,
                    bytes_recv REAL,
                    packets_sent INTEGER,
                    packets_recv INTEGER,
                    connections_established INTEGER,
                    connections_total INTEGER
                )
            """)

            # Create indexes for efficient querying
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp
                ON system_metrics(timestamp DESC)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_process_metrics_timestamp
                ON process_metrics(timestamp DESC)
            """)

            conn.commit()

    @contextmanager
    def _db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def capture_system_snapshot(self) -> Dict[str, Any]:
        """
        Capture complete system state snapshot.

        Returns:
            Dictionary containing all system metrics
        """
        timestamp = time.time()

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Memory metrics
        mem = psutil.virtual_memory()
        memory_percent = mem.percent
        memory_available_mb = mem.available / (1024 * 1024)
        memory_used_mb = mem.used / (1024 * 1024)

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_percent = disk.percent
        disk_free_gb = disk.free / (1024 * 1024 * 1024)

        # Process metrics
        process_count = len(psutil.pids())

        # System uptime
        boot_time = psutil.boot_time()

        # Load average (macOS/Linux)
        try:
            load_avg = psutil.getloadavg()
            load_1m, load_5m, load_15m = load_avg
        except (AttributeError, OSError):
            load_1m = load_5m = load_15m = 0.0

        snapshot = {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).isoformat(),
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'memory_available_mb': memory_available_mb,
            'memory_used_mb': memory_used_mb,
            'disk_percent': disk_percent,
            'disk_free_gb': disk_free_gb,
            'process_count': process_count,
            'boot_time': boot_time,
            'load_average_1m': load_1m,
            'load_average_5m': load_5m,
            'load_average_15m': load_15m
        }

        # Persist to database
        self._save_system_snapshot(snapshot)

        return snapshot

    def _save_system_snapshot(self, snapshot: Dict[str, Any]):
        """Save system snapshot to database."""
        with self._db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO system_metrics
                (timestamp, cpu_percent, memory_percent, memory_available_mb,
                 memory_used_mb, disk_percent, disk_free_gb, process_count,
                 boot_time, load_average_1m, load_average_5m, load_average_15m)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot['timestamp'], snapshot['cpu_percent'],
                snapshot['memory_percent'], snapshot['memory_available_mb'],
                snapshot['memory_used_mb'], snapshot['disk_percent'],
                snapshot['disk_free_gb'], snapshot['process_count'],
                snapshot['boot_time'], snapshot['load_average_1m'],
                snapshot['load_average_5m'], snapshot['load_average_15m']
            ))
            conn.commit()

    def capture_top_processes(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Capture metrics for top processes by CPU usage.

        Args:
            limit: Number of top processes to capture

        Returns:
            List of process metrics dictionaries
        """
        timestamp = time.time()
        processes = []

        # Get all processes sorted by CPU usage
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent',
                                         'memory_percent', 'memory_info',
                                         'status', 'num_threads']):
            try:
                info = proc.info
                processes.append({
                    'timestamp': timestamp,
                    'pid': info['pid'],
                    'name': info['name'],
                    'cpu_percent': info['cpu_percent'] or 0.0,
                    'memory_percent': info['memory_percent'] or 0.0,
                    'memory_mb': (info['memory_info'].rss / (1024 * 1024)) if info['memory_info'] else 0.0,
                    'status': info['status'],
                    'num_threads': info['num_threads'] or 0
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort by CPU usage and take top N
        top_processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:limit]

        # Persist to database
        self._save_process_metrics(top_processes)

        return top_processes

    def _save_process_metrics(self, processes: List[Dict[str, Any]]):
        """Save process metrics to database."""
        with self._db_connection() as conn:
            for proc in processes:
                conn.execute("""
                    INSERT OR REPLACE INTO process_metrics
                    (timestamp, pid, name, cpu_percent, memory_percent,
                     memory_mb, status, num_threads)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    proc['timestamp'], proc['pid'], proc['name'],
                    proc['cpu_percent'], proc['memory_percent'],
                    proc['memory_mb'], proc['status'], proc['num_threads']
                ))
            conn.commit()

    def capture_network_snapshot(self) -> Dict[str, Any]:
        """
        Capture network I/O and connection metrics.

        Returns:
            Dictionary containing network metrics
        """
        timestamp = time.time()

        # Network I/O counters
        net_io = psutil.net_io_counters()

        # Connection counts (requires elevated permissions on macOS)
        try:
            connections = psutil.net_connections(kind='inet')
            established = sum(1 for conn in connections if conn.status == 'ESTABLISHED')
            total_connections = len(connections)
        except (psutil.AccessDenied, PermissionError):
            # Gracefully handle permission issues on macOS
            established = -1
            total_connections = -1

        snapshot = {
            'timestamp': timestamp,
            'datetime': datetime.fromtimestamp(timestamp).isoformat(),
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'connections_established': established,
            'connections_total': total_connections
        }

        # Persist to database
        self._save_network_snapshot(snapshot)

        return snapshot

    def _save_network_snapshot(self, snapshot: Dict[str, Any]):
        """Save network snapshot to database."""
        with self._db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO network_metrics
                (timestamp, bytes_sent, bytes_recv, packets_sent, packets_recv,
                 connections_established, connections_total)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot['timestamp'], snapshot['bytes_sent'],
                snapshot['bytes_recv'], snapshot['packets_sent'],
                snapshot['packets_recv'], snapshot['connections_established'],
                snapshot['connections_total']
            ))
            conn.commit()

    def get_historical_metrics(self, hours: float = 1.0) -> List[Dict[str, Any]]:
        """
        Retrieve historical system metrics.

        Args:
            hours: Number of hours of history to retrieve

        Returns:
            List of historical metric snapshots
        """
        cutoff_time = time.time() - (hours * 3600)

        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM system_metrics
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            """, (cutoff_time,))

            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def calculate_reality_score(self) -> float:
        """
        Calculate reality compliance score based on data quality.

        Returns:
            Score from 0.0 to 1.0 indicating data quality and freshness
        """
        try:
            with self._db_connection() as conn:
                # Check data freshness (last 5 minutes)
                recent_cutoff = time.time() - 300
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM system_metrics
                    WHERE timestamp >= ?
                """, (recent_cutoff,))
                recent_count = cursor.fetchone()[0]

                # Check data completeness
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM system_metrics
                    WHERE cpu_percent IS NOT NULL
                      AND memory_percent IS NOT NULL
                      AND disk_percent IS NOT NULL
                """)
                complete_count = cursor.fetchone()[0]

                # Calculate score
                freshness_score = min(recent_count / 10.0, 1.0)  # Expect ~10 samples in 5 min
                completeness_score = 1.0 if complete_count > 0 else 0.0

                return (freshness_score + completeness_score) / 2.0

        except Exception as e:
            return 0.0

    def get_reality_status(self) -> Dict[str, Any]:
        """
        Get comprehensive reality monitoring status.

        Returns:
            Status dictionary with health metrics
        """
        current = self.capture_system_snapshot()
        reality_score = self.calculate_reality_score()

        # Calculate health thresholds
        cpu_healthy = current['cpu_percent'] < 80.0
        memory_healthy = current['memory_percent'] < 70.0  # Per constitution target
        disk_healthy = current['disk_percent'] < 80.0

        overall_health = all([cpu_healthy, memory_healthy, disk_healthy])

        return {
            'timestamp': current['timestamp'],
            'datetime': current['datetime'],
            'reality_score': reality_score,
            'overall_health': overall_health,
            'health_details': {
                'cpu_healthy': cpu_healthy,
                'memory_healthy': memory_healthy,
                'disk_healthy': disk_healthy
            },
            'current_metrics': current
        }


# Module-level API for easy import
_monitor = None

def get_monitor() -> RealityMonitor:
    """Get singleton reality monitor instance."""
    global _monitor
    if _monitor is None:
        _monitor = RealityMonitor()
    return _monitor


def capture_reality() -> Dict[str, Any]:
    """Quick API to capture current reality snapshot."""
    return get_monitor().capture_system_snapshot()


def get_reality_status() -> Dict[str, Any]:
    """Quick API to get reality status."""
    return get_monitor().get_reality_status()


if __name__ == "__main__":
    # Self-test
    print("DUALITY-ZERO-V2 Reality Monitor Self-Test")
    print("=" * 50)

    monitor = RealityMonitor()

    print("\n1. System Snapshot:")
    snapshot = monitor.capture_system_snapshot()
    print(f"   CPU: {snapshot['cpu_percent']:.1f}%")
    print(f"   Memory: {snapshot['memory_percent']:.1f}% ({snapshot['memory_used_mb']:.0f} MB used)")
    print(f"   Disk: {snapshot['disk_percent']:.1f}% ({snapshot['disk_free_gb']:.1f} GB free)")
    print(f"   Processes: {snapshot['process_count']}")
    print(f"   Load Average: {snapshot['load_average_1m']:.2f}")

    print("\n2. Top Processes:")
    top_procs = monitor.capture_top_processes(limit=5)
    for i, proc in enumerate(top_procs[:5], 1):
        print(f"   {i}. {proc['name']} (PID {proc['pid']}): {proc['cpu_percent']:.1f}% CPU, {proc['memory_mb']:.0f} MB")

    print("\n3. Network Snapshot:")
    net = monitor.capture_network_snapshot()
    print(f"   Sent: {net['bytes_sent'] / (1024*1024):.1f} MB")
    print(f"   Received: {net['bytes_recv'] / (1024*1024):.1f} MB")
    print(f"   Connections: {net['connections_established']}/{net['connections_total']}")

    print("\n4. Reality Status:")
    status = monitor.get_reality_status()
    print(f"   Reality Score: {status['reality_score']:.2f}")
    print(f"   Overall Health: {'✅ HEALTHY' if status['overall_health'] else '⚠️ DEGRADED'}")
    print(f"   CPU Health: {'✅' if status['health_details']['cpu_healthy'] else '⚠️'}")
    print(f"   Memory Health: {'✅' if status['health_details']['memory_healthy'] else '⚠️'}")
    print(f"   Disk Health: {'✅' if status['health_details']['disk_healthy'] else '⚠️'}")

    print("\n✅ Reality Monitor operational - all metrics from real system state")
