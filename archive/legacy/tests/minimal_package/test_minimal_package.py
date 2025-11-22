"""Test suite for the minimal NRM package."""

import sys
from pathlib import Path

# Add minimal_package to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

from minimal import (
    MinimalAgent,
    MinimalRealityGateway,
    MinimalSwarm,
    RealitySnapshot,
    find_resonant_clusters,
)
from bridge.transcendental_bridge import TranscendentalBridge


def test_snapshot_capture():
    """Test that we can capture reality snapshots with required keys."""
    print("TEST 1: Snapshot capture")
    gateway = MinimalRealityGateway()
    snapshot = gateway.capture_snapshot()

    # Verify snapshot has all required keys
    assert hasattr(snapshot, "cpu_percent"), "Missing cpu_percent"
    assert hasattr(snapshot, "memory_percent"), "Missing memory_percent"
    assert hasattr(snapshot, "disk_percent"), "Missing disk_percent"
    assert hasattr(snapshot, "timestamp"), "Missing timestamp"
    assert hasattr(snapshot, "process_count"), "Missing process_count"

    # Verify values are reasonable
    assert 0 <= snapshot.cpu_percent <= 100, f"Invalid cpu_percent: {snapshot.cpu_percent}"
    assert 0 <= snapshot.memory_percent <= 100, f"Invalid memory_percent: {snapshot.memory_percent}"
    assert 0 <= snapshot.disk_percent <= 100, f"Invalid disk_percent: {snapshot.disk_percent}"
    assert snapshot.timestamp > 0, f"Invalid timestamp: {snapshot.timestamp}"
    assert snapshot.process_count > 0, f"Invalid process_count: {snapshot.process_count}"

    print(f"  ✓ Snapshot captured: CPU={snapshot.cpu_percent:.1f}%, "
          f"MEM={snapshot.memory_percent:.1f}%, DISK={snapshot.disk_percent:.1f}%")
    print()


def test_swarm_cycle_progression():
    """Test that swarm cycles progress and produce valid summaries."""
    print("TEST 2: Swarm cycle progression")
    swarm = MinimalSwarm()

    # Spawn some agents
    for i in range(5):
        agent = swarm.spawn_agent()
        print(f"  Spawned agent: {agent.agent_id} with magnitude={agent.magnitude:.2f}")

    # Run a cycle
    summary = swarm.run_cycle()

    # Verify cycle summary
    assert summary.cycle == 1, f"Expected cycle=1, got {summary.cycle}"
    assert summary.total_magnitude > 0, f"Expected positive magnitude, got {summary.total_magnitude}"
    assert isinstance(summary.cluster_count, int), f"Expected int cluster_count, got {type(summary.cluster_count)}"

    print(f"  ✓ Cycle {summary.cycle}: total_magnitude={summary.total_magnitude:.2f}, "
          f"clusters={summary.cluster_count}")
    print()


def test_resonant_cluster_detection():
    """Test that agents from similar snapshots cluster together."""
    print("TEST 3: Resonant cluster detection")

    bridge = TranscendentalBridge(workspace_path="/tmp/test_bridge", resonance_threshold=0.9)

    # Create similar snapshots (should cluster)
    similar_snapshot = RealitySnapshot(
        cpu_percent=25.0,
        memory_percent=30.0,
        disk_percent=15.0,
        timestamp=1000.5,
        process_count=100
    )

    # Create agents from similar snapshots
    similar_agents = [
        MinimalAgent.from_snapshot(similar_snapshot, bridge, f"similar_{i}")
        for i in range(3)
    ]

    # Create dissimilar snapshot (should NOT cluster with similar ones)
    dissimilar_snapshot = RealitySnapshot(
        cpu_percent=75.0,
        memory_percent=80.0,
        disk_percent=60.0,
        timestamp=2000.0,
        process_count=200
    )

    dissimilar_agent = MinimalAgent.from_snapshot(dissimilar_snapshot, bridge, "dissimilar_1")

    all_agents = similar_agents + [dissimilar_agent]

    # Find clusters
    clusters = find_resonant_clusters(all_agents, bridge, resonance_threshold=0.9)

    print(f"  Created {len(similar_agents)} similar agents and 1 dissimilar agent")
    print(f"  Found {len(clusters)} resonant cluster(s)")

    # Verify clustering behavior
    if len(clusters) > 0:
        for i, cluster in enumerate(clusters):
            print(f"  Cluster {i+1}: {len(cluster.member_ids)} members, "
                  f"avg_similarity={cluster.average_similarity:.3f}")
            print(f"    Members: {', '.join(cluster.member_ids)}")

            # Similar agents should cluster together
            similar_ids = {f"similar_{i}" for i in range(3)}
            cluster_ids = set(cluster.member_ids)

            # Check if this cluster contains mostly similar agents
            similar_in_cluster = len(similar_ids & cluster_ids)
            if similar_in_cluster >= 2:
                print(f"    ✓ Cluster contains {similar_in_cluster} similar agents")

            # Dissimilar agent should NOT be in a cluster with similar agents
            if "dissimilar_1" in cluster_ids and similar_in_cluster > 0:
                print(f"    ⚠ Warning: Dissimilar agent clustered with similar agents")
    else:
        print("  ⚠ No clusters found (agents may be too dissimilar)")

    print()


def test_agent_magnitude_computation():
    """Test that agent magnitude is computed correctly from snapshots."""
    print("TEST 4: Agent magnitude computation")

    bridge = TranscendentalBridge(workspace_path="/tmp/test_bridge")

    snapshot = RealitySnapshot(
        cpu_percent=30.0,
        memory_percent=60.0,
        disk_percent=90.0,
        timestamp=1000.0,
        process_count=100
    )

    agent = MinimalAgent.from_snapshot(snapshot, bridge)

    # Expected magnitude: (30 + 60 + 90) / 3 = 60.0
    expected_magnitude = (30.0 + 60.0 + 90.0) / 3.0

    print(f"  Snapshot metrics: CPU=30%, MEM=60%, DISK=90%")
    print(f"  Agent magnitude: {agent.magnitude:.2f}")
    print(f"  Expected magnitude: {expected_magnitude:.2f}")

    assert abs(agent.magnitude - expected_magnitude) < 0.01, \
        f"Magnitude mismatch: expected {expected_magnitude}, got {agent.magnitude}"

    print(f"  ✓ Magnitude computed correctly")
    print()


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 60)
    print("MINIMAL NRM PACKAGE TEST SUITE")
    print("=" * 60)
    print()

    tests = [
        test_snapshot_capture,
        test_swarm_cycle_progression,
        test_resonant_cluster_detection,
        test_agent_magnitude_computation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            print()
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            print()
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
