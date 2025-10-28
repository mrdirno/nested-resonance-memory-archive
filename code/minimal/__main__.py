"""Command line entry point for the minimal NRM package."""

from __future__ import annotations

import argparse
from pathlib import Path

from .reality import MinimalRealityGateway
from .simulation import MinimalSwarm


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the minimal NRM swarm")
    parser.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Optional workspace directory for storing reality artefacts.",
    )
    parser.add_argument("--cycles", type=int, default=3, help="Number of update cycles to execute.")
    parser.add_argument("--agents", type=int, default=3, help="Number of agents to spawn before running cycles.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    gateway = MinimalRealityGateway(workspace_path=args.workspace) if args.workspace else None
    swarm = MinimalSwarm(gateway=gateway)

    for _ in range(args.agents):
        swarm.spawn_agent()

    for _ in range(args.cycles):
        summary = swarm.run_cycle()
        print(f"Cycle {summary.cycle}: total magnitude={summary.total_magnitude:.3f}, clusters={summary.cluster_count}")
        for cluster in swarm.describe_clusters():
            print(f"  Cluster {cluster.member_ids} avg_similarity={cluster.average_similarity:.3f}")


if __name__ == "__main__":
    main()
