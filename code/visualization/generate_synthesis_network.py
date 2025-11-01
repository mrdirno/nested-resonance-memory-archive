#!/usr/bin/env python
"""
Cross-Paper Synthesis Network Visualization

Generates a publication-quality network diagram showing the 5 major themes
from the NRM research synthesis and their connections across all 9 papers.

Based on: archive/NRM_RESEARCH_SYNTHESIS_2025.md (Cycle 798)

Author: Aldrin Payopay
Email: aldrin.gdf@gmail.com
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
License: GPL-3.0
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

# Theme and paper connections (from research synthesis)
themes = {
    'Theme 1: Reality Grounding': {
        'papers': ['Paper 1', 'Paper 3', 'Paper 8'],
        'color': '#3498db',  # Blue
        'key_finding': '±5% threshold validates computational expense',
        'position': (0.2, 0.75)
    },
    'Theme 2: Multi-Timescale': {
        'papers': ['Paper 6', 'Paper 6B', 'Paper 7'],
        'color': '#2ecc71',  # Green
        'key_finding': '235× timescale separation (τ=557 vs τ=2.37)',
        'position': (0.8, 0.75)
    },
    'Theme 3: Regime Boundaries': {
        'papers': ['Paper 2', 'Paper 7'],
        'color': '#e74c3c',  # Red
        'key_finding': 'V4 boundaries match empirical transitions',
        'position': (0.2, 0.45)
    },
    'Theme 4: Stochastic Dynamics': {
        'papers': ['Paper 4', 'Paper 7'],
        'color': '#f39c12',  # Orange
        'key_finding': 'Demographic noise maintains persistent variance',
        'position': (0.5, 0.25)
    },
    'Theme 5: Pattern Mining': {
        'papers': ['Paper 5D'],
        'color': '#9b59b6',  # Purple
        'key_finding': '80% replicability + noise-aware thresholds',
        'position': (0.8, 0.45)
    },
}

# Novel discoveries (from synthesis)
discoveries = [
    'Fractal Overhead (Paper 3)',
    'Reality-Grounding Signature (Papers 3,8)',
    '235× Timescale Separation (Paper 7)',
    'Demographic Noise Persistence (Paper 7)',
]

# Create figure
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Draw themes as boxes
theme_boxes = {}
for theme_name, theme_data in themes.items():
    x, y = theme_data['position']

    # Theme box
    box = FancyBboxPatch(
        (x - 0.12, y - 0.08), 0.24, 0.16,
        boxstyle="round,pad=0.01",
        edgecolor=theme_data['color'],
        facecolor=theme_data['color'],
        alpha=0.2,
        linewidth=2.5
    )
    ax.add_patch(box)

    # Theme label (bold, larger)
    ax.text(x, y + 0.05, theme_name.split(':')[1].strip(),
            ha='center', va='center',
            fontsize=11, fontweight='bold',
            color=theme_data['color'])

    # Papers involved (smaller)
    papers_text = ' | '.join(theme_data['papers'])
    ax.text(x, y + 0.01, papers_text,
            ha='center', va='center',
            fontsize=8, style='italic')

    # Key finding (smaller, wrapped)
    finding = theme_data['key_finding']
    if len(finding) > 40:
        # Wrap long findings
        mid = len(finding) // 2
        space_idx = finding.find(' ', mid - 10, mid + 10)
        if space_idx != -1:
            finding = finding[:space_idx] + '\n' + finding[space_idx+1:]
    ax.text(x, y - 0.04, finding,
            ha='center', va='center',
            fontsize=7, color='gray')

    theme_boxes[theme_name] = (x, y)

# Draw connections between themes with shared papers
# Paper 7 appears in Themes 2, 3, 4 - connect them
connections = [
    ('Theme 2: Multi-Timescale', 'Theme 3: Regime Boundaries', 'Paper 7', 'solid'),
    ('Theme 2: Multi-Timescale', 'Theme 4: Stochastic Dynamics', 'Paper 7', 'solid'),
    ('Theme 3: Regime Boundaries', 'Theme 4: Stochastic Dynamics', 'Paper 7', 'solid'),
    ('Theme 1: Reality Grounding', 'Theme 3: Regime Boundaries', 'Validation', 'dashed'),
]

for theme1, theme2, label, style in connections:
    x1, y1 = theme_boxes[theme1]
    x2, y2 = theme_boxes[theme2]

    # Draw arrow
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle='-',
        linestyle=style,
        color='gray',
        alpha=0.4,
        linewidth=1.5 if style == 'solid' else 1.0,
        zorder=1
    )
    ax.add_patch(arrow)

    # Label (midpoint)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my, label,
               ha='center', va='center',
               fontsize=7, color='gray',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8,
                        edgecolor='none'),
               zorder=2)

# Add central synthesis circle
cx, cy = 0.5, 0.55
circle = plt.Circle((cx, cy), 0.08, color='gold', alpha=0.3, zorder=0)
ax.add_patch(circle)
ax.text(cx, cy + 0.02, 'NRM Research\nSynthesis',
       ha='center', va='center',
       fontsize=10, fontweight='bold')
ax.text(cx, cy - 0.03, '9 Papers',
       ha='center', va='center',
       fontsize=8, style='italic', color='gray')

# Add novel discoveries box (bottom)
discoveries_y = 0.08
ax.text(0.5, discoveries_y + 0.06, 'Novel Discoveries (4)',
       ha='center', va='center',
       fontsize=11, fontweight='bold')
for i, discovery in enumerate(discoveries):
    x_pos = 0.15 + (i * 0.2)
    ax.text(x_pos, discoveries_y, f'• {discovery}',
           ha='left', va='center',
           fontsize=8, color='darkgreen')

# Add portfolio summary (top)
summary_text = (
    'Research Portfolio Synthesis: 5 Major Themes Across 9 Papers\n'
    '200+ Experiments | 450,000+ Simulation Cycles | 0.913/1.0 Reproducibility'
)
ax.text(0.5, 0.95, summary_text,
       ha='center', va='top',
       fontsize=12, fontweight='bold',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.3))

# Add legend for theme categories
legend_elements = []
for theme_name, theme_data in themes.items():
    theme_short = theme_name.split(':')[1].strip()
    papers_count = len(theme_data['papers'])
    legend_elements.append(
        mpatches.Patch(
            facecolor=theme_data['color'],
            edgecolor=theme_data['color'],
            alpha=0.3,
            label=f'{theme_short} ({papers_count} papers)'
        )
    )

ax.legend(handles=legend_elements,
         loc='lower right',
         framealpha=0.9,
         fontsize=9,
         title='Themes by Paper Count')

# Add temporal stewardship note
note_text = (
    'Temporal Stewardship Encoding:\n'
    'Formulae: r(t)=0.025-0.0013t, τ_slow/τ_fast=235, CV=√(1/N)\n'
    'Protocols: ±5% threshold, 80% replicability, tier ranking\n'
    'Patterns: Extreme I/O-bound signature, memory fragmentation'
)
ax.text(0.02, 0.02, note_text,
       ha='left', va='bottom',
       fontsize=7, color='gray',
       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.5))

plt.tight_layout()

# Save figure
output_path = '/Users/aldrinpayopay/nested-resonance-memory-archive/data/figures/research_synthesis_network.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Synthesis network visualization saved to: {output_path}")
print(f"Figure size: 14×10 inches @ 300 DPI")
print(f"\nThemes Summary:")
print(f"  Total themes: {len(themes)}")
print(f"  Papers involved: 9 (Papers 1-8 + 5D)")
print(f"  Theme with most papers: Multi-Timescale (3 papers)")
print(f"  Novel discoveries: {len(discoveries)}")
print(f"\nCross-Theme Connections:")
print(f"  Paper 7 appears in 3 themes (central to synthesis)")
print(f"  Papers 3,8 share Reality Grounding theme")
print(f"  Papers 6,6B,7 form Multi-Timescale cluster")

plt.show()
