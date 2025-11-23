#!/usr/bin/env python3
"""
Graphical Abstract Generator for C186 Hierarchical Advantage Manuscript
Generates 1200×600 px @ 300 DPI publication-quality PNG for Nature Communications

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1077)
License: GPL-3.0
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyBboxPatch, FancyArrowPatch, Rectangle, Wedge
import numpy as np

# Color palette (from specification)
COLOR_FLAT = '#2E86C1'          # Blue for flat/single-scale
COLOR_HIERARCHICAL = '#27AE60'  # Green for hierarchical
COLOR_FAILURE = '#E74C3C'       # Red for failure/struggle
COLOR_ENERGY = '#F39C12'        # Orange/yellow for energy
COLOR_BG = '#F8F9F9'            # Light gray background
COLOR_TEXT = '#2C3E50'          # Dark gray/charcoal text

def draw_panel_1_puzzle(ax):
    """Panel 1: The Puzzle - Flat vs Hierarchical comparison"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'THE PUZZLE', ha='center', va='top',
            fontsize=14, fontweight='bold', color=COLOR_TEXT)

    # Flat system (top)
    ax.text(5, 8.5, 'Flat System', ha='center', va='top',
            fontsize=10, fontweight='bold', color=COLOR_FLAT)
    flat_circle = Circle((5, 6.5), 1.5, facecolor=COLOR_FLAT, alpha=0.3,
                         edgecolor=COLOR_FLAT, linewidth=2)
    ax.add_patch(flat_circle)

    # Draw agents as dots in flat system (200 agents)
    np.random.seed(42)
    for _ in range(40):  # Representative subset
        angle = np.random.uniform(0, 2*np.pi)
        radius = np.random.uniform(0, 1.3)
        x = 5 + radius * np.cos(angle)
        y = 6.5 + radius * np.sin(angle)
        ax.plot(x, y, 'o', color=COLOR_FLAT, markersize=2)

    ax.text(5, 4.8, '200 agents\n1 population', ha='center', va='top',
            fontsize=8, color=COLOR_TEXT, style='italic')

    # Hierarchical system (bottom)
    ax.text(5, 4.0, 'Hierarchical System', ha='center', va='top',
            fontsize=10, fontweight='bold', color=COLOR_HIERARCHICAL)

    # Draw 10 compartments (2 rows of 5)
    compartment_positions = [
        (2, 2.5), (3.2, 2.5), (4.4, 2.5), (5.6, 2.5), (6.8, 2.5),
        (2, 1.2), (3.2, 1.2), (4.4, 1.2), (5.6, 1.2), (6.8, 1.2)
    ]

    for x, y in compartment_positions:
        comp_circle = Circle((x, y), 0.35, facecolor=COLOR_HIERARCHICAL, alpha=0.3,
                            edgecolor=COLOR_HIERARCHICAL, linewidth=1.5)
        ax.add_patch(comp_circle)

        # Add agents to compartment (20 agents each)
        for _ in range(4):  # Representative subset
            angle = np.random.uniform(0, 2*np.pi)
            radius = np.random.uniform(0, 0.25)
            agent_x = x + radius * np.cos(angle)
            agent_y = y + radius * np.sin(angle)
            ax.plot(agent_x, agent_y, 'o', color=COLOR_HIERARCHICAL, markersize=1.5)

    # Migration arrows (weak connectivity)
    for i in range(len(compartment_positions) - 1):
        x1, y1 = compartment_positions[i]
        x2, y2 = compartment_positions[i + 1]
        arrow = FancyArrowPatch((x1 + 0.35, y1), (x2 - 0.35, y2),
                               arrowstyle='->', mutation_scale=8,
                               color=COLOR_HIERARCHICAL, alpha=0.4, linewidth=0.5)
        ax.add_patch(arrow)

    ax.text(5, 0.3, '200 agents\n10 populations\n0.5% migration', ha='center', va='top',
            fontsize=8, color=COLOR_TEXT, style='italic')

    # Question mark
    ax.text(5, 4.5, '?', ha='center', va='center',
            fontsize=24, fontweight='bold', color=COLOR_TEXT)


def draw_panel_2_finding(ax):
    """Panel 2: The Finding - Bar chart comparison"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'THE FINDING', ha='center', va='top',
            fontsize=14, fontweight='bold', color=COLOR_TEXT)

    # Bar chart
    bar_width = 1.2
    flat_height = 5.0  # Represents ~6.25%
    hier_height = 0.8  # Represents <1.0%

    # Flat bar
    flat_bar = Rectangle((2.9, 2), bar_width, flat_height,
                         facecolor=COLOR_FLAT, edgecolor=COLOR_FLAT, linewidth=2)
    ax.add_patch(flat_bar)
    ax.text(3.5, 2 + flat_height + 0.2, '6.25%', ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=COLOR_FLAT)
    ax.text(3.5, 1.5, 'Flat', ha='center', va='top',
            fontsize=9, color=COLOR_TEXT)

    # Hierarchical bar
    hier_bar = Rectangle((5.9, 2), bar_width, hier_height,
                         facecolor=COLOR_HIERARCHICAL, edgecolor=COLOR_HIERARCHICAL, linewidth=2)
    ax.add_patch(hier_bar)
    ax.text(6.5, 2 + hier_height + 0.2, '<1.0%', ha='center', va='bottom',
            fontsize=11, fontweight='bold', color=COLOR_HIERARCHICAL)
    ax.text(6.5, 1.5, 'Hierarchical', ha='center', va='top',
            fontsize=9, color=COLOR_TEXT)

    # Y-axis label
    ax.text(1.8, 5, 'Critical Spawn\nFrequency', ha='right', va='center',
            fontsize=9, color=COLOR_TEXT, rotation=90)

    # Efficiency arrow
    arrow_y = 7.5
    ax.annotate('', xy=(6.5, arrow_y), xytext=(3.5, arrow_y),
                arrowprops=dict(arrowstyle='->', lw=2, color=COLOR_TEXT))
    ax.text(5, arrow_y + 0.3, 'α < 0.5', ha='center', va='bottom',
            fontsize=12, fontweight='bold', color=COLOR_TEXT,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))

    # Surprise annotation
    ax.text(5, 8.5, 'Hierarchy needs <50% frequency\n(not 2× as predicted!)',
            ha='center', va='top', fontsize=9, color=COLOR_TEXT,
            style='italic')

    # Exclamation mark
    ax.text(8.5, 6, '!', ha='center', va='center',
            fontsize=20, fontweight='bold', color=COLOR_FAILURE)


def draw_panel_3_mechanisms(ax):
    """Panel 3: Three Mechanisms"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'THREE MECHANISMS', ha='center', va='top',
            fontsize=14, fontweight='bold', color=COLOR_TEXT)

    # Mechanism 1: Risk Isolation (top third)
    y_top = 8.0
    ax.text(5, y_top, '1. Risk Isolation', ha='center', va='top',
            fontsize=10, fontweight='bold', color=COLOR_TEXT)

    # Draw compartments - one failed (red), others healthy (green)
    comp_y = y_top - 1.2
    for i, x in enumerate([2.5, 3.5, 4.5, 5.5, 6.5, 7.5]):
        color = COLOR_FAILURE if i == 2 else COLOR_HIERARCHICAL
        alpha = 0.6 if i == 2 else 0.3
        comp = Circle((x, comp_y), 0.3, facecolor=color, alpha=alpha,
                     edgecolor=color, linewidth=1.5)
        ax.add_patch(comp)

    ax.text(5, comp_y - 0.6, 'Failure contained locally', ha='center', va='top',
            fontsize=8, color=COLOR_TEXT, style='italic')

    # Mechanism 2: Migration Rescue (middle third)
    y_mid = 5.0
    ax.text(5, y_mid, '2. Migration Rescue', ha='center', va='top',
            fontsize=10, fontweight='bold', color=COLOR_TEXT)

    # Draw source and sink populations with arrows
    comp_y_rescue = y_mid - 1.2

    # Large (source) population
    source = Circle((3, comp_y_rescue), 0.4, facecolor=COLOR_HIERARCHICAL, alpha=0.5,
                   edgecolor=COLOR_HIERARCHICAL, linewidth=2)
    ax.add_patch(source)
    ax.text(3, comp_y_rescue, 'S', ha='center', va='center',
            fontsize=9, fontweight='bold', color=COLOR_HIERARCHICAL)

    # Small (sink) population
    sink = Circle((7, comp_y_rescue), 0.25, facecolor=COLOR_FAILURE, alpha=0.3,
                 edgecolor=COLOR_FAILURE, linewidth=2)
    ax.add_patch(sink)
    ax.text(7, comp_y_rescue, 's', ha='center', va='center',
            fontsize=7, fontweight='bold', color=COLOR_FAILURE)

    # Migration arrow
    migration_arrow = FancyArrowPatch((3.4, comp_y_rescue), (6.75, comp_y_rescue),
                                     arrowstyle='->', mutation_scale=15,
                                     color=COLOR_HIERARCHICAL, linewidth=2)
    ax.add_patch(migration_arrow)
    ax.text(5, comp_y_rescue + 0.15, '0.5%/cycle', ha='center', va='bottom',
            fontsize=7, color=COLOR_TEXT, bbox=dict(boxstyle='round,pad=0.2',
            facecolor='white', alpha=0.8))

    ax.text(5, comp_y_rescue - 0.6, 'Demographic support', ha='center', va='top',
            fontsize=8, color=COLOR_TEXT, style='italic')

    # Mechanism 3: Energy Discipline (bottom third)
    y_bottom = 2.0
    ax.text(5, y_bottom, '3. Energy Discipline', ha='center', va='top',
            fontsize=10, fontweight='bold', color=COLOR_TEXT)

    # Draw compartments with energy meters
    comp_y_energy = y_bottom - 1.2
    for i, x in enumerate([2.5, 3.5, 4.5, 5.5, 6.5, 7.5]):
        # Compartment
        comp = Circle((x, comp_y_energy), 0.3, facecolor=COLOR_HIERARCHICAL, alpha=0.2,
                     edgecolor=COLOR_HIERARCHICAL, linewidth=1.5)
        ax.add_patch(comp)

        # Energy meter (vertical bar)
        energy_level = np.random.uniform(0.4, 0.8)
        meter = Rectangle((x - 0.08, comp_y_energy - 0.15), 0.16, energy_level * 0.3,
                         facecolor=COLOR_ENERGY, alpha=0.7, edgecolor=COLOR_TEXT, linewidth=0.5)
        ax.add_patch(meter)

    ax.text(5, comp_y_energy - 0.5, 'Local sustainability', ha='center', va='top',
            fontsize=8, color=COLOR_TEXT, style='italic')


def draw_panel_4_applications(ax):
    """Panel 4: Cross-domain Applications"""
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')

    # Title
    ax.text(5, 9.5, 'APPLICATIONS', ha='center', va='top',
            fontsize=14, fontweight='bold', color=COLOR_TEXT)

    applications = [
        ('Metapopulations', 8.0, '🌳'),
        ('Neural Modules', 6.0, '🧠'),
        ('Immune System', 4.0, '🛡️'),
        ('Microservices', 2.0, '💻')
    ]

    for label, y, icon in applications:
        # Icon placeholder (use simple shapes since emoji rendering varies)
        if 'Meta' in label:
            # Tree/habitat fragments
            for dx in [-0.4, 0, 0.4]:
                tree_base = Circle((5 + dx, y), 0.15, facecolor=COLOR_HIERARCHICAL, alpha=0.5)
                ax.add_patch(tree_base)
                ax.plot([5 + dx, 5 + dx], [y, y + 0.3], color=COLOR_HIERARCHICAL, linewidth=2)
            # Connection arrows
            for dx in [-0.2, 0.2]:
                arr = FancyArrowPatch((5 + dx - 0.15, y), (5 + dx + 0.15, y),
                                     arrowstyle='<->', mutation_scale=6,
                                     color=COLOR_HIERARCHICAL, alpha=0.3, linewidth=1)
                ax.add_patch(arr)

        elif 'Neural' in label:
            # Brain modules
            brain_shape = Wedge((5, y), 0.5, 0, 180, facecolor=COLOR_HIERARCHICAL, alpha=0.3)
            ax.add_patch(brain_shape)
            # Module divisions
            for angle in [45, 90, 135]:
                rad = np.radians(angle)
                ax.plot([5, 5 + 0.5*np.cos(rad)], [y, y + 0.5*np.sin(rad)],
                       color=COLOR_HIERARCHICAL, linewidth=1.5)

        elif 'Immune' in label:
            # Lymph nodes
            for dx in [-0.3, 0.3]:
                node = Circle((5 + dx, y), 0.2, facecolor=COLOR_HIERARCHICAL, alpha=0.5,
                            edgecolor=COLOR_HIERARCHICAL, linewidth=1.5)
                ax.add_patch(node)
            # Connecting vessel
            ax.plot([4.7, 5.3], [y, y], color=COLOR_HIERARCHICAL, linewidth=2)

        else:  # Microservices
            # Server clusters
            for i, dx in enumerate([-0.4, -0.1, 0.2]):
                server = Rectangle((5 + dx - 0.12, y - 0.15), 0.24, 0.3,
                                  facecolor=COLOR_HIERARCHICAL, alpha=0.4,
                                  edgecolor=COLOR_HIERARCHICAL, linewidth=1.5)
                ax.add_patch(server)
                # Network connections
                if i < 2:
                    ax.plot([5 + dx + 0.12, 5 + dx + 0.18], [y, y],
                           color=COLOR_HIERARCHICAL, linewidth=1, linestyle='--')

        ax.text(5, y - 0.6, label, ha='center', va='top',
                fontsize=9, color=COLOR_TEXT, fontweight='bold')


def generate_graphical_abstract():
    """Generate complete graphical abstract"""
    # Set up figure with 4 panels
    # 1200×600 pixels @ 300 DPI = 4"×2" physical size
    fig = plt.figure(figsize=(4, 2), dpi=300, facecolor=COLOR_BG)

    # Create 4 subplots with appropriate widths
    # Panel widths: 25%, 25%, 30%, 20%
    gs = fig.add_gridspec(1, 4, width_ratios=[0.25, 0.25, 0.30, 0.20],
                          left=0.02, right=0.98, top=0.96, bottom=0.04,
                          wspace=0.05)

    ax1 = fig.add_subplot(gs[0])  # The Puzzle
    ax2 = fig.add_subplot(gs[1])  # The Finding
    ax3 = fig.add_subplot(gs[2])  # Three Mechanisms
    ax4 = fig.add_subplot(gs[3])  # Applications

    # Draw each panel
    draw_panel_1_puzzle(ax1)
    draw_panel_2_finding(ax2)
    draw_panel_3_mechanisms(ax3)
    draw_panel_4_applications(ax4)

    # Add overall title (optional)
    fig.text(0.5, 0.985, 'Resilience Through Redundancy: Hierarchical Advantage in Energy-Constrained Systems',
             ha='center', va='top', fontsize=13, fontweight='bold', color=COLOR_TEXT)

    # Save as PNG at 300 DPI WITHOUT bbox_inches='tight' to preserve exact dimensions
    temp_path = '/tmp/c186_graphical_abstract_temp.png'
    plt.savefig(temp_path, dpi=300, facecolor=COLOR_BG, edgecolor='none')
    plt.close()

    # Resize to EXACT 1200×600 pixels using PIL
    from PIL import Image
    img = Image.open(temp_path)
    img_resized = img.resize((1200, 600), Image.LANCZOS)

    # Set DPI metadata
    output_path = '/Volumes/dual/DUALITY-ZERO-V2/data/figures/c186_graphical_abstract.png'
    img_resized.save(output_path, dpi=(300, 300))
    print(f"Graphical abstract saved to: {output_path}")

    # Also save a thumbnail for preview (200×100 px per specification)
    thumbnail_path = '/Volumes/dual/DUALITY-ZERO-V2/data/figures/c186_graphical_abstract_thumbnail.png'
    img_thumbnail = img_resized.resize((200, 100), Image.LANCZOS)
    img_thumbnail.save(thumbnail_path, dpi=(300, 300))
    print(f"Thumbnail saved to: {thumbnail_path}")

    # Cleanup temp file
    import os
    os.remove(temp_path)

    # Print file info
    import os
    file_size = os.path.getsize(output_path)
    print(f"\nFile size: {file_size / 1024 / 1024:.2f} MB")

    if file_size > 5 * 1024 * 1024:
        print("⚠️  WARNING: File size exceeds 5 MB Nature Communications limit!")
    else:
        print("✅ File size within 5 MB limit")

    return output_path


if __name__ == '__main__':
    print("="*70)
    print("C186 Graphical Abstract Generator")
    print("Nature Communications Submission")
    print("="*70)
    print()

    output_path = generate_graphical_abstract()

    print("\n" + "="*70)
    print("Graphical Abstract Generation Complete")
    print("="*70)
    print(f"Output: {output_path}")
    print("\nSpecifications:")
    print("  - Dimensions: 1200×600 pixels (4\"×2\" at 300 DPI)")
    print("  - Format: PNG")
    print("  - Color Space: RGB")
    print("  - Background: Light gray (#F8F9F9)")
    print("\nNext Steps:")
    print("  1. Review graphical abstract for clarity and impact")
    print("  2. Test thumbnail readability (200×100 px)")
    print("  3. Validate colorblind-friendly palette")
    print("  4. Integrate into Nature Communications submission")
    print("="*70)
