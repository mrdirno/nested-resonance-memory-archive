#!/usr/bin/env python3
"""
Fractal Swarm Performance Profiler

Profiles FractalSwarm composition-decomposition cycles to identify
performance bottlenecks and measure scaling characteristics.

Measures:
- Agent spawning performance
- Evolution cycle efficiency
- Composition detection speed
- Decomposition/burst overhead
- Memory management costs
- Database persistence costs

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import argparse
import cProfile
import pstats
import time
import tempfile
from pathlib import Path
from typing import Dict, List, Any
from io import StringIO
import json

# Add paths for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "fractal"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from fractal.fractal_swarm import FractalSwarm
from core.reality_interface import RealityInterface


class FractalSwarmProfiler:
    """
    Performance profiler for FractalSwarm operations.

    Profiles key operations and generates performance reports
    for optimization and scaling analysis.
    """

    def __init__(self, workspace_path: str = None):
        """
        Initialize profiler.

        Args:
            workspace_path: Path for temp workspace (default: temp dir)
        """
        if workspace_path is None:
            self.workspace_path = Path(tempfile.mkdtemp(prefix="fractal_profile_"))
        else:
            self.workspace_path = Path(workspace_path)
            self.workspace_path.mkdir(exist_ok=True)

        self.results = {}

    def profile_agent_spawning(
        self,
        num_agents: int = 100
    ) -> Dict[str, Any]:
        """
        Profile agent spawning performance.

        Args:
            num_agents: Number of agents to spawn

        Returns:
            Dict with timing and stats
        """
        print(f"Profiling agent spawning ({num_agents} agents)...")

        # Create swarm
        swarm = FractalSwarm(
            workspace_path=str(self.workspace_path / "spawn_test"),
            max_agents=num_agents * 2,
            clear_on_init=True
        )

        reality = RealityInterface()

        # Profile spawning
        profiler = cProfile.Profile()
        start_time = time.time()

        profiler.enable()
        for i in range(num_agents):
            metrics = reality.get_system_metrics()
            swarm.spawn_agent(metrics)
        profiler.disable()

        elapsed = time.time() - start_time

        # Get stats
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions

        return {
            'operation': 'agent_spawning',
            'num_agents': num_agents,
            'total_time': elapsed,
            'avg_time_per_agent': elapsed / num_agents,
            'agents_per_second': num_agents / elapsed if elapsed > 0 else 0,
            'profile_output': stream.getvalue()
        }

    def profile_evolution_cycles(
        self,
        num_agents: int = 50,
        num_cycles: int = 100
    ) -> Dict[str, Any]:
        """
        Profile evolution cycle performance.

        Args:
            num_agents: Number of agents in swarm
            num_cycles: Number of evolution cycles

        Returns:
            Dict with timing and stats
        """
        print(f"Profiling evolution cycles ({num_cycles} cycles, {num_agents} agents)...")

        # Create and populate swarm
        swarm = FractalSwarm(
            workspace_path=str(self.workspace_path / "evolution_test"),
            max_agents=num_agents * 2,
            clear_on_init=True
        )

        reality = RealityInterface()
        for i in range(num_agents):
            metrics = reality.get_system_metrics()
            swarm.spawn_agent(metrics)

        # Profile evolution cycles
        profiler = cProfile.Profile()
        start_time = time.time()

        profiler.enable()
        for i in range(num_cycles):
            swarm.evolve_cycle(delta_time=1.0)
        profiler.disable()

        elapsed = time.time() - start_time

        # Get stats
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)

        return {
            'operation': 'evolution_cycles',
            'num_agents': num_agents,
            'num_cycles': num_cycles,
            'total_time': elapsed,
            'avg_time_per_cycle': elapsed / num_cycles,
            'cycles_per_second': num_cycles / elapsed if elapsed > 0 else 0,
            'profile_output': stream.getvalue()
        }

    def profile_composition_detection(
        self,
        num_agents: int = 100,
        num_iterations: int = 50
    ) -> Dict[str, Any]:
        """
        Profile composition (cluster detection) performance.

        Args:
            num_agents: Number of agents
            num_iterations: Number of detection iterations

        Returns:
            Dict with timing and stats
        """
        print(f"Profiling composition detection ({num_iterations} iterations, {num_agents} agents)...")

        # Create and populate swarm
        swarm = FractalSwarm(
            workspace_path=str(self.workspace_path / "composition_test"),
            max_agents=num_agents * 2,
            clear_on_init=True
        )

        reality = RealityInterface()
        agents = []
        for i in range(num_agents):
            metrics = reality.get_system_metrics()
            agent = swarm.spawn_agent(metrics)
            if agent:
                agents.append(agent)

        # Profile cluster detection
        profiler = cProfile.Profile()
        start_time = time.time()

        profiler.enable()
        for i in range(num_iterations):
            swarm.composition.detect_clusters(agents)
        profiler.disable()

        elapsed = time.time() - start_time

        # Get stats
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)

        return {
            'operation': 'composition_detection',
            'num_agents': num_agents,
            'num_iterations': num_iterations,
            'total_time': elapsed,
            'avg_time_per_iteration': elapsed / num_iterations,
            'iterations_per_second': num_iterations / elapsed if elapsed > 0 else 0,
            'profile_output': stream.getvalue()
        }

    def profile_memory_management(
        self,
        memory_size: int = 1000,
        num_redistributions: int = 100
    ) -> Dict[str, Any]:
        """
        Profile memory bounding and redistribution performance.

        Args:
            memory_size: Size of global memory
            num_redistributions: Number of redistribution cycles

        Returns:
            Dict with timing and stats
        """
        print(f"Profiling memory management ({num_redistributions} cycles, {memory_size} states)...")

        # Create swarm with memory
        swarm = FractalSwarm(
            workspace_path=str(self.workspace_path / "memory_test"),
            max_memory_size=memory_size,
            clear_on_init=True
        )

        # Fill memory
        from bridge.transcendental_bridge import TranscendentalBridge
        bridge = TranscendentalBridge()

        for i in range(memory_size):
            state = bridge.reality_to_phase({'cpu_percent': float(i % 100)})
            swarm.global_memory.append(state)

        # Spawn some agents
        reality = RealityInterface()
        for i in range(10):
            metrics = reality.get_system_metrics()
            swarm.spawn_agent(metrics)

        # Profile memory operations
        profiler = cProfile.Profile()
        start_time = time.time()

        profiler.enable()
        for i in range(num_redistributions):
            # Simulate memory bounding + redistribution (from evolve_cycle)
            swarm.global_memory.sort(key=lambda s: s.magnitude, reverse=True)
            swarm.global_memory = swarm.global_memory[:swarm.max_memory_size]

            # Redistribution
            active_agents = [a for a in swarm.agents.values() if a.is_active]
            if swarm.global_memory and active_agents:
                redistribution_size = max(10, swarm.max_memory_size // 10)
                for j, memory_state in enumerate(swarm.global_memory[:redistribution_size]):
                    if active_agents:
                        recipient = active_agents[j % len(active_agents)]
                        recipient.absorb_memory([memory_state])
        profiler.disable()

        elapsed = time.time() - start_time

        # Get stats
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.strip_dirs()
        stats.sort_stats('cumulative')
        stats.print_stats(20)

        return {
            'operation': 'memory_management',
            'memory_size': memory_size,
            'num_redistributions': num_redistributions,
            'total_time': elapsed,
            'avg_time_per_redistribution': elapsed / num_redistributions,
            'redistributions_per_second': num_redistributions / elapsed if elapsed > 0 else 0,
            'profile_output': stream.getvalue()
        }

    def run_full_profile(self) -> Dict[str, Any]:
        """
        Run full profiling suite.

        Returns:
            Dict with all profiling results
        """
        print("=" * 80)
        print("FRACTAL SWARM PERFORMANCE PROFILER")
        print("=" * 80)
        print()

        results = {
            'timestamp': time.time(),
            'profiles': []
        }

        # Profile agent spawning
        results['profiles'].append(
            self.profile_agent_spawning(num_agents=100)
        )
        print()

        # Profile evolution cycles
        results['profiles'].append(
            self.profile_evolution_cycles(num_agents=50, num_cycles=100)
        )
        print()

        # Profile composition detection
        results['profiles'].append(
            self.profile_composition_detection(num_agents=100, num_iterations=50)
        )
        print()

        # Profile memory management
        results['profiles'].append(
            self.profile_memory_management(memory_size=1000, num_redistributions=100)
        )
        print()

        return results

    def generate_report(self, results: Dict[str, Any]) -> str:
        """
        Generate human-readable profiling report.

        Args:
            results: Profiling results from run_full_profile()

        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 80)
        lines.append("FRACTAL SWARM PERFORMANCE PROFILE REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTimestamp: {time.ctime(results['timestamp'])}")
        lines.append("")

        for profile in results['profiles']:
            lines.append("-" * 80)
            lines.append(f"OPERATION: {profile['operation'].upper()}")
            lines.append("-" * 80)

            if profile['operation'] == 'agent_spawning':
                lines.append(f"  Agents spawned: {profile['num_agents']}")
                lines.append(f"  Total time: {profile['total_time']:.3f}s")
                lines.append(f"  Avg time per agent: {profile['avg_time_per_agent']*1000:.2f}ms")
                lines.append(f"  Throughput: {profile['agents_per_second']:.1f} agents/sec")

            elif profile['operation'] == 'evolution_cycles':
                lines.append(f"  Agents: {profile['num_agents']}")
                lines.append(f"  Cycles: {profile['num_cycles']}")
                lines.append(f"  Total time: {profile['total_time']:.3f}s")
                lines.append(f"  Avg time per cycle: {profile['avg_time_per_cycle']*1000:.2f}ms")
                lines.append(f"  Throughput: {profile['cycles_per_second']:.1f} cycles/sec")

            elif profile['operation'] == 'composition_detection':
                lines.append(f"  Agents: {profile['num_agents']}")
                lines.append(f"  Iterations: {profile['num_iterations']}")
                lines.append(f"  Total time: {profile['total_time']:.3f}s")
                lines.append(f"  Avg time per iteration: {profile['avg_time_per_iteration']*1000:.2f}ms")
                lines.append(f"  Throughput: {profile['iterations_per_second']:.1f} iterations/sec")

            elif profile['operation'] == 'memory_management':
                lines.append(f"  Memory size: {profile['memory_size']} states")
                lines.append(f"  Redistributions: {profile['num_redistributions']}")
                lines.append(f"  Total time: {profile['total_time']:.3f}s")
                lines.append(f"  Avg time per redistribution: {profile['avg_time_per_redistribution']*1000:.2f}ms")
                lines.append(f"  Throughput: {profile['redistributions_per_second']:.1f} redistributions/sec")

            lines.append("")
            lines.append("Top functions by cumulative time:")
            lines.append(profile['profile_output'][:1000])  # First 1000 chars of profile
            lines.append("")

        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Profile FractalSwarm performance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full profiling suite
  python profile_fractal_swarm.py

  # Save results as JSON
  python profile_fractal_swarm.py --json profile_results.json

  # Use custom workspace
  python profile_fractal_swarm.py --workspace /tmp/profile_workspace
        """
    )

    parser.add_argument('--workspace', type=str, default=None,
                       help='Workspace path for temp files')
    parser.add_argument('--json', type=str, default=None,
                       help='Save results as JSON to file')

    args = parser.parse_args()

    # Create profiler
    profiler = FractalSwarmProfiler(workspace_path=args.workspace)

    # Run profiling
    results = profiler.run_full_profile()

    # Generate and print report
    report = profiler.generate_report(results)
    print(report)

    # Save JSON if requested
    if args.json:
        with open(args.json, 'w') as f:
            # Remove profile_output from JSON (too verbose)
            json_results = {
                'timestamp': results['timestamp'],
                'profiles': [
                    {k: v for k, v in p.items() if k != 'profile_output'}
                    for p in results['profiles']
                ]
            }
            json.dump(json_results, f, indent=2)
        print(f"\nResults saved to: {args.json}")


if __name__ == '__main__':
    main()
