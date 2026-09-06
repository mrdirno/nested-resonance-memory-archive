"""Analytical correctness checks for the recurrence statistic, not physics data.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0-only
"""
import json
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "analysis"))
from halo_memory_estimator import Geometry, analytical_pair, exact_interval


class EstimatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads((ROOT / "archive/reports/2026-09-05_halo_memory_estimator_design.json").read_text())
        cls.geometry = Geometry(cls.design)

    def test_center_and_group_are_exact_and_preserve_support(self):
        g = self.geometry
        self.assertEqual(3, g.q[15, 15, 15])
        self.assertEqual(g.q[0, 0, 0], g.q[-1, -1, -1])
        identity = np.arange(g.mask.sum())
        self.assertTrue(np.array_equal(g.rotations[0], identity))
        self.assertEqual(24, len({rotation.tobytes() for rotation in g.rotations}))
        for rotation in g.rotations:
            self.assertTrue(np.array_equal(np.sort(rotation), identity))
            self.assertTrue(np.array_equal(g.shell[rotation], g.shell))
        # Closure matters to the exact orientation-rank reference, not just count.
        members = {rotation.tobytes() for rotation in g.rotations}
        for a in g.rotations:
            for b in g.rotations:
                self.assertIn(a[b].tobytes(), members)

    def test_closed_form_radial_profiles_are_unmeasurable(self):
        z, y, x = np.indices((32, 32, 32), dtype=float)
        r2 = (x - 15.5) ** 2 + (y - 15.5) ** 2 + (z - 15.5) ** 2
        for density in (np.ones_like(r2), np.exp(-r2 / 18), (1 + r2 / 4) ** -2.5):
            with self.subTest(profile=float(density.sum())):
                field = self.geometry.field(density)
                self.assertFalse(field["eligible"])
                self.assertIn("insufficient_angular_variance", field["reasons"])
                measured = self.geometry.comparison(field, field)
                self.assertIsNone(measured["correlation"])
                self.assertIsNone(measured["alarm"])

    def test_empty_and_concentrated_support_do_not_become_zero_scores(self):
        self.assertFalse(self.geometry.field(np.zeros((32,) * 3))["eligible"])
        point = np.zeros((32,) * 3)
        point[17, 18, 19] = 1
        field = self.geometry.field(point)
        self.assertIn("insufficient_residual_support", field["reasons"])
        self.assertIsNone(self.geometry.comparison(field, field)["correlation"])

    def test_invalid_density_is_rejected(self):
        for value in (-1, np.nan, np.inf):
            density = np.ones((32,) * 3)
            density[1, 2, 3] = value
            with self.assertRaises(ValueError):
                self.geometry.field(density)

    def test_analytical_injection_preserves_shell_mass_and_known_correlation(self):
        g = self.geometry
        envelope = 1 / (1 + g.q.astype(float) / 100)
        for family in ("iid", "smooth_sigma2"):
            a, b = analytical_pair(g, envelope, np.random.default_rng(912), family, 0.3)
            for density in (a, b):
                self.assertGreaterEqual(float(density.min()), 0)
                np.testing.assert_allclose(g.radial_envelope(density), envelope, rtol=1e-12, atol=0)
            measured = g.comparison(g.field(a), g.field(b))
            self.assertTrue(measured["eligible"])
            self.assertAlmostEqual(0.3, measured["correlation"], places=10)

    def test_independent_null_is_not_orthogonalized_and_static_figure_repeats(self):
        g = self.geometry
        a, b = analytical_pair(g, np.ones((32,) * 3), np.random.default_rng(913), "smooth_sigma2")
        af, bf = g.field(a), g.field(b)
        self.assertGreater(abs(g.comparison(af, bf)["correlation"]), 1e-8)
        repeated = g.comparison(af, af)
        self.assertAlmostEqual(1, repeated["correlation"], places=12)
        self.assertTrue(repeated["alarm"])

    def test_full_rotation_orbit_has_at_most_one_rank_exceedance(self):
        g = self.geometry
        a, b = analytical_pair(g, np.ones((32,) * 3), np.random.default_rng(914), "smooth_sigma2")
        af, bf = g.field(a), g.field(b)
        ranks = []
        for rotation in g.rotations:
            moved = {**bf, "residual": bf["residual"][rotation]}
            ranks.append(g.comparison(af, moved)["orientation_rank"])
        self.assertLessEqual(sum(rank <= 0.05 for rank in ranks), 1)
        self.assertGreaterEqual(min(ranks), 1 / 24)

    def test_exact_binomial_interval_keeps_uncertainty_at_extremes(self):
        self.assertEqual([0.0, 1.0], exact_interval(0, 0))
        low, high = exact_interval(0, 100)
        self.assertEqual(0, low)
        self.assertGreater(high, 0.03)
        low, high = exact_interval(100, 100)
        self.assertLess(low, 0.97)
        self.assertEqual(1, high)


if __name__ == "__main__":
    unittest.main()
