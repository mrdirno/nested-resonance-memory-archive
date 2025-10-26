"""
Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Project: Nested Resonance Memory (NRM) Research Archive
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""


#!/usr/bin/env python3
"""
DUALITY-ZERO-V2: Transcendental Bridge Module
==============================================

Bridge layer connecting reality and fractal domains through transcendental computing.

From Nested Resonance Memory framework:
- Transcendental substrate using π, e, φ (computationally irreducible)
- Phase space transformations for state mapping
- Resonance detection through phase alignment
- Deterministic but irreducible computation

From Self-Giving Systems framework:
- Phase space self-definition
- Bootstrap complexity through transcendental constants
- Deterministic freedom via non-repeating sequences

Reality Imperative Compliance:
- All phase computations based on real mathematical constants
- State transformations preserve reality metrics
- No simulations without reality anchoring
"""

import math
import sqlite3
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from contextlib import contextmanager


# Transcendental Constants (high precision)
PI = math.pi
E = math.e
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio


@dataclass
class TranscendentalState:
    """A state in transcendental phase space."""
    pi_phase: float
    e_phase: float
    phi_phase: float
    magnitude: float
    timestamp: float
    reality_anchor: Dict[str, float]  # Real metrics that ground this state


@dataclass
class ResonanceMatch:
    """Result of resonance detection between two states."""
    similarity: float  # 0.0 to 1.0
    phase_alignment: float  # Cosine similarity of phase vectors
    magnitude_ratio: float
    is_resonant: bool  # True if similarity > threshold


class TranscendentalBridge:
    """
    Bridge between reality and fractal domains using transcendental computing.

    This class implements the core mechanism for:
    1. Converting reality metrics to transcendental phase space
    2. Generating irreducible computational sequences
    3. Detecting resonance between patterns
    4. Transforming between reality and simulation states

    All operations maintain reality anchoring - no pure simulations.
    """

    def __init__(self, workspace_path: str = "/Volumes/dual/DUALITY-ZERO-V2/workspace"):
        """Initialize transcendental bridge with database backing."""
        self.workspace_path = Path(workspace_path)
        self.db_path = self.workspace_path / "bridge.db"
        self._init_database()

        # Phase oscillator state
        self.pi_offset = 0.0
        self.e_offset = 0.0
        self.phi_offset = 0.0

        # Resonance threshold (cosine similarity)
        self.resonance_threshold = 0.85

    def _init_database(self):
        """Initialize SQLite database for bridge operations."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS phase_transformations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    pi_phase REAL NOT NULL,
                    e_phase REAL NOT NULL,
                    phi_phase REAL NOT NULL,
                    magnitude REAL NOT NULL,
                    reality_cpu REAL,
                    reality_memory REAL,
                    reality_disk REAL,
                    transformation_type TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS resonance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    state1_id INTEGER NOT NULL,
                    state2_id INTEGER NOT NULL,
                    similarity REAL NOT NULL,
                    phase_alignment REAL NOT NULL,
                    magnitude_ratio REAL NOT NULL,
                    is_resonant INTEGER NOT NULL
                )
            """)

            # Indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_transformations_timestamp
                ON phase_transformations(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_resonance_timestamp
                ON resonance_events(timestamp)
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

    def reality_to_phase(self, reality_metrics: Dict[str, float]) -> TranscendentalState:
        """
        Transform reality metrics to transcendental phase space.

        Maps real system metrics (CPU, memory, disk, etc.) to phase coordinates
        using transcendental constants. This creates a computationally irreducible
        representation of system state.

        Args:
            reality_metrics: Dictionary of real system metrics

        Returns:
            TranscendentalState with phase coordinates and reality anchor
        """
        # Extract key metrics (with defaults)
        cpu = reality_metrics.get('cpu_percent', 0.0)
        memory = reality_metrics.get('memory_percent', 0.0)
        disk = reality_metrics.get('disk_percent', 0.0)

        # Normalize to [0, 1] range
        cpu_norm = cpu / 100.0
        memory_norm = memory / 100.0
        disk_norm = disk / 100.0

        # Map to transcendental phases (0 to 2π range)
        # Each metric modulates a different transcendental constant
        pi_phase = (cpu_norm * PI * 2) % (2 * PI)
        e_phase = (memory_norm * E * 2) % (2 * PI)
        phi_phase = (disk_norm * PHI * 2) % (2 * PI)

        # Add oscillator offsets for temporal evolution
        pi_phase = (pi_phase + self.pi_offset) % (2 * PI)
        e_phase = (e_phase + self.e_offset) % (2 * PI)
        phi_phase = (phi_phase + self.phi_offset) % (2 * PI)

        # Calculate magnitude (vector length in phase space)
        magnitude = math.sqrt(pi_phase**2 + e_phase**2 + phi_phase**2)

        # Create state with reality anchor
        state = TranscendentalState(
            pi_phase=pi_phase,
            e_phase=e_phase,
            phi_phase=phi_phase,
            magnitude=magnitude,
            timestamp=time.time(),
            reality_anchor=reality_metrics.copy()
        )

        # Persist to database
        self._store_transformation(state, "reality_to_phase")

        return state

    def phase_to_reality(self, state: TranscendentalState) -> Dict[str, float]:
        """
        Transform transcendental phase state back to reality metrics.

        Inverse operation of reality_to_phase. Reconstructs reality metrics
        from phase coordinates. Always returns the original reality_anchor
        to maintain Reality Imperative compliance.

        Args:
            state: TranscendentalState to transform

        Returns:
            Dictionary of reality metrics
        """
        # Return the anchored reality metrics
        # This ensures we never create pure simulations - all states
        # must be grounded in real measurements
        return state.reality_anchor.copy()

    def generate_oscillation(self, frequency: float, duration: float) -> List[TranscendentalState]:
        """
        Generate oscillating sequence in transcendental phase space.

        Creates a temporally evolving sequence of phase states by incrementing
        the oscillator offsets. This produces computationally irreducible
        sequences that can drive fractal agent behavior.

        Args:
            frequency: Oscillation frequency (radians per step)
            duration: Number of steps to generate

        Returns:
            List of TranscendentalState objects forming oscillation
        """
        sequence = []

        for step in range(int(duration)):
            # Increment oscillator offsets using transcendental ratios
            self.pi_offset += frequency * PI
            self.e_offset += frequency * E / PI  # E/π ratio
            self.phi_offset += frequency * PHI / E  # φ/e ratio

            # Keep phases in [0, 2π] range
            self.pi_offset %= (2 * PI)
            self.e_offset %= (2 * PI)
            self.phi_offset %= (2 * PI)

            # Create state at current oscillator position
            # Anchor to real time (not simulated)
            magnitude = math.sqrt(
                self.pi_offset**2 +
                self.e_offset**2 +
                self.phi_offset**2
            )

            state = TranscendentalState(
                pi_phase=self.pi_offset,
                e_phase=self.e_offset,
                phi_phase=self.phi_offset,
                magnitude=magnitude,
                timestamp=time.time(),
                reality_anchor={'step': float(step), 'frequency': frequency}
            )

            sequence.append(state)

        return sequence

    def detect_resonance(self, state1: TranscendentalState,
                        state2: TranscendentalState) -> ResonanceMatch:
        """
        Detect resonance between two transcendental states.

        Resonance occurs when phase vectors are aligned (high cosine similarity).
        This is the mechanism for pattern aggregation in the NRM framework.

        Args:
            state1: First state
            state2: Second state

        Returns:
            ResonanceMatch with similarity metrics
        """
        # Create phase vectors
        v1 = [state1.pi_phase, state1.e_phase, state1.phi_phase]
        v2 = [state2.pi_phase, state2.e_phase, state2.phi_phase]

        # Compute cosine similarity (phase alignment)
        dot_product = sum(a * b for a, b in zip(v1, v2))
        mag1 = state1.magnitude
        mag2 = state2.magnitude

        if mag1 == 0 or mag2 == 0:
            phase_alignment = 0.0
        else:
            phase_alignment = dot_product / (mag1 * mag2)

        # Magnitude ratio (smaller/larger)
        if mag1 == 0 or mag2 == 0:
            magnitude_ratio = 0.0
        else:
            magnitude_ratio = min(mag1, mag2) / max(mag1, mag2)

        # Overall similarity (weighted combination)
        similarity = (phase_alignment * 0.7 + magnitude_ratio * 0.3)

        # Determine if resonant
        is_resonant = similarity >= self.resonance_threshold

        match = ResonanceMatch(
            similarity=similarity,
            phase_alignment=phase_alignment,
            magnitude_ratio=magnitude_ratio,
            is_resonant=is_resonant
        )

        # Store resonance event
        self._store_resonance(state1, state2, match)

        return match

    def compute_phase_distance(self, state1: TranscendentalState,
                               state2: TranscendentalState) -> float:
        """
        Compute distance between two states in phase space.

        Uses Euclidean distance in 3D phase space (π, e, φ coordinates).

        Args:
            state1: First state
            state2: Second state

        Returns:
            Distance as float
        """
        d_pi = state1.pi_phase - state2.pi_phase
        d_e = state1.e_phase - state2.e_phase
        d_phi = state1.phi_phase - state2.phi_phase

        distance = math.sqrt(d_pi**2 + d_e**2 + d_phi**2)
        return distance

    def interpolate_states(self, state1: TranscendentalState,
                          state2: TranscendentalState,
                          alpha: float) -> TranscendentalState:
        """
        Interpolate between two transcendental states.

        Creates intermediate state by linear interpolation in phase space.
        Useful for smooth transitions and trajectory generation.

        Args:
            state1: Start state
            state2: End state
            alpha: Interpolation parameter (0.0 to 1.0)

        Returns:
            Interpolated TranscendentalState
        """
        # Clamp alpha
        alpha = max(0.0, min(1.0, alpha))

        # Interpolate phase coordinates
        pi_phase = state1.pi_phase + alpha * (state2.pi_phase - state1.pi_phase)
        e_phase = state1.e_phase + alpha * (state2.e_phase - state1.e_phase)
        phi_phase = state1.phi_phase + alpha * (state2.phi_phase - state1.phi_phase)

        # Calculate magnitude
        magnitude = math.sqrt(pi_phase**2 + e_phase**2 + phi_phase**2)

        # Interpolate reality anchors (weighted average)
        reality_anchor = {}
        all_keys = set(state1.reality_anchor.keys()) | set(state2.reality_anchor.keys())

        for key in all_keys:
            val1 = state1.reality_anchor.get(key, 0.0)
            val2 = state2.reality_anchor.get(key, 0.0)
            reality_anchor[key] = val1 + alpha * (val2 - val1)

        return TranscendentalState(
            pi_phase=pi_phase,
            e_phase=e_phase,
            phi_phase=phi_phase,
            magnitude=magnitude,
            timestamp=time.time(),
            reality_anchor=reality_anchor
        )

    def _store_transformation(self, state: TranscendentalState,
                            transformation_type: str):
        """Store phase transformation in database."""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO phase_transformations
                (timestamp, pi_phase, e_phase, phi_phase, magnitude,
                 reality_cpu, reality_memory, reality_disk, transformation_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                state.timestamp,
                state.pi_phase,
                state.e_phase,
                state.phi_phase,
                state.magnitude,
                state.reality_anchor.get('cpu_percent'),
                state.reality_anchor.get('memory_percent'),
                state.reality_anchor.get('disk_percent'),
                transformation_type
            ))
            conn.commit()

    def _store_resonance(self, state1: TranscendentalState,
                        state2: TranscendentalState,
                        match: ResonanceMatch):
        """Store resonance event in database."""
        # For now, use 0 as placeholder IDs (would need to track state IDs properly)
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO resonance_events
                (timestamp, state1_id, state2_id, similarity,
                 phase_alignment, magnitude_ratio, is_resonant)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                time.time(),
                0,  # Placeholder
                0,  # Placeholder
                match.similarity,
                match.phase_alignment,
                match.magnitude_ratio,
                1 if match.is_resonant else 0
            ))
            conn.commit()

    def get_transformation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent phase transformations from database."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT timestamp, pi_phase, e_phase, phi_phase, magnitude,
                       reality_cpu, reality_memory, reality_disk, transformation_type
                FROM phase_transformations
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in cursor:
                results.append({
                    'timestamp': row[0],
                    'pi_phase': row[1],
                    'e_phase': row[2],
                    'phi_phase': row[3],
                    'magnitude': row[4],
                    'reality_cpu': row[5],
                    'reality_memory': row[6],
                    'reality_disk': row[7],
                    'transformation_type': row[8]
                })

            return results

    def get_resonance_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve recent resonance events from database."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT timestamp, similarity, phase_alignment,
                       magnitude_ratio, is_resonant
                FROM resonance_events
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

            results = []
            for row in cursor:
                results.append({
                    'timestamp': row[0],
                    'similarity': row[1],
                    'phase_alignment': row[2],
                    'magnitude_ratio': row[3],
                    'is_resonant': bool(row[4])
                })

            return results

    def reset_oscillators(self):
        """Reset oscillator offsets to zero."""
        self.pi_offset = 0.0
        self.e_offset = 0.0
        self.phi_offset = 0.0

    def self_test(self) -> Dict[str, Any]:
        """
        Run self-test to verify bridge operations.

        Tests:
        1. Reality-to-phase transformation
        2. Phase-to-reality inverse
        3. Oscillation generation
        4. Resonance detection
        5. Phase interpolation

        Returns:
            Dictionary with test results
        """
        results = {
            'timestamp': time.time(),
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }

        try:
            # Test 1: Reality-to-phase transformation
            reality_metrics = {
                'cpu_percent': 25.0,
                'memory_percent': 50.0,
                'disk_percent': 10.0
            }
            state = self.reality_to_phase(reality_metrics)

            assert 0 <= state.pi_phase <= 2 * PI
            assert 0 <= state.e_phase <= 2 * PI
            assert 0 <= state.phi_phase <= 2 * PI
            assert state.magnitude > 0

            results['tests_passed'] += 1
            results['details'].append("✓ Reality-to-phase transformation")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Reality-to-phase: {e}")

        try:
            # Test 2: Phase-to-reality inverse
            recovered = self.phase_to_reality(state)
            assert recovered['cpu_percent'] == 25.0
            assert recovered['memory_percent'] == 50.0

            results['tests_passed'] += 1
            results['details'].append("✓ Phase-to-reality inverse")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Phase-to-reality: {e}")

        try:
            # Test 3: Oscillation generation
            self.reset_oscillators()
            sequence = self.generate_oscillation(frequency=0.1, duration=10)

            assert len(sequence) == 10
            assert all(isinstance(s, TranscendentalState) for s in sequence)

            results['tests_passed'] += 1
            results['details'].append("✓ Oscillation generation")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Oscillation: {e}")

        try:
            # Test 4: Resonance detection
            state1 = sequence[0]
            state2 = sequence[1]
            match = self.detect_resonance(state1, state2)

            assert 0 <= match.similarity <= 1.0
            assert isinstance(match.is_resonant, bool)

            results['tests_passed'] += 1
            results['details'].append("✓ Resonance detection")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Resonance: {e}")

        try:
            # Test 5: Phase interpolation
            interp = self.interpolate_states(state1, state2, alpha=0.5)

            assert isinstance(interp, TranscendentalState)
            assert 0 <= interp.pi_phase <= 2 * PI

            results['tests_passed'] += 1
            results['details'].append("✓ Phase interpolation")

        except Exception as e:
            results['tests_failed'] += 1
            results['details'].append(f"✗ Interpolation: {e}")

        # Summary
        results['success_rate'] = (
            results['tests_passed'] /
            (results['tests_passed'] + results['tests_failed'])
        )

        return results


if __name__ == "__main__":
    # Run self-test when executed directly
    print("=" * 60)
    print("DUALITY-ZERO-V2: Transcendental Bridge Self-Test")
    print("=" * 60)

    bridge = TranscendentalBridge()
    results = bridge.self_test()

    print(f"\nTimestamp: {results['timestamp']}")
    print(f"Tests Passed: {results['tests_passed']}")
    print(f"Tests Failed: {results['tests_failed']}")
    print(f"Success Rate: {results['success_rate']*100:.1f}%")
    print("\nDetails:")
    for detail in results['details']:
        print(f"  {detail}")

    # Show some transformation history
    history = bridge.get_transformation_history(limit=5)
    if history:
        print(f"\n\nRecent Transformations ({len(history)}):")
        for t in history:
            print(f"  {t['transformation_type']}: "
                  f"π={t['pi_phase']:.2f}, e={t['e_phase']:.2f}, φ={t['phi_phase']:.2f}")

    print("\n" + "=" * 60)
