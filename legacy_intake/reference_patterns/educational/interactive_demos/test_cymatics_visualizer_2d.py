import unittest
import numpy as np
import sys
import os
import matplotlib.pyplot as plt

# Add the parent directory of 'educational' to the Python path
# This allows importing CymaticsVisualizer2D from educational.interactive_demos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from educational.interactive_demos.cymatics_visualizer_2d import CymaticsVisualizer2D

class TestCymaticsVisualizer2D(unittest.TestCase):

    def test_pattern_shape(self):
        """Test if the generated pattern has the correct shape (resolution x resolution)."""
        resolutions = [10, 50, 100]
        for res in resolutions:
            with self.subTest(resolution=res):
                visualizer = CymaticsVisualizer2D(resolution=res)
                # Test with default rectangular pattern
                pattern_rect = visualizer.chladni_pattern_2d(pattern_type="rectangular")
                self.assertEqual(pattern_rect.shape, (res, res))
                
                # Test with polar pattern
                pattern_polar = visualizer.chladni_pattern_2d(pattern_type="polar")
                self.assertEqual(pattern_polar.shape, (res, res))

                # Test with hybrid pattern
                pattern_hybrid = visualizer.chladni_pattern_2d(pattern_type="hybrid")
                self.assertEqual(pattern_hybrid.shape, (res, res))

                # Test with lissajous pattern
                pattern_lissajous = visualizer.chladni_pattern_2d(pattern_type="lissajous")
                self.assertEqual(pattern_lissajous.shape, (res, res))

    def test_default_parameters_instantiation(self):
        """Test if the visualizer instantiates with default parameters without error."""
        try:
            visualizer = CymaticsVisualizer2D()
            # Check a few default parameter values
            self.assertEqual(visualizer.freq_x, 3.0)
            self.assertEqual(visualizer.mode_m, 3)
            self.assertEqual(visualizer.wave_type, "sine")
        except Exception as e:
            self.fail(f"CymaticsVisualizer2D instantiation failed with default parameters: {e}")

    def test_wave_type_transformations(self):
        """Test the apply_wave_type method for different wave types."""
        visualizer = CymaticsVisualizer2D(resolution=10) # Small resolution for quick test
        # Create a simple base pattern (e.g., a sine wave scaled from -1 to 1)
        base_pattern = np.sin(np.linspace(-np.pi, np.pi, 100)).reshape((10,10))

        # Test sine wave (should return pattern as is)
        visualizer.wave_type = "sine"
        transformed_sine = visualizer.apply_wave_type(base_pattern.copy())
        np.testing.assert_array_almost_equal(transformed_sine, base_pattern)

        # Test square wave
        visualizer.wave_type = "square"
        transformed_square = visualizer.apply_wave_type(base_pattern.copy())
        self.assertTrue(np.all(transformed_square <= 1.0) and np.all(transformed_square >= -1.0))
        # Check that signs are preserved or zero
        self.assertTrue(np.all( (np.sign(transformed_square) == np.sign(base_pattern)) | (transformed_square == 0) ))

        # Test triangle wave
        visualizer.wave_type = "triangle"
        transformed_triangle = visualizer.apply_wave_type(base_pattern.copy())
        self.assertTrue(np.all(transformed_triangle <= 1.0) and np.all(transformed_triangle >= -1.0))

        # Test sawtooth wave
        visualizer.wave_type = "sawtooth"
        transformed_sawtooth = visualizer.apply_wave_type(base_pattern.copy())
        self.assertTrue(np.all(transformed_sawtooth < 1.0) and np.all(transformed_sawtooth >= -1.0))

class TestCymaticsVisualizerStateChanges(unittest.TestCase):
    # Define MockSlider and MockRadio at class level for use in multiple tests
    class MockSlider:
        def __init__(self, val, initial_val=None):
            self.val = val
            self.initial_val = initial_val if initial_val is not None else val
        def set_val(self, val):
            self.val = val
        def reset(self):
            self.val = self.initial_val

    class MockRadio:
        def __init__(self):
            self.active_index = -1
        def set_active(self, index):
            self.active_index = index

    def setUp(self):
        self.old_backend = plt.get_backend()
        plt.switch_backend('Agg')
        self.visualizer = CymaticsVisualizer2D(resolution=10)
        # Assign general-purpose mock sliders and radios that can be configured per test or used directly
        self.visualizer.slider_freq_x = TestCymaticsVisualizerStateChanges.MockSlider(self.visualizer.freq_x, initial_val=3.0)
        self.visualizer.slider_freq_y = TestCymaticsVisualizerStateChanges.MockSlider(self.visualizer.freq_y, initial_val=3.0)
        self.visualizer.slider_freq_r = TestCymaticsVisualizerStateChanges.MockSlider(self.visualizer.freq_r, initial_val=2.0)
        self.visualizer.slider_mode_m = TestCymaticsVisualizerStateChanges.MockSlider(self.visualizer.mode_m, initial_val=3)
        self.visualizer.slider_mode_n = TestCymaticsVisualizerStateChanges.MockSlider(self.visualizer.mode_n, initial_val=2)
        self.visualizer.slider_phase = TestCymaticsVisualizerStateChanges.MockSlider(self.visualizer.phase, initial_val=0.0)
        self.visualizer.radio_wave = TestCymaticsVisualizerStateChanges.MockRadio()
        self.visualizer.radio_pattern = TestCymaticsVisualizerStateChanges.MockRadio()

    def tearDown(self):
        plt.switch_backend(self.old_backend)
        plt.close('all') # Close any figures created

    def test_on_slider_change_updates_params(self):
        # Use the class-level MockSlider, no need to redefine here
        # Set specific values for this test if needed
        self.visualizer.slider_freq_x.val = 5.5
        self.visualizer.slider_freq_y.val = 6.5
        self.visualizer.slider_freq_r.val = 7.5
        self.visualizer.slider_mode_m.val = 4
        self.visualizer.slider_mode_n.val = 5
        self.visualizer.slider_phase.val = 1.5
        
        self.visualizer.on_slider_change(None)

        self.assertEqual(self.visualizer.freq_x, 5.5)
        self.assertEqual(self.visualizer.freq_y, 6.5)
        self.assertEqual(self.visualizer.freq_r, 7.5)
        self.assertEqual(self.visualizer.mode_m, 4)
        self.assertEqual(self.visualizer.mode_n, 5)
        self.assertAlmostEqual(self.visualizer.phase, 1.5)

    def test_on_pattern_change(self):
        self.visualizer.on_pattern_change("polar")
        self.assertEqual(self.visualizer.pattern_type, "polar") # Corrected attribute
        self.visualizer.on_pattern_change("hybrid")
        self.assertEqual(self.visualizer.pattern_type, "hybrid") # Corrected attribute

    def test_on_wave_change(self):
        self.visualizer.on_wave_change("square")
        self.assertEqual(self.visualizer.wave_type, "square")
        self.visualizer.on_wave_change("triangle")
        self.assertEqual(self.visualizer.wave_type, "triangle")

    def test_toggle_animation(self):
        initial_state = self.visualizer.animate
        # Mock button object with a 'label' attribute that has a 'set_text' method
        class MockTextLabel:
            def __init__(self, text):
                self._text = text
            def set_text(self, text):
                self._text = text
            def get_text(self): # Added for assertion, though not in original Button.label
                return self._text

        class MockButton: 
            def __init__(self, label_text):
                self.label = MockTextLabel(label_text)
        
        self.visualizer.btn_animate = MockButton("Start Animation")

        self.visualizer.toggle_animation(None) # Event arg not used
        self.assertEqual(self.visualizer.animate, not initial_state)
        self.assertEqual(self.visualizer.btn_animate.label.get_text(), "Stop Animation")

        self.visualizer.toggle_animation(None)
        self.assertEqual(self.visualizer.animate, initial_state)
        self.assertEqual(self.visualizer.btn_animate.label.get_text(), "Start Animation")

    def test_reset_parameters(self):
        # Change some parameters on the visualizer
        self.visualizer.freq_x = 10.0
        self.visualizer.mode_m = 8
        self.visualizer.wave_type = "square"
        self.visualizer.pattern_type = "polar"

        # Default values for assertion
        default_freq_x = 3.0
        default_mode_m = 3
        default_wave_type = "sine"
        default_pattern_type = "rectangular"

        # Mock sliders are already on self.visualizer from setUp,
        # their initial_val is set to the defaults. reset() will use these.
        # Ensure the visualizer's current slider values are different before reset, so we see the change.
        self.visualizer.slider_freq_x.val = self.visualizer.freq_x # e.g., 10.0
        self.visualizer.slider_mode_m.val = self.visualizer.mode_m # e.g., 8
        # (other sliders can be left as setUp or changed too)

        self.visualizer.reset_parameters(None)

        self.assertEqual(self.visualizer.freq_x, default_freq_x)
        self.assertEqual(self.visualizer.mode_m, default_mode_m)
        self.assertEqual(self.visualizer.wave_type, default_wave_type)
        self.assertEqual(self.visualizer.pattern_type, default_pattern_type)
        
        self.assertEqual(self.visualizer.slider_freq_x.val, default_freq_x)
        self.assertEqual(self.visualizer.slider_mode_m.val, default_mode_m)
        self.assertEqual(self.visualizer.radio_wave.active_index, 0)
        self.assertEqual(self.visualizer.radio_pattern.active_index, 0)


if __name__ == '__main__':
    unittest.main() 