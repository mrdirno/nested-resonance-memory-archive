#!/usr/bin/env python3
"""
Generate Preliminary C176 V6 Incremental Validation Figures

Purpose: Create trajectory and threshold analysis visualizations based on
         available seed data (seed 42 complete + partial seed 123 data)
         for immediate Paper 2 integration readiness.

Design: Two publication-quality figures @ 300 DPI:
  1. Multi-scale timescale trajectory (spawn success, population, spawns/agent)
  2. Spawns per agent threshold analysis (C171 + C176 incremental)

Strategy: Preliminary analysis with available data, ready for immediate
          finalization when all 5 seeds complete.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
Date: 2025-11-02
Cycle: 911
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json

# Output directory
OUTPUT_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2/data/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# SEED 42 DATA (COMPLETE - From log output)
# ============================================================================

seed_42_trajectory = {
    'cycles': [0, 250, 500, 750, 1000],
    'population': [1, 7, 12, 18, 24],
    'spawn_attempts': [0, 7, 13, 19, 25],
    'spawn_successes': [0, 6, 11, 17, 23],
    'spawn_success_rate': [0.0, 85.7, 84.6, 89.5, 92.0],
}

# Calculate spawns per agent at each checkpoint
seed_42_spawns_per_agent = []
for i, cycles in enumerate(seed_42_trajectory['cycles']):
    if seed_42_trajectory['spawn_attempts'][i] == 0:
        seed_42_spawns_per_agent.append(0.0)
    else:
        avg_pop = (1 + seed_42_trajectory['population'][i]) / 2
        spawns_per_agent = seed_42_trajectory['spawn_attempts'][i] / avg_pop
        seed_42_spawns_per_agent.append(spawns_per_agent)

seed_42_trajectory['spawns_per_agent'] = seed_42_spawns_per_agent

# ============================================================================
# SEED 123 DATA (PARTIAL - From log output, 500/1000 cycles)
# ============================================================================

seed_123_trajectory = {
    'cycles': [0, 250, 500],
    'population': [1, 8, 12],
    'spawn_attempts': [0, 7, 13],
    'spawn_successes': [0, 7, 11],
    'spawn_success_rate': [0.0, 100.0, 84.6],
}

# Calculate spawns per agent
seed_123_spawns_per_agent = []
for i, cycles in enumerate(seed_123_trajectory['cycles']):
    if seed_123_trajectory['spawn_attempts'][i] == 0:
        seed_123_spawns_per_agent.append(0.0)
    else:
        avg_pop = (1 + seed_123_trajectory['population'][i]) / 2
        spawns_per_agent = seed_123_trajectory['spawn_attempts'][i] / avg_pop
        seed_123_spawns_per_agent.append(spawns_per_agent)

seed_123_trajectory['spawns_per_agent'] = seed_123_spawns_per_agent

# ============================================================================
# C171 REFERENCE DATA (Historical baseline - 3000 cycles)
# ============================================================================

# From analyze_spawns_per_agent.py Cycle 907 analysis
# C171 mean: 8.38 spawns/agent, ~23% spawn success, ~17 agents

c171_summary = {
    'mean_spawns_per_agent': 8.38,
    'mean_spawn_success': 23.0,
    'mean_population': 17.43,
    'cycles': 3000,
}

# ============================================================================
# FIGURE 1: MULTI-SCALE TIMESCALE TRAJECTORY
# ============================================================================

def generate_trajectory_figure():
    """Generate multi-scale timescale trajectory visualization."""

    fig, axes = plt.subplots(3, 1, figsize=(10, 12))

    # Colors
    color_42 = '#2E86AB'  # Blue
    color_123 = '#A23B72'  # Purple
    color_expected = '#F18F01'  # Orange

    # SUBPLOT 1: Spawn Success Rate
    ax1 = axes[0]

    # Seed 42 (complete)
    ax1.plot(seed_42_trajectory['cycles'],
             seed_42_trajectory['spawn_success_rate'],
             marker='o', linewidth=2, markersize=8,
             color=color_42, label='Seed 42 (complete)', zorder=3)

    # Seed 123 (partial)
    ax1.plot(seed_123_trajectory['cycles'],
             seed_123_trajectory['spawn_success_rate'],
             marker='s', linewidth=2, markersize=8,
             color=color_123, linestyle='--',
             label='Seed 123 (partial)', zorder=3)

    # Expected range (revised hypothesis: 70-90%)
    ax1.axhspan(70, 90, alpha=0.2, color=color_expected,
                label='Expected range (70-90%)')

    # Original expectation (simple hypothesis: ~50%)
    ax1.axhline(50, color='gray', linestyle=':', alpha=0.5,
                label='Original expectation (50%)')

    # C171 baseline (3000 cycles)
    ax1.axhline(c171_summary['mean_spawn_success'],
                color='red', linestyle='-.', alpha=0.6,
                label=f'C171 baseline (3000 cycles): {c171_summary["mean_spawn_success"]:.0f}%')

    ax1.set_xlabel('Cycles', fontsize=11)
    ax1.set_ylabel('Spawn Success Rate (%)', fontsize=11)
    ax1.set_title('A. Spawn Success Rate vs. Time (1000 Cycles)',
                  fontsize=12, fontweight='bold')
    ax1.legend(loc='best', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(-50, 1050)
    ax1.set_ylim(0, 105)

    # SUBPLOT 2: Population Growth
    ax2 = axes[1]

    # Seed 42
    ax2.plot(seed_42_trajectory['cycles'],
             seed_42_trajectory['population'],
             marker='o', linewidth=2, markersize=8,
             color=color_42, label='Seed 42', zorder=3)

    # Seed 123
    ax2.plot(seed_123_trajectory['cycles'],
             seed_123_trajectory['population'],
             marker='s', linewidth=2, markersize=8,
             color=color_123, linestyle='--',
             label='Seed 123 (partial)', zorder=3)

    # Expected range (revised: 18-20)
    ax2.axhspan(18, 20, alpha=0.2, color=color_expected,
                label='Expected range (18-20)')

    # Original expectation (10-15)
    ax2.axhspan(10, 15, alpha=0.1, color='gray',
                label='Original expectation (10-15)')

    # C171 baseline
    ax2.axhline(c171_summary['mean_population'],
                color='red', linestyle='-.', alpha=0.6,
                label=f'C171 baseline: {c171_summary["mean_population"]:.1f}')

    ax2.set_xlabel('Cycles', fontsize=11)
    ax2.set_ylabel('Population (agents)', fontsize=11)
    ax2.set_title('B. Population Growth Trajectory',
                  fontsize=12, fontweight='bold')
    ax2.legend(loc='best', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(-50, 1050)
    ax2.set_ylim(0, 26)

    # SUBPLOT 3: Spawns Per Agent
    ax3 = axes[2]

    # Seed 42
    ax3.plot(seed_42_trajectory['cycles'],
             seed_42_trajectory['spawns_per_agent'],
             marker='o', linewidth=2, markersize=8,
             color=color_42, label='Seed 42', zorder=3)

    # Seed 123
    ax3.plot(seed_123_trajectory['cycles'],
             seed_123_trajectory['spawns_per_agent'],
             marker='s', linewidth=2, markersize=8,
             color=color_123, linestyle='--',
             label='Seed 123 (partial)', zorder=3)

    # Threshold markers
    ax3.axhline(2, color='green', linestyle='--', alpha=0.6,
                linewidth=2, label='Threshold: 2 (high/transition boundary)')
    ax3.axhline(4, color='orange', linestyle='--', alpha=0.6,
                linewidth=2, label='Threshold: 4 (transition/low boundary)')

    # C171 baseline
    ax3.axhline(c171_summary['mean_spawns_per_agent'],
                color='red', linestyle='-.', alpha=0.6,
                label=f'C171 baseline: {c171_summary["mean_spawns_per_agent"]:.2f}')

    # Expected zone (<2 for high success)
    ax3.axhspan(0, 2, alpha=0.15, color='green')
    ax3.axhspan(2, 4, alpha=0.15, color='yellow')
    ax3.axhspan(4, 10, alpha=0.15, color='red')

    ax3.set_xlabel('Cycles', fontsize=11)
    ax3.set_ylabel('Spawns Per Agent', fontsize=11)
    ax3.set_title('C. Cumulative Spawns Per Agent (Threshold Analysis)',
                  fontsize=12, fontweight='bold')
    ax3.legend(loc='best', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(-50, 1050)
    ax3.set_ylim(0, 10)

    plt.tight_layout()

    # Save
    output_path = OUTPUT_DIR / "c176_v6_incremental_trajectory_preliminary.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Trajectory figure saved: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()

# ============================================================================
# FIGURE 2: SPAWNS PER AGENT THRESHOLD ANALYSIS
# ============================================================================

def generate_threshold_figure():
    """Generate spawns/agent vs spawn success threshold analysis."""

    # Load C171 data for comparison
    c171_path = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle171_fractal_swarm_bistability.json")

    c171_spawns_per_agent = []
    c171_spawn_success = []

    if c171_path.exists():
        with open(c171_path, 'r') as f:
            c171_data = json.load(f)

        for exp in c171_data['experiments']:
            spawn_count = exp['spawn_count']
            final_pop = exp['final_agent_count']

            # Calculate spawns per agent (same method as analysis script)
            avg_pop = (1 + final_pop) / 2
            spawns_per_agent = spawn_count / avg_pop

            c171_spawns_per_agent.append(spawns_per_agent)
            # Approximate spawn success (from Cycle 903: ~23%)
            c171_spawn_success.append(23.0)

    # C176 V6 incremental data (seed 42 complete)
    c176_spawns_per_agent = [seed_42_trajectory['spawns_per_agent'][-1]]  # Final value: 2.0
    c176_spawn_success = [seed_42_trajectory['spawn_success_rate'][-1]]  # Final: 92.0%

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # C171 data (3000 cycles)
    if c171_spawns_per_agent:
        ax.scatter(c171_spawns_per_agent, c171_spawn_success,
                  s=100, alpha=0.6, color='blue',
                  label='C171 (3000 cycles, 2.0-3.0%)', zorder=2)

    # C176 V6 incremental (1000 cycles)
    ax.scatter(c176_spawns_per_agent, c176_spawn_success,
              s=200, alpha=0.8, color='red', marker='*',
              edgecolors='black', linewidths=1.5,
              label='C176 V6 Incremental (1000 cycles, 2.5%)', zorder=3)

    # Threshold zones (horizontal)
    ax.axhline(y=70, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    ax.axhline(y=40, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    ax.axhline(y=20, color='gray', linestyle='--', alpha=0.3, linewidth=1)

    # Threshold zones (vertical)
    ax.axvline(x=2, color='gray', linestyle='--', alpha=0.3, linewidth=1)
    ax.axvline(x=4, color='gray', linestyle='--', alpha=0.3, linewidth=1)

    # Zone labels
    ax.text(1, 85, 'HIGH\nSUCCESS\n(70-100%)',
            fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    ax.text(3, 55, 'TRANSITION\n(40-70%)',
            fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
    ax.text(8, 25, 'LOW\nSUCCESS\n(20-30%)',
            fontsize=9, ha='center', va='center',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.3))

    # Labels and title
    ax.set_xlabel('Spawn Attempts Per Agent', fontsize=12)
    ax.set_ylabel('Spawn Success Rate (%)', fontsize=12)
    ax.set_title('Energy Constraint Threshold: Spawns/Agent vs. Success Rate',
                fontsize=14, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.2)

    # Set limits
    ax.set_xlim(0, 14)
    ax.set_ylim(15, 105)

    plt.tight_layout()

    # Save
    output_path = OUTPUT_DIR / "spawns_per_agent_threshold_with_c176_preliminary.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Threshold figure saved: {output_path}")
    print(f"  Size: {output_path.stat().st_size / 1024:.1f} KB")

    plt.close()

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Generate preliminary figures for Paper 2 integration."""

    print("=" * 80)
    print("CYCLE 911: PRELIMINARY C176 V6 FIGURE GENERATION")
    print("=" * 80)
    print()
    print("Purpose: Create publication-quality figures based on available data")
    print("         (seed 42 complete + partial seed 123) for immediate")
    print("         Paper 2 integration readiness.")
    print()
    print("Strategy: Preliminary analysis now, finalize when all 5 seeds complete")
    print()

    # Generate figures
    print("Generating Figure 1: Multi-scale trajectory...")
    generate_trajectory_figure()
    print()

    print("Generating Figure 2: Spawns/agent threshold analysis...")
    generate_threshold_figure()
    print()

    print("=" * 80)
    print("PRELIMINARY FIGURES COMPLETE")
    print("=" * 80)
    print()
    print("✓ Two publication-quality figures @ 300 DPI generated")
    print("✓ Ready for Paper 2 integration when validation completes")
    print()
    print("Next: Finalize figures with all 5 seeds when incremental validation done")
    print()

if __name__ == "__main__":
    main()
