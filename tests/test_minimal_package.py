"""Validation for the lightweight minimal NRM package."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from bridge.transcendental_bridge import TranscendentalBridge

from minimal import (
    MinimalAgent,
    MinimalRealityGateway,
    MinimalSwarm,
    RealitySnapshot,
    find_resonant_clusters,
)


@pytest.fixture()
def temp_workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    return workspace


def test_capture_snapshot_produces_metrics(temp_workspace: Path) -> None:
    gateway = MinimalRealityGateway(workspace_path=temp_workspace)
    snapshot = gateway.capture_snapshot()
    assert isinstance(snapshot, RealitySnapshot)
    data = snapshot.as_dict()
    assert {"cpu_percent", "memory_percent", "disk_percent", "timestamp", "process_count"} <= data.keys()


def test_minimal_swarm_cycle_progression(temp_workspace: Path) -> None:
    bridge_path = temp_workspace / "bridge"
    bridge_path.mkdir(parents=True, exist_ok=True)
    bridge = TranscendentalBridge(workspace_path=str(bridge_path))

    snapshots: Iterator[RealitySnapshot] = iter(
        [
            RealitySnapshot(10.0, 20.0, 5.0, 0.0, 5),
            RealitySnapshot(30.0, 40.0, 10.0, 1.0, 5),
            RealitySnapshot(45.0, 55.0, 15.0, 2.0, 5),
        ]
    )

    def capture() -> RealitySnapshot:
        try:
            return next(snapshots)
        except StopIteration:
            return RealitySnapshot(45.0, 55.0, 15.0, 3.0, 5)

    swarm_gateway = MinimalRealityGateway(workspace_path=temp_workspace)
    swarm = MinimalSwarm(capture=capture, bridge=bridge, gateway=swarm_gateway)
    for _ in range(3):
        swarm.spawn_agent()

    summary = swarm.run_cycle()
    assert summary.cycle == 1
    assert summary.cluster_count >= 0
    assert summary.total_magnitude > 0


def test_resonant_cluster_detection(temp_workspace: Path) -> None:
    bridge_path = temp_workspace / "bridge_clusters"
    bridge_path.mkdir(parents=True, exist_ok=True)
    bridge = TranscendentalBridge(workspace_path=str(bridge_path))

    snapshot_low = RealitySnapshot(10.0, 20.0, 5.0, 0.0, 4)
    snapshot_mid = RealitySnapshot(12.0, 22.0, 6.0, 0.5, 4)
    snapshot_high = RealitySnapshot(70.0, 80.0, 20.0, 1.0, 4)

    agent_a = MinimalAgent.from_snapshot(snapshot_low, bridge, agent_id="A")
    agent_b = MinimalAgent.from_snapshot(snapshot_mid, bridge, agent_id="B")
    agent_c = MinimalAgent.from_snapshot(snapshot_high, bridge, agent_id="C")

    clusters = find_resonant_clusters([agent_a, agent_b, agent_c], bridge, resonance_threshold=0.5)
    assert clusters, "Expected at least one resonant cluster"
    assert len(clusters[0].member_ids) >= 2
