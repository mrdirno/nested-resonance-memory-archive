#!/usr/bin/env python3
"""
Overhead Authentication Module - Gate 1.4 Implementation
=========================================================

Implements the ±5% Overhead Authentication Protocol from Paper 1 as a standing
CI validation system.

**Purpose:** Validate that reality-grounded systems maintain predictable
computational expense, distinguishing them from pure simulations.

**Protocol:** For any reality-grounded operation with N measurements, average
cost C, and simulation baseline T_sim:

    Predicted Overhead: O_pred = (N × C) / T_sim
    Observed Overhead: O_obs = T_measured / T_sim
    Authentication: |O_obs - O_pred| / O_pred ≤ 0.05 (±5%)

**Gate 1.4 Criteria:**
- ±5% threshold enforced
- CI integration blocks PRs if reality link degraded
- Automated validation on every commit
- Audit trail maintained in database

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import json
import time
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from contextlib import contextmanager
from datetime import datetime
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class OverheadMeasurement:
    """Record of a single overhead measurement."""
    timestamp: str
    operation_name: str
    instrumentation_count: int  # N: Number of measurements
    per_call_cost_ms: float  # C: Average cost per call (milliseconds)
    baseline_runtime_min: float  # T_sim: Pure simulation baseline (minutes)
    measured_runtime_min: float  # T_measured: Actual runtime (minutes)
    predicted_overhead: float  # O_pred = (N × C) / T_sim
    observed_overhead: float  # O_obs = T_measured / T_sim
    relative_error: float  # |O_obs - O_pred| / O_pred
    passes_authentication: bool  # relative_error ≤ 0.05
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OverheadManifest:
    """Manifest of authenticated overhead measurements."""
    version: str
    created: str
    description: str
    measurements: List[OverheadMeasurement]
    threshold_percent: float = 5.0  # ±5% default
    total_measurements: int = 0
    passing_measurements: int = 0
    pass_rate: float = 0.0


class OverheadAuthenticator:
    """
    Overhead Authentication System - Gate 1.4.

    Validates computational expense predictions to ensure reality grounding.
    """

    VERSION = "1.0.0"
    THRESHOLD_PERCENT = 5.0  # ±5% from Paper 1

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialize overhead authenticator.

        Args:
            workspace_path: Path for database and manifest storage
        """
        if workspace_path is None:
            workspace_path = str(Path(__file__).parent.parent.parent / "workspace")

        self.workspace_path = Path(workspace_path)
        self.workspace_path.mkdir(parents=True, exist_ok=True)

        self.manifest_path = self.workspace_path / "overhead_manifest.json"
        self.db_path = self.workspace_path / "overhead_validation.db"

        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database for overhead tracking."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS overhead_measurements (
                    measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation_name TEXT NOT NULL,
                    instrumentation_count INTEGER NOT NULL,
                    per_call_cost_ms REAL NOT NULL,
                    baseline_runtime_min REAL NOT NULL,
                    measured_runtime_min REAL NOT NULL,
                    predicted_overhead REAL NOT NULL,
                    observed_overhead REAL NOT NULL,
                    relative_error REAL NOT NULL,
                    passes_authentication BOOLEAN NOT NULL,
                    metadata TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS validation_history (
                    validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    total_measurements INTEGER NOT NULL,
                    passing_measurements INTEGER NOT NULL,
                    pass_rate REAL NOT NULL,
                    threshold_percent REAL NOT NULL,
                    validation_passed BOOLEAN NOT NULL
                )
            """)

            # Indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_measurements_timestamp
                ON overhead_measurements(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_measurements_operation
                ON overhead_measurements(operation_name)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_validation_timestamp
                ON validation_history(timestamp)
            """)

            conn.commit()

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(str(self.db_path))
        try:
            yield conn
        finally:
            conn.close()

    def measure_overhead(
        self,
        operation_name: str,
        instrumentation_count: int,
        per_call_cost_ms: float,
        baseline_runtime_min: float,
        measured_runtime_min: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OverheadMeasurement:
        """
        Measure and authenticate computational overhead.

        Args:
            operation_name: Name of operation being validated
            instrumentation_count: Number of measurements (N)
            per_call_cost_ms: Average cost per measurement (C, milliseconds)
            baseline_runtime_min: Pure simulation baseline (T_sim, minutes)
            measured_runtime_min: Actual measured runtime (T_measured, minutes)
            metadata: Optional additional metadata

        Returns:
            OverheadMeasurement with authentication result
        """
        # Compute predicted overhead
        # Total instrumentation time = N × C (convert C from ms to minutes)
        total_instrumentation_min = (instrumentation_count * per_call_cost_ms) / (1000.0 * 60.0)

        # Predicted overhead factor: O_pred = (N × C) / T_sim
        # This gives the overhead as a dimensionless multiplier
        predicted_overhead = total_instrumentation_min / baseline_runtime_min

        # Compute observed overhead
        # O_obs = T_measured / T_sim
        observed_overhead = measured_runtime_min / baseline_runtime_min

        # Compute relative error
        # ε = |O_obs - O_pred| / O_pred
        if predicted_overhead > 0:
            relative_error = abs(observed_overhead - predicted_overhead) / predicted_overhead
        else:
            relative_error = float('inf')

        # Authentication criterion: ε ≤ 0.05 (±5%)
        threshold = self.THRESHOLD_PERCENT / 100.0
        passes = relative_error <= threshold

        # Create measurement record
        measurement = OverheadMeasurement(
            timestamp=datetime.now().isoformat(),
            operation_name=operation_name,
            instrumentation_count=instrumentation_count,
            per_call_cost_ms=per_call_cost_ms,
            baseline_runtime_min=baseline_runtime_min,
            measured_runtime_min=measured_runtime_min,
            predicted_overhead=predicted_overhead,
            observed_overhead=observed_overhead,
            relative_error=relative_error,
            passes_authentication=passes,
            metadata=metadata or {}
        )

        # Persist to database
        self._save_measurement(measurement)

        return measurement

    def _save_measurement(self, measurement: OverheadMeasurement) -> None:
        """Save measurement to database."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO overhead_measurements (
                    timestamp, operation_name, instrumentation_count,
                    per_call_cost_ms, baseline_runtime_min, measured_runtime_min,
                    predicted_overhead, observed_overhead, relative_error,
                    passes_authentication, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                measurement.timestamp,
                measurement.operation_name,
                measurement.instrumentation_count,
                measurement.per_call_cost_ms,
                measurement.baseline_runtime_min,
                measurement.measured_runtime_min,
                measurement.predicted_overhead,
                measurement.observed_overhead,
                measurement.relative_error,
                measurement.passes_authentication,
                json.dumps(measurement.metadata)
            ))
            conn.commit()

    def create_manifest(
        self,
        measurements: List[OverheadMeasurement],
        description: str = "Overhead authentication manifest"
    ) -> OverheadManifest:
        """
        Create overhead authentication manifest.

        Args:
            measurements: List of overhead measurements
            description: Human-readable description

        Returns:
            OverheadManifest
        """
        total = len(measurements)
        passing = sum(1 for m in measurements if m.passes_authentication)
        pass_rate = passing / total if total > 0 else 0.0

        manifest = OverheadManifest(
            version=self.VERSION,
            created=datetime.now().isoformat(),
            description=description,
            measurements=measurements,
            threshold_percent=self.THRESHOLD_PERCENT,
            total_measurements=total,
            passing_measurements=passing,
            pass_rate=pass_rate
        )

        # Save to JSON
        self._save_manifest(manifest)

        return manifest

    def _save_manifest(self, manifest: OverheadManifest) -> None:
        """Save manifest to JSON file."""
        manifest_dict = {
            'version': manifest.version,
            'created': manifest.created,
            'description': manifest.description,
            'threshold_percent': manifest.threshold_percent,
            'total_measurements': manifest.total_measurements,
            'passing_measurements': manifest.passing_measurements,
            'pass_rate': manifest.pass_rate,
            'measurements': [asdict(m) for m in manifest.measurements]
        }

        self.manifest_path.write_text(json.dumps(manifest_dict, indent=2))

    def load_manifest(
        self,
        manifest_path: Optional[Path] = None
    ) -> Optional[OverheadManifest]:
        """
        Load overhead manifest from JSON.

        Args:
            manifest_path: Path to manifest (defaults to self.manifest_path)

        Returns:
            OverheadManifest or None if file doesn't exist
        """
        if manifest_path is None:
            manifest_path = self.manifest_path

        if not manifest_path.exists():
            return None

        data = json.loads(manifest_path.read_text())

        measurements = [
            OverheadMeasurement(**m) for m in data['measurements']
        ]

        manifest = OverheadManifest(
            version=data['version'],
            created=data['created'],
            description=data['description'],
            measurements=measurements,
            threshold_percent=data['threshold_percent'],
            total_measurements=data['total_measurements'],
            passing_measurements=data['passing_measurements'],
            pass_rate=data['pass_rate']
        )

        return manifest

    def validate_manifest(
        self,
        manifest_path: Optional[Path] = None,
        strict: bool = True
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Validate overhead manifest - Gate 1.4 CI check.

        Args:
            manifest_path: Path to manifest
            strict: If True, fail on any authentication failures

        Returns:
            Tuple of (passed, errors, warnings)
        """
        errors = []
        warnings = []

        manifest = self.load_manifest(manifest_path)

        if manifest is None:
            errors.append("Manifest file not found")
            return False, errors, warnings

        print("=" * 80)
        print("OVERHEAD AUTHENTICATION VALIDATION")
        print("=" * 80)
        print()
        print(f"Manifest: {manifest_path or self.manifest_path}")
        print(f"Description: {manifest.description}")
        print(f"Created: {manifest.created}")
        print(f"Threshold: ±{manifest.threshold_percent}%")
        print(f"Measurements: {manifest.total_measurements}")
        print()

        # Validate each measurement
        for i, measurement in enumerate(manifest.measurements, 1):
            status = "✓" if measurement.passes_authentication else "✗"
            error_pct = measurement.relative_error * 100

            print(f"{status} [{i}/{manifest.total_measurements}] {measurement.operation_name}")
            print(f"    Predicted: {measurement.predicted_overhead:.4f}×")
            print(f"    Observed:  {measurement.observed_overhead:.4f}×")
            print(f"    Error:     {error_pct:.2f}% (threshold: ±{manifest.threshold_percent}%)")

            if not measurement.passes_authentication:
                error_msg = (
                    f"{measurement.operation_name}: relative error {error_pct:.2f}% "
                    f"exceeds ±{manifest.threshold_percent}% threshold"
                )
                errors.append(error_msg)
                print(f"    ⚠️  AUTHENTICATION FAILED")
            print()

        print("=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)
        print()
        print(f"Total measurements: {manifest.total_measurements}")
        print(f"Passing: {manifest.passing_measurements}")
        print(f"Failing: {manifest.total_measurements - manifest.passing_measurements}")
        print(f"Pass rate: {manifest.pass_rate * 100:.1f}%")
        print()

        # Determine overall pass/fail
        if errors:
            print("✗ AUTHENTICATION FAILED")
            print()
            for error in errors:
                print(f"  ERROR: {error}")
        else:
            print("✓ AUTHENTICATION PASSED")

        print()
        print("=" * 80)

        # Record validation
        self._record_validation(manifest, len(errors) == 0)

        passed = len(errors) == 0
        return passed, errors, warnings

    def _record_validation(
        self,
        manifest: OverheadManifest,
        passed: bool
    ) -> None:
        """Record validation attempt to database."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO validation_history (
                    timestamp, total_measurements, passing_measurements,
                    pass_rate, threshold_percent, validation_passed
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                manifest.total_measurements,
                manifest.passing_measurements,
                manifest.pass_rate,
                manifest.threshold_percent,
                passed
            ))
            conn.commit()

    def get_recent_measurements(
        self,
        hours: float = 24.0,
        operation_name: Optional[str] = None
    ) -> List[OverheadMeasurement]:
        """
        Get recent overhead measurements.

        Args:
            hours: Number of hours to look back
            operation_name: Optional filter by operation name

        Returns:
            List of OverheadMeasurement
        """
        measurements = []

        with self._get_connection() as conn:
            if operation_name:
                cursor = conn.execute("""
                    SELECT * FROM overhead_measurements
                    WHERE operation_name = ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                """, (operation_name,))
            else:
                cursor = conn.execute("""
                    SELECT * FROM overhead_measurements
                    ORDER BY timestamp DESC
                    LIMIT 100
                """)

            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                # Remove measurement_id, parse metadata
                data.pop('measurement_id')
                if data.get('metadata'):
                    data['metadata'] = json.loads(data['metadata'])
                else:
                    data['metadata'] = {}

                measurements.append(OverheadMeasurement(**data))

        return measurements

    def get_statistics(self) -> Dict[str, Any]:
        """Get overhead authentication statistics."""
        with self._get_connection() as conn:
            # Total measurements
            cursor = conn.execute("SELECT COUNT(*) FROM overhead_measurements")
            total = cursor.fetchone()[0]

            # Passing measurements
            cursor = conn.execute("""
                SELECT COUNT(*) FROM overhead_measurements
                WHERE passes_authentication = 1
            """)
            passing = cursor.fetchone()[0]

            # Recent validations
            cursor = conn.execute("""
                SELECT * FROM validation_history
                ORDER BY timestamp DESC
                LIMIT 10
            """)
            columns = [desc[0] for desc in cursor.description]
            recent_validations = [
                dict(zip(columns, row)) for row in cursor.fetchall()
            ]

        pass_rate = passing / total if total > 0 else 0.0

        return {
            'total_measurements': total,
            'passing_measurements': passing,
            'pass_rate': pass_rate,
            'threshold_percent': self.THRESHOLD_PERCENT,
            'recent_validations': recent_validations
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Overhead Authentication System - Gate 1.4"
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Measure command
    measure_parser = subparsers.add_parser(
        'measure',
        help='Record overhead measurement'
    )
    measure_parser.add_argument(
        '--name',
        required=True,
        help='Operation name'
    )
    measure_parser.add_argument(
        '--count',
        type=int,
        required=True,
        help='Instrumentation count (N)'
    )
    measure_parser.add_argument(
        '--cost-ms',
        type=float,
        required=True,
        help='Per-call cost in milliseconds (C)'
    )
    measure_parser.add_argument(
        '--baseline-min',
        type=float,
        required=True,
        help='Baseline runtime in minutes (T_sim)'
    )
    measure_parser.add_argument(
        '--measured-min',
        type=float,
        required=True,
        help='Measured runtime in minutes (T_measured)'
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate overhead manifest (CI check)'
    )
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on any authentication failures'
    )
    validate_parser.add_argument(
        '--manifest',
        type=Path,
        help='Path to manifest file'
    )

    # Create command
    create_parser = subparsers.add_parser(
        'create',
        help='Create overhead manifest from recent measurements'
    )
    create_parser.add_argument(
        '--description',
        default="Overhead authentication manifest",
        help='Manifest description'
    )
    create_parser.add_argument(
        '--hours',
        type=float,
        default=24.0,
        help='Hours of history to include'
    )

    # Stats command
    stats_parser = subparsers.add_parser(
        'stats',
        help='Show overhead authentication statistics'
    )

    args = parser.parse_args()

    authenticator = OverheadAuthenticator()

    if args.command == 'measure':
        measurement = authenticator.measure_overhead(
            operation_name=args.name,
            instrumentation_count=args.count,
            per_call_cost_ms=args.cost_ms,
            baseline_runtime_min=args.baseline_min,
            measured_runtime_min=args.measured_min
        )

        status = "✓ PASSED" if measurement.passes_authentication else "✗ FAILED"
        print(f"Overhead Authentication: {status}")
        print(f"  Predicted: {measurement.predicted_overhead:.4f}×")
        print(f"  Observed:  {measurement.observed_overhead:.4f}×")
        print(f"  Error:     {measurement.relative_error * 100:.2f}%")

        sys.exit(0 if measurement.passes_authentication else 1)

    elif args.command == 'validate':
        passed, errors, warnings = authenticator.validate_manifest(
            manifest_path=args.manifest,
            strict=args.strict
        )
        sys.exit(0 if passed else 1)

    elif args.command == 'create':
        measurements = authenticator.get_recent_measurements(hours=args.hours)

        if not measurements:
            print("No measurements found in database")
            sys.exit(1)

        manifest = authenticator.create_manifest(
            measurements=measurements,
            description=args.description
        )

        print(f"Created manifest: {authenticator.manifest_path}")
        print(f"  Measurements: {manifest.total_measurements}")
        print(f"  Pass rate: {manifest.pass_rate * 100:.1f}%")

    elif args.command == 'stats':
        stats = authenticator.get_statistics()

        print("Overhead Authentication Statistics")
        print("=" * 40)
        print(f"Total measurements: {stats['total_measurements']}")
        print(f"Passing: {stats['passing_measurements']}")
        print(f"Pass rate: {stats['pass_rate'] * 100:.1f}%")
        print(f"Threshold: ±{stats['threshold_percent']}%")

    else:
        parser.print_help()
        sys.exit(1)
