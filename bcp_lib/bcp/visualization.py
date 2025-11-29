"""
BCP Visualization - Plotting Utilities
=======================================

Publication-ready visualizations for BCP analysis.
"""

from typing import List, Optional, Tuple, Any, Callable
import numpy as np

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

from .core import BCPModel, BCPResult, AttentionItem


def _check_matplotlib():
    """Raise ImportError if matplotlib not available."""
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install with: pip install matplotlib"
        )


def plot_triage(result: BCPResult,
                title: Optional[str] = None,
                figsize: Tuple[float, float] = (10, 6),
                save_path: Optional[str] = None) -> Any:
    """
    Plot triage results as a bar chart.

    Args:
        result: BCPResult from model.allocate()
        title: Optional plot title
        figsize: Figure size (width, height)
        save_path: Optional path to save figure

    Returns:
        matplotlib figure
    """
    _check_matplotlib()

    fig, ax = plt.subplots(figsize=figsize)

    # Create data
    all_items = result.attended + result.ignored
    colors = ['green'] * len(result.attended) + ['red'] * len(result.ignored)
    y_pos = np.arange(len(all_items))

    # Plot bars
    ax.barh(y_pos, [1] * len(all_items), color=colors, alpha=0.7)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(all_items)
    ax.set_xlim(0, 1.2)

    # Add status labels
    for i, item in enumerate(all_items):
        status = "ATTENDED" if i < len(result.attended) else "IGNORED"
        ax.text(1.05, i, status, va='center', fontsize=10,
                color='green' if status == "ATTENDED" else 'red')

    # Title and labels
    if title is None:
        title = f"BCP Triage: {result.phase.value} (B={result.budget:.2f}, λ={result.lambda_:.2f})"
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_xlabel('Status')

    # Legend
    legend_elements = [
        mpatches.Patch(color='green', alpha=0.7, label=f'Attended ({result.n_attended})'),
        mpatches.Patch(color='red', alpha=0.7, label=f'Ignored ({result.n_ignored})')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_phase_transitions(model: Optional[BCPModel] = None,
                           budget_range: Tuple[float, float] = (0.1, 3.0),
                           n_points: int = 100,
                           figsize: Tuple[float, float] = (12, 5),
                           save_path: Optional[str] = None) -> Any:
    """
    Plot lambda and phase transitions across budget range.

    Args:
        model: BCPModel (uses defaults if None)
        budget_range: (min, max) budget to plot
        n_points: Number of points to sample
        figsize: Figure size
        save_path: Optional path to save figure

    Returns:
        matplotlib figure
    """
    _check_matplotlib()

    if model is None:
        model = BCPModel()

    budgets = np.linspace(budget_range[0], budget_range[1], n_points)

    lambdas = [model.compute_lambda(b) for b in budgets]
    phases = [model.determine_phase(b).value for b in budgets]

    # Phase colors
    phase_colors = {
        'abundance': '#2ecc71',
        'scarcity': '#f1c40f',
        'crisis': '#e74c3c'
    }

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Left: Lambda curve
    ax1.plot(budgets, lambdas, 'b-', linewidth=2)
    ax1.set_xlabel('Budget (B)', fontsize=12)
    ax1.set_ylabel('Metabolic Pressure (λ)', fontsize=12)
    ax1.set_title('λ(B) = k / (ε + B)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Add phase regions to lambda plot
    prev_phase = phases[0]
    start_idx = 0
    for i, phase in enumerate(phases):
        if phase != prev_phase or i == len(phases) - 1:
            ax1.axvspan(budgets[start_idx], budgets[i-1] if i > 0 else budgets[i],
                       alpha=0.15, color=phase_colors.get(prev_phase, 'gray'))
            start_idx = i
            prev_phase = phase

    # Right: Phase diagram
    phase_nums = {'crisis': 0, 'scarcity': 1, 'abundance': 2}
    phase_values = [phase_nums.get(p, 1) for p in phases]

    ax2.fill_between(budgets, phase_values, alpha=0.5, color='blue', step='mid')
    ax2.set_xlabel('Budget (B)', fontsize=12)
    ax2.set_ylabel('Phase', fontsize=12)
    ax2.set_yticks([0, 1, 2])
    ax2.set_yticklabels(['Crisis', 'Scarcity', 'Abundance'])
    ax2.set_title('Phase Transitions', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Add threshold lines
    ax2.axvline(x=model.crisis_threshold, color='red', linestyle='--',
                alpha=0.7, label=f'Crisis (B={model.crisis_threshold})')
    ax2.axvline(x=model.abundance_threshold, color='green', linestyle='--',
                alpha=0.7, label=f'Abundance (B={model.abundance_threshold})')
    ax2.legend(loc='lower right', fontsize=9)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_budget_sweep(items_fn: Callable[[], List[AttentionItem]],
                      model: Optional[BCPModel] = None,
                      budget_range: Tuple[float, float] = (0.1, 3.0),
                      n_points: int = 50,
                      figsize: Tuple[float, float] = (12, 6),
                      save_path: Optional[str] = None) -> Any:
    """
    Plot triage decisions across a budget sweep.

    Args:
        items_fn: Function that returns a list of AttentionItem
        model: BCPModel (uses defaults if None)
        budget_range: (min, max) budget range
        n_points: Number of budget points
        figsize: Figure size
        save_path: Optional path to save figure

    Returns:
        matplotlib figure
    """
    _check_matplotlib()

    if model is None:
        model = BCPModel()

    budgets = np.linspace(budget_range[0], budget_range[1], n_points)

    # Get item names from first call
    sample_items = items_fn()
    item_names = [item.name for item in sample_items]

    # Track each item's status across budgets
    status_matrix = []

    for budget in budgets:
        items = items_fn()
        result = model.allocate(items, budget)
        row = [1 if name in result.attended else 0 for name in item_names]
        status_matrix.append(row)

    status_matrix = np.array(status_matrix)

    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    im = ax.imshow(status_matrix.T, aspect='auto', cmap='RdYlGn',
                   extent=[budgets[0], budgets[-1], -0.5, len(item_names)-0.5])

    ax.set_yticks(range(len(item_names)))
    ax.set_yticklabels(item_names)
    ax.set_xlabel('Budget (B)', fontsize=12)
    ax.set_ylabel('Items', fontsize=12)
    ax.set_title('Attention Allocation Across Budget', fontsize=14, fontweight='bold')

    # Add phase boundaries
    ax.axvline(x=model.crisis_threshold, color='white', linestyle='--', linewidth=2)
    ax.axvline(x=model.abundance_threshold, color='white', linestyle='--', linewidth=2)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, ticks=[0, 1])
    cbar.ax.set_yticklabels(['Ignored', 'Attended'])

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig


def plot_sweep_summary(results: List[BCPResult],
                       budgets: np.ndarray,
                       figsize: Tuple[float, float] = (14, 5),
                       save_path: Optional[str] = None) -> Any:
    """
    Plot summary statistics from a budget sweep.

    Args:
        results: List of BCPResult from model.sweep_budgets()
        budgets: Array of budget values used
        figsize: Figure size
        save_path: Optional path to save figure

    Returns:
        matplotlib figure
    """
    _check_matplotlib()

    n_attended = [r.n_attended for r in results]
    lambdas = [r.lambda_ for r in results]
    phases = [r.phase.value for r in results]

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=figsize)

    # Items attended
    ax1.plot(budgets, n_attended, 'g-', linewidth=2, marker='o', markersize=4)
    ax1.set_xlabel('Budget (B)', fontsize=12)
    ax1.set_ylabel('Items Attended', fontsize=12)
    ax1.set_title('Attention Allocation', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Lambda
    ax2.plot(budgets, lambdas, 'r-', linewidth=2)
    ax2.set_xlabel('Budget (B)', fontsize=12)
    ax2.set_ylabel('Lambda (λ)', fontsize=12)
    ax2.set_title('Metabolic Pressure', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    # Phase distribution
    phase_counts = {}
    for p in phases:
        phase_counts[p] = phase_counts.get(p, 0) + 1

    colors = {'abundance': '#2ecc71', 'scarcity': '#f1c40f', 'crisis': '#e74c3c'}
    ax3.bar(phase_counts.keys(), phase_counts.values(),
            color=[colors.get(p, 'gray') for p in phase_counts.keys()],
            alpha=0.7)
    ax3.set_xlabel('Phase', fontsize=12)
    ax3.set_ylabel('Count', fontsize=12)
    ax3.set_title('Phase Distribution', fontsize=13, fontweight='bold')

    plt.suptitle('BCP Budget Sweep Summary', fontsize=14, fontweight='bold')
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')

    return fig
