#!/usr/bin/env python3
"""
Real-Time Validation Campaign Dashboard

Purpose: Live monitoring and visualization of C186-C189 validation campaign progress

This dashboard provides real-time status updates during the ~28-hour validation
campaign, tracking:
- Experiment completion rates (C186: 10, C187: 30, C188: 40, C189: 100)
- Runtime estimates and projections
- Preliminary validation results
- Resource utilization (CPU, memory, disk)
- Error detection and alerting

The goal is to maintain visibility during extended experimental execution,
enabling proactive intervention if issues arise while documenting progress
for publication reporting.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1024
License: GPL-3.0

Co-Authored-By: Claude <noreply@anthropic.com>
"""

import os
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import statistics


@dataclass
class ExperimentStatus:
    """Container for experiment status."""
    cycle_id: str
    total_experiments: int
    completed_experiments: int
    status: str  # "not_started", "running", "complete"
    elapsed_time: Optional[float] = None  # seconds
    estimated_remaining: Optional[float] = None  # seconds
    current_seed: Optional[int] = None
    process_pid: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_mb: Optional[float] = None


class ValidationCampaignDashboard:
    """Real-time monitoring dashboard for validation campaign."""

    def __init__(self):
        """Initialize dashboard with experiment configurations."""
        self.experiments = {
            "C186": {
                "log_path": Path("/tmp/c186_output.log"),
                "results_path": Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle186_metapopulation_hierarchical_validation_results.json"),
                "total": 10,
                "estimated_hours": 6.0
            },
            "C187": {
                "log_path": Path("/tmp/c187_output.log"),
                "results_path": Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle187_network_structure_effects_results.json"),
                "total": 30,
                "estimated_hours": 5.0
            },
            "C188": {
                "log_path": Path("/tmp/c188_output.log"),
                "results_path": Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle188_memory_effects_results.json"),
                "total": 40,
                "estimated_hours": 6.7
            },
            "C189": {
                "log_path": Path("/tmp/c189_output.log"),
                "results_path": Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle189_burst_clustering_results.json"),
                "total": 100,
                "estimated_hours": 16.7
            },
        }

        self.campaign_start = None
        self.last_update = None

    def get_experiment_status(self, cycle_id: str) -> ExperimentStatus:
        """
        Get current status of an experiment.

        Args:
            cycle_id: Experiment identifier (C186, C187, etc.)

        Returns:
            ExperimentStatus object
        """
        config = self.experiments[cycle_id]
        log_path = config["log_path"]
        results_path = config["results_path"]
        total = config["total"]

        # Check if complete (results JSON exists)
        if results_path.exists():
            try:
                with open(results_path, 'r') as f:
                    data = json.load(f)
                    if data.get('status') == 'complete':
                        return ExperimentStatus(
                            cycle_id=cycle_id,
                            total_experiments=total,
                            completed_experiments=total,
                            status="complete",
                            elapsed_time=None,
                            estimated_remaining=0.0
                        )
            except:
                pass

        # Parse log file
        if not log_path.exists():
            return ExperimentStatus(
                cycle_id=cycle_id,
                total_experiments=total,
                completed_experiments=0,
                status="not_started"
            )

        try:
            with open(log_path, 'r') as f:
                log_content = f.read()

            lines = log_content.strip().split('\n')

            # Count completed experiments
            completed = log_content.count('Basin A:')  # Results marker

            # Check if currently running
            current_seed = None
            for line in reversed(lines):
                if 'Running seed' in line and '...' in line:
                    try:
                        current_seed = int(line.split('seed ')[-1].replace('...', '').strip())
                        break
                    except:
                        pass

            # Determine status
            if completed >= total:
                status = "complete"
            elif current_seed is not None:
                status = "running"
            elif completed > 0:
                status = "running"  # Between experiments
            else:
                status = "running"  # Just started

            # Try to find PID and get process info
            process_pid = None
            cpu_percent = None
            memory_mb = None

            # Check common PIDs (would be better to track in PID file)
            for pid in [33600, 33601, 33602, 33603]:  # Common PIDs
                try:
                    result = subprocess.run(
                        ['ps', '-p', str(pid), '-o', 'comm,pcpu,rss'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0 and 'python' in result.stdout.lower():
                        lines = result.stdout.strip().split('\n')
                        if len(lines) >= 2:
                            data = lines[1].split()
                            if len(data) >= 3:
                                cpu_percent = float(data[1])
                                memory_mb = float(data[2]) / 1024  # RSS in KB, convert to MB
                                process_pid = pid
                                break
                except:
                    pass

            # Estimate time
            elapsed_time = None
            estimated_remaining = None

            if completed > 0:
                # Rough estimate: total_time / completed * remaining
                estimated_hours = config["estimated_hours"]
                per_experiment_hours = estimated_hours / total
                estimated_remaining = (total - completed) * per_experiment_hours * 3600  # seconds

            return ExperimentStatus(
                cycle_id=cycle_id,
                total_experiments=total,
                completed_experiments=completed,
                status=status,
                elapsed_time=elapsed_time,
                estimated_remaining=estimated_remaining,
                current_seed=current_seed,
                process_pid=process_pid,
                cpu_percent=cpu_percent,
                memory_mb=memory_mb
            )

        except Exception as e:
            print(f"Error checking {cycle_id}: {e}")
            return ExperimentStatus(
                cycle_id=cycle_id,
                total_experiments=total,
                completed_experiments=0,
                status="error"
            )

    def get_campaign_progress(self) -> Dict:
        """
        Get overall campaign progress.

        Returns:
            dict with campaign-level statistics
        """
        statuses = {
            cycle_id: self.get_experiment_status(cycle_id)
            for cycle_id in self.experiments.keys()
        }

        total_experiments = sum(s.total_experiments for s in statuses.values())
        completed_experiments = sum(s.completed_experiments for s in statuses.values())

        overall_progress = (completed_experiments / total_experiments) * 100 if total_experiments > 0 else 0.0

        # Count by status
        complete_count = sum(1 for s in statuses.values() if s.status == "complete")
        running_count = sum(1 for s in statuses.values() if s.status == "running")
        not_started_count = sum(1 for s in statuses.values() if s.status == "not_started")

        # Estimate remaining time
        total_remaining = sum(
            s.estimated_remaining or 0.0
            for s in statuses.values()
            if s.status != "complete"
        )

        return {
            'statuses': statuses,
            'total_experiments': total_experiments,
            'completed_experiments': completed_experiments,
            'overall_progress': overall_progress,
            'complete_count': complete_count,
            'running_count': running_count,
            'not_started_count': not_started_count,
            'estimated_remaining_hours': total_remaining / 3600 if total_remaining else 0.0,
            'timestamp': datetime.now()
        }

    def render_dashboard(self) -> str:
        """
        Render dashboard as formatted text.

        Returns:
            Formatted dashboard string
        """
        progress = self.get_campaign_progress()

        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("VALIDATION CAMPAIGN DASHBOARD")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Timestamp: {progress['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Overall Progress
        lines.append("CAMPAIGN OVERVIEW")
        lines.append("-" * 80)
        lines.append(f"Total Experiments: {progress['completed_experiments']}/{progress['total_experiments']} ({progress['overall_progress']:.1f}%)")
        lines.append(f"Experiments Complete: {progress['complete_count']}/4")
        lines.append(f"Experiments Running: {progress['running_count']}/4")
        lines.append(f"Experiments Pending: {progress['not_started_count']}/4")

        if progress['estimated_remaining_hours'] > 0:
            lines.append(f"Estimated Remaining: {progress['estimated_remaining_hours']:.1f} hours")
            eta = datetime.now() + timedelta(hours=progress['estimated_remaining_hours'])
            lines.append(f"Estimated Completion: {eta.strftime('%Y-%m-%d %H:%M:%S')}")

        lines.append("")

        # Per-Experiment Status
        lines.append("EXPERIMENT STATUS")
        lines.append("-" * 80)

        for cycle_id in ["C186", "C187", "C188", "C189"]:
            status = progress['statuses'][cycle_id]

            # Status emoji
            if status.status == "complete":
                emoji = "✅"
            elif status.status == "running":
                emoji = "⏳"
            elif status.status == "not_started":
                emoji = "⏸️"
            else:
                emoji = "❌"

            lines.append(f"{emoji} {cycle_id}: {status.completed_experiments}/{status.total_experiments} experiments")

            if status.status == "running":
                if status.current_seed:
                    lines.append(f"   Current: Seed {status.current_seed}")

                if status.process_pid:
                    lines.append(f"   Process: PID {status.process_pid}, CPU {status.cpu_percent:.1f}%, Memory {status.memory_mb:.1f} MB")

                if status.estimated_remaining:
                    remaining_min = status.estimated_remaining / 60
                    lines.append(f"   Estimated Remaining: {remaining_min:.1f} minutes")

            elif status.status == "complete":
                lines.append(f"   Status: Complete ✓")

            elif status.status == "not_started":
                lines.append(f"   Status: Pending")

            lines.append("")

        # Progress Bar
        lines.append("OVERALL PROGRESS")
        lines.append("-" * 80)

        bar_width = 50
        filled = int((progress['overall_progress'] / 100) * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)

        lines.append(f"[{bar}] {progress['overall_progress']:.1f}%")
        lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    def save_dashboard_snapshot(self, output_path: Path):
        """
        Save current dashboard state to file.

        Args:
            output_path: Path to save snapshot
        """
        dashboard_text = self.render_dashboard()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(dashboard_text)

    def monitor_continuous(self, interval: int = 60, duration: int = 3600):
        """
        Continuously monitor campaign and print updates.

        Args:
            interval: Update interval in seconds
            duration: Total monitoring duration in seconds
        """
        start_time = time.time()

        print("Starting continuous monitoring...")
        print(f"Update interval: {interval} seconds")
        print(f"Duration: {duration / 3600:.1f} hours")
        print("")

        while (time.time() - start_time) < duration:
            # Clear screen (Unix-like systems)
            os.system('clear' if os.name != 'nt' else 'cls')

            # Render and print dashboard
            dashboard = self.render_dashboard()
            print(dashboard)

            # Save snapshot
            snapshot_path = Path("/Volumes/dual/DUALITY-ZERO-V2/archive/monitoring/dashboard_snapshot.txt")
            self.save_dashboard_snapshot(snapshot_path)

            # Check if complete
            progress = self.get_campaign_progress()
            if progress['complete_count'] == 4:
                print("\n🎉 CAMPAIGN COMPLETE!")
                break

            # Wait for next update
            time.sleep(interval)


def main():
    """Run dashboard once and display current status."""

    dashboard = ValidationCampaignDashboard()

    # Render and print
    output = dashboard.render_dashboard()
    print(output)

    # Save snapshot
    snapshot_path = Path("/Volumes/dual/DUALITY-ZERO-V2/archive/monitoring/dashboard_snapshot.txt")
    dashboard.save_dashboard_snapshot(snapshot_path)

    print(f"\n📊 Dashboard snapshot saved to: {snapshot_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--monitor":
        # Continuous monitoring mode
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        duration = int(sys.argv[3]) if len(sys.argv) > 3 else 28 * 3600  # 28 hours default

        dashboard = ValidationCampaignDashboard()
        dashboard.monitor_continuous(interval=interval, duration=duration)
    else:
        # Single snapshot mode
        main()
