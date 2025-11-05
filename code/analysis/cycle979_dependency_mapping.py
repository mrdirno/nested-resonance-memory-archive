#!/usr/bin/env python3
"""
Cycle 979: Pattern Dependency Mapping

Identifies dependencies between 123 patterns using:
1. Content dependency: Pattern A references Pattern B's content
2. Temporal dependency: Pattern A appeared after Pattern B (potential foundation)
3. Category dependency: SF → MP → FP → MR → TS hierarchical flow

Creates dependency network to identify:
- Foundational patterns (high out-degree: many patterns depend on them)
- Derived patterns (high in-degree: depend on many patterns)
- Independent patterns (isolated nodes)

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import pandas as pd
import re
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

# File paths
PATTERN_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_DATABASE.csv"
LINEAGE_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_LINEAGE.csv"
OUTPUT_CSV = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_DEPENDENCIES.csv"
OUTPUT_FIG = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/pattern_dependency_network.png"

# Category hierarchy (for hierarchical dependencies)
CATEGORY_HIERARCHY = {
    'SF': 1,  # Scientific Findings (foundation)
    'MP': 2,  # Methodological Principles (build on findings)
    'FP': 3,  # Framework Principles (synthesize methods)
    'MR': 4,  # Meta-Research (reflect on process)
    'TS': 5   # Temporal Stewardship (highest abstraction)
}

def load_patterns():
    """Load pattern database and lineage data"""
    patterns = pd.read_csv(PATTERN_DB, quotechar='"', escapechar='\\')
    lineage = pd.read_csv(LINEAGE_DB)

    # Merge to get cycle numbers
    merged = patterns.merge(
        lineage[['Pattern_ID', 'First_Cycle_Num', 'Last_Cycle_Num', 'Lifespan_Cycles']],
        on='Pattern_ID',
        how='left'
    )
    return merged

def extract_pattern_references(content):
    """Extract pattern IDs mentioned in content (e.g., 'P2-SF-011')"""
    # Pattern ID format: PREFIX-CATEGORY-NUMBER
    # Examples: P2-SF-011, CS-TS-001, CC-MP-006, FD-OP-001
    pattern = r'\b([A-Z]{1,2}-[A-Z]{2}-\d{3})\b'
    matches = re.findall(pattern, content)
    return list(set(matches))  # Unique references

def identify_content_dependencies(patterns_df):
    """Find patterns that reference other patterns in their content"""
    dependencies = []

    for idx, row in patterns_df.iterrows():
        pattern_id = row['Pattern_ID']
        content = str(row['Content'])

        # Find pattern IDs mentioned in content
        referenced_patterns = extract_pattern_references(content)

        for ref_pattern in referenced_patterns:
            if ref_pattern != pattern_id:  # Don't self-reference
                dependencies.append({
                    'Pattern_ID': pattern_id,
                    'Depends_On': ref_pattern,
                    'Dependency_Type': 'Content',
                    'Strength': 'Strong'  # Explicit reference
                })

    return dependencies

def identify_temporal_dependencies(patterns_df, min_cycle_gap=50):
    """
    Patterns that appeared significantly earlier may be foundational.
    Temporal dependency: Pattern A depends on Pattern B if:
    - B appeared ≥50 cycles before A
    - Same category or related framework
    """
    dependencies = []

    for idx_a, row_a in patterns_df.iterrows():
        pattern_a = row_a['Pattern_ID']
        cycle_a = row_a['First_Cycle_Num']
        category_a = row_a['Category']
        framework_a = row_a['Framework']

        if pd.isna(cycle_a):
            continue

        for idx_b, row_b in patterns_df.iterrows():
            if idx_a == idx_b:
                continue

            pattern_b = row_b['Pattern_ID']
            cycle_b = row_b['First_Cycle_Num']
            category_b = row_b['Category']
            framework_b = row_b['Framework']

            if pd.isna(cycle_b):
                continue

            # Pattern B appeared significantly earlier
            if cycle_b + min_cycle_gap <= cycle_a:
                # Same category or related framework
                if category_a == category_b or framework_a == framework_b:
                    dependencies.append({
                        'Pattern_ID': pattern_a,
                        'Depends_On': pattern_b,
                        'Dependency_Type': 'Temporal',
                        'Strength': 'Moderate'
                    })

    return dependencies

def identify_category_dependencies(patterns_df):
    """
    Category hierarchy: SF → MP → FP → MR → TS
    Higher-level patterns may depend on lower-level patterns of same framework
    """
    dependencies = []

    for idx_a, row_a in patterns_df.iterrows():
        pattern_a = row_a['Pattern_ID']
        category_a = row_a['Category']
        framework_a = row_a['Framework']

        level_a = CATEGORY_HIERARCHY.get(category_a, 0)

        for idx_b, row_b in patterns_df.iterrows():
            if idx_a == idx_b:
                continue

            pattern_b = row_b['Pattern_ID']
            category_b = row_b['Category']
            framework_b = row_b['Framework']

            level_b = CATEGORY_HIERARCHY.get(category_b, 0)

            # Pattern A (higher level) may depend on Pattern B (lower level)
            # Same framework increases likelihood
            if level_a > level_b and framework_a == framework_b:
                dependencies.append({
                    'Pattern_ID': pattern_a,
                    'Depends_On': pattern_b,
                    'Dependency_Type': 'Category',
                    'Strength': 'Weak'
                })

    return dependencies

def create_dependency_network(dependencies_df, patterns_df):
    """Create NetworkX directed graph"""
    G = nx.DiGraph()

    # Add all patterns as nodes
    for idx, row in patterns_df.iterrows():
        G.add_node(
            row['Pattern_ID'],
            category=row['Category'],
            framework=row['Framework'],
            lifespan=row.get('Lifespan_Cycles', 0)
        )

    # Add edges (dependencies)
    for idx, row in dependencies_df.iterrows():
        source = row['Pattern_ID']  # Pattern that depends
        target = row['Depends_On']  # Pattern being depended on
        dep_type = row['Dependency_Type']
        strength = row['Strength']

        # Only add edge if both nodes exist
        if source in G.nodes and target in G.nodes:
            G.add_edge(
                source,
                target,
                type=dep_type,
                strength=strength
            )

    return G

def analyze_network(G):
    """Calculate network statistics"""
    stats = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'density': nx.density(G),
        'avg_in_degree': sum(dict(G.in_degree()).values()) / G.number_of_nodes(),
        'avg_out_degree': sum(dict(G.out_degree()).values()) / G.number_of_nodes(),
    }

    # Identify foundational patterns (high in-degree = many depend on them)
    in_degrees = dict(G.in_degree())
    foundational = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:10]

    # Identify derived patterns (high out-degree = depend on many)
    out_degrees = dict(G.out_degree())
    derived = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:10]

    # Identify isolated patterns (no dependencies)
    isolated = [node for node in G.nodes() if G.degree(node) == 0]

    stats['foundational_top10'] = foundational
    stats['derived_top10'] = derived
    stats['isolated_count'] = len(isolated)
    stats['isolated_patterns'] = isolated

    return stats

def visualize_network(G, output_path):
    """Create network visualization"""
    plt.figure(figsize=(16, 12), dpi=300)

    # Layout
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)

    # Node colors by category
    category_colors = {
        'SF': '#1f77b4',  # Blue
        'MP': '#ff7f0e',  # Orange
        'FP': '#2ca02c',  # Green
        'MR': '#d62728',  # Red
        'TS': '#9467bd'   # Purple
    }

    node_colors = [category_colors.get(G.nodes[node].get('category', 'SF'), 'gray')
                   for node in G.nodes()]

    # Node sizes by in-degree (foundational patterns larger)
    in_degrees = dict(G.in_degree())
    node_sizes = [100 + in_degrees.get(node, 0) * 50 for node in G.nodes()]

    # Draw network
    nx.draw_networkx_nodes(
        G, pos,
        node_color=node_colors,
        node_size=node_sizes,
        alpha=0.7
    )

    nx.draw_networkx_edges(
        G, pos,
        alpha=0.3,
        arrows=True,
        arrowsize=10,
        edge_color='gray'
    )

    # Labels (only show top 20 by in-degree)
    top_20_nodes = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    top_20_ids = [node for node, _ in top_20_nodes]
    labels = {node: node for node in top_20_ids}

    nx.draw_networkx_labels(
        G, pos,
        labels=labels,
        font_size=6
    )

    plt.title("Pattern Dependency Network (123 Patterns)\nNode size = Foundational strength (in-degree)",
              fontsize=14, fontweight='bold')

    # Legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color,
                   markersize=10, label=category)
        for category, color in category_colors.items()
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Network visualization saved: {output_path}")
    plt.close()

def main():
    print("="*80)
    print("CYCLE 979: PATTERN DEPENDENCY MAPPING")
    print("="*80)
    print()

    # Load data
    print("Loading patterns and lineage data...")
    patterns_df = load_patterns()
    print(f"  → {len(patterns_df)} patterns loaded")
    print()

    # Identify dependencies
    print("Identifying content dependencies...")
    content_deps = identify_content_dependencies(patterns_df)
    print(f"  → {len(content_deps)} content dependencies found")
    print()

    print("Identifying temporal dependencies (≥50 cycle gap)...")
    temporal_deps = identify_temporal_dependencies(patterns_df, min_cycle_gap=50)
    print(f"  → {len(temporal_deps)} temporal dependencies found")
    print()

    print("Identifying category dependencies (SF→MP→FP→MR→TS)...")
    category_deps = identify_category_dependencies(patterns_df)
    print(f"  → {len(category_deps)} category dependencies found")
    print()

    # Combine all dependencies
    all_deps = content_deps + temporal_deps + category_deps
    dependencies_df = pd.DataFrame(all_deps)

    print(f"Total dependencies identified: {len(dependencies_df)}")
    print(f"  - Content (Strong): {len(content_deps)}")
    print(f"  - Temporal (Moderate): {len(temporal_deps)}")
    print(f"  - Category (Weak): {len(category_deps)}")
    print()

    # Save dependencies
    print(f"Saving dependencies: {OUTPUT_CSV}")
    dependencies_df.to_csv(OUTPUT_CSV, index=False)
    print(f"  → {len(dependencies_df)} dependencies saved")
    print()

    # Create network
    print("Creating dependency network...")
    G = create_dependency_network(dependencies_df, patterns_df)
    print(f"  → Network created: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print()

    # Analyze network
    print("Analyzing network properties...")
    stats = analyze_network(G)
    print(f"  Density: {stats['density']:.4f}")
    print(f"  Average in-degree: {stats['avg_in_degree']:.2f}")
    print(f"  Average out-degree: {stats['avg_out_degree']:.2f}")
    print(f"  Isolated patterns: {stats['isolated_count']}")
    print()

    print("Top 10 Foundational Patterns (most depended upon):")
    for pattern, in_degree in stats['foundational_top10']:
        category = G.nodes[pattern].get('category', 'Unknown')
        print(f"  {pattern} (in-degree={in_degree}, category={category})")
    print()

    print("Top 10 Derived Patterns (depend on most others):")
    for pattern, out_degree in stats['derived_top10']:
        category = G.nodes[pattern].get('category', 'Unknown')
        print(f"  {pattern} (out-degree={out_degree}, category={category})")
    print()

    # Visualize
    print("Creating network visualization...")
    visualize_network(G, OUTPUT_FIG)
    print()

    print("="*80)
    print("CYCLE 979 ANALYSIS COMPLETE")
    print("="*80)
    print()
    print(f"Outputs:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_FIG}")
    print()
    print(f"Next: Cycle 980 (Cluster Identification)")
    print()

if __name__ == '__main__':
    main()
