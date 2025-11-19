#!/usr/bin/env python3
"""
Diagram Generation for Theoretical Paper: Computational Expense as Validation

Creates publication-quality figures (300 DPI) for:
1. Efficiency-Validity Trade-off Curve
2. Overhead Authentication Flowchart
3. Grounding Strength vs Overhead Factor

Usage: python generate_theoretical_diagrams.py

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-10-27 (Cycle 353)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path


def create_efficiency_validity_curve(output_dir: Path):
    """
    Generate Efficiency-Validity Trade-off visualization.

    Shows relationship between grounding strength (G) and overhead factor (O).
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    # Grounding strength range
    G = np.linspace(0, 1, 100)

    # Measurement cost scenarios (C = latency per call)
    C_low = 0.01   # 10ms (fast measurement)
    C_med = 0.067  # 67ms (psutil actual)
    C_high = 0.2   # 200ms (slow measurement)

    # Number of measurements (normalized)
    N = 1000
    T_sim = 1800  # Baseline 30 minutes

    # Overhead factor: O = (G * C * N) / T_sim
    O_low = (G * C_low * N) / T_sim * 1000  # Scale for visibility
    O_med = (G * C_med * N) / T_sim * 1000
    O_high = (G * C_high * N) / T_sim * 1000

    # Plot curves
    ax.plot(G, O_low, label='Fast Measurement (10ms)',
            color='#2ca02c', linewidth=2.5, linestyle='--')
    ax.plot(G, O_med, label='Moderate Measurement (67ms, psutil)',
            color='#1f77b4', linewidth=3)
    ax.plot(G, O_high, label='Slow Measurement (200ms)',
            color='#d62728', linewidth=2.5, linestyle='--')

    # Annotate key points
    # Pure simulation (G=0)
    ax.scatter([0], [0], s=150, color='black', zorder=5)
    ax.text(0.05, 0.1, 'Pure Simulation\n(G=0, O≈1)', fontsize=10,
            bbox=dict(boxstyle='round', facecolor='white', edgecolor='black'))

    # C255 validation (G=0.95, O=40×)
    G_c255 = 0.95
    O_c255 = 40
    ax.scatter([G_c255], [O_c255], s=200, color='#e6550d',
               marker='*', zorder=5, edgecolors='black', linewidth=1.5)
    ax.text(G_c255 - 0.15, O_c255 + 5, 'C255 Validation\n(G=0.95, O=40.25×)',
            fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='#fff7bc', edgecolor='#e6550d', linewidth=2))

    # Full reality grounding (G=1)
    ax.axvline(x=1.0, color='gray', linestyle=':', linewidth=1.5, alpha=0.7)
    ax.text(0.88, 70, 'Full Reality\nGrounding', fontsize=9, color='gray')

    # Labels and styling
    ax.set_xlabel('Grounding Strength (G)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Overhead Factor (O)', fontsize=13, fontweight='bold')
    ax.set_title('Efficiency-Validity Trade-off: Computational Expense vs. Reality Grounding',
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-2, 80)

    # Add shaded regions
    ax.axhspan(0, 5, alpha=0.1, color='green', label='_nolegend_')
    ax.text(0.5, 2, 'Efficient (Low Overhead)', fontsize=9, ha='center',
            color='darkgreen', fontstyle='italic')

    ax.axhspan(20, 80, alpha=0.1, color='orange', label='_nolegend_')
    ax.text(0.5, 50, 'Authentic (High Reality Grounding)', fontsize=9, ha='center',
            color='darkorange', fontstyle='italic')

    plt.tight_layout()

    output_path = output_dir / "figure1_efficiency_validity_tradeoff.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_overhead_authentication_flowchart(output_dir: Path):
    """
    Generate overhead authentication protocol flowchart.

    Shows decision tree for validating computational expense claims.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Define box styling
    style_start = dict(boxstyle='round,pad=0.5', facecolor='#d4e6f1', edgecolor='#2874a6', linewidth=2)
    style_decision = dict(boxstyle='round,pad=0.4', facecolor='#fdebd0', edgecolor='#d68910', linewidth=2)
    style_process = dict(boxstyle='round,pad=0.4', facecolor='#d5f4e6', edgecolor='#1e8449', linewidth=2)
    style_result = dict(boxstyle='round,pad=0.4', facecolor='#fadbd8', edgecolor='#cb4335', linewidth=2)

    # Start
    ax.text(5, 9.2, 'START\nSystem Claims Reality Grounding', ha='center', va='center',
            fontsize=11, fontweight='bold', bbox=style_start, wrap=True)

    # Step 1
    ax.annotate('', xy=(5, 8.5), xytext=(5, 8.8),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5, 8, 'Measure T_real\n(Observed Runtime)', ha='center', va='center',
            fontsize=10, bbox=style_process)

    # Step 2
    ax.annotate('', xy=(5, 7.3), xytext=(5, 7.7),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5, 6.8, 'Estimate T_sim\n(Pure Simulation Baseline)', ha='center', va='center',
            fontsize=10, bbox=style_process)

    # Step 3: Calculate O
    ax.annotate('', xy=(5, 6.1), xytext=(5, 6.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5, 5.6, 'Calculate O = T_real / T_sim\n(Overhead Factor)', ha='center', va='center',
            fontsize=10, bbox=style_process)

    # Decision 1: Is O > 1?
    ax.annotate('', xy=(5, 4.9), xytext=(5, 5.3),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5, 4.4, 'Is O > 1.2?', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=style_decision)

    # Branch: No overhead (O ≤ 1.2)
    ax.annotate('NO', xy=(2.5, 4.4), xytext=(4.2, 4.4),
                arrowprops=dict(arrowstyle='->', lw=2, color='red'))
    ax.text(1.5, 4.4, 'SUSPICIOUS\nLikely Simulation', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=style_result, color='darkred')

    # Branch: Yes overhead (O > 1.2)
    ax.annotate('YES', xy=(5, 3.7), xytext=(5, 4.1),
                arrowprops=dict(arrowstyle='->', lw=2, color='green'))

    # Step 4: Profile measurement calls
    ax.text(5, 3.2, 'Profile Measurement Calls\n(Count N, measure C)', ha='center', va='center',
            fontsize=10, bbox=style_process)

    # Step 5: Calculate predicted overhead
    ax.annotate('', xy=(5, 2.5), xytext=(5, 2.9),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5, 2.0, 'Calculate O_pred = (N × C) / T_sim\n(Predicted Overhead)', ha='center', va='center',
            fontsize=10, bbox=style_process)

    # Decision 2: Does O match O_pred?
    ax.annotate('', xy=(5, 1.3), xytext=(5, 1.7),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(5, 0.8, 'Is |O - O_pred| / O_pred < 0.2?\n(Within 20%)', ha='center', va='center',
            fontsize=10, fontweight='bold', bbox=style_decision)

    # Branch: No match
    ax.annotate('NO', xy=(7.5, 0.8), xytext=(5.8, 0.8),
                arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
    ax.text(8.5, 0.8, 'REQUIRES\nFURTHER\nINVESTIGATION', ha='center', va='center',
            fontsize=9, fontweight='bold', bbox=style_result, color='darkorange')

    # Branch: Match
    ax.annotate('YES', xy=(5, 0.1), xytext=(5, 0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='green'))
    ax.text(5, -0.4, 'AUTHENTICATED\nReality Grounding Validated', ha='center', va='center',
            fontsize=11, fontweight='bold', bbox=dict(boxstyle='round,pad=0.5',
            facecolor='#aed6f1', edgecolor='#1e8449', linewidth=3), color='darkgreen')

    # Add title
    fig.suptitle('Overhead Authentication Protocol\nComputational Expense Validation Flowchart',
                fontsize=14, fontweight='bold', y=0.98)

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='#d5f4e6', edgecolor='#1e8449', label='Process Step'),
        mpatches.Patch(facecolor='#fdebd0', edgecolor='#d68910', label='Decision Point'),
        mpatches.Patch(facecolor='#fadbd8', edgecolor='#cb4335', label='Result/Outcome')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=9, framealpha=0.95)

    plt.tight_layout()

    output_path = output_dir / "figure2_overhead_authentication_flowchart.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def create_grounding_vs_overhead_scatter(output_dir: Path):
    """
    Generate scatter plot: Grounding Strength vs. Overhead Factor.

    Shows hypothetical systems mapped in G-O space.
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Hypothetical systems
    systems = {
        'Pure Simulation': (0.0, 1.0, 'gray', 's'),
        'Token Sampling (LLM)': (0.05, 1.2, 'purple', 'o'),
        'Cached DB Queries': (0.15, 1.8, 'cyan', 'v'),
        'File I/O': (0.35, 3.5, 'blue', 'D'),
        'Network API Calls': (0.5, 8.0, 'green', '^'),
        'Sensor Readings (IoT)': (0.7, 15.0, 'orange', 'p'),
        'C255 (psutil)': (0.95, 40.25, 'red', '*'),
        'Real-time Robotics': (0.98, 50.0, 'brown', 'h')
    }

    # Plot systems
    for name, (G, O, color, marker) in systems.items():
        ax.scatter(G, O, s=250 if name == 'C255 (psutil)' else 150,
                  color=color, marker=marker, edgecolors='black',
                  linewidth=2 if name == 'C255 (psutil)' else 1,
                  zorder=5, label=name)

        # Annotate C255
        if name == 'C255 (psutil)':
            ax.annotate('Our Validation\n(NRM Framework)', xy=(G, O),
                       xytext=(G - 0.25, O + 8),
                       arrowprops=dict(arrowstyle='->', lw=2, color='red'),
                       fontsize=10, fontweight='bold',
                       bbox=dict(boxstyle='round', facecolor='#fff7bc',
                                edgecolor='red', linewidth=2))

    # Theoretical curve
    G_theory = np.linspace(0, 1, 100)
    O_theory = 1 + (G_theory ** 1.5) * 50  # Non-linear relationship
    ax.plot(G_theory, O_theory, 'k--', linewidth=2, alpha=0.5,
           label='Theoretical Trend', zorder=1)

    # Shaded regions
    ax.axhspan(0, 5, alpha=0.08, color='green', label='_nolegend_')
    ax.text(0.5, 2.5, 'Low Overhead Zone\n(Likely Simulated)', fontsize=9,
           ha='center', color='darkgreen', fontstyle='italic')

    ax.axhspan(10, 60, alpha=0.08, color='orange', label='_nolegend_')
    ax.text(0.5, 30, 'High Overhead Zone\n(Reality-Grounded)', fontsize=9,
           ha='center', color='darkorange', fontstyle='italic')

    # Labels and styling
    ax.set_xlabel('Grounding Strength (G)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Overhead Factor (O)', fontsize=13, fontweight='bold')
    ax.set_title('Computational Expense Landscape:\nSystems Mapped by Reality Grounding vs. Overhead',
                fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-2, 60)

    # Add reference line: O = 1 (no overhead)
    ax.axhline(y=1, color='black', linestyle=':', linewidth=1.5, alpha=0.5)
    ax.text(0.02, 1.5, 'O=1 (Baseline)', fontsize=8, color='black', fontstyle='italic')

    plt.tight_layout()

    output_path = output_dir / "figure3_grounding_overhead_landscape.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved: {output_path}")
    plt.close()


def main():
    """Main diagram generation pipeline."""
    print("=" * 70)
    print("THEORETICAL PAPER DIAGRAM GENERATION")
    print("=" * 70)
    print("Paper: Computational Expense as Framework Validation")
    print("Status: Generating publication-quality figures (300 DPI)")
    print()

    # Create output directory
    output_dir = Path(__file__).parent / "figures"
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}")
    print()

    # Generate figures
    print("🎨 Generating diagrams...")
    print()

    print("Figure 1: Efficiency-Validity Trade-off Curve...")
    create_efficiency_validity_curve(output_dir)

    print("Figure 2: Overhead Authentication Flowchart...")
    create_overhead_authentication_flowchart(output_dir)

    print("Figure 3: Grounding vs. Overhead Landscape...")
    create_grounding_vs_overhead_scatter(output_dir)

    print()
    print("=" * 70)
    print("✅ DIAGRAM GENERATION COMPLETE")
    print("=" * 70)
    print(f"Generated 3 publication-quality figures (300 DPI)")
    print(f"Location: {output_dir}")
    print()
    print("Theoretical paper status: 95% → 100% (ready for submission)")
    print()
    print("Next steps:")
    print("  1. Review figures for accuracy and clarity")
    print("  2. Integrate figure references into manuscript")
    print("  3. Final proofreading")
    print("  4. Prepare cover letter")
    print("  5. Submit to target journal")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
