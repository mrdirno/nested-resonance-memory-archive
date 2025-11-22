#!/usr/bin/env python3

import sys
import os

# Ensure the script can find the angular_standing_wave_analysis module
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
sys.path.append(os.path.join(PROJECT_ROOT, "research/simulations/implementations/core_versions"))

from angular_standing_wave_analysis import AngularStandingWaveAnalyzer, SimulationParameters
import numpy as np


def test_angular_analysis():
    print("🧪 Testing Angular Analysis with Synthetic Standing Waves")
    print("=" * 60)

    # Create analyzer
    analyzer = AngularStandingWaveAnalyzer(grid_size=16, box_size=500.0, subsample_size=10000)

    # Generate synthetic data with standing waves
    print("🔧 Generating synthetic data with standing waves...")
    synthetic_positions = analyzer._generate_synthetic_data()

    print(f"✅ Generated {len(synthetic_positions):,} synthetic positions")

    # Run angular analysis
    print("\n🔍 Running angular standing wave search...")
    results = analyzer.angular_standing_wave_search(synthetic_positions, n_angles=50)

    print("\n📊 Results:")
    print(f"   Best coherence score: {results['best_coherence']:.4f}")
    print(f"   Number of orientations tested: {results['n_angles_tested']}")

    if results["best_orientation"]:
        direction = results["best_orientation"]["direction"]
        print(f"   Best orientation: [{direction[0]:.3f}, {direction[1]:.3f}, {direction[2]:.3f}]")

    # Test top 3 orientations with detailed analysis
    if len(results["orientations"]) >= 3:
        print("\n🎯 Detailed analysis of top 3 orientations:")

        for i in range(3):
            orientation = results["orientations"][i]
            direction = np.array(orientation["direction"])
            coherence = results["coherence_scores"][i]

            print(f"\n   Orientation {i+1}:")
            print(f"     Direction: [{direction[0]:.3f}, {direction[1]:.3f}, {direction[2]:.3f}]")
            print(f"     Coherence score: {coherence:.4f}")

            # Detailed analysis
            detailed = analyzer.targeted_directional_analysis(synthetic_positions, direction)

            n_coherent = detailed.get("n_coherent_modes", 0)
            max_coherence = detailed.get("max_coherence", 0.0)

            print(f"     Coherent modes: {n_coherent}")
            print(f"     Max coherence strength: {max_coherence:.4f}")

            # Show coherent modes if any
            if "coherent_modes" in detailed and len(detailed["coherent_modes"]) > 0:
                print("     Coherent wavelengths:")
                for mode in detailed["coherent_modes"][:3]:  # Show top 3
                    wavelength = mode.get("wavelength_mpc_h", 0)
                    phase_std = mode.get("phase_std", 0)
                    print(f"       {wavelength:.1f} Mpc/h (phase_std: {phase_std:.3f})")

    # Summary
    total_coherent = sum([results["coherence_scores"][i] for i in range(min(5, len(results["coherence_scores"])))])
    print("\n📈 Summary:")
    print(f"   Total coherence (top 5): {total_coherent:.4f}")
    print(f"   Average coherence: {np.mean(results['coherence_scores']):.4f}")
    print(f"   Coherence range: {np.min(results['coherence_scores']):.4f} - {np.max(results['coherence_scores']):.4f}")

    # Check if we detected the synthetic standing wave
    detected = total_coherent > 2.7  # Threshold for detection
    print(f"   Standing wave detected: {detected}")

    return results

if __name__ == "__main__":
    results = test_angular_analysis()
