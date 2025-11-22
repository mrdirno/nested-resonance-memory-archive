import unittest
import numpy as np
import sys
import os
import matplotlib.pyplot as plt # Add for backend switching

# Add the parent directory of 'educational' to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from educational.interactive_demos.cymatics_visualizer_3d import CosmicCymaticsVisualizer3D

class TestCosmicCymaticsVisualizer3D(unittest.TestCase):

    def test_pattern_shape_and_type(self):
        """Test if the generated 3D pattern has the correct shape and numeric type."""
        resolutions = [10, 20] # Keep resolutions small for faster tests
        for res in resolutions:
            with self.subTest(resolution=res):
                visualizer = CosmicCymaticsVisualizer3D(grid_size=res)
                pattern = visualizer.calculate_3d_cymatics_pattern()
                self.assertEqual(pattern.shape, (res, res, res))
                self.assertTrue(np.issubdtype(pattern.dtype, np.number), "Pattern data type should be numeric.")

    def test_default_parameters_instantiation(self):
        """Test if the 3D visualizer instantiates with default parameters without error."""
        try:
            visualizer = CosmicCymaticsVisualizer3D(grid_size=10) # Use small grid size
            # Check a few default parameter values from visualizer.params
            self.assertEqual(visualizer.params["frequency"], 80.0)
            self.assertEqual(visualizer.params["mode_m"], 3)
            self.assertEqual(visualizer.params["amplitude"], 1.0)
        except Exception as e:
            self.fail(f"CosmicCymaticsVisualizer3D instantiation failed: {e}")

    def test_pattern_value_range(self):
        """Test if pattern values are within a reasonable range given amplitude and damping."""
        visualizer = CosmicCymaticsVisualizer3D(grid_size=10)
        visualizer.params["amplitude"] = 2.0
        pattern = visualizer.calculate_3d_cymatics_pattern()
        # With amplitude, values can exceed +/- 1 before damping, but should be scaled by amplitude
        # Max possible value of spatial_pattern * temporal is 1. Damping is <=1.
        # So, abs(pattern) should be <= amplitude.
        self.assertTrue(np.all(np.abs(pattern) <= visualizer.params["amplitude"] + 1e-9), # Add tolerance for float precision
                        f"Pattern values exceed expected max amplitude. Max val: {np.max(np.abs(pattern))}")

    def test_frequency_changes_pattern(self):
        """Test that changing frequency affects the pattern (indirect test)."""
        viz1 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz1.params["frequency"] = 50.0
        pattern1 = viz1.calculate_3d_cymatics_pattern()

        viz2 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz2.params["frequency"] = 100.0 # Different frequency
        pattern2 = viz2.calculate_3d_cymatics_pattern()

        # Patterns should be different if frequency is different
        self.assertFalse(np.array_equal(pattern1, pattern2), "Changing frequency did not alter the pattern.")

    def test_mode_m_changes_pattern(self):
        """Test that changing mode_m affects the pattern."""
        viz1 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz1.params["mode_m"] = 2
        pattern1 = viz1.calculate_3d_cymatics_pattern()

        viz2 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz2.params["mode_m"] = 5 
        pattern2 = viz2.calculate_3d_cymatics_pattern()
        self.assertFalse(np.array_equal(pattern1, pattern2), "Changing mode_m did not alter the pattern.")

    def test_mode_n_changes_pattern(self):
        """Test that changing mode_n affects the pattern."""
        viz1 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz1.params["mode_n"] = 2
        pattern1 = viz1.calculate_3d_cymatics_pattern()

        viz2 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz2.params["mode_n"] = 5 
        pattern2 = viz2.calculate_3d_cymatics_pattern()
        self.assertFalse(np.array_equal(pattern1, pattern2), "Changing mode_n did not alter the pattern.")

    def test_mode_p_changes_pattern(self):
        """Test that changing mode_p affects the pattern."""
        viz1 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz1.params["mode_p"] = 1
        pattern1 = viz1.calculate_3d_cymatics_pattern()

        viz2 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz2.params["mode_p"] = 3 
        pattern2 = viz2.calculate_3d_cymatics_pattern()
        self.assertFalse(np.array_equal(pattern1, pattern2), "Changing mode_p did not alter the pattern.")

    def test_damping_changes_pattern(self):
        """Test that changing damping affects the pattern and its scale."""
        viz_low_damp = CosmicCymaticsVisualizer3D(grid_size=10)
        viz_low_damp.params["damping"] = 0.1
        pattern_low_damp = viz_low_damp.calculate_3d_cymatics_pattern()

        viz_high_damp = CosmicCymaticsVisualizer3D(grid_size=10)
        viz_high_damp.params["damping"] = 1.0 
        pattern_high_damp = viz_high_damp.calculate_3d_cymatics_pattern()

        self.assertFalse(np.array_equal(pattern_low_damp, pattern_high_damp), "Changing damping did not alter the pattern.")
        # Higher damping should generally result in smaller absolute values overall
        self.assertTrue(np.mean(np.abs(pattern_high_damp)) < np.mean(np.abs(pattern_low_damp)),
                        "Higher damping did not reduce mean pattern amplitude as expected.")

    def test_time_changes_pattern(self):
        """Test that changing time affects the pattern due to temporal component."""
        viz_t0 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz_t0.params["time"] = 0.0
        viz_t0.params["frequency"] = 1.0 # Use a non-zero frequency
        viz_t0.params["phase"] = 0.0      # Explicitly set phase to 0 for predictability
        pattern_t0 = viz_t0.calculate_3d_cymatics_pattern()

        viz_t1 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz_t1.params["time"] = 0.5 # Changed time to 0.5 for cos(pi) = -1
        viz_t1.params["frequency"] = 1.0
        viz_t1.params["phase"] = 0.0
        pattern_t1 = viz_t1.calculate_3d_cymatics_pattern()

        self.assertFalse(np.array_equal(pattern_t0, pattern_t1), "Changing time from 0.0 to 0.5 did not alter the pattern when frequency=1.0.")

        # Test with another time that should also be different
        viz_t2 = CosmicCymaticsVisualizer3D(grid_size=10)
        viz_t2.params["time"] = 0.25 # cos(pi/2) = 0
        viz_t2.params["frequency"] = 1.0
        viz_t2.params["phase"] = 0.0
        pattern_t2 = viz_t2.calculate_3d_cymatics_pattern()
        self.assertFalse(np.array_equal(pattern_t0, pattern_t2), "Changing time from 0.0 to 0.25 did not alter the pattern.")
        self.assertFalse(np.array_equal(pattern_t1, pattern_t2), "Pattern for time 0.5 was same as for time 0.25.")

class TestCosmicCymaticsVisualizer3DStateChanges(unittest.TestCase):
    class MockSlider:
        def __init__(self, val, initial_val=None):
            self.val = val
            self.initial_val = initial_val if initial_val is not None else val
        def set_val(self, val):
            self.val = val
        def reset(self):
            self.val = self.initial_val

    class MockLabel:
        def __init__(self, text): self._text = text
        def get_text(self): return self._text

    class MockCheckButtons:
        def __init__(self, labels, actives):
            self.labels = [TestCosmicCymaticsVisualizer3DStateChanges.MockLabel(label) for label in labels]
            self._actives = list(actives) # Store internal state
            # Ensure get_status uses the instance's current _actives state
            self.get_status = lambda: self._actives 
        def set_active(self, idx, status):
            if 0 <= idx < len(self._actives):
                self._actives[idx] = status

    def setUp(self):
        self.old_backend = plt.get_backend()
        plt.switch_backend('Agg')
        self.visualizer = CosmicCymaticsVisualizer3D(grid_size=10) 
        
        # Setup mock UI elements that the visualizer's methods might interact with
        self.visualizer.slider_frequency = TestCosmicCymaticsVisualizer3DStateChanges.MockSlider(self.visualizer.params["frequency"], self.visualizer.params["frequency"])
        self.visualizer.slider_mode_m = TestCosmicCymaticsVisualizer3DStateChanges.MockSlider(self.visualizer.params["mode_m"], self.visualizer.params["mode_m"])
        self.visualizer.slider_mode_n = TestCosmicCymaticsVisualizer3DStateChanges.MockSlider(self.visualizer.params["mode_n"], self.visualizer.params["mode_n"])
        self.visualizer.slider_mode_p = TestCosmicCymaticsVisualizer3DStateChanges.MockSlider(self.visualizer.params["mode_p"], self.visualizer.params["mode_p"])
        self.visualizer.slider_amplitude = TestCosmicCymaticsVisualizer3DStateChanges.MockSlider(self.visualizer.params["amplitude"], self.visualizer.params["amplitude"])
        self.visualizer.slider_slice_z = TestCosmicCymaticsVisualizer3DStateChanges.MockSlider(self.visualizer.params["slice_z"], self.visualizer.params["slice_z"])

        # For _update_display_options
        # The method expects self.display_options_btns.labels and self.display_options_btns.get_status()
        # self.display_options_btns.labels should be a list of objects with get_text()
        # self.display_options_btns.get_status() should return a list of booleans
        labels = ["Show Galaxies", "Show Nodes"]
        actives = [self.visualizer.params["show_galaxies"], self.visualizer.params["show_nodes"]]
        self.visualizer.display_options_btns = TestCosmicCymaticsVisualizer3DStateChanges.MockCheckButtons(labels, actives)

    def tearDown(self):
        plt.switch_backend(self.old_backend)
        plt.close('all')

    def test_update_frequency(self):
        self.visualizer._update_frequency(100.0)
        self.assertEqual(self.visualizer.params["frequency"], 100.0)

    def test_update_mode_m(self):
        self.visualizer._update_mode_m(5)
        self.assertEqual(self.visualizer.params["mode_m"], 5)

    def test_update_mode_n(self):
        self.visualizer._update_mode_n(6)
        self.assertEqual(self.visualizer.params["mode_n"], 6)

    def test_update_mode_p(self):
        self.visualizer._update_mode_p(3)
        self.assertEqual(self.visualizer.params["mode_p"], 3)
    
    def test_update_amplitude(self):
        self.visualizer._update_amplitude(2.5)
        self.assertEqual(self.visualizer.params["amplitude"], 2.5)

    def test_update_slice(self):
        self.visualizer._update_slice(0.75)
        self.assertEqual(self.visualizer.params["slice_z"], 0.75)

    def test_update_display_options(self):
        # Simulate check button status: Show Galaxies=False, Show Nodes=True
        # _update_display_options uses label text to update params
        self.visualizer.display_options_btns._actives = [False, True] 
        self.visualizer._update_display_options("Show Galaxies") # Label clicked (irrelevant for this mock)
        self.assertEqual(self.visualizer.params["show_galaxies"], False)
        self.assertEqual(self.visualizer.params["show_nodes"], True)

        self.visualizer.display_options_btns._actives = [True, False]
        self.visualizer._update_display_options("Show Nodes")
        self.assertEqual(self.visualizer.params["show_galaxies"], False)
        self.assertEqual(self.visualizer.params["show_nodes"], False)

    def test_reset_parameters(self):
        # Change some params
        self.visualizer.params["frequency"] = 200.0
        self.visualizer.params["mode_m"] = 5
        self.visualizer.params["show_galaxies"] = False

        # Store initial defaults from CosmicCymaticsVisualizer3D.__init__
        default_freq = 80.0
        default_mode_m = 3
        default_show_galaxies = True
        
        # Ensure sliders reflect changed values before reset, so their .reset() is meaningful
        self.visualizer.slider_frequency.val = 200.0
        self.visualizer.slider_mode_m.val = 5
        # Ensure check buttons reflect changed state before reset
        self.visualizer.display_options_btns._actives = [False, self.visualizer.params["show_nodes"]]

        self.visualizer._reset_parameters(None) # Event arg not used

        self.assertEqual(self.visualizer.params["frequency"], default_freq)
        self.assertEqual(self.visualizer.params["mode_m"], default_mode_m)
        self.assertEqual(self.visualizer.params["show_galaxies"], default_show_galaxies)
        
        # Check if UI mock elements were told to reset
        self.assertEqual(self.visualizer.slider_frequency.val, default_freq)
        self.assertEqual(self.visualizer.slider_mode_m.val, default_mode_m)
        # self.visualizer.display_options_btns.set_active should have been called for each button
        # This mock for CheckButtons is a bit basic. A real one would have its status updated.
        # The source code for _reset_parameters calls self.display_options_btns.set_active(i, True/False)
        # My current MockCheckButtons does not use set_active to change _actives for simplicity.
        # For now, checking the param is the most important.


if __name__ == '__main__':
    unittest.main() 