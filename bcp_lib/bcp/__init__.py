"""
Budget-Constrained Perception (BCP) Library
============================================

A universal framework for attention allocation under resource constraints.

The BCP equation:
    V(a) = E[Gain(a)] - λ(B) × Cost(a) - γ × Complexity

Where:
    - V(a): Value of action a
    - E[Gain(a)]: Expected benefit if attended to
    - λ(B) = k / (ε + B): Metabolic pressure (inverse of budget)
    - Cost(a): Resource cost to attend
    - γ: Complexity penalty coefficient

This library provides tools for:
    - Modeling attention allocation across domains
    - Predicting phase transitions (Abundance → Scarcity → Crisis)
    - Real-time system monitoring with BCP-based triage

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

__version__ = "1.0.0"
__author__ = "Aldrin Payopay"
__email__ = "aldrin.gdf@gmail.com"

from .core import (
    AttentionItem,
    BCPModel,
    Phase,
    BCPResult,
)

from .monitor import BCPMonitor

from .domains import (
    create_generic_scenario,
    DOMAIN_PRESETS,
)

# Visualization (optional - requires matplotlib)
try:
    from .visualization import (
        plot_triage,
        plot_phase_transitions,
        plot_budget_sweep,
        plot_sweep_summary,
    )
    _VIZ_AVAILABLE = True
except ImportError:
    _VIZ_AVAILABLE = False

__all__ = [
    "AttentionItem",
    "BCPModel",
    "Phase",
    "BCPResult",
    "BCPMonitor",
    "create_generic_scenario",
    "DOMAIN_PRESETS",
]

if _VIZ_AVAILABLE:
    __all__.extend([
        "plot_triage",
        "plot_phase_transitions",
        "plot_budget_sweep",
        "plot_sweep_summary",
    ])
