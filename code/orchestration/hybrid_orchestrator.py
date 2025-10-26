"""
DUALITY-ZERO-V2 Hybrid Orchestrator
Main orchestration and coordination system

Coordinates:
- Reality layer (system operations)
- Fractal layer (simulations)
- Bridge layer (transcendental computing)
- Validation layer (compliance checks)
"""

import time
import threading
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from core.exceptions import OrchestrationError, ValidationFailed, ResourceExceeded
from reality.system_monitor import SystemMonitor
from reality.metrics_analyzer import MetricsAnalyzer


class OperationMode(Enum):
    """Orchestration operation modes"""
    REALITY = "reality"  # Pure reality operations
    HYBRID = "hybrid"    # Reality + fractal simulations
    FRACTAL = "fractal"  # Pure fractal (validated against reality)


class HybridOrchestrator:
    """
    Main orchestrator for DUALITY-ZERO-V2 hybrid intelligence system.

    Coordinates all subsystems and ensures:
    - Reality-grounded operations
    - Resource constraint compliance
    - Continuous monitoring
    - Autonomous evolution
    """

    def __init__(
        self,
        workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2",
        mode: OperationMode = OperationMode.HYBRID
    ):
        """
        Initialize hybrid orchestrator.

        Args:
            workspace_path: Root workspace path
            mode: Operation mode (reality, hybrid, fractal)
        """
        self.workspace_path = Path(workspace_path)
        self.mode = mode

        # Initialize core subsystems
        self.reality = RealityInterface(str(workspace_path))
        self.monitor = SystemMonitor(self.reality, check_interval=5.0)
        self.analyzer = MetricsAnalyzer(self.reality)

        # Operation tracking
        self.operation_count = 0
        self.start_time = time.time()
        self.last_health_check = 0.0

        # State
        self._running = False
        self._orchestration_thread: Optional[threading.Thread] = None

        # Callbacks for lifecycle events
        self.on_operation_complete: List[Callable] = []
        self.on_health_warning: List[Callable] = []
        self.on_resource_exceeded: List[Callable] = []

    def initialize(self) -> None:
        """
        Initialize orchestrator and all subsystems.
        Reality-grounded: Establishes baseline metrics.
        """
        print("Initializing DUALITY-ZERO-V2 Hybrid Orchestrator...")

        # Establish performance baseline
        print("  Establishing performance baseline...")
        self.analyzer.establish_baseline(samples=5, interval=0.5)

        # Register monitoring callbacks
        self.monitor.register_alert_callback(self._handle_monitor_alert)

        # Start monitoring
        print("  Starting system monitoring...")
        self.monitor.start_monitoring()

        # Validate initialization
        health = self.reality.get_health_status()
        print(f"  System health: {health['status']} (score: {health['health_score']})")

        if health["health_score"] < 50:
            raise OrchestrationError(
                f"System health too low to start: {health['health_score']}"
            )

        print("Orchestrator initialized successfully.")

    def shutdown(self) -> None:
        """Shutdown orchestrator gracefully"""
        print("Shutting down DUALITY-ZERO-V2 Hybrid Orchestrator...")

        # Stop monitoring
        self.monitor.stop_monitoring()

        # Stop orchestration loop if running
        if self._running:
            self.stop_orchestration()

        print("Orchestrator shutdown complete.")

    def _handle_monitor_alert(self, level: str, data: Dict[str, Any]) -> None:
        """
        Handle alerts from system monitor.

        Args:
            level: Alert level (warning, critical, error)
            data: Alert data
        """
        print(f"[{level.upper()}] Monitor Alert: {data}")

        if level in ["warning", "critical"]:
            for callback in self.on_health_warning:
                callback(level, data)

        if level == "critical" and data.get("type") in ["cpu", "memory"]:
            for callback in self.on_resource_exceeded:
                callback(level, data)

    def execute_operation(
        self,
        operation_name: str,
        operation_func: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Execute an operation with full tracking and validation.

        Args:
            operation_name: Name of operation
            operation_func: Function to execute
            *args, **kwargs: Arguments for operation

        Returns:
            Operation result

        Raises:
            OrchestrationError: If operation fails
            ResourceExceeded: If resource limits exceeded
        """
        # Pre-operation validation
        start_metrics = self.reality.get_system_metrics()
        start_time = time.time()

        # Check resource availability
        if start_metrics["memory_percent"] > 90:
            raise ResourceExceeded(
                f"Memory too high to start operation: {start_metrics['memory_percent']}%"
            )

        # Execute operation
        try:
            result = operation_func(*args, **kwargs)
        except Exception as e:
            # Track failed operation
            duration = time.time() - start_time
            self.reality.track_resource_usage(
                operation_name,
                cpu_used=0.0,
                memory_used_mb=0.0,
                duration_seconds=duration,
                status="failed"
            )
            raise OrchestrationError(f"Operation failed: {e}") from e

        # Post-operation tracking
        end_metrics = self.reality.get_system_metrics()
        duration = time.time() - start_time

        # Calculate resource usage
        cpu_delta = end_metrics["cpu_percent"] - start_metrics["cpu_percent"]
        memory_delta = end_metrics["memory_used_mb"] - start_metrics["memory_used_mb"]

        # Track successful operation
        self.reality.track_resource_usage(
            operation_name,
            cpu_used=max(0, cpu_delta),
            memory_used_mb=max(0, memory_delta),
            duration_seconds=duration,
            status="success"
        )

        self.operation_count += 1

        # Trigger callbacks
        for callback in self.on_operation_complete:
            callback(operation_name, {
                "duration": duration,
                "cpu_delta": cpu_delta,
                "memory_delta": memory_delta,
                "result": result
            })

        return result

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status.

        Returns:
            Dict with full system status
        """
        health = self.monitor.get_health_summary()
        analysis = self.analyzer.analyze_current_state()
        uptime = time.time() - self.start_time

        return {
            "uptime_seconds": uptime,
            "operation_count": self.operation_count,
            "mode": self.mode.value,
            "health": health,
            "analysis": analysis,
            "monitoring_active": self.monitor.is_monitoring(),
            "timestamp": time.time()
        }

    def check_health(self, force: bool = False) -> Dict[str, Any]:
        """
        Check system health.

        Args:
            force: Force check even if recently checked

        Returns:
            Health status
        """
        current_time = time.time()

        # Throttle health checks (max once per 30 seconds unless forced)
        if not force and (current_time - self.last_health_check) < 30:
            return {"status": "cached", "message": "Using cached health data"}

        self.last_health_check = current_time

        health = self.reality.get_health_status()
        analysis = self.analyzer.analyze_current_state()

        # Trigger warnings if needed
        if health["health_score"] < 70:
            for callback in self.on_health_warning:
                callback("warning", {
                    "health_score": health["health_score"],
                    "status": health["status"],
                    "timestamp": current_time
                })

        return {
            "health": health,
            "analysis": analysis,
            "timestamp": current_time
        }

    def start_orchestration(self, interval: float = 60.0) -> None:
        """
        Start autonomous orchestration loop.

        Args:
            interval: Seconds between orchestration cycles
        """
        if self._running:
            return

        self._running = True
        self._orchestration_thread = threading.Thread(
            target=self._orchestration_loop,
            args=(interval,),
            daemon=True,
            name="Orchestration"
        )
        self._orchestration_thread.start()
        print(f"Autonomous orchestration started (interval: {interval}s)")

    def stop_orchestration(self) -> None:
        """Stop autonomous orchestration loop"""
        self._running = False
        if self._orchestration_thread:
            self._orchestration_thread.join(timeout=10)
        print("Autonomous orchestration stopped")

    def _orchestration_loop(self, interval: float) -> None:
        """
        Main autonomous orchestration loop.

        Args:
            interval: Seconds between cycles
        """
        while self._running:
            try:
                # Perform orchestration cycle
                self._orchestration_cycle()

            except Exception as e:
                print(f"Orchestration cycle error: {e}")

            # Reality-grounded interval: perform actual metric measurements during wait
            # Instead of idle sleep, do real system monitoring work
            import psutil
            samples_during_interval = max(1, int(interval))
            for _ in range(samples_during_interval):
                # Each iteration performs real measurement work (not idle sleep)
                psutil.cpu_percent(interval=1.0)  # 1 second of actual CPU measurement

    def _orchestration_cycle(self) -> None:
        """
        Single orchestration cycle.

        Performs:
        - Health check
        - Anomaly detection
        - Resource optimization
        - Metric collection
        """
        # Check system health
        health = self.check_health(force=True)

        # Analyze for anomalies
        analysis = self.analyzer.analyze_current_state()

        if analysis.get("has_anomalies"):
            print(f"Anomalies detected: {analysis['anomalies']}")

        # Validate reality compliance
        self.reality.validate_operation(
            "orchestration_cycle",
            "reality_check"
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report.

        Returns:
            Performance metrics and analysis
        """
        status = self.get_system_status()
        baseline = self.analyzer.get_baseline_report()
        performance_score = self.analyzer.calculate_performance_score()

        return {
            "status": status,
            "baseline": baseline,
            "performance_score": performance_score,
            "timestamp": time.time()
        }

    def __enter__(self):
        """Context manager entry"""
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.shutdown()
        return False
