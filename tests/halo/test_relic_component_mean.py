"""Checks for the first of two null-safety fixes made to
experiments/halo/relic_component_decomposition.py with Ring 30's results
(analysis/2026-09-22_relic_intervention.md, "Results").

The frozen scorer writes a value it could not form (NaN or inf) as JSON null. The report's mean()
already dropped NaN; it now drops null the same way, and the two stranger means that called np.mean
directly now call mean(). The recorded lag-two row is null in one lag-one-eligible epoch of two
intervened runs, which crashed the report. These tests pin mean() only. The second fix (None for
the recorded S and p of a run the scorer left unmeasurable) lives in main() and is covered by the
byte comparisons in the Results, not here: on the two null-free inputs (the Ring 29 control and the
Ring 30 identity arm) the output is byte-identical before and after the change. The two
intervened arms each hold a null, so the unchanged script stops on both and has no earlier output
to compare against.

Author: Aldrin Payopay <aldrin.gdf@gmail.com> - GPL-3.0-only
"""
import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'experiments', 'halo'))
rc = pytest.importorskip('relic_component_decomposition')


def test_mean_drops_null_like_nan():
    assert rc.mean([1.0, None, float('nan'), 3.0]) == 2.0


def test_mean_of_nothing_available_is_nan():
    assert math.isnan(rc.mean([None, float('nan')]))
    assert math.isnan(rc.mean([]))


def test_mean_unchanged_without_null():
    xs = [0.1, -0.25, 0.3125]
    assert rc.mean(xs) == float(sum(xs) / len(xs))


def test_nested_mean_of_an_all_null_row_is_dropped():
    # the stranger mean of an epoch whose row is all null is NaN, and the outer mean skips it
    rows = [[0.2, 0.4], [None, None], [0.0, 0.2]]
    assert rc.mean([rc.mean(r) for r in rows]) == pytest.approx(0.2)
