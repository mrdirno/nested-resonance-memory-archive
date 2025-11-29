#!/usr/bin/env python3
"""
BCP DAEMON - Production Budget-Constrained Perception Monitor
==============================================================
Gate 205: Real-World Application

A production-ready daemon that continuously monitors system resources
using BCP theory and logs state changes to SQLite.

Features:
- Continuous monitoring with configurable interval
- SQLite database for historical data
- Phase transition detection and alerting
- Triage recommendations based on current state
- Graceful shutdown handling

Usage:
    python bcp_daemon.py --interval 5 --db /path/to/bcp.db

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
License: GPL-3.0
"""

import psutil
import sqlite3
import time
import signal
import argparse
import json
import os
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass
class BCPConfig:
    abundance_threshold: float = 0.7
    scarcity_threshold: float = 0.5
    crisis_threshold: float = 0.3
    lambda_scale: float = 50.0
    gamma: float = 0.1
    tasks: Dict[str, Dict] = None
    
    def __post_init__(self):
        if self.tasks is None:
            self.tasks = {
                'cpu_percent': {'gain': 0.9, 'cost': 0.1},
                'memory_percent': {'gain': 0.85, 'cost': 0.05},
                'disk_usage': {'gain': 0.7, 'cost': 0.2},
                'network_io': {'gain': 0.5, 'cost': 0.3},
                'disk_io': {'gain': 0.4, 'cost': 0.25},
                'swap_usage': {'gain': 0.3, 'cost': 0.1},
                'process_count': {'gain': 0.2, 'cost': 0.15},
            }


@dataclass
class BCPState:
    timestamp: str
    phase: str
    budget: float
    lambda_: float
    complexity: float
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    swap_percent: float
    process_count: int
    monitored_tasks: str
    triaged_tasks: str
    alert: Optional[str]


class BCPDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bcp_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                phase TEXT NOT NULL,
                budget REAL NOT NULL,
                lambda_ REAL NOT NULL,
                complexity REAL NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_percent REAL,
                swap_percent REAL,
                process_count INTEGER,
                monitored_tasks TEXT,
                triaged_tasks TEXT,
                alert TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS phase_transitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                from_phase TEXT NOT NULL,
                to_phase TEXT NOT NULL,
                budget REAL NOT NULL
            )
        ''')
        self.conn.commit()
    
    def log_state(self, state: BCPState):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO bcp_states 
            (timestamp, phase, budget, lambda_, complexity, cpu_percent, 
             memory_percent, disk_percent, swap_percent, process_count,
             monitored_tasks, triaged_tasks, alert)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            state.timestamp, state.phase, state.budget, state.lambda_,
            state.complexity, state.cpu_percent, state.memory_percent,
            state.disk_percent, state.swap_percent, state.process_count,
            state.monitored_tasks, state.triaged_tasks, state.alert
        ))
        self.conn.commit()
    
    def log_transition(self, timestamp: str, from_phase: str, to_phase: str, budget: float):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO phase_transitions (timestamp, from_phase, to_phase, budget)
            VALUES (?, ?, ?, ?)
        ''', (timestamp, from_phase, to_phase, budget))
        self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()


class BCPDaemon:
    def __init__(self, config: BCPConfig, db: BCPDatabase):
        self.config = config
        self.db = db
        self.running = False
        self.last_phase = None
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        print("\n[BCP] Shutdown signal received.")
        self.running = False
    
    def compute_budget(self) -> Tuple[float, Dict]:
        try:
            cpu = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory().percent
            disk = psutil.disk_usage('/').percent
            swap = psutil.swap_memory().percent
        except:
            cpu = memory = disk = swap = 50.0
        
        metrics = {'cpu_percent': cpu, 'memory_percent': memory,
                   'disk_percent': disk, 'swap_percent': swap}
        weights = {'cpu_percent': 0.35, 'memory_percent': 0.35,
                   'disk_percent': 0.2, 'swap_percent': 0.1}
        budget = sum((1 - metrics[k]/100) * weights[k] for k in weights)
        return budget, metrics
    
    def compute_lambda(self, budget: float) -> float:
        return self.config.lambda_scale / (1.0 + budget * 10)
    
    def compute_complexity(self) -> Tuple[float, int]:
        try:
            process_count = len(psutil.pids())
            normalized = min(1.0, process_count / 500)
        except:
            process_count = 250
            normalized = 0.5
        return normalized, process_count
    
    def determine_phase(self, budget: float) -> str:
        if budget >= self.config.abundance_threshold:
            return 'abundance'
        elif budget >= self.config.scarcity_threshold:
            return 'scarcity'
        elif budget >= self.config.crisis_threshold:
            return 'crisis'
        else:
            return 'collapse'
    
    def compute_triage(self, lambda_: float, complexity: float) -> Tuple[List[str], List[str]]:
        monitored, triaged = [], []
        for task, params in self.config.tasks.items():
            value = params['gain'] - lambda_ * params['cost'] - self.config.gamma * complexity
            (monitored if value > 0 else triaged).append(task)
        return monitored, triaged
    
    def sample(self) -> BCPState:
        budget, metrics = self.compute_budget()
        lambda_ = self.compute_lambda(budget)
        complexity, process_count = self.compute_complexity()
        phase = self.determine_phase(budget)
        monitored, triaged = self.compute_triage(lambda_, complexity)
        
        alert = None
        timestamp = datetime.now().isoformat()
        
        if self.last_phase and phase != self.last_phase:
            alert = f"PHASE TRANSITION: {self.last_phase} -> {phase}"
            self.db.log_transition(timestamp, self.last_phase, phase, budget)
            print(f"[BCP] {alert}")
        
        self.last_phase = phase
        
        return BCPState(
            timestamp=timestamp, phase=phase, budget=budget,
            lambda_=lambda_, complexity=complexity,
            cpu_percent=metrics['cpu_percent'],
            memory_percent=metrics['memory_percent'],
            disk_percent=metrics['disk_percent'],
            swap_percent=metrics['swap_percent'],
            process_count=process_count,
            monitored_tasks=json.dumps(monitored),
            triaged_tasks=json.dumps(triaged),
            alert=alert
        )
    
    def run(self, interval: float = 5.0, max_samples: int = None):
        self.running = True
        sample_count = 0
        
        print(f"[BCP] Daemon started. Interval: {interval}s")
        
        while self.running and (max_samples is None or sample_count < max_samples):
            state = self.sample()
            self.db.log_state(state)
            sample_count += 1
            
            phase_emoji = {'abundance': 'G', 'scarcity': 'Y', 'crisis': 'R', 'collapse': 'X'}
            print(f"[{state.timestamp[:19]}] [{phase_emoji.get(state.phase, '?')}] "
                  f"{state.phase:10s} | B={state.budget:.3f} | "
                  f"Monitored: {len(json.loads(state.monitored_tasks))}/7")
            
            if max_samples and sample_count >= max_samples:
                break
            time.sleep(interval)
        
        print(f"[BCP] Stopped. Samples: {sample_count}")
        self.db.close()
        return sample_count


def main():
    parser = argparse.ArgumentParser(description='BCP Daemon')
    parser.add_argument('--interval', type=float, default=5.0)
    parser.add_argument('--db', type=str, default='/Volumes/dual/DUALITY-ZERO-V2/data/bcp_monitor.db')
    parser.add_argument('--samples', type=int, default=None, help='Max samples (for testing)')
    args = parser.parse_args()
    
    print("=" * 50)
    print("BCP DAEMON - Gate 205: Real-World Application")
    print("=" * 50)
    
    config = BCPConfig()
    db = BCPDatabase(args.db)
    daemon = BCPDaemon(config, db)
    daemon.run(interval=args.interval, max_samples=args.samples)


if __name__ == "__main__":
    main()
