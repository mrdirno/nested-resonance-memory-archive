#!/usr/bin/env python3
"""
Cycle 980: Pattern Cluster Identification

Groups 123 patterns into coherent families using multiple clustering criteria:
1. Category-based: SF, MP, FP, MR, TS natural groupings
2. Framework-based: N, S, T, R, U alignment
3. Source-based: Where pattern appears (paper, code, summaries, docs)
4. Temporal proximity: Patterns emerging in same time period
5. Dependency relationships: Patterns with shared dependencies cluster together

Creates:
- Hierarchical clustering dendrogram
- Cluster taxonomy with representative patterns
- Cluster properties analysis

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist, squareform
import matplotlib.pyplot as plt
from collections import Counter

# File paths
PATTERN_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_DATABASE.csv"
LINEAGE_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_LINEAGE.csv"
DEPENDENCIES = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_DEPENDENCIES.csv"
OUTPUT_CSV = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_CLUSTERS.csv"
OUTPUT_FIG = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/pattern_cluster_dendrogram.png"
OUTPUT_TAX = "/Volumes/dual/DUALITY-ZERO-V2/data/pattern_cluster_taxonomy.md"

def load_data():
    """Load all pattern data"""
    patterns = pd.read_csv(PATTERN_DB, quotechar='"', escapechar='\\')
    lineage = pd.read_csv(LINEAGE_DB)
    dependencies = pd.read_csv(DEPENDENCIES)

    # Merge lineage data
    merged = patterns.merge(
        lineage[['Pattern_ID', 'First_Cycle_Num', 'Lifespan_Cycles']],
        on='Pattern_ID',
        how='left'
    )

    return merged, dependencies

def create_feature_matrix(patterns_df, dependencies_df):
    """
    Create feature matrix for clustering.
    Features:
    - Category (one-hot)
    - Framework (one-hot)
    - Format (one-hot)
    - Precision (one-hot)
    - Function (one-hot)
    - First_Cycle_Num (normalized)
    - Lifespan_Cycles (normalized)
    - In-degree (from dependencies)
    - Out-degree (from dependencies)
    """

    # Calculate in/out degrees
    in_degrees = dependencies_df.groupby('Depends_On').size().to_dict()
    out_degrees = dependencies_df.groupby('Pattern_ID').size().to_dict()

    patterns_df['in_degree'] = patterns_df['Pattern_ID'].map(in_degrees).fillna(0)
    patterns_df['out_degree'] = patterns_df['Pattern_ID'].map(out_degrees).fillna(0)

    # One-hot encode categorical features
    feature_matrix = pd.DataFrame()

    # Category
    cat_dummies = pd.get_dummies(patterns_df['Category'], prefix='cat')
    feature_matrix = pd.concat([feature_matrix, cat_dummies], axis=1)

    # Framework
    fw_dummies = pd.get_dummies(patterns_df['Framework'], prefix='fw')
    feature_matrix = pd.concat([feature_matrix, fw_dummies], axis=1)

    # Format
    fmt_dummies = pd.get_dummies(patterns_df['Format'], prefix='fmt')
    feature_matrix = pd.concat([feature_matrix, fmt_dummies], axis=1)

    # Precision
    prec_dummies = pd.get_dummies(patterns_df['Precision'], prefix='prec')
    feature_matrix = pd.concat([feature_matrix, prec_dummies], axis=1)

    # Function
    func_dummies = pd.get_dummies(patterns_df['Function'], prefix='func')
    feature_matrix = pd.concat([feature_matrix, func_dummies], axis=1)

    # Normalize numerical features
    first_cycle = patterns_df['First_Cycle_Num'].fillna(patterns_df['First_Cycle_Num'].median())
    feature_matrix['first_cycle_norm'] = (first_cycle - first_cycle.min()) / (first_cycle.max() - first_cycle.min())

    lifespan = patterns_df['Lifespan_Cycles'].fillna(patterns_df['Lifespan_Cycles'].median())
    feature_matrix['lifespan_norm'] = (lifespan - lifespan.min()) / (lifespan.max() - lifespan.min())

    in_deg = patterns_df['in_degree']
    feature_matrix['in_degree_norm'] = (in_deg - in_deg.min()) / (in_deg.max() - in_deg.min() + 1)

    out_deg = patterns_df['out_degree']
    feature_matrix['out_degree_norm'] = (out_deg - out_deg.min()) / (out_deg.max() - out_deg.min() + 1)

    # Ensure all columns are numeric
    feature_matrix = feature_matrix.astype(float)

    return feature_matrix

def perform_hierarchical_clustering(feature_matrix, n_clusters=12):
    """Perform hierarchical clustering"""
    # Calculate distance matrix
    distances = pdist(feature_matrix, metric='euclidean')

    # Perform linkage
    linkage_matrix = linkage(distances, method='ward')

    # Cut dendrogram to get clusters
    cluster_labels = fcluster(linkage_matrix, n_clusters, criterion='maxclust')

    return linkage_matrix, cluster_labels

def create_dendrogram(linkage_matrix, pattern_ids, output_path):
    """Create dendrogram visualization"""
    plt.figure(figsize=(20, 10), dpi=300)

    dendrogram(
        linkage_matrix,
        labels=pattern_ids.values,
        leaf_rotation=90,
        leaf_font_size=6
    )

    plt.title("Pattern Hierarchical Clustering Dendrogram (123 Patterns)\nWard Linkage, Euclidean Distance",
              fontsize=16, fontweight='bold')
    plt.xlabel("Pattern ID", fontsize=12)
    plt.ylabel("Distance (Ward Linkage)", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Dendrogram saved: {output_path}")
    plt.close()

def analyze_clusters(patterns_df, cluster_labels):
    """Analyze cluster properties"""
    patterns_df['Cluster'] = cluster_labels

    cluster_stats = []

    for cluster_id in sorted(patterns_df['Cluster'].unique()):
        cluster = patterns_df[patterns_df['Cluster'] == cluster_id]

        # Count patterns
        n_patterns = len(cluster)

        # Category distribution
        category_dist = cluster['Category'].value_counts().to_dict()
        dominant_category = cluster['Category'].mode()[0] if len(cluster) > 0 else None

        # Framework distribution
        framework_dist = cluster['Framework'].value_counts().to_dict()
        dominant_framework = cluster['Framework'].mode()[0] if len(cluster) > 0 else None

        # Source distribution (first two letters of Pattern_ID)
        sources = cluster['Pattern_ID'].str.split('-').str[0].value_counts().to_dict()
        dominant_source = cluster['Pattern_ID'].str.split('-').str[0].mode()[0] if len(cluster) > 0 else None

        # Temporal statistics
        first_cycle_mean = cluster['First_Cycle_Num'].mean()
        lifespan_mean = cluster['Lifespan_Cycles'].mean()

        # Dependency statistics
        in_degree_mean = cluster['in_degree'].mean()
        out_degree_mean = cluster['out_degree'].mean()

        # Representative patterns (highest in-degree)
        representatives = cluster.nlargest(3, 'in_degree')['Pattern_ID'].tolist()

        cluster_stats.append({
            'Cluster_ID': cluster_id,
            'N_Patterns': n_patterns,
            'Dominant_Category': dominant_category,
            'Category_Distribution': category_dist,
            'Dominant_Framework': dominant_framework,
            'Framework_Distribution': framework_dist,
            'Dominant_Source': dominant_source,
            'Source_Distribution': sources,
            'Mean_First_Cycle': first_cycle_mean,
            'Mean_Lifespan': lifespan_mean,
            'Mean_In_Degree': in_degree_mean,
            'Mean_Out_Degree': out_degree_mean,
            'Representatives': representatives
        })

    return cluster_stats

def create_cluster_taxonomy(cluster_stats, patterns_df, output_path):
    """Create comprehensive cluster taxonomy markdown"""

    with open(output_path, 'w') as f:
        f.write("# PATTERN CLUSTER TAXONOMY\n\n")
        f.write("**Generated:** Cycle 980 (Pattern Archaeology Phase 3)\n")
        f.write("**Method:** Hierarchical clustering (Ward linkage, Euclidean distance)\n")
        f.write("**Patterns:** 123 patterns across 12 clusters\n\n")
        f.write("---\n\n")

        for stats in cluster_stats:
            cluster_id = stats['Cluster_ID']
            n_patterns = stats['N_Patterns']

            f.write(f"## CLUSTER {cluster_id}: {stats['Dominant_Category']}-{stats['Dominant_Framework']} Cluster\n\n")
            f.write(f"**Size:** {n_patterns} patterns ({n_patterns/123*100:.1f}%)\n\n")

            # Characteristics
            f.write("### Characteristics\n\n")
            f.write(f"- **Dominant Category:** {stats['Dominant_Category']}\n")
            f.write(f"  - Distribution: {stats['Category_Distribution']}\n")
            f.write(f"- **Dominant Framework:** {stats['Dominant_Framework']}\n")
            f.write(f"  - Distribution: {stats['Framework_Distribution']}\n")
            f.write(f"- **Dominant Source:** {stats['Dominant_Source']}\n")
            f.write(f"  - Distribution: {stats['Source_Distribution']}\n")
            f.write(f"- **Temporal Range:** Mean first appearance Cycle {stats['Mean_First_Cycle']:.0f}\n")
            f.write(f"- **Persistence:** Mean lifespan {stats['Mean_Lifespan']:.0f} cycles\n")
            f.write(f"- **Foundational Strength:** Mean in-degree {stats['Mean_In_Degree']:.1f}\n")
            f.write(f"- **Derivation Complexity:** Mean out-degree {stats['Mean_Out_Degree']:.1f}\n\n")

            # Representative patterns
            f.write("### Representative Patterns\n\n")
            for rep_id in stats['Representatives']:
                pattern = patterns_df[patterns_df['Pattern_ID'] == rep_id].iloc[0]
                content = pattern['Content'][:80] + "..." if len(pattern['Content']) > 80 else pattern['Content']
                f.write(f"**{rep_id}:** {content}\n\n")

            # All patterns in cluster
            f.write("### All Patterns in Cluster\n\n")
            cluster_patterns = patterns_df[patterns_df['Cluster'] == cluster_id].sort_values('in_degree', ascending=False)
            for idx, row in cluster_patterns.iterrows():
                f.write(f"- {row['Pattern_ID']} ({row['Category']}, {row['Framework']}, in-degree={row['in_degree']:.0f})\n")
            f.write("\n---\n\n")

    print(f"Cluster taxonomy saved: {output_path}")

def main():
    print("="*80)
    print("CYCLE 980: PATTERN CLUSTER IDENTIFICATION")
    print("="*80)
    print()

    # Load data
    print("Loading patterns, lineage, and dependencies...")
    patterns_df, dependencies_df = load_data()
    print(f"  → {len(patterns_df)} patterns loaded")
    print(f"  → {len(dependencies_df)} dependencies loaded")
    print()

    # Create feature matrix
    print("Creating feature matrix for clustering...")
    feature_matrix = create_feature_matrix(patterns_df, dependencies_df)
    print(f"  → Feature matrix: {feature_matrix.shape[0]} patterns × {feature_matrix.shape[1]} features")
    print()

    # Perform clustering
    print("Performing hierarchical clustering (Ward linkage)...")
    linkage_matrix, cluster_labels = perform_hierarchical_clustering(feature_matrix, n_clusters=12)
    print(f"  → {len(set(cluster_labels))} clusters identified")
    print()

    # Analyze clusters
    print("Analyzing cluster properties...")
    cluster_stats = analyze_clusters(patterns_df, cluster_labels)

    # Print summary
    print(f"\nCluster Size Distribution:")
    for stats in sorted(cluster_stats, key=lambda x: x['N_Patterns'], reverse=True):
        print(f"  Cluster {stats['Cluster_ID']}: {stats['N_Patterns']} patterns "
              f"({stats['Dominant_Category']}-{stats['Dominant_Framework']}, "
              f"mean in-degree={stats['Mean_In_Degree']:.1f})")
    print()

    # Save cluster assignments
    print(f"Saving cluster assignments: {OUTPUT_CSV}")
    patterns_df[['Pattern_ID', 'Cluster', 'Category', 'Framework', 'in_degree', 'out_degree']].to_csv(
        OUTPUT_CSV, index=False
    )
    print(f"  → {len(patterns_df)} patterns with cluster labels saved")
    print()

    # Create visualizations
    print("Creating dendrogram visualization...")
    create_dendrogram(linkage_matrix, patterns_df['Pattern_ID'], OUTPUT_FIG)
    print()

    # Create taxonomy
    print("Creating cluster taxonomy...")
    create_cluster_taxonomy(cluster_stats, patterns_df, OUTPUT_TAX)
    print()

    print("="*80)
    print("CYCLE 980 ANALYSIS COMPLETE")
    print("="*80)
    print()
    print(f"Outputs:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_FIG}")
    print(f"  - {OUTPUT_TAX}")
    print()
    print(f"Next: Cycle 981 (Survival Analysis)")
    print()

if __name__ == '__main__':
    main()
