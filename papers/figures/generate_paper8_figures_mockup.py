#!/usr/bin/env python3
"""
Paper 8 Figure Generation: Mockup Version with Simulated Data

Generates 6 publication-quality figures (300 DPI) for Paper 8:
- Figure 1: Runtime Variance Timeline
- Figure 2: Hypothesis Testing Results (5 panels)
- Figure 3: Optimization Impact Comparison
- Figure 4: Framework Connection (NRM Emergent Complexity)
- Figure S1: Literature Synthesis Timeline
- Figure S2: Hypothesis Prioritization Matrix

Status: Mockup with simulated data (awaiting C256 completion for real data)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Computational Partner: Claude (DUALITY-ZERO-V2)
Date: 2025-10-30 (Cycle 672)
License: GPL-3.0
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from matplotlib.gridspec import GridSpec
import numpy as np
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial']

def generate_figure1_runtime_variance_timeline():
    """Figure 1: Runtime Variance Timeline with Non-Linear Acceleration"""
    print("Generating Figure 1: Runtime Variance Timeline...")

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)

    # Baseline expectation
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=2,
               label='Baseline expectation (20.1h)', zorder=1)

    # Actual runtime data (simulated non-linear curve)
    time_points = np.array([0, 10, 20, 30, 31, 32, 33, 34, 34.5])
    variance_pct = np.array([0, 5, 15, 49.3, 54.2, 60, 66, 71, 71.6])

    ax.plot(time_points, variance_pct, color='#2171B5', linewidth=3,
            label='C256 actual variance', zorder=3)

    # Milestone markers
    milestones = {
        'Early (30h)': (30.0, 49.3, 'o', '#2171B5'),
        'Middle (31h)': (31.0, 54.2, 's', '#FC8D59'),
        'Late (34.5h)': (34.5, 71.6, 'D', '#E34A33')
    }

    for label, (x, y, marker, color) in milestones.items():
        ax.scatter(x, y, s=150, marker=marker, color=color,
                   edgecolor='black', linewidth=1.5, label=label, zorder=5)

    # Axes
    ax.set_xlabel('Elapsed CPU Time (hours)', fontsize=12, weight='bold')
    ax.set_ylabel('Cumulative Variance (%)', fontsize=12, weight='bold')
    ax.set_title('C256 Runtime Variance: Non-Linear Acceleration Pattern',
                 fontsize=14, weight='bold')
    ax.set_xlim(-1, 36)
    ax.set_ylim(-5, 80)

    # Grid and legend
    ax.grid(True, alpha=0.3, linestyle=':')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)

    # Acceleration inset
    ax_inset = fig.add_axes([0.60, 0.15, 0.28, 0.25])
    phases = ['Early\n(0-30h)', 'Middle\n(30-31h)', 'Late\n(31-34.5h)']
    accel_rates = [2.45, 2.71, 3.56]
    colors_inset = ['#2171B5', '#FC8D59', '#E34A33']

    ax_inset.bar(phases, accel_rates, color=colors_inset, edgecolor='black', linewidth=1.5)
    ax_inset.set_ylabel('Accel. Rate (%/h)', fontsize=9, weight='bold')
    ax_inset.set_title('Acceleration Increasing', fontsize=10, weight='bold')
    ax_inset.grid(True, alpha=0.3, axis='y')
    ax_inset.set_ylim(0, 4)

    plt.tight_layout()
    plt.savefig('paper8_fig1_runtime_variance_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Figure 1 saved: paper8_fig1_runtime_variance_timeline.png")


def generate_figure2_hypothesis_testing():
    """Figure 2: Hypothesis Testing Results (5 panels)"""
    print("Generating Figure 2: Hypothesis Testing Results...")

    fig = plt.figure(figsize=(10, 12), dpi=300)
    gs = GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.3)

    np.random.seed(42)

    # Panel A: H1 (System Resource Contention)
    ax_h1 = fig.add_subplot(gs[0, 0])
    time_h1 = np.linspace(0, 34, 100)
    cpu_load = 45 + 5 * np.sin(time_h1 / 5) + np.random.normal(0, 2, 100)
    mem_load = 60 + 3 * np.sin(time_h1 / 7) + np.random.normal(0, 1.5, 100)

    ax_h1.plot(time_h1, cpu_load, color='#E34A33', linewidth=2, label='CPU load (%)')
    ax_h1.plot(time_h1, mem_load, color='#2171B5', linewidth=2, label='Memory load (%)')

    r_cpu = np.corrcoef(time_h1, cpu_load)[0, 1]
    validation_h1 = 'REFUTED' if abs(r_cpu) < 0.3 else 'VALIDATED'
    color_h1 = '#238B45' if validation_h1 == 'VALIDATED' else '#E34A33'

    ax_h1.text(0.05, 0.95, f'r = {r_cpu:.3f}\np = 0.127', transform=ax_h1.transAxes,
               fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    ax_h1.text(0.95, 0.95, validation_h1, transform=ax_h1.transAxes,
               fontsize=11, weight='bold', va='top', ha='right',
               bbox=dict(boxstyle='round', facecolor=color_h1, alpha=0.4))

    ax_h1.set_xlabel('Time (hours)', fontsize=10, weight='bold')
    ax_h1.set_ylabel('Load (%)', fontsize=10, weight='bold')
    ax_h1.set_title('H1: System Resource Contention', fontsize=11, weight='bold')
    ax_h1.legend(loc='lower right', fontsize=8)
    ax_h1.grid(True, alpha=0.3)

    # Panel B: H2 (Memory Fragmentation)
    ax_h2 = fig.add_subplot(gs[0, 1])
    cycles_h2 = np.arange(0, 3000, 30)
    memory_rss = 500 + 0.05 * cycles_h2 + 0.00002 * cycles_h2**2 + np.random.normal(0, 15, len(cycles_h2))

    ax_h2.scatter(cycles_h2, memory_rss, alpha=0.4, s=20, color='#2171B5', label='Data')

    # Linear fit
    p_linear = np.polyfit(cycles_h2, memory_rss, 1)
    linear_fit = np.polyval(p_linear, cycles_h2)
    r2_linear = 1 - (np.sum((memory_rss - linear_fit)**2) / np.sum((memory_rss - np.mean(memory_rss))**2))

    # Polynomial fit
    p_poly = np.polyfit(cycles_h2, memory_rss, 2)
    poly_fit = np.polyval(p_poly, cycles_h2)
    r2_poly = 1 - (np.sum((memory_rss - poly_fit)**2) / np.sum((memory_rss - np.mean(memory_rss))**2))

    delta_r2 = r2_poly - r2_linear

    ax_h2.plot(cycles_h2, linear_fit, color='#6BAED6', linewidth=2, label=f'Linear (R²={r2_linear:.3f})')
    ax_h2.plot(cycles_h2, poly_fit, color='#E34A33', linewidth=2, label=f'Poly (R²={r2_poly:.3f})')

    validation_h2 = 'VALIDATED' if delta_r2 > 0.1 else 'REFUTED'
    color_h2 = '#238B45' if validation_h2 == 'VALIDATED' else '#E34A33'

    ax_h2.text(0.05, 0.95, f'ΔR² = {delta_r2:.3f}', transform=ax_h2.transAxes,
               fontsize=9, va='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    ax_h2.text(0.95, 0.95, validation_h2, transform=ax_h2.transAxes,
               fontsize=11, weight='bold', va='top', ha='right',
               bbox=dict(boxstyle='round', facecolor=color_h2, alpha=0.4))

    ax_h2.set_xlabel('Cycle Number', fontsize=10, weight='bold')
    ax_h2.set_ylabel('Memory RSS (MB)', fontsize=10, weight='bold')
    ax_h2.set_title('H2: Memory Fragmentation', fontsize=11, weight='bold')
    ax_h2.legend(loc='lower right', fontsize=8)
    ax_h2.grid(True, alpha=0.3)

    # Panel C: H3 (I/O Accumulation)
    ax_h3 = fig.add_subplot(gs[1, 0])
    calls_millions = np.linspace(0, 1.08, 100)
    latency = 0.5 + 0.003 * calls_millions * 1000 + np.random.normal(0, 0.2, 100)

    ax_h3.scatter(calls_millions, latency, alpha=0.4, s=20, color='#2171B5')

    slope_h3, intercept_h3, r_h3, p_h3, se_h3 = linregress(calls_millions, latency)
    line_h3 = slope_h3 * calls_millions + intercept_h3
    ax_h3.plot(calls_millions, line_h3, color='#E34A33', linewidth=2, label='Linear fit')

    validation_h3 = 'VALIDATED' if slope_h3 > 0.001 and r_h3**2 > 0.3 else 'REFUTED'
    color_h3 = '#238B45' if validation_h3 == 'VALIDATED' else '#E34A33'

    ax_h3.text(0.05, 0.95, f'Slope = {slope_h3:.4f} ms/M\nR² = {r_h3**2:.3f}',
               transform=ax_h3.transAxes, fontsize=9, va='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    ax_h3.text(0.95, 0.95, validation_h3, transform=ax_h3.transAxes,
               fontsize=11, weight='bold', va='top', ha='right',
               bbox=dict(boxstyle='round', facecolor=color_h3, alpha=0.4))

    ax_h3.set_xlabel('psutil Calls (millions)', fontsize=10, weight='bold')
    ax_h3.set_ylabel('Call Latency (ms)', fontsize=10, weight='bold')
    ax_h3.set_title('H3: I/O Accumulation', fontsize=11, weight='bold')
    ax_h3.legend(loc='lower right', fontsize=8)
    ax_h3.grid(True, alpha=0.3)

    # Panel D: H4 (Thermal Throttling)
    ax_h4 = fig.add_subplot(gs[1, 1])
    ax_h4_freq = ax_h4.twinx()

    time_h4 = np.linspace(0, 34, 100)
    temp = 65 + 2 * np.sin(time_h4 / 8) + np.random.normal(0, 1, 100)
    freq = 100 - 0.5 * np.sin(time_h4 / 8) + np.random.normal(0, 0.5, 100)

    line_temp = ax_h4.plot(time_h4, temp, color='#E34A33', linewidth=2, label='Temperature (°C)')
    line_freq = ax_h4_freq.plot(time_h4, freq, color='#2171B5', linewidth=2, label='Frequency (% nominal)')

    r_temp = np.corrcoef(time_h4, temp)[0, 1]
    r_freq = np.corrcoef(time_h4, freq)[0, 1]

    validation_h4 = 'REFUTED'
    color_h4 = '#E34A33'

    ax_h4.text(0.05, 0.95, f'Temp r = {r_temp:.3f}\nFreq r = {r_freq:.3f}',
               transform=ax_h4.transAxes, fontsize=9, va='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    ax_h4.text(0.95, 0.95, validation_h4, transform=ax_h4.transAxes,
               fontsize=11, weight='bold', va='top', ha='right',
               bbox=dict(boxstyle='round', facecolor=color_h4, alpha=0.4))

    ax_h4.set_xlabel('Time (hours)', fontsize=10, weight='bold')
    ax_h4.set_ylabel('Temperature (°C)', fontsize=10, weight='bold', color='#E34A33')
    ax_h4_freq.set_ylabel('Frequency (% nominal)', fontsize=10, weight='bold', color='#2171B5')
    ax_h4.set_title('H4: Thermal Throttling', fontsize=11, weight='bold')
    ax_h4.tick_params(axis='y', labelcolor='#E34A33')
    ax_h4_freq.tick_params(axis='y', labelcolor='#2171B5')

    lines = line_temp + line_freq
    labels = [l.get_label() for l in lines]
    ax_h4.legend(lines, labels, loc='upper right', fontsize=8)
    ax_h4.grid(True, alpha=0.3)

    # Panel E: H5 (Emergent Complexity) - spans bottom row
    ax_h5 = fig.add_subplot(gs[2, :])
    cycles_h5 = np.arange(0, 3000, 10)
    runtime_per_cycle = 10 + 0.015 * cycles_h5 + np.random.normal(0, 1.5, len(cycles_h5))

    ax_h5.scatter(cycles_h5, runtime_per_cycle, alpha=0.3, s=10, color='#2171B5', label='Per-cycle runtime')

    slope_h5, intercept_h5, r_h5, p_h5, se_h5 = linregress(cycles_h5, runtime_per_cycle)
    line_h5 = slope_h5 * cycles_h5 + intercept_h5
    ax_h5.plot(cycles_h5, line_h5, color='#E34A33', linewidth=3, label='Linear fit')

    validation_h5 = 'VALIDATED' if slope_h5 > 0.01 and r_h5**2 > 0.3 else 'REFUTED'
    color_h5 = '#238B45' if validation_h5 == 'VALIDATED' else '#E34A33'

    ax_h5.text(0.05, 0.95, f'Slope = {slope_h5:.4f} ms/cycle\nR² = {r_h5**2:.3f}\np < 0.001',
               transform=ax_h5.transAxes, fontsize=10, va='top',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))
    ax_h5.text(0.95, 0.95, validation_h5, transform=ax_h5.transAxes,
               fontsize=12, weight='bold', va='top', ha='right',
               bbox=dict(boxstyle='round', facecolor=color_h5, alpha=0.4))

    ax_h5.set_xlabel('Cycle Number', fontsize=11, weight='bold')
    ax_h5.set_ylabel('Per-Cycle Runtime (ms)', fontsize=11, weight='bold')
    ax_h5.set_title('H5: Emergent Complexity (NRM Pattern Memory)', fontsize=12, weight='bold')
    ax_h5.legend(loc='lower right', fontsize=9)
    ax_h5.grid(True, alpha=0.3)

    plt.suptitle('Hypothesis Testing Results: C256 Runtime Variance',
                 fontsize=16, weight='bold', y=0.995)

    plt.savefig('paper8_fig2_hypothesis_testing_results.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Figure 2 saved: paper8_fig2_hypothesis_testing_results.png")


def generate_figure3_optimization_impact():
    """Figure 3: Optimization Impact Comparison"""
    print("Generating Figure 3: Optimization Impact Comparison...")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), dpi=300)

    # Panel A: Runtime comparison
    experiments = ['C256\n(Unoptimized)', 'C257-C260\n(Optimized)']
    runtimes_hours = [34.5, 0.2]
    colors = ['#E34A33', '#2171B5']

    bars_runtime = ax1.bar(experiments, runtimes_hours, color=colors,
                           edgecolor='black', linewidth=2, width=0.6)

    # Error bars for optimized
    ax1.errorbar([1], [0.2], yerr=[[0.017], [0.017]], fmt='none',
                 ecolor='black', capsize=10, linewidth=2)

    # Speedup annotation
    ax1.annotate('', xy=(1, 1), xytext=(0, 30),
                 arrowprops=dict(arrowstyle='<->', lw=3, color='#238B45'))
    ax1.text(0.5, 15, '160-190×\nspeedup', fontsize=13, weight='bold',
             ha='center', color='#238B45', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Value labels
    ax1.text(0, 34.5 + 1.5, '34.5h', ha='center', fontsize=11, weight='bold')
    ax1.text(1, 0.2 + 1.5, '~12 min', ha='center', fontsize=11, weight='bold')

    ax1.set_ylabel('Runtime (hours, log scale)', fontsize=12, weight='bold')
    ax1.set_yscale('log')
    ax1.set_ylim(0.1, 50)
    ax1.set_title('Runtime Comparison', fontsize=14, weight='bold')
    ax1.grid(True, alpha=0.3, axis='y', which='both')

    # Panel B: psutil call reduction
    calls_millions = [1.08, 0.012]

    bars_calls = ax2.bar(experiments, calls_millions, color=colors,
                         edgecolor='black', linewidth=2, width=0.6)

    # Reduction annotation
    ax2.annotate('', xy=(1, 0.02), xytext=(0, 0.8),
                 arrowprops=dict(arrowstyle='<->', lw=3, color='#FC8D59'))
    ax2.text(0.5, 0.1, '90×\nreduction', fontsize=13, weight='bold',
             ha='center', color='#FC8D59', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Call frequency labels
    ax2.text(0, 1.08 * 1.2, '90 per cycle', fontsize=10, ha='center', weight='bold')
    ax2.text(1, 0.012 * 2, '1 per cycle\n(cached)', fontsize=10, ha='center', weight='bold')

    ax2.set_ylabel('Total psutil calls (millions, log scale)', fontsize=12, weight='bold')
    ax2.set_yscale('log')
    ax2.set_ylim(0.005, 2)
    ax2.set_title('psutil Call Reduction', fontsize=14, weight='bold')
    ax2.grid(True, alpha=0.3, axis='y', which='both')

    plt.suptitle('Optimization Impact: C256 vs. C257-C260', fontsize=16, weight='bold')
    plt.tight_layout()
    plt.savefig('paper8_fig3_optimization_impact.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Figure 3 saved: paper8_fig3_optimization_impact.png")


def generate_figure4_framework_connection():
    """Figure 4: Framework Connection (NRM Emergent Complexity)"""
    print("Generating Figure 4: Framework Connection...")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 10), dpi=300)

    np.random.seed(42)

    # Panel A: Pattern memory accumulation
    cycles = np.arange(0, 12001, 100)
    patterns = 500 * (1 - np.exp(-cycles / 3000)) + np.random.normal(0, 10, len(cycles))
    patterns = np.maximum(patterns, 0)

    ax1.plot(cycles, patterns, color='#2171B5', linewidth=2.5, label='Pattern Memory')
    ax1.fill_between(cycles, 0, patterns, alpha=0.2, color='#2171B5')

    # Phase annotations
    phases = [
        ('Early: Rapid\naccumulation', 2000, 250, '#238B45'),
        ('Middle: Slower\ngrowth', 6000, 400, '#FC8D59'),
        ('Late: Saturation', 10000, 480, '#E34A33')
    ]

    for label, x, y, color in phases:
        ax1.axvline(x, color=color, linestyle='--', alpha=0.5, linewidth=2)
        ax1.text(x + 200, y, label, fontsize=9, va='bottom',
                 bbox=dict(boxstyle='round', facecolor='white', edgecolor=color, alpha=0.9))

    ax1.set_xlabel('Cycle Number', fontsize=12, weight='bold')
    ax1.set_ylabel('Pattern Memory Size\n(# patterns stored)', fontsize=12, weight='bold')
    ax1.set_title('NRM Pattern Memory Accumulation', fontsize=14, weight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='lower right', fontsize=10)
    ax1.set_xlim(0, 12000)
    ax1.set_ylim(0, 550)

    # Inset: Pattern types pie chart
    ax1_inset = fig.add_axes([0.65, 0.62, 0.25, 0.18])
    pattern_types = ['Composition', 'Decomposition', 'Resonance']
    sizes = [60, 25, 15]
    colors_pie = ['#2171B5', '#FC8D59', '#238B45']

    ax1_inset.pie(sizes, labels=pattern_types, colors=colors_pie, autopct='%1.0f%%',
                  textprops={'fontsize': 8, 'weight': 'bold'}, startangle=90)
    ax1_inset.set_title('Pattern Types', fontsize=9, weight='bold')

    # Panel B: Runtime vs. Pattern Memory
    pattern_sizes = np.random.randint(0, 500, 1000)
    runtimes = 10 + 0.05 * pattern_sizes + np.random.normal(0, 2, 1000)

    ax2.scatter(pattern_sizes, runtimes, alpha=0.3, s=10, color='#2171B5')

    # Linear regression
    slope, intercept, r_value, p_value, std_err = linregress(pattern_sizes, runtimes)
    line = slope * np.array([0, 500]) + intercept
    ax2.plot([0, 500], line, color='#E34A33', linewidth=3, label='Linear fit')

    # Statistics box
    stats_text = f'Slope = {slope:.3f} ms/pattern\nR² = {r_value**2:.3f}\np < 0.001'
    ax2.text(0.05, 0.95, stats_text, transform=ax2.transAxes,
             fontsize=10, va='top', weight='bold',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    # Validation badge
    if slope > 0.01 and r_value**2 > 0.3:
        ax2.text(0.95, 0.95, 'VALIDATED\n(H5)', transform=ax2.transAxes,
                 fontsize=12, weight='bold', va='top', ha='right',
                 bbox=dict(boxstyle='round', facecolor='#238B45', alpha=0.4))

    # Framework prediction annotation
    ax2.text(0.5, 0.05, 'NRM Prediction: Emergent Complexity → Runtime Variance',
             transform=ax2.transAxes, fontsize=11, weight='bold', ha='center',
             style='italic', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))

    ax2.set_xlabel('Pattern Memory Size (# patterns)', fontsize=12, weight='bold')
    ax2.set_ylabel('Per-Cycle Runtime (ms)', fontsize=12, weight='bold')
    ax2.set_title('Runtime vs. Pattern Memory (H5 Validation)', fontsize=14, weight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='lower right', fontsize=10)
    ax2.set_xlim(0, 500)

    plt.tight_layout()
    plt.savefig('paper8_fig4_framework_connection.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Figure 4 saved: paper8_fig4_framework_connection.png")


def generate_figureS1_literature_synthesis():
    """Figure S1: Literature Synthesis Timeline"""
    print("Generating Figure S1: Literature Synthesis Timeline...")

    fig, ax = plt.subplots(figsize=(12, 4), dpi=300)

    # Timeline events
    events = [
        ('Dec 2024', 'ragoragino.dev\ncase study', 0, 'Literature', '#2171B5'),
        ('Dec 2024', 'Pymalloc\nmechanism', 0.5, 'Literature', '#2171B5'),
        ('Oct 2025', 'C256 experiment\n(+73% variance)', 10, 'Observation', '#FC8D59'),
        ('Oct 2025', 'Literature review\n(Cycle 670)', 10.5, 'Analysis', '#FC8D59'),
        ('Oct 2025', 'H2 refined\n(fragmentation)', 11, 'Synthesis', '#238B45'),
        ('Oct 2025', 'Paper 8 drafted\n(Cycle 671)', 11.5, 'Publication', '#238B45')
    ]

    # Plot events
    for date, label, x, event_type, color in events:
        ax.scatter(x, 0, s=600, marker='o', color=color, edgecolor='black',
                   linewidth=2, zorder=5)
        ax.text(x, 0.25, label, fontsize=8, ha='center',
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.3, edgecolor='black'))
        ax.text(x, -0.25, date, fontsize=9, ha='center', weight='bold')

    # Arrows
    arrow1 = FancyArrowPatch((0.25, -0.05), (10.25, -0.05),
                            connectionstyle='arc3,rad=0.3', arrowstyle='->',
                            mutation_scale=25, linewidth=2.5, color='#737373', zorder=1)
    ax.add_patch(arrow1)
    ax.text(5.25, 0.6, 'Temporal Stewardship Encoding', fontsize=10, ha='center',
            style='italic', weight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

    arrow2 = FancyArrowPatch((0.5, 0.05), (11, 0.05),
                            connectionstyle='arc3,rad=-0.15', arrowstyle='->',
                            mutation_scale=25, linewidth=2.5, color='#737373', zorder=1)
    ax.add_patch(arrow2)
    ax.text(5.75, -0.55, 'Literature-Informed Refinement', fontsize=10, ha='center',
            style='italic', weight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='black'))

    arrow3 = FancyArrowPatch((10, 0.08), (11, 0.08),
                            arrowstyle='->', mutation_scale=20, linewidth=2,
                            color='#238B45', zorder=1)
    ax.add_patch(arrow3)
    ax.text(10.5, 0.45, 'Empirical\nValidation', fontsize=8, ha='center',
            style='italic', weight='bold',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#238B45'))

    # Axes formatting
    ax.set_xlim(-1, 12.5)
    ax.set_ylim(-0.8, 0.9)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.spines['bottom'].set_linewidth(3)

    ax.set_title('Literature Synthesis Timeline: December 2024 → October 2025',
                 fontsize=14, weight='bold', pad=20)

    # Legend
    legend_elements = [
        mpatches.Patch(color='#2171B5', label='Literature'),
        mpatches.Patch(color='#FC8D59', label='Observation/Analysis'),
        mpatches.Patch(color='#238B45', label='Synthesis/Publication')
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=10, framealpha=0.9)

    plt.tight_layout()
    plt.savefig('paper8_figS1_literature_synthesis_timeline.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Figure S1 saved: paper8_figS1_literature_synthesis_timeline.png")


def generate_figureS2_hypothesis_prioritization():
    """Figure S2: Hypothesis Prioritization Matrix"""
    print("Generating Figure S2: Hypothesis Prioritization Matrix...")

    # Data
    hypotheses = ['H2\n(Fragmentation)', 'H5\n(Emergent\nComplexity)',
                  'H3\n(I/O\nAccumulation)', 'H1\n(Resource\nContention)',
                  'H4\n(Thermal\nThrottling)']
    criteria = ['Literature\nSupport', 'Empirical\nEvidence',
                'Testability', 'Publication\nImpact', 'Overall\nScore']

    scores = np.array([
        [5, 4, 5, 5, 4.75],  # H2
        [3, 4, 5, 5, 4.25],  # H5
        [2, 4, 4, 4, 3.50],  # H3
        [1, 2, 3, 2, 2.00],  # H1
        [1, 1, 2, 2, 1.50]   # H4
    ])

    # Figure setup
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)

    # Heatmap
    im = ax.imshow(scores, cmap='RdYlGn', aspect='auto', vmin=1, vmax=5)

    # Axes
    ax.set_xticks(np.arange(len(criteria)))
    ax.set_yticks(np.arange(len(hypotheses)))
    ax.set_xticklabels(criteria, fontsize=11, weight='bold')
    ax.set_yticklabels(hypotheses, fontsize=11, weight='bold')

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')

    # Annotate scores
    for i in range(len(hypotheses)):
        for j in range(len(criteria)):
            text = ax.text(j, i, f'{scores[i, j]:.2f}',
                          ha='center', va='center', color='black',
                          fontsize=10, weight='bold')

    # Tier labels
    tiers = ['Tier 1\n(Highly Probable)', 'Tier 2\n(Plausible)', 'Tier 2\n(Plausible)',
             'Tier 3\n(Possible)', 'Tier 3\n(Possible)']
    for i, tier in enumerate(tiers):
        color = '#238B45' if 'Tier 1' in tier else ('#FC8D59' if 'Tier 2' in tier else '#E34A33')
        ax.text(5.4, i, tier, fontsize=9, va='center', weight='bold',
                bbox=dict(boxstyle='round', facecolor=color, alpha=0.4, edgecolor='black'))

    # Colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.15)
    cbar.set_label('Score (1=Low, 5=High)', fontsize=11, weight='bold')

    # Title
    ax.set_title('Hypothesis Prioritization Matrix\n(Literature-Informed Refinement)',
                 fontsize=14, weight='bold', pad=15)

    plt.tight_layout()
    plt.savefig('paper8_figS2_hypothesis_prioritization.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✓ Figure S2 saved: paper8_figS2_hypothesis_prioritization.png")


def main():
    """Generate all Paper 8 figures"""
    print("\n" + "="*60)
    print("Paper 8 Figure Generation: Mockup Version")
    print("="*60 + "\n")
    print("Status: Simulated data (awaiting C256 completion)\n")

    # Generate all figures
    generate_figure1_runtime_variance_timeline()
    generate_figure2_hypothesis_testing()
    generate_figure3_optimization_impact()
    generate_figure4_framework_connection()
    generate_figureS1_literature_synthesis()
    generate_figureS2_hypothesis_prioritization()

    print("\n" + "="*60)
    print("✓ All 6 figures generated successfully!")
    print("="*60)
    print("\nOutput files:")
    print("  - paper8_fig1_runtime_variance_timeline.png")
    print("  - paper8_fig2_hypothesis_testing_results.png")
    print("  - paper8_fig3_optimization_impact.png")
    print("  - paper8_fig4_framework_connection.png")
    print("  - paper8_figS1_literature_synthesis_timeline.png")
    print("  - paper8_figS2_hypothesis_prioritization.png")
    print("\nNext steps:")
    print("  1. Execute Phase 1A/1B hypothesis testing (post-C256)")
    print("  2. Replace simulated data with real experimental data")
    print("  3. Verify figure quality (resolution, readability, colorblind-friendly)")
    print("  4. Integrate into Paper 8 manuscript")
    print("  5. Submit to PLOS Computational Biology\n")


if __name__ == '__main__':
    main()
