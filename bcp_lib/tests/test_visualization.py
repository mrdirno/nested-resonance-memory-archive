"""Render actual BCP figures with Agg and inspect their recorded data.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
"""

import numpy as np
import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from bcp import AttentionItem, BCPModel
from bcp.visualization import plot_budget_sweep, plot_phase_transitions, plot_sweep_summary, plot_triage


@pytest.fixture(autouse=True)
def close_test_figures():
    yield
    plt.close("all")


def items():
    return [AttentionItem("cheap", 1, 0.05), AttentionItem("expensive", 0.2, 5)]


def render(kind, save_path=None):
    if kind == "triage":
        return plot_triage(BCPModel().allocate(items(), 1), save_path=save_path)
    if kind == "phases":
        return plot_phase_transitions(n_points=5, save_path=save_path)
    if kind == "sweep":
        return plot_budget_sweep(items, n_points=5, save_path=save_path)
    budgets = np.array([0.1, 1, 3])
    return plot_sweep_summary(BCPModel().sweep_budgets(items, budgets), budgets, save_path=save_path)


@pytest.mark.parametrize("kind", ["triage", "phases", "sweep", "summary"])
def test_plots_export_real_pngs_and_return_owned_figures(tmp_path, kind):
    destination = tmp_path / (kind + ".png")
    fig = render(kind, destination)
    assert destination.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert destination.stat().st_size > 1000
    assert fig.number in plt.get_fignums()
    fig.canvas.draw()
    pixels = np.asarray(fig.canvas.buffer_rgba())
    assert pixels[:, :, :3].std() > 10
    plt.close(fig)
    assert fig.number not in plt.get_fignums()


@pytest.mark.parametrize("kind", ["triage", "phases", "sweep", "summary"])
def test_failed_export_releases_new_figure(tmp_path, kind):
    existing = plt.figure()
    before = plt.get_fignums()
    with pytest.raises(FileNotFoundError):
        render(kind, tmp_path / "absent" / "plot.png")
    assert plt.get_fignums() == before
    assert existing.number in before


def test_heatmap_rows_match_item_labels_and_preserve_binary_scale():
    fig = plot_budget_sweep(items, budget_range=(0.1, 3), n_points=5)
    ax = fig.axes[0]
    im = ax.images[0]
    assert [label.get_text() for label in ax.get_yticklabels()] == ["cheap", "expensive"]
    assert im.origin == "lower"  # y=0 must display the first named item.
    np.testing.assert_array_equal(im.get_array(), [[0, 1, 1, 1, 1], [0, 0, 0, 0, 0]])
    assert im.get_clim() == (0, 1)
    left, right, _, _ = im.get_extent()
    centers = left + (np.arange(5) + 0.5) * (right - left) / 5
    np.testing.assert_allclose(centers, np.linspace(0.1, 3, 5))
    # An all-ignored sweep must keep the same categorical colors.
    all_ignored = plot_budget_sweep(items, budget_range=(0.001, 0.01), n_points=2)
    assert all_ignored.axes[0].images[0].get_clim() == (0, 1)


def test_phase_regions_cover_full_requested_range_at_actual_thresholds():
    model = BCPModel(crisis_threshold=0.25, abundance_threshold=1.25)
    fig = plot_phase_transitions(model, budget_range=(0.1, 3), n_points=3)
    ax = fig.axes[0]
    bounds = []
    for patch in ax.patches:
        data = ax.transData.inverted().transform(patch.get_transform().transform(patch.get_path().vertices))
        bounds.append([data[:, 0].min(), data[:, 0].max()])
    np.testing.assert_allclose(bounds, [[0.1, 0.25], [0.25, 1.25], [1.25, 3]])
    np.testing.assert_allclose(ax.lines[0].get_ydata(), [model.compute_lambda(b) for b in [0.1, 1.55, 3]])
    # The phase diagram must cross at configured thresholds even with a coarse grid.
    stairs = fig.axes[1].patches[0].get_data()
    np.testing.assert_allclose(stairs.edges, [0.1, 0.25, 1.25, 3])
    np.testing.assert_array_equal(stairs.values, [0, 1, 2])


def test_summary_and_triage_display_allocated_results():
    budgets = np.array([0.1, 1, 3])
    results = BCPModel().sweep_budgets(items, budgets)
    fig = plot_sweep_summary(results, budgets)
    np.testing.assert_array_equal(fig.axes[0].lines[0].get_xdata(), budgets)
    np.testing.assert_array_equal(fig.axes[0].lines[0].get_ydata(), [0, 1, 1])
    assert [bar.get_height() for bar in fig.axes[2].patches] == [1, 1, 1]
    triage = plot_triage(results[1], title="Observed allocation")
    assert triage.axes[0].get_title() == "Observed allocation"
    assert [text.get_text() for text in triage.axes[0].texts] == ["ATTENDED", "IGNORED"]


@pytest.mark.parametrize("kwargs", [{"n_points": 0}, {"n_points": 1}, {"n_points": 2.5}, {"budget_range": (1, 1)}, {"budget_range": (3, 0)}, {"budget_range": (0, float("inf"))}])
def test_invalid_sweep_arguments_do_not_allocate_figures(kwargs):
    before = plt.get_fignums()
    for plot in (plot_phase_transitions, lambda **args: plot_budget_sweep(items, **args)):
        with pytest.raises(ValueError):
            plot(**kwargs)
    assert plt.get_fignums() == before


def test_missing_duplicate_and_changing_item_sets_are_rejected():
    with pytest.raises(ValueError, match="non-empty"):
        plot_budget_sweep(lambda: [], n_points=2)
    with pytest.raises(ValueError, match="unique"):
        plot_budget_sweep(lambda: [AttentionItem("x", 1, 1), AttentionItem("x", 2, 1)], n_points=2)
    samples = iter([[AttentionItem("first", 1, 1)], [AttentionItem("different", 1, 1)]])
    with pytest.raises(ValueError, match="same item names"):
        plot_budget_sweep(lambda: next(samples), n_points=2)
    assert plt.get_fignums() == []


def test_summary_rejects_mismatched_or_nonfinite_budgets():
    results = [BCPModel().allocate(items(), 1)]
    for budgets in ([], [1, 2], [float("nan")], [2], [[1]]):
        with pytest.raises(ValueError):
            plot_sweep_summary(results, np.array(budgets))
    with pytest.raises(ValueError):
        plot_sweep_summary([], np.array([]))
    assert plt.get_fignums() == []
