"""
BCP Monitor - Real-time system monitoring with BCP-based triage.

This module provides tools for monitoring system resources and
applying BCP allocation to decide what to track.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Callable
from .core import BCPModel, AttentionItem, BCPResult, Phase


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
            MonitorSample with allocation results and collected metrics
        """
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
        for name in result.attended:
            task = self.tasks.get(name)
            if task and task['collector']:
                try:
                    metrics[name] = task['collector']()
                except Exception:
                    metrics[name] = float('nan')

        return MonitorSample(
            timestamp=time.time(),
            budget=budget,
            phase=result.phase,
            lambda_=result.lambda_,
            attended_tasks=result.attended,
            ignored_tasks=result.ignored,
            metrics=metrics
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
            interval: Seconds between samples
            duration: Total monitoring duration in seconds
            callback: Optional function called with each sample

        Returns:
            List of all collected samples
        """
        samples = []
        start_time = time.time()

        while time.time() - start_time < duration:
            budget = budget_fn()
            sample = self.sample(budget)
            samples.append(sample)

            if callback:
                callback(sample)

            time.sleep(interval)

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

    # Add system monitoring tasks with realistic gain/cost
    monitor.add_task(
        "cpu_percent",
        gain=0.9,
        cost=0.1,
        collector=lambda: psutil.cpu_percent(interval=0)
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
    """
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1) / 100
        mem = psutil.virtual_memory().percent / 100
        return (1 - cpu) * (1 - mem)
    except ImportError:
        return 0.5  # Default if psutil not available
