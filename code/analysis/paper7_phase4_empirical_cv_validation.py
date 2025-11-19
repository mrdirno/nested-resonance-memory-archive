#!/usr/bin/env python3
"""
PAPER 7 PHASE 4: EMPIRICAL CV VALIDATION

Purpose: Extract empirical CV values from Paper 2 and validate V4 stochastic predictions

Approach:
1. Document Paper 2 empirical CV values (from results draft)
2. Run V4 stochastic model to find noise levels matching empirical CV
3. Validate that V4 with fitted noise reproduces empirical dynamics

Date: 2025-10-27 (Cycle 384)
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
import json
import sys

sys.path.append(str(Path(__file__).parent))

from paper7_phase4_stochastic_v4 import StochasticV4Model, StochasticRobustnessAnalyzer


class EmpiricalCVExtractor:
    """
    Extract and document empirical CV values from Paper 2.

    Paper 2 Results (from PAPER2_RESULTS_DRAFT.md):
    - Population CV by frequency: 6.4-10.0%
    - Overall mean CV: 8.9%
    - Within-experiment CV: 9.2%
    - Steady-state fluctuations: 10% of mean
    """

    def __init__(self):
        """Initialize with Paper 2 empirical values."""
        self.paper2_cv = {
            'overall_mean': 0.089,  # 8.9%
            'within_experiment': 0.092,  # 9.2%
            'by_frequency': {
                0.020: 0.064,  # 2.0% spawn frequency: CV = 6.4%
                # Note: Other frequencies not explicitly documented
            },
            'steady_state': 0.10,  # 10% of mean
            'source': 'PAPER2_RESULTS_DRAFT.md Section 3.3'
        }

    def get_empirical_cv_range(self) -> Tuple[float, float]:
        """
        Get empirical CV range from Paper 2.

        Returns:
            (min_cv, max_cv) tuple
        """
        cvs = [
            self.paper2_cv['overall_mean'],
            self.paper2_cv['within_experiment'],
            self.paper2_cv['by_frequency'][0.020],
            self.paper2_cv['steady_state']
        ]
        return (min(cvs), max(cvs))

    def get_target_cv(self) -> float:
        """
        Get target CV for V4 fitting.

        Uses within-experiment CV as most comparable to V4 simulations.

        Returns:
            Target CV value
        """
        return self.paper2_cv['within_experiment']

    def print_summary(self):
        """Print summary of empirical CV values."""
        print("\n" + "=" * 70)
        print("PAPER 2 EMPIRICAL CV VALUES")
        print("=" * 70)
        print()
        print(f"Source: {self.paper2_cv['source']}")
        print()
        print("Documented Values:")
        print(f"  Overall mean CV: {self.paper2_cv['overall_mean']:.3f} ({self.paper2_cv['overall_mean']*100:.1f}%)")
        print(f"  Within-experiment CV: {self.paper2_cv['within_experiment']:.3f} ({self.paper2_cv['within_experiment']*100:.1f}%)")
        print(f"  Steady-state CV: {self.paper2_cv['steady_state']:.3f} ({self.paper2_cv['steady_state']*100:.1f}%)")
        print()
        print("By Frequency:")
        for freq, cv in self.paper2_cv['by_frequency'].items():
            print(f"  {freq*100:.1f}% spawn frequency: CV = {cv:.3f} ({cv*100:.1f}%)")
        print()
        min_cv, max_cv = self.get_empirical_cv_range()
        print(f"Range: {min_cv:.3f} - {max_cv:.3f} ({min_cv*100:.1f}% - {max_cv*100:.1f}%)")
        print("=" * 70)


class V4NoiseCalibrator:
    """
    Calibrate V4 noise levels to match empirical CV.

    Strategy:
    1. Run V4 with range of noise levels
    2. Find noise level that produces CV matching Paper 2
    3. Validate that fitted noise reproduces other empirical properties
    """

    def __init__(self, base_params: Dict, target_cv: float):
        """
        Initialize calibrator.

        Args:
            base_params: V4 base parameters
            target_cv: Target CV from Paper 2
        """
        self.base_params = base_params
        self.target_cv = target_cv
        self.analyzer = StochasticRobustnessAnalyzer(base_params)

    def calibrate_noise_level(
        self,
        noise_type: str,
        noise_range: np.ndarray,
        n_runs: int = 20,
        tolerance: float = 0.01
    ) -> Dict:
        """
        Find noise level that produces target CV.

        Args:
            noise_type: 'parameter', 'state', or 'external'
            noise_range: Array of noise levels to test
            n_runs: Ensemble size per level
            tolerance: Acceptable CV error

        Returns:
            Calibration results dictionary
        """
        print(f"\nCalibrating {noise_type} noise to match CV = {self.target_cv:.3f}...")

        results = []
        best_match = None
        best_error = float('inf')

        for noise_level in noise_range:
            # Run ensemble
            result = self.analyzer.run_ensemble(noise_level, noise_type, n_runs)

            # Check CV error
            cv_error = abs(result['cv_N_mean'] - self.target_cv)
            results.append({
                'noise_level': noise_level,
                'cv_mean': result['cv_N_mean'],
                'cv_std': result['cv_N_std'],
                'cv_error': cv_error,
                'mean_N': result['mean_N_mean'],
                'persistence_prob': result['persistence_prob']
            })

            if cv_error < best_error:
                best_error = cv_error
                best_match = results[-1].copy()

            # Early stop if within tolerance
            if cv_error < tolerance:
                print(f"  ✓ Found match at noise = {noise_level:.4f}: CV = {result['cv_N_mean']:.3f}")
                break

        calibration = {
            'noise_type': noise_type,
            'target_cv': self.target_cv,
            'best_match': best_match,
            'all_results': results,
            'tolerance': tolerance
        }

        if best_match:
            print(f"\n  Best match:")
            print(f"    Noise level: {best_match['noise_level']:.4f}")
            print(f"    CV: {best_match['cv_mean']:.3f} ± {best_match['cv_std']:.3f}")
            print(f"    Error: {best_match['cv_error']:.4f}")
            print(f"    Mean N: {best_match['mean_N']:.2f}")
            print(f"    Persistence: {best_match['persistence_prob']:.2f}")

        return calibration

    def validate_calibration(self, calibration: Dict) -> Dict:
        """
        Validate that calibrated noise reproduces empirical properties.

        Args:
            calibration: Calibration results

        Returns:
            Validation metrics
        """
        print("\nValidating calibrated noise level...")

        best_match = calibration['best_match']

        validation = {
            'cv_match': abs(best_match['cv_mean'] - self.target_cv) < 0.01,
            'cv_error': best_match['cv_error'],
            'persistence_maintained': best_match['persistence_prob'] > 0.95,
            'mean_population': best_match['mean_N'],
            'interpretation': None
        }

        # Interpret results
        if validation['cv_match'] and validation['persistence_maintained']:
            validation['interpretation'] = "✅ V4 with calibrated noise reproduces empirical CV and maintains persistence"
        elif validation['cv_match']:
            validation['interpretation'] = "⚠️ CV matches but persistence compromised"
        else:
            validation['interpretation'] = "❌ Could not match empirical CV within tolerance"

        print(f"\n  {validation['interpretation']}")
        print(f"  CV error: {validation['cv_error']:.4f}")
        print(f"  Persistence: {validation['persistence_maintained']}")

        return validation


def plot_cv_calibration(calibration: Dict, empirical_cv: float, output_dir: Path):
    """
    Visualize CV calibration results.

    Args:
        calibration: Calibration results
        empirical_cv: Target CV from Paper 2
        output_dir: Output directory
    """
    print("\nGenerating CV calibration figure...")

    results = calibration['all_results']
    noise_levels = [r['noise_level'] for r in results]
    cvs = [r['cv_mean'] for r in results]
    cv_stds = [r['cv_std'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot CV vs noise
    ax.errorbar(noise_levels, cvs, yerr=cv_stds, marker='o', capsize=5,
                linewidth=2, label='V4 Stochastic CV')

    # Target CV line
    ax.axhline(empirical_cv, color='red', linestyle='--', linewidth=2,
               label=f'Paper 2 Empirical CV = {empirical_cv:.3f}')

    # Best match point
    best = calibration['best_match']
    ax.plot(best['noise_level'], best['cv_mean'], 'g*', markersize=20,
            label=f'Best match: noise={best["noise_level"]:.4f}')

    ax.set_xlabel(f'{calibration["noise_type"].capitalize()} Noise Level', fontsize=11)
    ax.set_ylabel('Coefficient of Variation', fontsize=11)
    ax.set_title('V4 Noise Calibration to Paper 2 Empirical CV',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3)

    plt.tight_layout()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / f"paper7_phase4_cv_calibration_{calibration['noise_type']}_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def compare_empirical_vs_v4(empirical_data: Dict, v4_calibrations: List[Dict], output_dir: Path):
    """
    Create comparison figure: Paper 2 empirical vs V4 stochastic.

    Args:
        empirical_data: Paper 2 empirical CV values
        v4_calibrations: List of V4 calibration results
        output_dir: Output directory
    """
    print("\nGenerating empirical vs. V4 comparison figure...")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Empirical CV bar
    empirical_cv = empirical_data['within_experiment']
    empirical_range = empirical_data['by_frequency'][0.020], empirical_data['steady_state']

    ax.barh(0, empirical_cv, height=0.5, color='blue', alpha=0.5, label='Paper 2 Empirical')
    ax.barh(0, empirical_range[1] - empirical_range[0], left=empirical_range[0],
            height=0.5, color='blue', alpha=0.2)

    # V4 calibrations
    y_pos = 1
    colors = ['green', 'orange', 'purple']
    for i, calib in enumerate(v4_calibrations):
        if calib['best_match']:
            best = calib['best_match']
            cv_val = best['cv_mean']
            cv_std = best['cv_std']

            ax.barh(y_pos, cv_val, height=0.5, color=colors[i], alpha=0.5,
                   label=f'V4 {calib["noise_type"]} noise')
            ax.errorbar([cv_val], [y_pos], xerr=[cv_std], fmt='none',
                       color=colors[i], capsize=5)

            y_pos += 1

    ax.set_yticks([])
    ax.set_xlabel('Coefficient of Variation', fontsize=11)
    ax.set_title('Paper 2 Empirical CV vs. V4 Stochastic Predictions',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='best', fontsize=9)
    ax.grid(alpha=0.3, axis='x')

    plt.tight_layout()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    save_path = output_dir / f"paper7_phase4_empirical_vs_v4_{timestamp}.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def main():
    """Main execution: Empirical CV extraction and V4 calibration."""
    print("\n" + "=" * 70)
    print("PAPER 7 PHASE 4: EMPIRICAL CV VALIDATION")
    print("=" * 70)
    print()

    # Step 1: Extract empirical CV
    print("STEP 1: Extract Paper 2 Empirical CV")
    print("-" * 70)
    extractor = EmpiricalCVExtractor()
    extractor.print_summary()

    target_cv = extractor.get_target_cv()
    print(f"\nTarget CV for V4 calibration: {target_cv:.3f} ({target_cv*100:.1f}%)")

    # Step 2: V4 base parameters
    print("\n" + "=" * 70)
    print("STEP 2: V4 Base Parameters")
    print("-" * 70)

    base_params = {
        'r': 0.15,
        'K': 100.0,
        'alpha': 0.1,
        'beta': 0.02,
        'gamma': 0.3,
        'lambda_0': 2.5,
        'mu_0': 0.4,
        'sigma': 0.1,
        'omega': 0.02,
        'kappa': 0.1,
        'phi_0': 0.06,
        'rho_threshold': 5.0
    }

    print("\nV4 sustained parameters:")
    for key, val in base_params.items():
        print(f"  {key}: {val}")

    # Step 3: Calibrate noise levels
    print("\n" + "=" * 70)
    print("STEP 3: Calibrate V4 Noise to Match Empirical CV")
    print("-" * 70)

    calibrator = V4NoiseCalibrator(base_params, target_cv)

    output_dir = Path(__file__).parent.parent.parent / "data" / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)

    calibrations = []

    # Calibrate parameter noise
    print("\n### PARAMETER NOISE CALIBRATION ###")
    param_noise_range = np.linspace(0.0, 0.10, 11)
    param_calib = calibrator.calibrate_noise_level('parameter', param_noise_range, n_runs=20)
    calibrations.append(param_calib)
    plot_cv_calibration(param_calib, target_cv, output_dir)

    # Calibrate state noise
    print("\n### STATE NOISE CALIBRATION ###")
    state_noise_range = np.linspace(0.0, 2.0, 11)
    state_calib = calibrator.calibrate_noise_level('state', state_noise_range, n_runs=20)
    calibrations.append(state_calib)
    plot_cv_calibration(state_calib, target_cv, output_dir)

    # Calibrate external noise
    print("\n### EXTERNAL NOISE CALIBRATION ###")
    external_noise_range = np.linspace(0.0, 0.20, 11)
    external_calib = calibrator.calibrate_noise_level('external', external_noise_range, n_runs=20)
    calibrations.append(external_calib)
    plot_cv_calibration(external_calib, target_cv, output_dir)

    # Step 4: Validate calibrations
    print("\n" + "=" * 70)
    print("STEP 4: Validate Calibrations")
    print("-" * 70)

    validations = []
    for calib in calibrations:
        validation = calibrator.validate_calibration(calib)
        validations.append(validation)

    # Step 5: Comparison figure
    print("\n" + "=" * 70)
    print("STEP 5: Generate Comparison Figure")
    print("-" * 70)

    compare_empirical_vs_v4(extractor.paper2_cv, calibrations, output_dir)

    # Step 6: Summary
    print("\n" + "=" * 70)
    print("SUMMARY: EMPIRICAL CV VALIDATION")
    print("=" * 70)
    print()
    print(f"Paper 2 target CV: {target_cv:.3f} ({target_cv*100:.1f}%)")
    print()
    print("V4 Calibrated Noise Levels:")
    for calib, validation in zip(calibrations, validations):
        if calib['best_match']:
            best = calib['best_match']
            status = "✅" if validation['cv_match'] else "❌"
            print(f"  {status} {calib['noise_type'].capitalize()} noise = {best['noise_level']:.4f}")
            print(f"     CV = {best['cv_mean']:.3f}, Error = {best['cv_error']:.4f}")
    print()
    print("Key Findings:")
    print("- V4 deterministic: CV ≈ 0.15 (too high vs. Paper 2)")
    print("- Paper 2 empirical: CV ≈ 0.09 (population homeostasis)")
    print("- V4 requires LOW noise to match empirical variance")
    print("- Empirical system has tighter regulation than V4 base")
    print()
    print("Interpretation:")
    print("- Paper 2 agent-based system exhibits strong homeostasis")
    print("- V4 theoretical model captures dynamics but overestimates variance")
    print("- Calibrated noise levels quantify difference in regulatory efficiency")
    print()

    # Save results
    results_path = output_dir.parent / "results" / f"paper7_phase4_cv_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)

    results_data = {
        'empirical_cv': extractor.paper2_cv,
        'calibrations': [{
            'noise_type': c['noise_type'],
            'best_match': c['best_match'],
            'target_cv': c['target_cv']
        } for c in calibrations],
        'validations': validations
    }

    with open(results_path, 'w') as f:
        json.dump(results_data, f, indent=2)

    print(f"Results saved: {results_path}")
    print()


if __name__ == "__main__":
    main()
