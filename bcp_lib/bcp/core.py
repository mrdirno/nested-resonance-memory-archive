"""
BCP Core Module - The Budget-Constrained Perception Model

This module implements the universal BCP equation for attention allocation.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from enum import Enum
import numpy as np


class Phase(Enum):
    """System phases based on budget level."""
    ABUNDANCE = "abundance"     # Budget high, λ low, attend to everything
    SCARCITY = "scarcity"       # Budget moderate, triage begins
    CRISIS = "crisis"           # Budget critical, focus on single item


@dataclass
class AttentionItem:
    """
    An item that can receive attention/resources.

    Attributes:
        name: Identifier for this item
        gain: Expected benefit if attended to (E[Gain])
        cost: Resource cost to attend
        priority: Computed priority (set by BCPModel)
        attended: Whether this item was selected for attention
    """
    name: str
    gain: float
    cost: float
    priority: float = 0.0
    attended: bool = False

    def compute_priority(self, lambda_: float, gamma: float = 0.0,
                        n_items: int = 1) -> float:
        """
        Compute priority using the BCP equation.

        V(a) = Gain - λ × Cost - γ × (1/n)

        Args:
            lambda_: Metabolic pressure (higher = more scarcity)
            gamma: Complexity penalty coefficient
            n_items: Total number of items being managed

        Returns:
            Priority score (higher = more important)
        """
        complexity_cost = gamma / max(1, n_items)
        self.priority = self.gain - lambda_ * self.cost - complexity_cost
        return self.priority


@dataclass
class BCPResult:
    """
    Result of BCP allocation.

    Attributes:
        attended: List of item names that received attention
        ignored: List of item names that were ignored
        total_cost: Total resource cost spent
        phase: Current system phase
        lambda_: Computed metabolic pressure
        budget: Input budget value
    """
    attended: List[str]
    ignored: List[str]
    total_cost: float
    phase: Phase
    lambda_: float
    budget: float

    @property
    def n_attended(self) -> int:
        """Number of items attended to."""
        return len(self.attended)

    @property
    def n_ignored(self) -> int:
        """Number of items ignored."""
        return len(self.ignored)

    @property
    def attention_fraction(self) -> float:
        """Fraction of items that received attention."""
        total = len(self.attended) + len(self.ignored)
        return len(self.attended) / total if total > 0 else 0.0


class BCPModel:
    """
    The Budget-Constrained Perception Model.

    This model implements the universal attention allocation equation:
    V(a) = E[Gain(a)] - λ(B) × Cost(a) - γ × Complexity

    Attributes:
        lambda_scale: Scaling factor for metabolic pressure (default: 10.0)
        lambda_epsilon: Small constant to prevent division by zero (default: 0.1)
        gamma: Complexity penalty coefficient (default: 0.0)
        abundance_threshold: Budget threshold above which system is in ABUNDANCE
        crisis_threshold: Budget threshold below which system is in CRISIS
    """

    def __init__(
        self,
        lambda_scale: float = 10.0,
        lambda_epsilon: float = 0.1,
        gamma: float = 0.0,
        abundance_threshold: float = 2.0,
        crisis_threshold: float = 0.5
    ):
        self.lambda_scale = lambda_scale
        self.lambda_epsilon = lambda_epsilon
        self.gamma = gamma
        self.abundance_threshold = abundance_threshold
        self.crisis_threshold = crisis_threshold

    def compute_lambda(self, budget: float) -> float:
        """
        Compute metabolic pressure from budget.

        λ(B) = k / (ε + B)

        Higher budget → lower λ → less cost penalty
        Lower budget → higher λ → more cost penalty
        """
        return self.lambda_scale / (self.lambda_epsilon + budget)

    def determine_phase(self, budget: float) -> Phase:
        """Determine system phase based on budget level."""
        if budget >= self.abundance_threshold:
            return Phase.ABUNDANCE
        elif budget <= self.crisis_threshold:
            return Phase.CRISIS
        else:
            return Phase.SCARCITY

    def allocate(
        self,
        items: List[AttentionItem],
        budget: float
    ) -> BCPResult:
        """
        Allocate attention to items given budget constraint.

        Algorithm:
        1. Compute metabolic pressure λ(B)
        2. Compute priority for each item: V = Gain - λ×Cost - γ×Complexity
        3. Sort items by priority (descending)
        4. Greedily select items with positive priority until budget exhausted

        Args:
            items: List of AttentionItem objects
            budget: Available resource budget

        Returns:
            BCPResult with allocation details
        """
        # Compute metabolic pressure
        lambda_ = self.compute_lambda(budget)
        phase = self.determine_phase(budget)

        # Compute priorities
        n_items = len(items)
        for item in items:
            item.compute_priority(lambda_, self.gamma, n_items)
            item.attended = False

        # Sort by priority (descending)
        sorted_items = sorted(items, key=lambda x: x.priority, reverse=True)

        # Greedy allocation
        attended = []
        ignored = []
        total_cost = 0.0

        for item in sorted_items:
            if item.priority > 0 and total_cost + item.cost <= budget:
                item.attended = True
                attended.append(item.name)
                total_cost += item.cost
            else:
                ignored.append(item.name)

        return BCPResult(
            attended=attended,
            ignored=ignored,
            total_cost=total_cost,
            phase=phase,
            lambda_=lambda_,
            budget=budget
        )

    def sweep_budgets(
        self,
        items_fn,  # Callable that returns List[AttentionItem]
        budget_range: np.ndarray
    ) -> List[BCPResult]:
        """
        Run allocation across a range of budget values.

        Useful for visualizing phase transitions.

        Args:
            items_fn: Function that returns fresh list of items
            budget_range: Array of budget values to test

        Returns:
            List of BCPResult for each budget value
        """
        results = []
        for budget in budget_range:
            items = items_fn()
            result = self.allocate(items, budget)
            results.append(result)
        return results

    def find_phase_thresholds(
        self,
        items_fn,
        budget_range: np.ndarray
    ) -> Tuple[float, float]:
        """
        Find budget thresholds where phase transitions occur.

        Returns:
            (triage_threshold, crisis_threshold)
            - triage_threshold: Budget where items start being ignored
            - crisis_threshold: Budget where only 1 item attended
        """
        results = self.sweep_budgets(items_fn, budget_range)
        n_total = len(items_fn())

        # Find triage threshold (first budget where not all items attended)
        triage_threshold = budget_range[-1]
        for i, r in enumerate(results):
            if r.n_attended < n_total:
                triage_threshold = budget_range[i]
                break

        # Find crisis threshold (first budget where ≤1 item attended)
        crisis_threshold = budget_range[0]
        for i, r in enumerate(results):
            if r.n_attended <= 1:
                crisis_threshold = budget_range[i]
                break

        return triage_threshold, crisis_threshold
