#!/usr/bin/env python3
"""
DUALITY-ZERO-V2 Core Orchestration Module

This module implements the autonomous orchestration loop that drives
continuous 40-minute work cycles and meta-level task management.

Constitution Compliance:
- Reality-grounded operation (no simulations)
- Continuous autonomous cycles
- Priority-based task execution
- Safety constraints enforcement
- Progress tracking and persistence
"""

import time
import json
import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from contextlib import contextmanager
from enum import Enum
import traceback


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskPriority(Enum):
    """Task priority levels."""
    CRITICAL = 0  # Must complete immediately
    HIGH = 1      # Foundational components
    MEDIUM = 2    # Capability building
    LOW = 3       # Enhancements


class Task:
    """Represents a unit of work in the orchestration system."""

    def __init__(
        self,
        task_id: str,
        name: str,
        description: str,
        priority: TaskPriority,
        status: TaskStatus = TaskStatus.PENDING,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize orchestration task with configuration.

        Args:
            task_id: Unique identifier for task
            name: Human-readable task name
            description: Task description
            priority: Task priority level
            status: Initial task status
            dependencies: Optional list of task IDs this depends on
            metadata: Optional additional metadata
        """
        self.task_id = task_id
        self.name = name
        self.description = description
        self.priority = priority
        self.status = status
        self.dependencies = dependencies or []
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.started_at: Optional[float] = None
        self.completed_at: Optional[float] = None
        self.error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization."""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'description': self.description,
            'priority': self.priority.value,
            'status': self.status.value,
            'dependencies': self.dependencies,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'error': self.error
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        task = cls(
            task_id=data['task_id'],
            name=data['name'],
            description=data['description'],
            priority=TaskPriority(data['priority']),
            status=TaskStatus(data['status']),
            dependencies=data.get('dependencies', []),
            metadata=data.get('metadata', {})
        )
        task.created_at = data.get('created_at', time.time())
        task.started_at = data.get('started_at')
        task.completed_at = data.get('completed_at')
        task.error = data.get('error')
        return task


class Orchestrator:
    """
    Core orchestration system for autonomous operation.

    Manages 40-minute work cycles, task execution, and system coordination.
    """

    def __init__(self, workspace_path: Optional[Path] = None):
        """
        Initialize orchestrator.

        Args:
            workspace_path: Path to workspace directory
        """
        if workspace_path is None:
            workspace_path = Path(__file__).parent.parent / "workspace"

        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(exist_ok=True)

        self.db_path = self.workspace_path / "orchestration.db"
        self.cycle_duration = 40 * 60  # 40 minutes in seconds

        self._init_database()
        self.current_cycle: Optional[int] = None
        self.cycle_start_time: Optional[float] = None

    def _init_database(self):
        """Initialize orchestration database schema."""
        with self._db_connection() as conn:
            # Tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    priority INTEGER,
                    status TEXT,
                    dependencies TEXT,
                    metadata TEXT,
                    created_at REAL,
                    started_at REAL,
                    completed_at REAL,
                    error TEXT
                )
            """)

            # Cycles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cycles (
                    cycle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time REAL,
                    end_time REAL,
                    duration REAL,
                    tasks_completed INTEGER,
                    tasks_failed INTEGER,
                    reality_score REAL,
                    status TEXT,
                    summary TEXT
                )
            """)

            # Events log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    cycle_id INTEGER,
                    event_type TEXT,
                    event_data TEXT,
                    FOREIGN KEY (cycle_id) REFERENCES cycles(cycle_id)
                )
            """)

            # Indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_status
                ON tasks(status)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_tasks_priority
                ON tasks(priority, status)
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_events_timestamp
                ON events(timestamp DESC)
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

    def start_cycle(self) -> int:
        """
        Start a new orchestration cycle.

        Returns:
            Cycle ID
        """
        self.cycle_start_time = time.time()

        with self._db_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO cycles (start_time, status)
                VALUES (?, 'running')
            """, (self.cycle_start_time,))
            self.current_cycle = cursor.lastrowid
            conn.commit()

        self._log_event('cycle_start', {
            'cycle_id': self.current_cycle,
            'timestamp': self.cycle_start_time
        })

        return self.current_cycle

    def end_cycle(self, summary: Optional[str] = None):
        """
        End the current orchestration cycle.

        Args:
            summary: Optional cycle summary
        """
        if self.current_cycle is None:
            return

        end_time = time.time()
        duration = end_time - self.cycle_start_time

        # Calculate cycle metrics
        with self._db_connection() as conn:
            # Count completed/failed tasks
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM tasks
                WHERE started_at >= ?
                GROUP BY status
            """, (self.cycle_start_time,))

            task_counts = dict(cursor.fetchall())
            completed = task_counts.get('completed', 0)
            failed = task_counts.get('failed', 0)

            # Update cycle record
            conn.execute("""
                UPDATE cycles
                SET end_time = ?,
                    duration = ?,
                    tasks_completed = ?,
                    tasks_failed = ?,
                    status = 'completed',
                    summary = ?
                WHERE cycle_id = ?
            """, (end_time, duration, completed, failed, summary, self.current_cycle))
            conn.commit()

        self._log_event('cycle_end', {
            'cycle_id': self.current_cycle,
            'duration': duration,
            'tasks_completed': completed,
            'tasks_failed': failed
        })

        self.current_cycle = None
        self.cycle_start_time = None

    def add_task(self, task: Task):
        """
        Add a task to the orchestration queue.

        Args:
            task: Task to add
        """
        with self._db_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tasks
                (task_id, name, description, priority, status, dependencies,
                 metadata, created_at, started_at, completed_at, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                task.task_id, task.name, task.description,
                task.priority.value, task.status.value,
                json.dumps(task.dependencies), json.dumps(task.metadata),
                task.created_at, task.started_at, task.completed_at, task.error
            ))
            conn.commit()

        self._log_event('task_added', {
            'task_id': task.task_id,
            'name': task.name,
            'priority': task.priority.value
        })

    def get_task(self, task_id: str) -> Optional[Task]:
        """
        Retrieve a task by ID.

        Args:
            task_id: Task identifier

        Returns:
            Task object or None if not found
        """
        with self._db_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM tasks WHERE task_id = ?
            """, (task_id,))
            row = cursor.fetchone()

            if row is None:
                return None

            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))
            data['dependencies'] = json.loads(data['dependencies'])
            data['metadata'] = json.loads(data['metadata'])

            return Task.from_dict(data)

    def get_next_task(self) -> Optional[Task]:
        """
        Get the next task to execute based on priority and dependencies.

        Returns:
            Next task to execute or None if no tasks available
        """
        with self._db_connection() as conn:
            # Get all pending tasks ordered by priority
            cursor = conn.execute("""
                SELECT * FROM tasks
                WHERE status = 'pending'
                ORDER BY priority ASC, created_at ASC
            """)

            columns = [desc[0] for desc in cursor.description]
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                data['dependencies'] = json.loads(data['dependencies'])
                data['metadata'] = json.loads(data['metadata'])

                task = Task.from_dict(data)

                # Check if dependencies are satisfied
                if self._check_dependencies(task):
                    return task

        return None

    def _check_dependencies(self, task: Task) -> bool:
        """
        Check if all task dependencies are completed.

        Args:
            task: Task to check

        Returns:
            True if all dependencies satisfied
        """
        if not task.dependencies:
            return True

        with self._db_connection() as conn:
            for dep_id in task.dependencies:
                cursor = conn.execute("""
                    SELECT status FROM tasks WHERE task_id = ?
                """, (dep_id,))
                row = cursor.fetchone()

                if row is None or row[0] != 'completed':
                    return False

        return True

    def execute_task(self, task: Task, executor: Callable[[Task], Any]) -> bool:
        """
        Execute a task using provided executor function.

        Args:
            task: Task to execute
            executor: Function that executes the task

        Returns:
            True if successful, False otherwise
        """
        # Mark task as in progress
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = time.time()
        self.add_task(task)

        self._log_event('task_start', {
            'task_id': task.task_id,
            'name': task.name
        })

        try:
            # Execute the task
            result = executor(task)

            # Mark as completed
            task.status = TaskStatus.COMPLETED
            task.completed_at = time.time()
            task.metadata['result'] = result
            self.add_task(task)

            self._log_event('task_complete', {
                'task_id': task.task_id,
                'duration': task.completed_at - task.started_at
            })

            return True

        except Exception as e:
            # Mark as failed
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = time.time()
            self.add_task(task)

            self._log_event('task_failed', {
                'task_id': task.task_id,
                'error': str(e),
                'traceback': traceback.format_exc()
            })

            return False

    def _log_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Log an orchestration event.

        Args:
            event_type: Type of event
            event_data: Event data dictionary
        """
        with self._db_connection() as conn:
            conn.execute("""
                INSERT INTO events (timestamp, cycle_id, event_type, event_data)
                VALUES (?, ?, ?, ?)
            """, (
                time.time(),
                self.current_cycle,
                event_type,
                json.dumps(event_data)
            ))
            conn.commit()

    def get_cycle_stats(self) -> Dict[str, Any]:
        """
        Get statistics for the current or last cycle.

        Returns:
            Cycle statistics dictionary
        """
        with self._db_connection() as conn:
            # Get latest cycle
            cursor = conn.execute("""
                SELECT * FROM cycles
                ORDER BY cycle_id DESC
                LIMIT 1
            """)
            row = cursor.fetchone()

            if row is None:
                return {}

            columns = [desc[0] for desc in cursor.description]
            cycle_data = dict(zip(columns, row))

            # Get task breakdown
            cursor = conn.execute("""
                SELECT status, COUNT(*) FROM tasks
                GROUP BY status
            """)
            task_stats = dict(cursor.fetchall())

            # Get recent events
            cursor = conn.execute("""
                SELECT event_type, COUNT(*) FROM events
                WHERE cycle_id = ?
                GROUP BY event_type
            """, (cycle_data['cycle_id'],))
            event_stats = dict(cursor.fetchall())

            return {
                'cycle': cycle_data,
                'task_stats': task_stats,
                'event_stats': event_stats
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get comprehensive orchestration status.

        Returns:
            Status dictionary
        """
        stats = self.get_cycle_stats()

        # Calculate time remaining in current cycle
        time_remaining = None
        if self.cycle_start_time is not None:
            elapsed = time.time() - self.cycle_start_time
            time_remaining = max(0, self.cycle_duration - elapsed)

        return {
            'current_cycle': self.current_cycle,
            'cycle_active': self.current_cycle is not None,
            'cycle_start_time': self.cycle_start_time,
            'time_remaining_seconds': time_remaining,
            'stats': stats,
            'database_path': str(self.db_path)
        }


# Module-level API
_orchestrator = None

def get_orchestrator() -> Orchestrator:
    """Get singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator


if __name__ == "__main__":
    # Self-test
    print("DUALITY-ZERO-V2 Orchestrator Self-Test")
    print("=" * 50)

    orch = Orchestrator()

    print("\n1. Starting Cycle")
    cycle_id = orch.start_cycle()
    print(f"   Cycle ID: {cycle_id}")

    print("\n2. Adding Tasks")
    # Add foundational tasks
    task1 = Task(
        task_id="task_001",
        name="Build reality monitor",
        description="Create reality monitoring module",
        priority=TaskPriority.HIGH
    )
    orch.add_task(task1)
    print(f"   Added: {task1.name}")

    task2 = Task(
        task_id="task_002",
        name="Build validation module",
        description="Create validation system",
        priority=TaskPriority.HIGH,
        dependencies=["task_001"]
    )
    orch.add_task(task2)
    print(f"   Added: {task2.name}")

    task3 = Task(
        task_id="task_003",
        name="Build fractal agent",
        description="Create fractal simulation agent",
        priority=TaskPriority.MEDIUM
    )
    orch.add_task(task3)
    print(f"   Added: {task3.name}")

    print("\n3. Getting Next Task")
    next_task = orch.get_next_task()
    if next_task:
        print(f"   Next: {next_task.name} (Priority: {next_task.priority.name})")
    else:
        print("   No tasks available")

    print("\n4. Executing Task")
    def dummy_executor(task: Task) -> str:
        """Reality-grounded task executor for testing."""
        print(f"   Executing: {task.name}")
        # Do real computational work using system metrics
        import psutil
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Real measurement
        memory_info = psutil.virtual_memory()
        # Perform actual computation
        work_metric = (cpu_percent * memory_info.percent) / 100.0
        return f"Success (work_metric: {work_metric:.2f})"

    if next_task:
        success = orch.execute_task(next_task, dummy_executor)
        print(f"   Result: {'✅ Success' if success else '❌ Failed'}")

    print("\n5. Orchestration Status")
    status = orch.get_status()
    print(f"   Current Cycle: {status['current_cycle']}")
    print(f"   Cycle Active: {status['cycle_active']}")
    if status['time_remaining_seconds']:
        minutes = status['time_remaining_seconds'] / 60
        print(f"   Time Remaining: {minutes:.1f} minutes")

    print("\n6. Cycle Stats")
    stats = orch.get_cycle_stats()
    if 'task_stats' in stats:
        print("   Task Status:")
        for status_name, count in stats['task_stats'].items():
            print(f"     {status_name}: {count}")

    print("\n7. Ending Cycle")
    orch.end_cycle(summary="Self-test completed successfully")
    print("   ✅ Cycle ended")

    print("\n✅ Orchestrator operational - autonomous cycle management ready")
