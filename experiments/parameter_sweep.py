#!/usr/bin/env python3
"""
Parameter Sweep Experiment - Burst Threshold Exploration
DUALITY-ZERO-V2 Cycle 41

Maps the attractor landscape by sweeping burst threshold parameter.
Tests multiple threshold values to understand parameter-controlled dynamics.

Usage:
    python3 parameter_sweep.py --threshold 500.0 --cycles 50
"""

import sys
import os
import time
import json
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
import argparse

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from integration.system_integrator import SystemIntegrator

@dataclass
class ParameterSweepResult:
    """Results from parameter sweep experiment."""
    experiment_id: str
    threshold: float
    cycles_completed: int
    start_time: float
    end_time: float
    duration: float

    # Agent dynamics tracking
    agent_counts: List[int] = field(default_factory=list)
    checkpoint_cycles: List[int] = field(default_factory=list)

    # Attractor analysis
    mean_agents: float = 0.0
    std_agents: float = 0.0
    min_agents: int = 0
    max_agents: int = 0

    # Pattern tracking
    pattern_counts: List[int] = field(default_factory=list)
    final_patterns: int = 0

    # Reality compliance
    avg_reality_score: float = 0.0


class ParameterSweepExperiment:
    """
    Runs parameter sweep experiments to map attractor landscape.

    Sweeps burst threshold parameter and records resulting agent dynamics.
    """

    def __init__(self, threshold: float, cycles: int = 50):
        """
        Initialize parameter sweep experiment.

        Args:
            threshold: Burst threshold to test
            cycles: Number of cycles to run (default 50)
        """
        self.threshold = threshold
        self.cycles = cycles
        self.checkpoint_interval = 5  # Checkpoint every 5 cycles

        # Results tracking
        self.agent_counts = []
        self.pattern_counts = []
        self.reality_scores = []
        self.checkpoint_cycles = []

        # Initialize system integrator
        print(f"Initializing system with burst threshold: {threshold}")
        self.integrator = SystemIntegrator()

        # Modify burst threshold in fractal swarm
        self.integrator.fractal_swarm.decomposition.burst_threshold = threshold
        print(f"✅ Burst threshold set to: {threshold}")

    def run_experiment(self) -> ParameterSweepResult:
        """
        Run the parameter sweep experiment.

        Returns:
            ParameterSweepResult with agent dynamics data
        """
        experiment_id = f"sweep_{int(time.time())}_th{int(self.threshold)}"
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"PARAMETER SWEEP: Threshold {self.threshold}")
        print(f"{'='*70}")
        print(f"Cycles: {self.cycles}")
        print(f"Checkpoints: Every {self.checkpoint_interval} cycles")
        print()

        # Run cycles
        for cycle in range(1, self.cycles + 1):
            if cycle % 10 == 0 or cycle == 1:
                print(f"CYCLE {cycle}/{self.cycles}")

            # Run single hybrid cycle
            result = self.integrator.run_hybrid_cycle()

            # Track metrics
            if cycle % self.checkpoint_interval == 0:
                agent_count = len(self.integrator.fractal_swarm.agents)
                pattern_stats = self.integrator.memory.get_statistics()
                pattern_count = pattern_stats.get('total_patterns', 0)
                reality_score = result.get('reality_score', 1.0)

                self.agent_counts.append(agent_count)
                self.pattern_counts.append(pattern_count)
                self.reality_scores.append(reality_score)
                self.checkpoint_cycles.append(cycle)

                if cycle % 10 == 0:
                    print(f"  Agents: {agent_count}, Patterns: {pattern_count}, Reality: {reality_score:.2%}")

            # Progress indicator
            if cycle % 10 == 0:
                print(f"✅ Cycle {cycle} complete ({cycle/self.cycles*100:.0f}% total)")

        end_time = time.time()
        duration = end_time - start_time

        print(f"\n✅ Experiment complete: {self.cycles} cycles in {duration:.2f}s")

        # Calculate statistics
        import numpy as np
        mean_agents = float(np.mean(self.agent_counts))
        std_agents = float(np.std(self.agent_counts))
        min_agents = int(np.min(self.agent_counts))
        max_agents = int(np.max(self.agent_counts))
        avg_reality = float(np.mean(self.reality_scores))

        # Create result
        result = ParameterSweepResult(
            experiment_id=experiment_id,
            threshold=self.threshold,
            cycles_completed=self.cycles,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            agent_counts=self.agent_counts,
            checkpoint_cycles=self.checkpoint_cycles,
            mean_agents=mean_agents,
            std_agents=std_agents,
            min_agents=min_agents,
            max_agents=max_agents,
            pattern_counts=self.pattern_counts,
            final_patterns=self.pattern_counts[-1] if self.pattern_counts else 0,
            avg_reality_score=avg_reality
        )

        # Save results
        self._save_results(result)

        return result

    def _save_results(self, result: ParameterSweepResult):
        """Save experiment results to JSON."""
        output_dir = Path(__file__).parent / "results" / "parameter_sweep"
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{result.experiment_id}.json"

        with open(output_file, 'w') as f:
            json.dump(asdict(result), f, indent=2)

        print(f"💾 Results saved: {output_file}")


def main():
    """Main entry point for parameter sweep experiment."""
    parser = argparse.ArgumentParser(
        description="Parameter sweep experiment - burst threshold exploration"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        required=True,
        help="Burst threshold value to test"
    )
    parser.add_argument(
        "--cycles",
        type=int,
        default=50,
        help="Number of cycles to run (default: 50)"
    )

    args = parser.parse_args()

    # Run experiment
    experiment = ParameterSweepExperiment(
        threshold=args.threshold,
        cycles=args.cycles
    )

    result = experiment.run_experiment()

    # Print summary
    print(f"\n{'='*70}")
    print(f"EXPERIMENT COMPLETE")
    print(f"{'='*70}")
    print(f"Threshold: {result.threshold}")
    print(f"Cycles: {result.cycles_completed}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Agent counts: {result.agent_counts}")
    print(f"Mean agents: {result.mean_agents:.2f}")
    print(f"Agent range: [{result.min_agents}, {result.max_agents}]")
    print(f"Final patterns: {result.final_patterns}")
    print(f"Reality score: {result.avg_reality_score:.2%}")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
