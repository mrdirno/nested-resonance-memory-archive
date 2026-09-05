"""Real filesystem, SQLite and psutil checks for BCP monitoring.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import math
import sqlite3
import time

import pytest

from bcp.monitor import BCPMonitor, compute_system_budget, create_system_monitor


def test_allocation_collects_selected_sqlite_and_file_metrics(tmp_path):
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"observed bytes")
    with sqlite3.connect(tmp_path / "observations.sqlite") as db:
        db.execute("CREATE TABLE readings(value REAL)")
        db.execute("INSERT INTO readings VALUES (2.75)")
        monitor = BCPMonitor(lambda_scale=0.1)
        monitor.add_task("sqlite", 1, 0.1, lambda: db.execute("SELECT value FROM readings").fetchone()[0])
        monitor.add_task("file_size", 1, 0.1, lambda: payload.stat().st_size)
        # An ignored collector would remove the file if it were called.
        monitor.add_task("too_expensive", 0.01, 10, payload.unlink)
        monitor.add_task("allocation_only", 1, 0.1)
        sample = monitor.sample(1)
        assert sample.metrics == {"sqlite": 2.75, "file_size": 14.0}
        assert sample.errors == {}
        assert sample.ignored_tasks == ["too_expensive"]
        assert "allocation_only" in sample.attended_tasks
        assert payload.is_file()
        assert abs(time.time() - sample.timestamp) < 5
        monitor.remove_task("file_size")
        monitor.remove_task("not_registered")
        assert "file_size" not in monitor.sample(1).attended_tasks


def test_collector_failures_are_distinct_from_measurements(tmp_path):
    invalid_number = tmp_path / "reading.txt"
    invalid_number.write_text("inf")
    monitor = BCPMonitor(lambda_scale=0.1)
    monitor.add_task("missing_file", 1, 0.1, lambda: (tmp_path / "missing").stat().st_size)
    monitor.add_task("nonfinite_file", 1, 0.1, lambda: float(invalid_number.read_text()))
    monitor.add_task("bad_type", 1, 0.1, lambda: {"value": 2})
    monitor.add_task("good_file", 1, 0.1, lambda: invalid_number.stat().st_size)
    sample = monitor.sample(1)
    assert sample.errors == {
        "missing_file": "FileNotFoundError", "nonfinite_file": "ValueError", "bad_type": "TypeError"
    }
    assert all(math.isnan(sample.metrics[name]) for name in sample.errors)
    assert sample.metrics["good_file"] == 3


def test_monitor_run_persists_callback_samples_and_bounds_sleep(tmp_path):
    with sqlite3.connect(tmp_path / "run.sqlite") as db:
        db.execute("CREATE TABLE samples(timestamp REAL, metric REAL)")
        monitor = BCPMonitor(lambda_scale=0.1)
        monitor.add_task("size", 1, 0.1, lambda: (tmp_path / "run.sqlite").stat().st_size)

        def record(sample):
            db.execute("INSERT INTO samples VALUES (?, ?)", (sample.timestamp, sample.metrics["size"]))

        started = time.monotonic()
        samples = monitor.run(lambda: 1.0, interval=2.0, duration=0.02, callback=record)
        elapsed = time.monotonic() - started
        assert len(samples) == 1
        assert elapsed < 1.0  # Regression: the old implementation always slept two seconds.
        assert db.execute("SELECT timestamp, metric FROM samples").fetchall() == [
            (samples[0].timestamp, samples[0].metrics["size"])
        ]
        assert monitor.run(lambda: 1.0, duration=0) == []


@pytest.mark.parametrize("interval,duration", [(0, 1), (-1, 1), (float("inf"), 1), (1, -1), (1, float("nan"))])
def test_invalid_schedule_is_rejected_before_sampling(interval, duration):
    with pytest.raises(ValueError):
        BCPMonitor().run(lambda: 1, interval=interval, duration=duration)


@pytest.mark.parametrize("budget", [-1, float("nan"), float("inf")])
def test_invalid_budget_is_rejected(budget):
    with pytest.raises(ValueError):
        BCPMonitor().sample(budget)


def test_system_collectors_measure_the_running_host():
    pytest.importorskip("psutil")
    sample = create_system_monitor().sample(100)
    assert sample.errors == {}
    assert set(sample.metrics) == {"cpu_percent", "memory_percent", "disk_usage", "swap_usage", "process_count"}
    assert all(0 <= sample.metrics[name] <= 100 for name in sample.metrics if name != "process_count")
    assert sample.metrics["process_count"] >= 1
    assert 0 <= compute_system_budget() <= 1
