#!/usr/bin/env python3
"""
Dynamic Experiment Coordinator
Autonomous pipeline execution for dynamically generated simulations.

Replaces the legacy C186 Experiment Coordinator with a dynamic architecture
that takes instructions from the Evolution Orchestrator.
"""

import json
import subprocess
import time
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import os

@dataclass
class ExperimentStatus:
    """Track status of individual experiment"""
    name: str
    script_path: Path
    results_path: Path
    analysis_script: Optional[Path]
    status: str  # 'pending', 'running', 'completed', 'failed'
    pid: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    runtime_seconds: Optional[float] = None

class DynamicExperimentCoordinator:
    """
    Coordinates dynamic experiment pipelines for evolutionary runs.
    """

    def __init__(self, workspace_root: Path = None):
        if workspace_root is None:
            workspace_root = Path(os.getcwd())
            
        self.workspace_root = workspace_root
        self.experiments_dir = workspace_root / 'experiments' / 'evolution'
        self.results_dir = workspace_root / 'data' / 'results'
        
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.pipeline: List[ExperimentStatus] = []

    def add_experiment(self, name: str, script_name: str, results_name: str) -> ExperimentStatus:
        exp = ExperimentStatus(
            name=name,
            script_path=self.experiments_dir / script_name,
            results_path=self.results_dir / results_name,
            analysis_script=None,
            status='pending'
        )
        self.pipeline.append(exp)
        return exp

    def launch_experiment(self, experiment: ExperimentStatus) -> bool:
        if not experiment.script_path.exists():
            print(f"  ❌ Script not found: {experiment.script_path}")
            return False

        try:
            log_file = self.experiments_dir / f"{experiment.script_path.stem}_output.log"
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    [sys.executable, '-u', str(experiment.script_path)],
                    cwd=self.experiments_dir,
                    stdout=log,
                    stderr=subprocess.STDOUT
                )

            experiment.pid = process.pid
            experiment.start_time = datetime.now()
            experiment.status = 'running'
            return True
        except Exception as e:
            print(f"  ❌ Launch error: {e}")
            return False

    def wait_for_completion(self, experiment: ExperimentStatus, timeout: int = 300) -> str:
        """Blocks until the experiment completes or times out."""
        if experiment.status != 'running':
            return experiment.status
            
        start_time = time.time()
        while True:
            # Check if process is still running
            try:
                # os.kill(pid, 0) checks if process exists without sending signal
                os.kill(experiment.pid, 0)
                is_running = True
            except OSError:
                is_running = False
                
            if not is_running:
                # Process finished
                experiment.end_time = datetime.now()
                experiment.runtime_seconds = (experiment.end_time - experiment.start_time).total_seconds()
                if experiment.results_path.exists():
                    experiment.status = 'completed'
                else:
                    experiment.status = 'failed'
                return experiment.status
                
            if time.time() - start_time > timeout:
                experiment.status = 'failed'
                try:
                    import signal
                    os.kill(experiment.pid, signal.SIGKILL)
                except OSError:
                    pass
                return 'failed'
                
            time.sleep(1)
