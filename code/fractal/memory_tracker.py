#!/usr/bin/env python3
"""
Memory Tracker for C188 Experiment

Tracks recent composition events per agent to implement refractory periods.

Theory (Extension 4, Part B):
    Agents retain memory of recent compositions, creating temporal
    selection bias against recently-composed agents.

    P(select agent i) ∝ exp(-n_recent / τ_memory)

    Where:
        n_recent = compositions involving agent i in last τ_memory cycles
        τ_memory = memory decay timescale

    Prediction:
        Memory reduces compositional burstiness (temporal clustering).
        Longer memory → higher spawn success, lower burstiness coefficient B.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-04
Cycle: 997
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
from collections import deque, defaultdict
from typing import List, Dict, Optional


class MemoryTracker:
    """
    Track composition event history for implementing refractory periods.

    Purpose:
        Record which agents participated in recent compositions.
        Enable memory-weighted selection that avoids recently-composed agents.

    Theory:
        Refractory periods spread compositional load temporally:
        - Recently composed agents: Lower selection probability
        - Rested agents: Higher selection probability
        - Effect: Reduces burstiness, increases spawn success
    """

    def __init__(self, memory_window: int):
        """
        Initialize memory tracker.

        Args:
            memory_window: Number of cycles to retain composition history (τ_memory)
        """
        self.memory_window = memory_window

        # Track composition events: {agent_id: deque of cycle_indices}
        self.composition_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=memory_window))

        # Current cycle index (updated externally)
        self.current_cycle = 0

    def record_composition(self, agent_ids: List[str], cycle_idx: int):
        """
        Record composition event involving multiple agents.

        Args:
            agent_ids: List of agent IDs participating in composition
            cycle_idx: Cycle index when composition occurred
        """
        self.current_cycle = cycle_idx

        for agent_id in agent_ids:
            self.composition_history[agent_id].append(cycle_idx)

    def count_recent_compositions(self, agent_id: str, window: Optional[int] = None) -> int:
        """
        Count compositions involving agent in recent history.

        Args:
            agent_id: Agent identifier
            window: Custom window size (if None, use self.memory_window)

        Returns:
            Number of recent composition events
        """
        if window is None:
            window = self.memory_window

        if agent_id not in self.composition_history:
            return 0

        # Count events within window
        recent_events = [
            cycle for cycle in self.composition_history[agent_id]
            if self.current_cycle - cycle <= window
        ]

        return len(recent_events)

    def get_memory_weight(self, agent_id: str, decay_factor: float = 2.0) -> float:
        """
        Calculate memory-based selection weight for agent.

        Weight decreases exponentially with recent composition count:
            weight = exp(-n_recent / decay_factor)

        Args:
            agent_id: Agent identifier
            decay_factor: Controls strength of memory effect (higher = weaker effect)

        Returns:
            Selection weight (0-1 range, 1 = fully rested, 0 = heavily composed)
        """
        n_recent = self.count_recent_compositions(agent_id)

        # Exponential decay
        weight = np.exp(-n_recent / decay_factor)

        return weight

    def get_all_weights(self, agent_ids: List[str], decay_factor: float = 2.0) -> Dict[str, float]:
        """
        Calculate memory weights for all agents.

        Args:
            agent_ids: List of agent identifiers
            decay_factor: Memory decay parameter

        Returns:
            dict mapping agent_id to selection weight
        """
        weights = {}
        for agent_id in agent_ids:
            weights[agent_id] = self.get_memory_weight(agent_id, decay_factor)

        return weights

    def clear_agent_history(self, agent_id: str):
        """
        Clear composition history for specific agent (e.g., after death).

        Args:
            agent_id: Agent identifier
        """
        if agent_id in self.composition_history:
            del self.composition_history[agent_id]

    def get_statistics(self) -> Dict:
        """
        Get tracker statistics for analysis.

        Returns:
            dict with memory tracker metrics
        """
        if len(self.composition_history) == 0:
            return {
                'n_agents_tracked': 0,
                'mean_recent_compositions': 0.0,
                'max_recent_compositions': 0,
                'memory_window': self.memory_window,
            }

        recent_counts = [
            self.count_recent_compositions(agent_id)
            for agent_id in self.composition_history.keys()
        ]

        return {
            'n_agents_tracked': len(self.composition_history),
            'mean_recent_compositions': float(np.mean(recent_counts)) if recent_counts else 0.0,
            'std_recent_compositions': float(np.std(recent_counts)) if recent_counts else 0.0,
            'max_recent_compositions': int(max(recent_counts)) if recent_counts else 0,
            'memory_window': self.memory_window,
        }


class BurstinessCalculator:
    """
    Calculate burstiness coefficient for temporal clustering analysis.

    Burstiness B quantifies temporal clustering of events:
        B = (σ_IEI - μ_IEI) / (σ_IEI + μ_IEI)

    Where IEI = inter-event intervals between compositions

    Interpretation:
        B = -1: Regular spacing (anti-bursty, periodic)
        B =  0: Random (Poisson process)
        B = +1: Highly clustered (bursty, avalanches)

    Theory:
        Memory should reduce burstiness:
        - No memory: B ≈ 0.3 (temporal clustering from energy depletion cascades)
        - Long memory: B ≈ 0.0 (spreading compositions temporally)
    """

    @staticmethod
    def calculate_burstiness(event_times: List[int]) -> float:
        """
        Calculate burstiness coefficient from event times.

        Args:
            event_times: List of cycle indices when events occurred

        Returns:
            Burstiness coefficient B ∈ [-1, 1]
        """
        if len(event_times) < 2:
            return 0.0  # Undefined for <2 events

        # Sort event times
        sorted_times = sorted(event_times)

        # Calculate inter-event intervals
        intervals = [sorted_times[i+1] - sorted_times[i] for i in range(len(sorted_times)-1)]

        if len(intervals) == 0:
            return 0.0

        # Calculate mean and std of intervals
        mean_iei = np.mean(intervals)
        std_iei = np.std(intervals)

        # Burstiness formula
        if (std_iei + mean_iei) == 0:
            return 0.0

        B = (std_iei - mean_iei) / (std_iei + mean_iei)

        return float(B)

    @staticmethod
    def calculate_autocorrelation(event_times: List[int], max_lag: int = 100) -> List[float]:
        """
        Calculate autocorrelation function for event sequence.

        Detects periodic or clustered temporal patterns.

        Args:
            event_times: List of cycle indices when events occurred
            max_lag: Maximum lag to compute autocorrelation

        Returns:
            List of autocorrelation values for lags 0 to max_lag
        """
        if len(event_times) < 2:
            return [0.0]

        # Create binary event sequence
        max_time = max(event_times)
        event_sequence = np.zeros(max_time + 1)
        for t in event_times:
            event_sequence[t] = 1

        # Calculate autocorrelation
        autocorr = []
        mean_events = np.mean(event_sequence)
        variance = np.var(event_sequence)

        if variance == 0:
            return [0.0] * (max_lag + 1)

        for lag in range(min(max_lag + 1, len(event_sequence))):
            if lag == 0:
                autocorr.append(1.0)
            else:
                # Pearson correlation at lag
                seq1 = event_sequence[:-lag]
                seq2 = event_sequence[lag:]

                if len(seq1) > 0:
                    cov = np.mean((seq1 - mean_events) * (seq2 - mean_events))
                    corr = cov / variance
                    autocorr.append(float(corr))
                else:
                    autocorr.append(0.0)

        return autocorr


if __name__ == "__main__":
    # Test memory tracker
    print("Memory Tracker Test")
    print("=" * 80)

    tracker = MemoryTracker(memory_window=100)

    # Simulate composition events
    print("Simulating composition events...")

    # Agent A composed at cycles 10, 20, 30 (frequent)
    tracker.record_composition(['agent_A'], 10)
    tracker.record_composition(['agent_A'], 20)
    tracker.record_composition(['agent_A'], 30)
    tracker.current_cycle = 50

    # Agent B composed at cycle 10 only (rested)
    tracker.record_composition(['agent_B'], 10)

    print(f"\nCurrent cycle: {tracker.current_cycle}")
    print(f"Agent A recent compositions: {tracker.count_recent_compositions('agent_A')}")
    print(f"Agent B recent compositions: {tracker.count_recent_compositions('agent_B')}")

    # Calculate weights
    weight_A = tracker.get_memory_weight('agent_A')
    weight_B = tracker.get_memory_weight('agent_B')

    print(f"\nMemory weights (selection probability):")
    print(f"Agent A (frequent): {weight_A:.3f}")
    print(f"Agent B (rested): {weight_B:.3f}")

    if weight_B > weight_A:
        print("✅ Rested agent has higher weight (memory effect working)")
    else:
        print("⚠️  Check implementation")

    print()

    # Test burstiness calculator
    print("Burstiness Calculator Test")
    print("-" * 80)

    # Regular events (anti-bursty)
    regular_events = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90]
    B_regular = BurstinessCalculator.calculate_burstiness(regular_events)
    print(f"Regular spacing: B = {B_regular:.3f} (expected ≈ -1)")

    # Random events (Poisson-like)
    random_events = [5, 12, 18, 35, 42, 61, 73, 89, 95]
    B_random = BurstinessCalculator.calculate_burstiness(random_events)
    print(f"Random spacing: B = {B_random:.3f} (expected ≈ 0)")

    # Bursty events (clustered)
    bursty_events = [1, 2, 3, 4, 50, 51, 52, 90, 91, 92, 93]
    B_bursty = BurstinessCalculator.calculate_burstiness(bursty_events)
    print(f"Bursty spacing: B = {B_bursty:.3f} (expected ≈ +1)")

    if B_regular < B_random < B_bursty:
        print("✅ Burstiness ordering correct")
    else:
        print("⚠️  Check burstiness calculation")
