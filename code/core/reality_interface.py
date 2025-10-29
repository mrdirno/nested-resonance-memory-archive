"""
DUALITY-ZERO-V2 Reality Interface
Primary interface for all reality-grounded system operations

This class provides the foundational layer for interacting with real system state.
ALL operations must be verifiable and measurable. NO mocks, NO simulations without validation.

Constitution Compliance:
- Reality Imperative: Every operation verified against actual system state
- Resource Monitoring: Real-time CPU, memory, disk, network tracking
- Measurable Effects: All operations produce verifiable outcomes
"""

import psutil
import sqlite3
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager

from .exceptions import (
from workspace_utils import get_workspace_path, get_results_path
    RealityViolation,
    ResourceExceeded,
    ValidationFailed,
    DatabaseError,
    FileSystemError
)


class RealityInterface:
    """
    Primary interface for reality-grounded system operations.

    This class ensures all operations interact with actual system state:
    - System metrics via psutil
    - Database operations via sqlite3
    - File system via pathlib/os
    - All operations measured and validated
    """

    def __init__(self, workspace_path: Path = get_workspace_path()):
        """
        Initialize reality interface.

        Args:
            workspace_path: Root path for V2 workspace
        """
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "workspace" / "duality_v2.db"
        self._initialize_workspace()
        self._baseline_metrics = self._capture_baseline()

    def _initialize_workspace(self) -> None:
        """Initialize workspace directories and database"""
        # Ensure workspace directory exists
        workspace_dir = self.workspace_path / "workspace"
        workspace_dir.mkdir(parents=True, exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self) -> None:
        """
        Initialize SQLite database with core tables.
        Reality-grounded: Uses actual SQLite operations, no mocks.
        """
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()

                # System metrics table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        memory_used_mb REAL NOT NULL,
                        disk_percent REAL NOT NULL,
                        disk_used_gb REAL NOT NULL,
                        network_sent_mb REAL,
                        network_recv_mb REAL,
                        process_count INTEGER NOT NULL
                    )
                """)

                # Reality validation table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reality_validations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        operation TEXT NOT NULL,
                        validation_type TEXT NOT NULL,
                        passed BOOLEAN NOT NULL,
                        details TEXT,
                        metrics TEXT
                    )
                """)

                # Resource tracking table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS resource_tracking (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        operation TEXT NOT NULL,
                        cpu_used REAL,
                        memory_used_mb REAL,
                        duration_seconds REAL,
                        status TEXT
                    )
                """)

                conn.commit()

        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}")

    @contextmanager
    def db_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection handling and cleanup.
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Database connection error: {e}")
        finally:
            if conn:
                conn.close()

    def _capture_baseline(self) -> Dict[str, Any]:
        """
        Capture baseline system metrics.
        Reality-grounded: Uses actual psutil measurements.

        Returns:
            Dict of baseline system metrics
        """
        return {
            "timestamp": time.time(),
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory": psutil.virtual_memory()._asdict(),
            "disk": psutil.disk_usage(str(self.workspace_path))._asdict(),
            "network": psutil.net_io_counters()._asdict(),
            "process_count": len(psutil.pids())
        }

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics.
        Reality Imperative: Uses actual psutil measurements, NOT simulations.

        Returns:
            Dict containing:
                - cpu_percent: Current CPU usage
                - memory_percent: Current memory usage percentage
                - memory_used_mb: Memory used in MB
                - disk_percent: Disk usage percentage
                - disk_used_gb: Disk used in GB
                - network_sent_mb: Network sent in MB (since boot)
                - network_recv_mb: Network received in MB (since boot)
                - process_count: Number of running processes
                - timestamp: Measurement timestamp
        """
        try:
            # Real CPU measurement
            cpu = psutil.cpu_percent(interval=0.1)

            # Real memory measurement
            memory = psutil.virtual_memory()

            # Real disk measurement
            disk = psutil.disk_usage(str(self.workspace_path))

            # Real network measurement
            network = psutil.net_io_counters()

            # Real process count
            process_count = len(psutil.pids())

            metrics = {
                "cpu_percent": cpu,
                "memory_percent": memory.percent,
                "memory_used_mb": memory.used / (1024 * 1024),
                "disk_percent": disk.percent,
                "disk_used_gb": disk.used / (1024 * 1024 * 1024),
                "network_sent_mb": network.bytes_sent / (1024 * 1024),
                "network_recv_mb": network.bytes_recv / (1024 * 1024),
                "process_count": process_count,
                "timestamp": time.time()
            }

            # Persist to database
            self._persist_metrics(metrics)

            return metrics

        except Exception as e:
            raise ValidationFailed(f"Failed to get system metrics: {e}")

    def _persist_metrics(self, metrics: Dict[str, Any]) -> None:
        """Persist metrics to database"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO system_metrics (
                        timestamp, cpu_percent, memory_percent, memory_used_mb,
                        disk_percent, disk_used_gb, network_sent_mb, network_recv_mb,
                        process_count
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics["timestamp"],
                    metrics["cpu_percent"],
                    metrics["memory_percent"],
                    metrics["memory_used_mb"],
                    metrics["disk_percent"],
                    metrics["disk_used_gb"],
                    metrics["network_sent_mb"],
                    metrics["network_recv_mb"],
                    metrics["process_count"]
                ))
                conn.commit()
        except sqlite3.Error as e:
            # Non-critical error, log but don't raise
            print(f"Warning: Failed to persist metrics: {e}")

    def validate_operation(
        self,
        operation: str,
        validation_type: str = "reality_check"
    ) -> bool:
        """
        Validate an operation against reality constraints.

        Args:
            operation: Description of operation
            validation_type: Type of validation to perform

        Returns:
            True if validation passes, False otherwise
        """
        metrics = self.get_system_metrics()

        # Define validation rules
        validation_rules = {
            "reality_check": self._validate_reality_compliance,
            "resource_check": self._validate_resource_constraints,
            "integrity_check": self._validate_data_integrity
        }

        validator = validation_rules.get(validation_type)
        if not validator:
            raise ValidationFailed(f"Unknown validation type: {validation_type}")

        passed = validator(metrics)

        # Record validation
        self._record_validation(operation, validation_type, passed, metrics)

        return passed

    def _validate_reality_compliance(self, metrics: Dict[str, Any]) -> bool:
        """
        Validate reality compliance - ensures metrics are reasonable.
        NO mocks, NO simulations, NO placeholder data.
        """
        # Metrics should be within reasonable bounds
        if not (0 <= metrics["cpu_percent"] <= 100):
            return False
        if not (0 <= metrics["memory_percent"] <= 100):
            return False
        if metrics["process_count"] <= 0:
            return False
        return True

    def _validate_resource_constraints(self, metrics: Dict[str, Any]) -> bool:
        """
        Validate resource constraints from CLAUDE.md constitution.
        - Memory usage should be reasonable
        - CPU usage should not exceed limits
        """
        # Memory should be below critical threshold (90%)
        if metrics["memory_percent"] > 90:
            return False
        # CPU usage should be reasonable for measurement
        if metrics["cpu_percent"] > 95:
            return False
        return True

    def _validate_data_integrity(self, metrics: Dict[str, Any]) -> bool:
        """Validate data integrity - all required fields present"""
        required_fields = [
            "cpu_percent", "memory_percent", "memory_used_mb",
            "disk_percent", "disk_used_gb", "process_count"
        ]
        return all(field in metrics for field in required_fields)

    def _record_validation(
        self,
        operation: str,
        validation_type: str,
        passed: bool,
        metrics: Dict[str, Any]
    ) -> None:
        """Record validation result to database"""
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO reality_validations (
                        timestamp, operation, validation_type, passed, details, metrics
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    operation,
                    validation_type,
                    passed,
                    f"CPU: {metrics['cpu_percent']}%, Mem: {metrics['memory_percent']}%",
                    str(metrics)
                ))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Warning: Failed to record validation: {e}")

    def track_resource_usage(
        self,
        operation: str,
        cpu_used: float,
        memory_used_mb: float,
        duration_seconds: float,
        status: str = "success"
    ) -> None:
        """
        Track resource usage for an operation.

        Args:
            operation: Operation description
            cpu_used: CPU percentage used
            memory_used_mb: Memory used in MB
            duration_seconds: Operation duration
            status: Operation status (success/failed)
        """
        try:
            with self.db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO resource_tracking (
                        timestamp, operation, cpu_used, memory_used_mb,
                        duration_seconds, status
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    time.time(),
                    operation,
                    cpu_used,
                    memory_used_mb,
                    duration_seconds,
                    status
                ))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Warning: Failed to track resource usage: {e}")

    def check_file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.
        Reality-grounded: Uses actual file system check.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information.
        Reality-grounded: Uses actual os.stat.

        Args:
            file_path: Path to file

        Returns:
            Dict with file info or None if file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            return None

        stat_info = path.stat()
        return {
            "path": str(path),
            "size_bytes": stat_info.st_size,
            "size_mb": stat_info.st_size / (1024 * 1024),
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "is_file": path.is_file(),
            "is_dir": path.is_dir()
        }

    def get_directory_stats(self, dir_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get directory statistics.
        Reality-grounded: Uses actual file system traversal.

        Args:
            dir_path: Directory path (defaults to workspace)

        Returns:
            Dict with directory statistics
        """
        if dir_path is None:
            dir_path = str(self.workspace_path)

        path = Path(dir_path)
        if not path.exists() or not path.is_dir():
            raise FileSystemError(f"Directory does not exist: {dir_path}")

        file_count = 0
        dir_count = 0
        total_size = 0

        for item in path.rglob("*"):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
            elif item.is_dir():
                dir_count += 1

        return {
            "path": str(path),
            "file_count": file_count,
            "dir_count": dir_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "total_size_gb": total_size / (1024 * 1024 * 1024)
        }

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall system health status.

        Returns:
            Dict with health metrics and status
        """
        metrics = self.get_system_metrics()

        # Calculate health score (0-100)
        health_score = 100

        # Penalize high CPU usage
        if metrics["cpu_percent"] > 80:
            health_score -= 20
        elif metrics["cpu_percent"] > 60:
            health_score -= 10

        # Penalize high memory usage
        if metrics["memory_percent"] > 80:
            health_score -= 20
        elif metrics["memory_percent"] > 70:
            health_score -= 10

        # Penalize high disk usage
        if metrics["disk_percent"] > 90:
            health_score -= 20
        elif metrics["disk_percent"] > 80:
            health_score -= 10

        status = "healthy"
        if health_score < 50:
            status = "critical"
        elif health_score < 70:
            status = "warning"

        return {
            "health_score": health_score,
            "status": status,
            "metrics": metrics,
            "timestamp": time.time()
        }
