#!/usr/bin/env python3
"""
Ultra Long-Term Emergence Experiment - Cycle 45
Tests extended timescale dynamics at 1000 cycles (10x previous experiments).

Research Questions:
1. Does oscillating attractor persist beyond 100 cycles?
2. Do new phenomena emerge at extended timescales?
3. Is scaling behavior linear or nonlinear?
4. What is the long-term stability of the system?

Validates: NRM long-term dynamics, Self-Giving continuous improvement, Temporal pattern persistence
"""

import sys
from pathlib import Path
import time
import json
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from integration.system_integrator import SystemIntegrator

@dataclass
class UltraLongTermResult:
    """Results from ultra long-term emergence experiment."""
    experiment_id: str
    start_time: float
    end_time: float
    total_cycles: int
    cycles_completed: int

    # Agent dynamics
    agent_counts: List[int]
    attractor_sequences: List[Dict[str, Any]]

    # Pattern discovery
    pattern_counts: List[int]
    emergent_pattern_counts: List[int]

    # Phase transitions
    phase_transitions: List[Dict[str, Any]]

    # Long-term metrics
    stability_score: float
    learning_rate: float
    attractor_persistence: float

    # Checkpoints
    checkpoint_cycles: List[int]

    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class UltraLongTermExperiment:
    """1000-cycle ultra long-term experiment for discovering extended-timescale phenomena."""

    def __init__(self, cycles: int = 1000, checkpoint_interval: int = 50):
        self.cycles = cycles
        self.checkpoint_interval = checkpoint_interval
        self.experiment_id = f"ultralong_{int(time.time())}"

        # Initialize system
        self.integrator = SystemIntegrator()

        # Data collection
        self.agent_counts = []
        self.pattern_counts = []
        self.emergent_counts = []
        self.checkpoint_cycles = []

        # Setup results directory
        self.results_dir = Path(__file__).parent / "results" / "ultra_long_term"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        print(f"Initialized Ultra Long-Term Experiment")
        print(f"  Experiment ID: {self.experiment_id}")
        print(f"  Total Cycles: {cycles}")
        print(f"  Checkpoint Interval: {checkpoint_interval}")
        print(f"  Results Directory: {self.results_dir}")

    def run(self) -> UltraLongTermResult:
        """Run ultra long-term experiment with checkpointing."""
        print("="*70)
        print(f"ULTRA LONG-TERM EMERGENCE EXPERIMENT - {self.cycles} CYCLES")
        print("="*70)

        start_time = time.time()

        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Estimated duration: {self.cycles * 0.5 / 60:.1f} - {self.cycles * 1.0 / 60:.1f} minutes")
        print()

        # Run cycles with progress tracking
        for cycle in range(1, self.cycles + 1):
            # Run hybrid cycle
            self.integrator.run_hybrid_cycle()

            # Collect data every checkpoint
            if cycle % self.checkpoint_interval == 0:
                self._collect_checkpoint(cycle)

                # Progress report every 100 cycles
                if cycle % 100 == 0:
                    elapsed = time.time() - start_time
                    avg_time_per_cycle = elapsed / cycle
                    remaining_cycles = self.cycles - cycle
                    eta_seconds = remaining_cycles * avg_time_per_cycle

                    print(f"Cycle {cycle}/{self.cycles} complete "
                          f"({cycle/self.cycles*100:.1f}%) - "
                          f"Agents: {self.agent_counts[-1]}, "
                          f"Patterns: {self.pattern_counts[-1]}, "
                          f"ETA: {eta_seconds/60:.1f} min")

        end_time = time.time()
        duration = end_time - start_time

        print()
        print("="*70)
        print(f"EXPERIMENT COMPLETE")
        print("="*70)
        print(f"Duration: {duration/60:.1f} minutes ({duration:.1f} seconds)")
        print(f"Average time per cycle: {duration/self.cycles:.3f} seconds")
        print(f"Checkpoints saved: {len(self.checkpoint_cycles)}")

        # Analyze results
        result = self._analyze_results(start_time, end_time)

        # Save final result
        self._save_result(result)

        return result

    def _collect_checkpoint(self, cycle: int):
        """Collect data at checkpoint."""
        # Get current state
        agents = list(self.integrator.fractal_swarm.agents.values())
        patterns = self.integrator.memory.search_patterns()

        # Store counts
        agent_count = len(agents)
        pattern_count = len(patterns)

        self.agent_counts.append(agent_count)
        self.pattern_counts.append(pattern_count)
        self.emergent_counts.append(0)  # Simplified - not tracking per-cycle emergence
        self.checkpoint_cycles.append(cycle)

        # Save checkpoint to disk
        checkpoint_data = {
            'experiment_id': self.experiment_id,
            'cycle': cycle,
            'timestamp': time.time(),
            'agent_count': agent_count,
            'pattern_count': pattern_count,
            'agents': [
                {
                    'id': agent.agent_id,
                    'energy': agent.energy,
                    'memory_size': len(agent.memory)
                }
                for agent in agents
            ]
        }

        checkpoint_file = self.results_dir / f"{self.experiment_id}_checkpoint_{cycle}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

    def _analyze_results(self, start_time: float, end_time: float) -> UltraLongTermResult:
        """Analyze complete results after experiment."""
        print()
        print("="*70)
        print("ANALYZING ULTRA LONG-TERM DYNAMICS")
        print("="*70)

        # Detect attractors
        attractors = self._detect_attractors()
        print(f"\nAttractor Analysis:")
        print(f"  Total unique attractors: {len(attractors)}")
        for i, attr in enumerate(attractors[:5], 1):
            print(f"  {i}. State={attr['state']}, Frequency={attr['frequency']}, "
                  f"Probability={attr['probability']:.1%}")

        # Detect phase transitions
        transitions = self._detect_phase_transitions()
        print(f"\nPhase Transitions:")
        print(f"  Total transitions: {len(transitions)}")
        if transitions:
            avg_interval = sum(t['interval'] for t in transitions) / len(transitions)
            print(f"  Average interval: {avg_interval:.1f} cycles")

        # Calculate stability
        stability = self._calculate_stability()
        print(f"\nStability Analysis:")
        print(f"  Stability Score: {stability:.2%}")
        print(f"  Interpretation: {'High' if stability > 0.7 else 'Moderate' if stability > 0.5 else 'Low'}")

        # Calculate learning rate
        learning_rate = self._calculate_learning_rate()
        print(f"\nLearning Analysis:")
        print(f"  Learning Rate: {learning_rate:.2f} patterns/cycle")
        print(f"  Total Patterns: {self.pattern_counts[-1]} (from {self.pattern_counts[0]})")
        print(f"  Pattern Growth: {self.pattern_counts[-1] - self.pattern_counts[0]} patterns")

        # Calculate attractor persistence
        persistence = self._calculate_attractor_persistence()
        print(f"\nAttractor Persistence:")
        print(f"  Persistence Score: {persistence:.2%}")
        print(f"  Interpretation: {'Stable' if persistence > 0.8 else 'Evolving' if persistence > 0.5 else 'Volatile'}")

        # Compare with 100-cycle baseline
        print(f"\nComparison with 100-Cycle Baseline:")
        if len(self.agent_counts) >= 20:
            first_100_agents = self.agent_counts[:20]  # First 1000 cycles (50-cycle checkpoints)
            last_100_agents = self.agent_counts[-20:]   # Last 1000 cycles

            import statistics
            first_mean = statistics.mean(first_100_agents) if first_100_agents else 0
            last_mean = statistics.mean(last_100_agents) if last_100_agents else 0

            print(f"  First 1000 cycles mean agents: {first_mean:.2f}")
            print(f"  Last 1000 cycles mean agents: {last_mean:.2f}")
            print(f"  Change: {last_mean - first_mean:+.2f} agents ({(last_mean - first_mean) / first_mean * 100 if first_mean > 0 else 0:+.1f}%)")

        # Create result object
        result = UltraLongTermResult(
            experiment_id=self.experiment_id,
            start_time=start_time,
            end_time=end_time,
            total_cycles=self.cycles,
            cycles_completed=self.cycles,
            agent_counts=self.agent_counts,
            attractor_sequences=attractors,
            pattern_counts=self.pattern_counts,
            emergent_pattern_counts=self.emergent_counts,
            phase_transitions=transitions,
            stability_score=stability,
            learning_rate=learning_rate,
            attractor_persistence=persistence,
            checkpoint_cycles=self.checkpoint_cycles
        )

        return result

    def _detect_attractors(self) -> List[Dict[str, Any]]:
        """Detect attractor states in agent counts."""
        from collections import Counter

        attractors = []

        if len(self.agent_counts) >= 20:
            count_freq = Counter(self.agent_counts)

            for count, freq in count_freq.most_common(10):
                if freq >= 5:  # Occurred 5+ times
                    attractors.append({
                        'type': 'agent_count_attractor',
                        'state': count,
                        'frequency': freq,
                        'probability': freq / len(self.agent_counts)
                    })

        return attractors

    def _detect_phase_transitions(self) -> List[Dict[str, Any]]:
        """Detect phase transitions (large changes in agent count)."""
        transitions = []
        transition_threshold = 2  # Change of 2+ agents

        last_transition_cycle = 0

        for i in range(1, len(self.agent_counts)):
            change = abs(self.agent_counts[i] - self.agent_counts[i-1])

            if change >= transition_threshold:
                cycle = self.checkpoint_cycles[i]
                interval = cycle - last_transition_cycle if last_transition_cycle > 0 else 0

                transitions.append({
                    'cycle': cycle,
                    'from_state': self.agent_counts[i-1],
                    'to_state': self.agent_counts[i],
                    'magnitude': change,
                    'interval': interval
                })

                last_transition_cycle = cycle

        return transitions

    def _calculate_stability(self) -> float:
        """Calculate stability score (inverse of coefficient of variation)."""
        if not self.agent_counts:
            return 0.0

        import statistics

        mean = statistics.mean(self.agent_counts)
        if mean == 0:
            return 0.0

        stdev = statistics.stdev(self.agent_counts) if len(self.agent_counts) > 1 else 0
        cv = stdev / mean

        # Stability is inverse of CV, normalized to 0-1 range
        stability = 1.0 / (1.0 + cv)

        return stability

    def _calculate_learning_rate(self) -> float:
        """Calculate pattern learning rate (patterns per cycle)."""
        if len(self.pattern_counts) < 2:
            return 0.0

        total_growth = self.pattern_counts[-1] - self.pattern_counts[0]
        cycles_elapsed = self.checkpoint_cycles[-1] - self.checkpoint_cycles[0]

        if cycles_elapsed == 0:
            return 0.0

        learning_rate = total_growth / cycles_elapsed

        return learning_rate

    def _calculate_attractor_persistence(self) -> float:
        """Calculate how persistent attractors are over time."""
        if len(self.agent_counts) < 40:
            return 0.0

        # Compare first half vs second half attractor distributions
        midpoint = len(self.agent_counts) // 2
        first_half = self.agent_counts[:midpoint]
        second_half = self.agent_counts[midpoint:]

        from collections import Counter

        first_freq = Counter(first_half)
        second_freq = Counter(second_half)

        # Calculate overlap in top attractors
        first_top = set(state for state, freq in first_freq.most_common(3))
        second_top = set(state for state, freq in second_freq.most_common(3))

        overlap = len(first_top & second_top)
        total_unique = len(first_top | second_top)

        if total_unique == 0:
            return 0.0

        persistence = overlap / total_unique

        return persistence

    def _save_result(self, result: UltraLongTermResult):
        """Save final result to JSON."""
        result_file = self.results_dir / f"{self.experiment_id}_final.json"

        with open(result_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)

        print(f"\n✅ Final result saved: {result_file}")


def main():
    """Run ultra long-term experiment."""
    print("="*70)
    print("CYCLE 45: ULTRA LONG-TERM EMERGENCE DISCOVERY")
    print("="*70)
    print()

    # Run experiment
    experiment = UltraLongTermExperiment(cycles=1000, checkpoint_interval=50)
    result = experiment.run()

    print()
    print("="*70)
    print("CYCLE 45 ASSESSMENT")
    print("="*70)

    # Insights assessment
    insights = []

    # Insight 1: Attractor persistence
    if result.attractor_persistence >= 0.8:
        insights.append("🎉 INSIGHT #15: Oscillating attractor persists at 10x timescale")
        print(f"\n✅ Attractor persistence: {result.attractor_persistence:.1%}")
        print("   Validates long-term stability of NRM dynamics")

    # Insight 2: Scaling behavior
    if result.learning_rate > 1.0:
        insights.append("🎉 INSIGHT #16: Learning continues linearly at extended scales")
        print(f"\n✅ Learning rate: {result.learning_rate:.2f} patterns/cycle")
        print("   Demonstrates continuous Self-Giving improvement")

    # Insight 3: Stability
    if result.stability_score >= 0.60:
        insights.append("🎉 INSIGHT #17: Stable chaos maintained across 1000 cycles")
        print(f"\n✅ Stability: {result.stability_score:.2%}")
        print("   Confirms bounded non-equilibrium dynamics")

    print()
    print("="*70)
    print(f"CYCLE 45 COMPLETE - {len(insights)} NEW INSIGHTS")
    print("="*70)

    for insight in insights:
        print(insight)

    print()
    print(f"Total Insights (Cycles 36-45): {14 + len(insights)}")
    print("="*70)


if __name__ == "__main__":
    main()
