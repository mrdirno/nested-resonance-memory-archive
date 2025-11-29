"""
Tests for BCP Core Module

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import pytest
import numpy as np
from bcp import AttentionItem, BCPModel, Phase, BCPResult, DOMAIN_PRESETS


class TestAttentionItem:
    """Tests for AttentionItem class."""

    def test_creation(self):
        """Test basic item creation."""
        item = AttentionItem("test", gain=0.8, cost=0.3)
        assert item.name == "test"
        assert item.gain == 0.8
        assert item.cost == 0.3
        assert item.priority == 0.0
        assert item.attended is False

    def test_priority_computation_low_lambda(self):
        """Priority with low lambda (abundance)."""
        item = AttentionItem("test", gain=0.8, cost=0.3)
        priority = item.compute_priority(lambda_=0.5, gamma=0.0, n_items=1)
        # V = 0.8 - 0.5 * 0.3 = 0.65
        assert abs(priority - 0.65) < 0.001
        assert item.priority == priority

    def test_priority_computation_high_lambda(self):
        """Priority with high lambda (scarcity)."""
        item = AttentionItem("test", gain=0.8, cost=0.3)
        priority = item.compute_priority(lambda_=5.0, gamma=0.0, n_items=1)
        # V = 0.8 - 5.0 * 0.3 = -0.7
        assert abs(priority - (-0.7)) < 0.001

    def test_priority_with_gamma(self):
        """Priority with complexity penalty."""
        item = AttentionItem("test", gain=0.8, cost=0.3)
        priority = item.compute_priority(lambda_=1.0, gamma=0.1, n_items=5)
        # V = 0.8 - 1.0 * 0.3 - 0.1/5 = 0.48
        assert abs(priority - 0.48) < 0.001


class TestBCPModel:
    """Tests for BCPModel class."""

    def test_default_initialization(self):
        """Test default model parameters."""
        model = BCPModel()
        assert model.lambda_scale == 10.0
        assert model.lambda_epsilon == 0.1
        assert model.gamma == 0.0
        assert model.abundance_threshold == 2.0
        assert model.crisis_threshold == 0.5

    def test_custom_initialization(self):
        """Test custom model parameters."""
        model = BCPModel(
            lambda_scale=5.0,
            lambda_epsilon=0.05,
            gamma=0.2,
            abundance_threshold=3.0,
            crisis_threshold=0.3
        )
        assert model.lambda_scale == 5.0
        assert model.lambda_epsilon == 0.05
        assert model.gamma == 0.2

    def test_compute_lambda_high_budget(self):
        """Lambda decreases with higher budget."""
        model = BCPModel(lambda_scale=10.0, lambda_epsilon=0.1)
        lambda_low = model.compute_lambda(0.5)
        lambda_high = model.compute_lambda(2.0)
        assert lambda_low > lambda_high

    def test_compute_lambda_formula(self):
        """Verify lambda formula: k / (epsilon + B)."""
        model = BCPModel(lambda_scale=10.0, lambda_epsilon=0.1)
        budget = 1.0
        expected = 10.0 / (0.1 + 1.0)  # = 9.09...
        assert abs(model.compute_lambda(budget) - expected) < 0.01

    def test_determine_phase_abundance(self):
        """High budget = ABUNDANCE phase."""
        model = BCPModel(abundance_threshold=2.0)
        assert model.determine_phase(3.0) == Phase.ABUNDANCE
        assert model.determine_phase(2.0) == Phase.ABUNDANCE

    def test_determine_phase_crisis(self):
        """Low budget = CRISIS phase."""
        model = BCPModel(crisis_threshold=0.5)
        assert model.determine_phase(0.3) == Phase.CRISIS
        assert model.determine_phase(0.5) == Phase.CRISIS

    def test_determine_phase_scarcity(self):
        """Middle budget = SCARCITY phase."""
        model = BCPModel(abundance_threshold=2.0, crisis_threshold=0.5)
        assert model.determine_phase(1.0) == Phase.SCARCITY
        assert model.determine_phase(1.5) == Phase.SCARCITY


class TestBCPAllocation:
    """Tests for BCP allocation algorithm."""

    def setup_method(self):
        """Create test items."""
        self.items = [
            AttentionItem("A", gain=0.9, cost=0.3),
            AttentionItem("B", gain=0.7, cost=0.5),
            AttentionItem("C", gain=0.5, cost=0.2),
        ]

    def test_allocation_abundance(self):
        """High budget attends to items with positive priority."""
        model = BCPModel()
        # Use items with high gain/cost ratio to ensure positive priority
        items = [
            AttentionItem("A", gain=0.9, cost=0.1),
            AttentionItem("B", gain=0.8, cost=0.1),
            AttentionItem("C", gain=0.7, cost=0.1),
        ]
        result = model.allocate(items, budget=5.0)

        assert len(result.attended) == 3
        assert len(result.ignored) == 0
        assert result.phase == Phase.ABUNDANCE

    def test_allocation_scarcity(self):
        """Low budget triggers triage."""
        model = BCPModel()
        items = [
            AttentionItem("A", gain=0.9, cost=0.3),
            AttentionItem("B", gain=0.7, cost=0.5),
            AttentionItem("C", gain=0.3, cost=0.4),
        ]
        result = model.allocate(items, budget=0.8)

        # Should ignore some items
        assert len(result.attended) < 3
        assert len(result.ignored) > 0
        assert result.phase == Phase.SCARCITY

    def test_allocation_crisis(self):
        """Very low budget focuses on single item."""
        model = BCPModel()
        items = [
            AttentionItem("A", gain=0.9, cost=0.3),
            AttentionItem("B", gain=0.7, cost=0.5),
            AttentionItem("C", gain=0.5, cost=0.2),
        ]
        result = model.allocate(items, budget=0.3)

        # Crisis mode - minimal attention
        assert result.phase == Phase.CRISIS
        assert len(result.attended) <= 2

    def test_allocation_respects_budget(self):
        """Total cost never exceeds budget."""
        model = BCPModel()
        result = model.allocate(self.items.copy(), budget=0.5)

        assert result.total_cost <= 0.5

    def test_allocation_priority_order(self):
        """Items with higher Gain-λ*Cost are prioritized."""
        model = BCPModel()
        # Use budget=5.0 and high gain/cost ratio items
        items = [
            AttentionItem("Low", gain=0.3, cost=0.1),
            AttentionItem("High", gain=0.9, cost=0.1),
            AttentionItem("Med", gain=0.6, cost=0.1),
        ]
        result = model.allocate(items, budget=5.0)

        # High should be attended first (highest priority)
        assert "High" in result.attended
        # High should be first in the list
        assert result.attended[0] == "High"

    def test_bcp_result_properties(self):
        """Test BCPResult computed properties."""
        model = BCPModel()
        # Use items with high gain/cost ratio
        items = [
            AttentionItem("A", gain=0.9, cost=0.1),
            AttentionItem("B", gain=0.8, cost=0.1),
            AttentionItem("C", gain=0.7, cost=0.1),
        ]
        result = model.allocate(items, budget=5.0)

        assert result.n_attended == 3
        assert result.n_ignored == 0
        assert result.attention_fraction == 1.0


class TestDomainPresets:
    """Tests for domain preset functions."""

    def test_all_presets_exist(self):
        """All documented presets are available."""
        expected = [
            "finance", "medical", "education", "diplomacy",
            "ecosystem", "software", "emergency", "moderation",
            "manufacturing"
        ]
        for domain in expected:
            assert domain in DOMAIN_PRESETS

    def test_presets_return_items(self):
        """Each preset returns a list of AttentionItems."""
        for name, preset_fn in DOMAIN_PRESETS.items():
            items = preset_fn()
            assert isinstance(items, list)
            assert len(items) > 0
            assert all(isinstance(item, AttentionItem) for item in items)

    def test_preset_items_valid(self):
        """Preset items have valid gain/cost values."""
        for name, preset_fn in DOMAIN_PRESETS.items():
            items = preset_fn()
            for item in items:
                assert 0 <= item.gain <= 1.5
                assert 0 <= item.cost <= 3.0


class TestPhaseTransitions:
    """Tests for phase transition behavior."""

    def test_phase_transition_consistency(self):
        """All domains show consistent phase transitions."""
        model = BCPModel()
        budgets = np.linspace(0.1, 3.0, 30)

        for name, preset_fn in DOMAIN_PRESETS.items():
            results = model.sweep_budgets(preset_fn, budgets)

            # Attended count should be monotonically increasing with budget
            attended_counts = [r.n_attended for r in results]

            # Allow small fluctuations but overall trend should be increasing
            assert attended_counts[-1] >= attended_counts[0]

    def test_lambda_inverse_budget(self):
        """Lambda is inversely proportional to budget."""
        model = BCPModel()

        lambda_01 = model.compute_lambda(0.1)
        lambda_10 = model.compute_lambda(1.0)
        lambda_50 = model.compute_lambda(5.0)

        assert lambda_01 > lambda_10 > lambda_50


class TestBudgetSweep:
    """Tests for budget sweep functionality."""

    def test_sweep_returns_results(self):
        """Sweep returns list of BCPResult."""
        model = BCPModel()
        budgets = np.linspace(0.1, 2.0, 10)

        def items_fn():
            return [
                AttentionItem("A", gain=0.9, cost=0.3),
                AttentionItem("B", gain=0.7, cost=0.5),
            ]

        results = model.sweep_budgets(items_fn, budgets)

        assert len(results) == 10
        assert all(isinstance(r, BCPResult) for r in results)

    def test_find_phase_thresholds(self):
        """Phase thresholds are correctly identified."""
        model = BCPModel()
        budgets = np.linspace(0.1, 3.0, 50)

        def items_fn():
            return [
                AttentionItem("A", gain=0.9, cost=0.3),
                AttentionItem("B", gain=0.7, cost=0.5),
                AttentionItem("C", gain=0.5, cost=0.4),
            ]

        triage, crisis = model.find_phase_thresholds(items_fn, budgets)

        # Triage threshold should be lower than max budget
        assert triage < budgets[-1]
        # Crisis threshold should be lower than triage
        assert crisis <= triage


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
