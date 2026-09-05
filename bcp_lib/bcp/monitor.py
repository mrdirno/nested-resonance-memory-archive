"""
BCP Monitor - Real-time system monitoring with BCP-based triage.

This module provides tools for monitoring system resources and
applying BCP allocation to decide what to track.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import math
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from .core import BCPModel, AttentionItem, Phase


@dataclass
class MonitorSample:
    """A single sample from the BCP monitor."""
    timestamp: float
    budget: float
    phase: Phase
    lambda_: float
    attended_tasks: List[str]
    ignored_tasks: List[str]
    metrics: Dict[str, float]
    # Exception classes only: exception messages may contain sensitive paths/data.
    errors: Dict[str, str] = field(default_factory=dict)


class BCPMonitor:
    """
    Real-time system monitor using BCP allocation.

    This monitor tracks system resources (CPU, memory, etc.) and uses
    the BCP equation to decide which metrics to actively monitor based
    on current resource budget.

    Example:
        >>> from bcp import BCPMonitor
        >>> monitor = BCPMonitor()
        >>> monitor.add_task("cpu", gain=0.9, cost=0.1, collector=lambda: psutil.cpu_percent())
        >>> monitor.add_task("memory", gain=0.8, cost=0.2, collector=lambda: psutil.virtual_memory().percent)
        >>> sample = monitor.sample(budget=1.0)
        >>> print(sample.attended_tasks)
    """

    def __init__(
        self,
        lambda_scale: float = 10.0,
        gamma: float = 0.0
    ):
        """
        Initialize the BCP monitor.

        Args:
            lambda_scale: Scaling factor for metabolic pressure
            gamma: Complexity penalty coefficient
        """
        self.model = BCPModel(lambda_scale=lambda_scale, gamma=gamma)
        self.tasks: Dict[str, Dict] = {}

    def add_task(
        self,
        name: str,
        gain: float,
        cost: float,
        collector: Optional[Callable[[], float]] = None
    ):
        """
        Add a monitoring task.

        Args:
            name: Task identifier
            gain: Expected value of monitoring this metric
            cost: Resource cost to collect this metric
            collector: Optional function to collect the metric value
        """
        self.tasks[name] = {
            'gain': gain,
            'cost': cost,
            'collector': collector
        }

    def remove_task(self, name: str):
        """Remove a monitoring task."""
        if name in self.tasks:
            del self.tasks[name]

    def sample(self, budget: float) -> MonitorSample:
        """
        Take a sample with BCP-based task allocation.

        Args:
            budget: Current resource budget

        Returns:
            MonitorSample with allocation results and collected metrics. Failed
            or non-finite readings are NaN, with their exception class in errors.
        """
        if not math.isfinite(budget) or budget < 0:
            raise ValueError("budget must be finite and non-negative")
        # Create attention items
        items = [
            AttentionItem(
                name=name,
                gain=task['gain'],
                cost=task['cost']
            )
            for name, task in self.tasks.items()
        ]

        # Run BCP allocation
        result = self.model.allocate(items, budget)

        # Collect metrics for attended tasks
        metrics = {}
        errors = {}
        for name in result.attended:
            task = self.tasks.get(name)
            if task and task['collector']:
                try:
                    value = float(task['collector']())
                    if not math.isfinite(value):
                        raise ValueError("collector returned a non-finite reading")
                    metrics[name] = value
                except Exception as exc:
                    metrics[name] = float('nan')
                    errors[name] = type(exc).__name__

        return MonitorSample(
            timestamp=time.time(),
            budget=budget,
            phase=result.phase,
            lambda_=result.lambda_,
            attended_tasks=result.attended,
            ignored_tasks=result.ignored,
            metrics=metrics,
            errors=errors
        )

    def run(
        self,
        budget_fn: Callable[[], float],
        interval: float = 1.0,
        duration: float = 10.0,
        callback: Optional[Callable[[MonitorSample], None]] = None
    ) -> List[MonitorSample]:
        """
        Run continuous monitoring for a duration.

        Args:
            budget_fn: Function that returns current budget
            interval: Positive seconds to wait after each sample/callback
            duration: Non-negative duration in seconds. Sleep is bounded by the
                remaining duration; a collector or callback already running is
                not interrupted and may extend the total elapsed time.
            callback: Optional function called with each sample

        Returns:
            List of all collected samples
        """
        if not math.isfinite(interval) or interval <= 0:
            raise ValueError("interval must be finite and positive")
        if not math.isfinite(duration) or duration < 0:
            raise ValueError("duration must be finite and non-negative")
        samples = []
        deadline = time.monotonic() + duration

        while time.monotonic() < deadline:
            budget = budget_fn()
            sample = self.sample(budget)
            samples.append(sample)

            if callback:
                callback(sample)

            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(interval, remaining))

        return samples


def create_system_monitor() -> BCPMonitor:
    """
    Create a monitor pre-configured for system metrics.

    Requires psutil to be installed.

    Returns:
        BCPMonitor with common system monitoring tasks
    """
    try:
        import psutil
    except ImportError:
        raise ImportError("psutil required for system monitoring. Install with: pip install psutil")

    monitor = BCPMonitor()

    # Gains/costs are configurable allocation weights, not measured overheads.
    monitor.add_task(
        "cpu_percent",
        gain=0.9,
        cost=0.1,
        # A blocking interval avoids psutil's meaningless first nonblocking 0.
        collector=lambda: psutil.cpu_percent(interval=0.1)
    )

    monitor.add_task(
        "memory_percent",
        gain=0.85,
        cost=0.1,
        collector=lambda: psutil.virtual_memory().percent
    )

    monitor.add_task(
        "disk_usage",
        gain=0.6,
        cost=0.2,
        collector=lambda: psutil.disk_usage('/').percent
    )

    monitor.add_task(
        "swap_usage",
        gain=0.4,
        cost=0.15,
        collector=lambda: psutil.swap_memory().percent
    )

    monitor.add_task(
        "process_count",
        gain=0.3,
        cost=0.25,
        collector=lambda: len(psutil.pids())
    )

    return monitor


def compute_system_budget() -> float:
    """
    Compute current system budget based on available resources.

    Budget = (1 - cpu_usage) × (1 - memory_usage)

    Higher available resources = higher budget.

    Returns:
        Budget value between 0 and 1

    Raises:
        ImportError: If psutil is absent; no substitute measurement is returned.
    """
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1) / 100
        mem = psutil.virtual_memory().percent / 100
        return (1 - cpu) * (1 - mem)
    except ImportError as exc:
        raise ImportError("psutil required for system monitoring. Install with: pip install psutil") from exc
