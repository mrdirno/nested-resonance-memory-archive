#!/usr/bin/env python3
"""
Paper 5 Series Master Launch Script
====================================

Coordinates execution of all Paper 5 experimental studies (5A-5F).

Papers:
  5A: Parameter Space Mapping (280 conditions, ~4.7 hours)
  5B: Temporal Pattern Dynamics (20 conditions, ~20 minutes)
  5C: Population Scaling Laws (50 conditions, ~1-2 hours)
  5D: Pattern Mining (COMPLETE - skipped)
  5E: Network Topology Effects (55 conditions, ~55 minutes)
  5F: Environmental Perturbations (140 conditions, ~2.3 hours)

Total Runtime: ~17-18 hours (545 NEW experiments, 5D uses existing data)

Usage:
  python paper5_series_master_launch.py --mode sequential
  python paper5_series_master_launch.py --mode parallel --max-concurrent 2
  python paper5_series_master_launch.py --papers 5A 5C --mode sequential

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import argparse
import json
import os
import psutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Constants
EXPERIMENTS_DIR = Path(__file__).parent
RESULTS_DIR = Path(__file__).parent.parent.parent / "data" / "results"
LOGS_DIR = Path(__file__).parent.parent.parent / "logs"

# Paper 5 Series Configuration
PAPER5_SERIES = {
    "5A": {
        "name": "Parameter Space Mapping",
        "script": "paper5a_parameter_sensitivity.py",
        "conditions": 280,
        "estimated_runtime_hours": 4.7,
        "description": "Systematic parameter sweep across growth rate, energy coupling, death rate",
        "skip": False
    },
    "5B": {
        "name": "Temporal Pattern Dynamics",
        "script": "paper5b_extended_timescale.py",
        "conditions": 20,
        "estimated_runtime_hours": 0.33,  # 20 minutes
        "description": "Extended 10,000-cycle experiments testing temporal stability",
        "skip": False
    },
    "5C": {
        "name": "Population Scaling Laws",
        "script": "paper5c_scaling_behavior.py",
        "conditions": 50,
        "estimated_runtime_hours": 1.5,
        "description": "Scaling behavior across population sizes (50-800 agents)",
        "skip": False
    },
    "5D": {
        "name": "Emergence Pattern Catalog",
        "script": "paper5d_pattern_mining.py",
        "conditions": 0,  # Uses existing C171/C175/C176/C177 data
        "estimated_runtime_hours": 0,
        "description": "Pattern mining (COMPLETE - 100% submission-ready)",
        "skip": True  # Already complete
    },
    "5E": {
        "name": "Network Topology Effects",
        "script": "paper5e_network_topology.py",
        "conditions": 55,
        "estimated_runtime_hours": 0.92,  # 55 minutes
        "description": "Topology analysis (fully connected, random, small-world, scale-free, lattice)",
        "skip": False
    },
    "5F": {
        "name": "Environmental Perturbations",
        "script": "paper5f_environmental_perturbations.py",
        "conditions": 140,
        "estimated_runtime_hours": 2.3,
        "description": "Robustness testing (agent removal, noise, shocks, perturbations)",
        "skip": False
    }
}


class Paper5SeriesOrchestrator:
    """Orchestrates execution of Paper 5 series experiments."""

    def __init__(self, mode: str = "sequential", max_concurrent: int = 1,
                 papers: Optional[List[str]] = None, dry_run: bool = False):
        self.mode = mode
        self.max_concurrent = max_concurrent
        self.papers = papers or ["5A", "5B", "5C", "5E", "5F"]  # 5D skipped
        self.dry_run = dry_run

        # Execution tracking
        self.start_time = None
        self.results = {}
        self.processes = {}

        # Create directories
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        # Logging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOGS_DIR / f"paper5_series_launch_{timestamp}.log"

    def log(self, message: str, level: str = "INFO"):
        """Log message to file and stdout."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    def check_resources(self) -> Tuple[float, float]:
        """Check current system resource usage."""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        return cpu_percent, memory_percent

    def check_blocking_processes(self) -> List[Tuple[int, str]]:
        """Check for long-running processes that might block execution."""
        blocking = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_times']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'cycle255' in cmdline.lower() or 'c255' in cmdline.lower():
                    cpu_hours = proc.info['cpu_times'].user / 3600
                    blocking.append((proc.info['pid'], f"C255 (CPU: {cpu_hours:.1f}h)"))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return blocking

    def estimate_total_runtime(self) -> float:
        """Estimate total runtime in hours."""
        total_hours = 0
        for paper_id in self.papers:
            if paper_id in PAPER5_SERIES and not PAPER5_SERIES[paper_id]["skip"]:
                total_hours += PAPER5_SERIES[paper_id]["estimated_runtime_hours"]
        return total_hours

    def run_paper(self, paper_id: str) -> Dict:
        """Execute a single Paper 5 experiment script."""
        paper_config = PAPER5_SERIES[paper_id]
        script_path = EXPERIMENTS_DIR / paper_config["script"]

        self.log(f"Starting Paper {paper_id}: {paper_config['name']}")
        self.log(f"  Script: {script_path.name}")
        self.log(f"  Conditions: {paper_config['conditions']}")
        self.log(f"  Estimated runtime: {paper_config['estimated_runtime_hours']:.2f} hours")

        if self.dry_run:
            self.log(f"DRY RUN: Would execute {script_path.name}", "DRYRUN")
            return {
                "paper_id": paper_id,
                "status": "DRY_RUN",
                "runtime_seconds": 0,
                "conditions_completed": 0
            }

        # Check script exists
        if not script_path.exists():
            self.log(f"ERROR: Script not found: {script_path}", "ERROR")
            return {
                "paper_id": paper_id,
                "status": "ERROR",
                "error": f"Script not found: {script_path}",
                "runtime_seconds": 0
            }

        # Execute script
        start_time = time.time()
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=paper_config["estimated_runtime_hours"] * 3600 * 1.5  # 1.5× safety margin
            )
            runtime = time.time() - start_time

            if result.returncode == 0:
                self.log(f"✅ Paper {paper_id} completed successfully ({runtime/3600:.2f} hours)")
                status = "SUCCESS"
            else:
                self.log(f"❌ Paper {paper_id} failed (exit code {result.returncode})", "ERROR")
                self.log(f"STDERR: {result.stderr[:500]}", "ERROR")
                status = "FAILED"

            return {
                "paper_id": paper_id,
                "status": status,
                "runtime_seconds": runtime,
                "runtime_hours": runtime / 3600,
                "exit_code": result.returncode,
                "stdout_lines": len(result.stdout.splitlines()),
                "stderr_lines": len(result.stderr.splitlines()),
                "conditions_completed": paper_config["conditions"] if status == "SUCCESS" else 0
            }

        except subprocess.TimeoutExpired:
            runtime = time.time() - start_time
            self.log(f"⏱️ Paper {paper_id} TIMEOUT after {runtime/3600:.2f} hours", "ERROR")
            return {
                "paper_id": paper_id,
                "status": "TIMEOUT",
                "runtime_seconds": runtime,
                "runtime_hours": runtime / 3600,
                "error": "Execution timeout exceeded"
            }
        except Exception as e:
            runtime = time.time() - start_time
            self.log(f"💥 Paper {paper_id} EXCEPTION: {str(e)}", "ERROR")
            return {
                "paper_id": paper_id,
                "status": "EXCEPTION",
                "runtime_seconds": runtime,
                "error": str(e)
            }

    def run_sequential(self):
        """Run all papers sequentially."""
        self.log("=" * 70)
        self.log("PAPER 5 SERIES: SEQUENTIAL EXECUTION")
        self.log("=" * 70)

        total_runtime = self.estimate_total_runtime()
        self.log(f"Total estimated runtime: {total_runtime:.2f} hours")
        self.log(f"Papers to execute: {', '.join(self.papers)}")

        # Check resources
        cpu, mem = self.check_resources()
        self.log(f"System resources: CPU={cpu:.1f}%, Memory={mem:.1f}%")

        # Check blocking processes
        blocking = self.check_blocking_processes()
        if blocking:
            self.log(f"⚠️  Blocking processes detected:", "WARNING")
            for pid, desc in blocking:
                self.log(f"  - PID {pid}: {desc}", "WARNING")
            self.log("Consider waiting for these to complete for optimal performance", "WARNING")

        # Execute papers
        self.start_time = time.time()
        for paper_id in self.papers:
            if paper_id in PAPER5_SERIES:
                if PAPER5_SERIES[paper_id]["skip"]:
                    self.log(f"⏭️  Skipping Paper {paper_id} (already complete)")
                    continue

                result = self.run_paper(paper_id)
                self.results[paper_id] = result
            else:
                self.log(f"⚠️  Unknown paper ID: {paper_id}", "WARNING")

        total_elapsed = time.time() - self.start_time
        self.log("=" * 70)
        self.log(f"SEQUENTIAL EXECUTION COMPLETE: {total_elapsed/3600:.2f} hours total")
        self.log("=" * 70)

    def run_parallel(self):
        """Run papers in parallel (up to max_concurrent)."""
        self.log("=" * 70)
        self.log("PAPER 5 SERIES: PARALLEL EXECUTION")
        self.log(f"Max concurrent: {self.max_concurrent}")
        self.log("=" * 70)

        # TODO: Implement parallel execution with process pool
        self.log("⚠️  Parallel mode not yet implemented", "WARNING")
        self.log("Falling back to sequential execution", "WARNING")
        self.run_sequential()

    def save_results(self):
        """Save execution results to JSON."""
        if not self.results:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = RESULTS_DIR / f"paper5_series_results_{timestamp}.json"

        summary = {
            "execution_mode": self.mode,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            "total_runtime_hours": (time.time() - self.start_time) / 3600 if self.start_time else 0,
            "papers_attempted": len(self.results),
            "papers_successful": sum(1 for r in self.results.values() if r.get("status") == "SUCCESS"),
            "papers_failed": sum(1 for r in self.results.values() if r.get("status") in ["FAILED", "TIMEOUT", "EXCEPTION"]),
            "total_conditions": sum(r.get("conditions_completed", 0) for r in self.results.values()),
            "papers": self.results
        }

        with open(results_file, "w") as f:
            json.dump(summary, f, indent=2)

        self.log(f"Results saved: {results_file}")

    def print_summary(self):
        """Print execution summary."""
        if not self.results:
            return

        self.log("")
        self.log("=" * 70)
        self.log("EXECUTION SUMMARY")
        self.log("=" * 70)

        for paper_id, result in self.results.items():
            status_emoji = {
                "SUCCESS": "✅",
                "FAILED": "❌",
                "TIMEOUT": "⏱️",
                "EXCEPTION": "💥",
                "DRY_RUN": "🔍"
            }.get(result["status"], "❓")

            runtime_str = f"{result.get('runtime_hours', 0):.2f}h" if result.get('runtime_hours') else "N/A"
            conditions_str = f"{result.get('conditions_completed', 0)} conditions" if result.get('conditions_completed') else "N/A"

            self.log(f"{status_emoji} Paper {paper_id}: {result['status']} - {runtime_str} - {conditions_str}")

        total_hours = sum(r.get('runtime_hours', 0) for r in self.results.values())
        total_conditions = sum(r.get('conditions_completed', 0) for r in self.results.values())
        self.log("")
        self.log(f"Total runtime: {total_hours:.2f} hours")
        self.log(f"Total conditions completed: {total_conditions}")
        self.log("=" * 70)

    def execute(self):
        """Main execution entry point."""
        try:
            if self.mode == "sequential":
                self.run_sequential()
            elif self.mode == "parallel":
                self.run_parallel()
            else:
                self.log(f"Unknown execution mode: {self.mode}", "ERROR")
                return

            self.save_results()
            self.print_summary()

        except KeyboardInterrupt:
            self.log("\n⚠️  Execution interrupted by user", "WARNING")
            self.save_results()
            self.print_summary()
            raise


def main():
    parser = argparse.ArgumentParser(
        description="Paper 5 Series Master Launch Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Sequential execution (all papers)
  python paper5_series_master_launch.py --mode sequential

  # Execute specific papers only
  python paper5_series_master_launch.py --papers 5A 5C --mode sequential

  # Dry run (no execution)
  python paper5_series_master_launch.py --dry-run

  # Parallel execution (when implemented)
  python paper5_series_master_launch.py --mode parallel --max-concurrent 2
        """
    )

    parser.add_argument("--mode", choices=["sequential", "parallel"], default="sequential",
                        help="Execution mode (default: sequential)")
    parser.add_argument("--papers", nargs="+", choices=["5A", "5B", "5C", "5E", "5F"],
                        help="Specific papers to execute (default: all non-skipped)")
    parser.add_argument("--max-concurrent", type=int, default=1,
                        help="Maximum concurrent processes in parallel mode (default: 1)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Dry run - show what would be executed without running")

    args = parser.parse_args()

    orchestrator = Paper5SeriesOrchestrator(
        mode=args.mode,
        max_concurrent=args.max_concurrent,
        papers=args.papers,
        dry_run=args.dry_run
    )

    orchestrator.execute()


if __name__ == "__main__":
    main()
