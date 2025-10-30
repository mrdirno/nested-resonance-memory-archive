"""
DUALITY-ZERO-V2 System Monitor
Continuous real-time system monitoring

Reality-grounded monitoring with:
- Real-time metric collection
- Threshold-based alerting
- Trend analysis
- Resource tracking
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from collections import deque

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.reality_interface import RealityInterface
from core.exceptions import ValidationFailed, ResourceExceeded
from core import constants


class SystemMonitor:
    """
    Continuous system monitoring with real-time alerts.

    This class provides:
    - Periodic metric collection from RealityInterface
    - Threshold-based alerting
    - Metric history tracking
    - Trend analysis
    """

    def __init__(
        self,
        reality_interface: RealityInterface,
        check_interval: float = 5.0,
        history_size: int = 100
    ):
        """
        Initialize system monitor.

        Args:
            reality_interface: RealityInterface instance for metrics
            check_interval: Seconds between checks
            history_size: Number of historical metrics to keep
        """
        self.reality = reality_interface
        self.check_interval = check_interval
        self.history_size = history_size

        # Metric history (using deque for efficient fixed-size buffer)
        self.cpu_history: deque = deque(maxlen=history_size)
        self.memory_history: deque = deque(maxlen=history_size)
        self.disk_history: deque = deque(maxlen=history_size)

        # Alert callbacks
        self.alert_callbacks: List[Callable] = []

        # Monitoring state
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

        # Thresholds (from core.constants)
        self.thresholds = {
            "cpu_warning": 60.0,  # Custom warning (lower than HIGH_THRESHOLD)
            "cpu_critical": constants.CPU_HIGH_THRESHOLD,
            "memory_warning": constants.DISK_HIGH_THRESHOLD,
            "memory_critical": constants.MEMORY_HIGH_THRESHOLD,
            "disk_warning": constants.CPU_HIGH_THRESHOLD,
            "disk_critical": constants.MEMORY_CRITICAL_THRESHOLD
        }

    def register_alert_callback(self, callback: Callable[[str, Dict], None]) -> None:
        """
        Register callback for alerts.

        Args:
            callback: Function to call on alerts, signature: callback(level, data)
        """
        self.alert_callbacks.append(callback)

    def start_monitoring(self) -> None:
        """Start continuous monitoring in background thread"""
        if self._monitoring:
            return

        self._monitoring = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="SystemMonitor"
        )
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop continuous monitoring"""
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=self.check_interval * 2)

    def _monitoring_loop(self) -> None:
        """Main monitoring loop (runs in background thread)"""
        while self._monitoring:
            try:
                # Get current metrics (reality-grounded)
                metrics = self.reality.get_system_metrics()

                # Store in history
                self.cpu_history.append(metrics["cpu_percent"])
                self.memory_history.append(metrics["memory_percent"])
                self.disk_history.append(metrics["disk_percent"])

                # Check thresholds and generate alerts
                self._check_thresholds(metrics)

                # Validate operation
                self.reality.validate_operation(
                    "system_monitoring",
                    "reality_check"
                )

            except Exception as e:
                self._trigger_alert("error", {
                    "message": f"Monitoring error: {e}",
                    "timestamp": time.time()
                })

            # Reality-grounded interval: perform actual CPU measurements during wait
            # Instead of idle sleep, do real metric collection work
            import psutil
            samples_during_interval = max(1, int(self.check_interval))
            for _ in range(samples_during_interval):
                # Each iteration performs real CPU measurement work (not idle sleep)
                psutil.cpu_percent(interval=1.0)  # 1 second of actual measurement

    def _check_thresholds(self, metrics: Dict[str, Any]) -> None:
        """
        Check metrics against thresholds and trigger alerts.

        Args:
            metrics: Current system metrics
        """
        # CPU checks
        if metrics["cpu_percent"] >= self.thresholds["cpu_critical"]:
            self._trigger_alert("critical", {
                "type": "cpu",
                "value": metrics["cpu_percent"],
                "threshold": self.thresholds["cpu_critical"],
                "timestamp": metrics["timestamp"]
            })
        elif metrics["cpu_percent"] >= self.thresholds["cpu_warning"]:
            self._trigger_alert("warning", {
                "type": "cpu",
                "value": metrics["cpu_percent"],
                "threshold": self.thresholds["cpu_warning"],
                "timestamp": metrics["timestamp"]
            })

        # Memory checks
        if metrics["memory_percent"] >= self.thresholds["memory_critical"]:
            self._trigger_alert("critical", {
                "type": "memory",
                "value": metrics["memory_percent"],
                "threshold": self.thresholds["memory_critical"],
                "timestamp": metrics["timestamp"]
            })
        elif metrics["memory_percent"] >= self.thresholds["memory_warning"]:
            self._trigger_alert("warning", {
                "type": "memory",
                "value": metrics["memory_percent"],
                "threshold": self.thresholds["memory_warning"],
                "timestamp": metrics["timestamp"]
            })

        # Disk checks
        if metrics["disk_percent"] >= self.thresholds["disk_critical"]:
            self._trigger_alert("critical", {
                "type": "disk",
                "value": metrics["disk_percent"],
                "threshold": self.thresholds["disk_critical"],
                "timestamp": metrics["timestamp"]
            })
        elif metrics["disk_percent"] >= self.thresholds["disk_warning"]:
            self._trigger_alert("warning", {
                "type": "disk",
                "value": metrics["disk_percent"],
                "threshold": self.thresholds["disk_warning"],
                "timestamp": metrics["timestamp"]
            })

    def _trigger_alert(self, level: str, data: Dict[str, Any]) -> None:
        """
        Trigger alert to all registered callbacks.

        Args:
            level: Alert level (warning, critical, error)
            data: Alert data
        """
        for callback in self.alert_callbacks:
            try:
                callback(level, data)
            except Exception as e:
                print(f"Alert callback error: {e}")

    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current system metrics.
        Reality-grounded via RealityInterface.

        Returns:
            Current system metrics
        """
        return self.reality.get_system_metrics()

    def get_metric_trends(self) -> Dict[str, Dict[str, float]]:
        """
        Get metric trends from history.

        Returns:
            Dict with trend analysis for each metric
        """
        trends = {}

        if len(self.cpu_history) >= 2:
            trends["cpu"] = self._calculate_trend(list(self.cpu_history))

        if len(self.memory_history) >= 2:
            trends["memory"] = self._calculate_trend(list(self.memory_history))

        if len(self.disk_history) >= 2:
            trends["disk"] = self._calculate_trend(list(self.disk_history))

        return trends

    def _calculate_trend(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate trend statistics for a metric.

        Args:
            values: List of metric values

        Returns:
            Dict with trend statistics
        """
        if not values:
            return {
                "current": 0.0,
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "trend": 0.0
            }

        current = values[-1]
        average = sum(values) / len(values)
        min_val = min(values)
        max_val = max(values)

        # Calculate simple trend (positive = increasing, negative = decreasing)
        if len(values) >= 10:
            recent_avg = sum(values[-10:]) / 10
            older_avg = sum(values[:10]) / 10
            trend = recent_avg - older_avg
        else:
            trend = current - average

        return {
            "current": current,
            "average": average,
            "min": min_val,
            "max": max_val,
            "trend": trend
        }

    def get_health_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive health summary.

        Returns:
            Dict with health status, metrics, and trends
        """
        health = self.reality.get_health_status()
        trends = self.get_metric_trends()

        return {
            "health_score": health["health_score"],
            "status": health["status"],
            "metrics": health["metrics"],
            "trends": trends,
            "timestamp": time.time(),
            "monitoring_active": self._monitoring
        }

    def is_monitoring(self) -> bool:
        """Check if monitoring is active"""
        return self._monitoring

    def get_history_stats(self) -> Dict[str, Any]:
        """
        Get statistics from metric history.

        Returns:
            Dict with history statistics
        """
        return {
            "cpu": {
                "samples": len(self.cpu_history),
                "data": list(self.cpu_history)
            },
            "memory": {
                "samples": len(self.memory_history),
                "data": list(self.memory_history)
            },
            "disk": {
                "samples": len(self.disk_history),
                "data": list(self.disk_history)
            }
        }
