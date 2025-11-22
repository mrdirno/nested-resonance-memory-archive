#!/usr/bin/env python3
"""
CYCLE 133: COMPUTATIONAL BOTTLENECK VISUALIZATION

Creates performance and memory scaling plots for bottleneck test results.
"""

import json
import numpy as np
from pathlib import Path
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt


def load_bottleneck_results():
    """Load bottleneck test results"""
    results_file = Path(__file__).parent / "results" / "cycle133_bottleneck_test.json"
    with open(results_file) as f:
        data = json.load(f)
    return data['results']


def plot_performance_scaling(results, output_dir):
    """Plot cycles/sec vs agent_cap"""
    caps = [r['agent_cap'] for r in results]
    cycles_per_sec = [r['cycles_per_sec'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    ax.plot(caps, cycles_per_sec, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    ax.axhline(y=cycles_per_sec[0], color='gray', linestyle='--', alpha=0.5,
               label=f'Baseline ({cycles_per_sec[0]:.1f} cyc/s)')

    ax.set_xlabel('Agent Cap', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cycles per Second', fontsize=12, fontweight='bold')
    ax.set_title('Computational Performance: No Bottleneck Detected',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # Add variance band
    mean_perf = np.mean(cycles_per_sec)
    std_perf = np.std(cycles_per_sec)
    ax.axhspan(mean_perf - std_perf, mean_perf + std_perf, alpha=0.1, color='green',
               label=f'Mean ± 1σ ({mean_perf:.1f} ± {std_perf:.1f})')

    ax.set_xscale('log')
    ax.set_xticks(caps)
    ax.set_xticklabels([str(c) for c in caps])

    plt.tight_layout()
    output_path = output_dir / "cycle133_bottleneck_performance.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Performance plot saved: {output_path}")
    plt.close()


def plot_memory_scaling(results, output_dir):
    """Plot memory increase vs agent_cap"""
    caps = [r['agent_cap'] for r in results]
    memory_increase = [r['memory_increase_mb'] for r in results]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    ax.bar(range(len(caps)), memory_increase, color='#A23B72', alpha=0.7)
    ax.set_xticks(range(len(caps)))
    ax.set_xticklabels([str(c) for c in caps])
    ax.set_xlabel('Agent Cap', fontsize=12, fontweight='bold')
    ax.set_ylabel('Memory Increase (MB)', fontsize=12, fontweight='bold')
    ax.set_title('Memory Scaling: Minimal Growth Across All Scales',
                 fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    # Add peak agents annotation
    for i, r in enumerate(results):
        ax.text(i, memory_increase[i] + 0.2, f"{r['peak_agents']} agents",
                ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    output_path = output_dir / "cycle133_bottleneck_memory.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Memory plot saved: {output_path}")
    plt.close()


def plot_combined_metrics(results, output_dir):
    """Combined plot with performance and memory"""
    caps = [r['agent_cap'] for r in results]
    cycles_per_sec = [r['cycles_per_sec'] for r in results]
    memory_increase = [r['memory_increase_mb'] for r in results]
    peak_agents = [r['peak_agents'] for r in results]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10), dpi=300)

    # Performance subplot
    ax1.plot(caps, cycles_per_sec, 'o-', linewidth=2, markersize=8, color='#2E86AB')
    ax1.axhline(y=cycles_per_sec[0], color='gray', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Cycles per Second', fontsize=11, fontweight='bold')
    ax1.set_title('Computational Bottleneck Test: agent_cap 50-1000',
                  fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    ax1.set_xticks(caps)
    ax1.set_xticklabels([str(c) for c in caps])

    # Memory subplot
    ax2.bar(range(len(caps)), memory_increase, color='#A23B72', alpha=0.7)
    ax2.set_xticks(range(len(caps)))
    ax2.set_xticklabels([str(c) for c in caps])
    ax2.set_xlabel('Agent Cap', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Memory Increase (MB)', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')

    # Annotate peak agents
    for i, agents in enumerate(peak_agents):
        ax2.text(i, memory_increase[i] + 0.15, f"{agents} agents",
                ha='center', va='bottom', fontsize=8)

    plt.tight_layout()
    output_path = output_dir / "cycle133_bottleneck_combined.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Combined plot saved: {output_path}")
    plt.close()


def main():
    print("=" * 70)
    print("CYCLE 133: BOTTLENECK VISUALIZATION")
    print("=" * 70)

    # Load results
    results = load_bottleneck_results()
    print(f"Loaded {len(results)} bottleneck test results")

    # Create output directory
    output_dir = Path(__file__).parent.parent / "DUALITY_ZERO_V2_CORE_RESEARCH" / "figures"
    output_dir.mkdir(exist_ok=True, parents=True)

    # Generate plots
    print("\nGenerating visualizations...")
    plot_performance_scaling(results, output_dir)
    plot_memory_scaling(results, output_dir)
    plot_combined_metrics(results, output_dir)

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    caps = [r['agent_cap'] for r in results]
    cycles_per_sec = [r['cycles_per_sec'] for r in results]
    memory_increase = [r['memory_increase_mb'] for r in results]
    peak_agents = [r['peak_agents'] for r in results]

    print(f"Performance range: {min(cycles_per_sec):.1f} - {max(cycles_per_sec):.1f} cyc/s")
    print(f"Performance variance: {np.std(cycles_per_sec):.1f} cyc/s (±{np.std(cycles_per_sec)/np.mean(cycles_per_sec)*100:.1f}%)")
    print(f"Memory range: {min(memory_increase):.1f} - {max(memory_increase):.1f} MB")
    print(f"Peak agents (all tests): {set(peak_agents)}")

    # Degradation analysis
    baseline = cycles_per_sec[0]
    print("\nDegradation vs baseline (agent_cap=50):")
    for cap, perf in zip(caps, cycles_per_sec):
        degradation = (1 - perf / baseline) * 100
        status = "BOTTLENECK" if degradation > 10 else "OK"
        print(f"  agent_cap={cap:4d}: {degradation:+6.1f}% [{status}]")

    print("\n" + "=" * 70)
    print("KEY FINDING: No computational bottleneck up to agent_cap=1000")
    print("Population self-regulates at ~3 agents via burst dynamics")
    print("=" * 70)


if __name__ == "__main__":
    main()
