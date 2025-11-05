#!/usr/bin/env python3
"""
Cycle 981: Pattern Survival Analysis

Quantifies pattern persistence using:
1. Survival time: Last_Occurrence - First_Occurrence (cycles)
2. Survival statistics by category, framework, format
3. Kaplan-Meier survival curves
4. Characteristics of long-lived vs. short-lived patterns

Identifies what makes patterns persist across research trajectory.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

# File paths
PATTERN_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_DATABASE.csv"
LINEAGE_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_LINEAGE.csv"
CLUSTERS = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_CLUSTERS.csv"
OUTPUT_CSV = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_SURVIVAL.csv"
OUTPUT_FIG = "/Volumes/dual/DUALITY-ZERO-V2/data/figures/pattern_survival_curves.png"
OUTPUT_MD = "/Volumes/dual/DUALITY-ZERO-V2/data/pattern_survival_statistics.md"

def load_data():
    """Load all pattern data"""
    patterns = pd.read_csv(PATTERN_DB, quotechar='"', escapechar='\\')
    lineage = pd.read_csv(LINEAGE_DB)
    clusters = pd.read_csv(CLUSTERS)

    # Merge all data
    merged = patterns.merge(lineage[['Pattern_ID', 'Lifespan_Cycles']], on='Pattern_ID', how='left')
    merged = merged.merge(clusters[['Pattern_ID', 'Cluster']], on='Pattern_ID', how='left')

    return merged

def calculate_survival_statistics(patterns_df):
    """Calculate survival statistics"""
    survival_stats = {
        'total_patterns': len(patterns_df),
        'mean_survival': patterns_df['Lifespan_Cycles'].mean(),
        'median_survival': patterns_df['Lifespan_Cycles'].median(),
        'min_survival': patterns_df['Lifespan_Cycles'].min(),
        'max_survival': patterns_df['Lifespan_Cycles'].max(),
        'std_survival': patterns_df['Lifespan_Cycles'].std(),
        'q25_survival': patterns_df['Lifespan_Cycles'].quantile(0.25),
        'q75_survival': patterns_df['Lifespan_Cycles'].quantile(0.75)
    }

    # By category
    category_stats = patterns_df.groupby('Category')['Lifespan_Cycles'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('count', 'count')
    ]).round(1)

    # By framework
    framework_stats = patterns_df.groupby('Framework')['Lifespan_Cycles'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('count', 'count')
    ]).round(1)

    # By format
    format_stats = patterns_df.groupby('Format')['Lifespan_Cycles'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('count', 'count')
    ]).round(1)

    # By precision
    precision_stats = patterns_df.groupby('Precision')['Lifespan_Cycles'].agg([
        ('mean', 'mean'),
        ('median', 'median'),
        ('count', 'count')
    ]).round(1)

    survival_stats['by_category'] = category_stats
    survival_stats['by_framework'] = framework_stats
    survival_stats['by_format'] = format_stats
    survival_stats['by_precision'] = precision_stats

    return survival_stats

def identify_long_lived_patterns(patterns_df, top_n=10):
    """Identify longest-lived patterns and their characteristics"""
    long_lived = patterns_df.nlargest(top_n, 'Lifespan_Cycles')

    characteristics = {
        'patterns': long_lived[['Pattern_ID', 'Lifespan_Cycles', 'Category', 'Framework', 'Format', 'Precision']].to_dict('records'),
        'common_category': long_lived['Category'].mode()[0] if len(long_lived) > 0 else None,
        'common_framework': long_lived['Framework'].mode()[0] if len(long_lived) > 0 else None,
        'common_format': long_lived['Format'].mode()[0] if len(long_lived) > 0 else None,
        'common_precision': long_lived['Precision'].mode()[0] if len(long_lived) > 0 else None
    }

    return characteristics

def identify_short_lived_patterns(patterns_df, threshold=10):
    """Identify short-lived patterns (survival < threshold cycles)"""
    short_lived = patterns_df[patterns_df['Lifespan_Cycles'] < threshold]

    characteristics = {
        'count': len(short_lived),
        'patterns': short_lived[['Pattern_ID', 'Lifespan_Cycles', 'Category', 'Framework']].to_dict('records'),
        'common_category': short_lived['Category'].mode()[0] if len(short_lived) > 0 else None,
        'common_framework': short_lived['Framework'].mode()[0] if len(short_lived) > 0 else None
    }

    return characteristics

def calculate_survival_curve(lifespans):
    """Calculate empirical survival curve (proportion surviving at each time point)"""
    sorted_lifespans = np.sort(lifespans)
    n = len(sorted_lifespans)
    times = []
    survival = []

    for i, t in enumerate(sorted_lifespans):
        times.append(t)
        survival.append((n - i) / n)  # Proportion still "alive" at time t

    return np.array(times), np.array(survival)

def create_kaplan_meier_curves(patterns_df, output_path):
    """Generate survival curves by category (manual implementation)"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)

    # Overall survival
    ax = axes[0, 0]
    times, survival = calculate_survival_curve(patterns_df['Lifespan_Cycles'].values)
    ax.plot(times, survival, linewidth=2, label='All Patterns', color='black')
    ax.set_title("Overall Pattern Survival Curve", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (cycles)", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    # By category
    ax = axes[0, 1]
    colors = {'SF': 'blue', 'MP': 'orange', 'FP': 'green', 'MR': 'red', 'TS': 'purple'}
    for category in sorted(patterns_df['Category'].unique()):
        subset = patterns_df[patterns_df['Category'] == category]
        times, survival = calculate_survival_curve(subset['Lifespan_Cycles'].values)
        ax.plot(times, survival, linewidth=2, label=f"{category} (n={len(subset)})",
                color=colors.get(category, 'gray'))
    ax.set_title("Survival by Category (SF/MP/FP/MR/TS)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (cycles)", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # By framework
    ax = axes[1, 0]
    for framework in sorted(patterns_df['Framework'].unique()):
        subset = patterns_df[patterns_df['Framework'] == framework]
        if len(subset) >= 3:  # Only plot if sufficient data
            times, survival = calculate_survival_curve(subset['Lifespan_Cycles'].values)
            ax.plot(times, survival, linewidth=2, label=f"{framework} (n={len(subset)})")
    ax.set_title("Survival by Framework (N/S/T/R/U)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (cycles)", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # By format
    ax = axes[1, 1]
    for fmt in sorted(patterns_df['Format'].unique()):
        subset = patterns_df[patterns_df['Format'] == fmt]
        if len(subset) >= 3:
            times, survival = calculate_survival_curve(subset['Lifespan_Cycles'].values)
            ax.plot(times, survival, linewidth=2, label=f"{fmt} (n={len(subset)})")
    ax.set_title("Survival by Format (P/D/C/M)", fontsize=14, fontweight='bold')
    ax.set_xlabel("Time (cycles)", fontsize=12)
    ax.set_ylabel("Survival Probability", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Survival curves saved: {output_path}")
    plt.close()

def create_survival_statistics_document(stats, long_lived, short_lived, output_path):
    """Create comprehensive statistics markdown"""
    with open(output_path, 'w') as f:
        f.write("# PATTERN SURVIVAL STATISTICS\n\n")
        f.write("**Generated:** Cycle 981 (Pattern Archaeology Phase 3)\n")
        f.write("**Method:** Lifespan calculation + Kaplan-Meier survival analysis\n")
        f.write(f"**Patterns:** {stats['total_patterns']} patterns analyzed\n\n")
        f.write("---\n\n")

        # Overall statistics
        f.write("## Overall Survival Statistics\n\n")
        f.write(f"- **Mean Lifespan:** {stats['mean_survival']:.1f} cycles\n")
        f.write(f"- **Median Lifespan:** {stats['median_survival']:.1f} cycles\n")
        f.write(f"- **Minimum:** {stats['min_survival']:.0f} cycles\n")
        f.write(f"- **Maximum:** {stats['max_survival']:.0f} cycles\n")
        f.write(f"- **Standard Deviation:** {stats['std_survival']:.1f} cycles\n")
        f.write(f"- **25th Percentile:** {stats['q25_survival']:.1f} cycles\n")
        f.write(f"- **75th Percentile:** {stats['q75_survival']:.1f} cycles\n\n")

        # By category
        f.write("## Survival by Category\n\n")
        f.write("| Category | Mean (cycles) | Median (cycles) | Count |\n")
        f.write("|----------|---------------|-----------------|-------|\n")
        for cat, row in stats['by_category'].iterrows():
            f.write(f"| {cat} | {row['mean']:.1f} | {row['median']:.1f} | {int(row['count'])} |\n")
        f.write("\n")

        # By framework
        f.write("## Survival by Framework\n\n")
        f.write("| Framework | Mean (cycles) | Median (cycles) | Count |\n")
        f.write("|-----------|---------------|-----------------|-------|\n")
        for fw, row in stats['by_framework'].iterrows():
            f.write(f"| {fw} | {row['mean']:.1f} | {row['median']:.1f} | {int(row['count'])} |\n")
        f.write("\n")

        # By format
        f.write("## Survival by Format\n\n")
        f.write("| Format | Mean (cycles) | Median (cycles) | Count |\n")
        f.write("|--------|---------------|-----------------|-------|\n")
        for fmt, row in stats['by_format'].iterrows():
            f.write(f"| {fmt} | {row['mean']:.1f} | {row['median']:.1f} | {int(row['count'])} |\n")
        f.write("\n")

        # By precision
        f.write("## Survival by Precision\n\n")
        f.write("| Precision | Mean (cycles) | Median (cycles) | Count |\n")
        f.write("|-----------|---------------|-----------------|-------|\n")
        for prec, row in stats['by_precision'].iterrows():
            f.write(f"| {prec} | {row['mean']:.1f} | {row['median']:.1f} | {int(row['count'])} |\n")
        f.write("\n")

        # Long-lived patterns
        f.write("## Top 10 Longest-Lived Patterns\n\n")
        f.write("| Pattern ID | Lifespan | Category | Framework | Format | Precision |\n")
        f.write("|------------|----------|----------|-----------|--------|--------|\n")
        for p in long_lived['patterns']:
            f.write(f"| {p['Pattern_ID']} | {p['Lifespan_Cycles']:.0f} | {p['Category']} | {p['Framework']} | {p['Format']} | {p['Precision']} |\n")
        f.write("\n")

        f.write(f"**Characteristics of Long-Lived Patterns:**\n")
        f.write(f"- Most common category: {long_lived['common_category']}\n")
        f.write(f"- Most common framework: {long_lived['common_framework']}\n")
        f.write(f"- Most common format: {long_lived['common_format']}\n")
        f.write(f"- Most common precision: {long_lived['common_precision']}\n\n")

        # Short-lived patterns
        f.write(f"## Short-Lived Patterns (< 10 cycles)\n\n")
        f.write(f"**Count:** {short_lived['count']} patterns\n\n")
        if short_lived['count'] > 0:
            f.write("| Pattern ID | Lifespan | Category | Framework |\n")
            f.write("|------------|----------|----------|-----------|\n")
            for p in short_lived['patterns']:
                f.write(f"| {p['Pattern_ID']} | {p['Lifespan_Cycles']:.0f} | {p['Category']} | {p['Framework']} |\n")
            f.write("\n")

            f.write(f"**Characteristics:**\n")
            f.write(f"- Most common category: {short_lived['common_category']}\n")
            f.write(f"- Most common framework: {short_lived['common_framework']}\n\n")

        f.write("---\n\n")
        f.write("*Generated: Cycle 981, Pattern Archaeology Phase 3*\n")

    print(f"Survival statistics saved: {output_path}")

def main():
    print("="*80)
    print("CYCLE 981: PATTERN SURVIVAL ANALYSIS")
    print("="*80)
    print()

    # Load data
    print("Loading patterns, lineage, and clusters...")
    patterns_df = load_data()
    print(f"  → {len(patterns_df)} patterns loaded")
    print()

    # Calculate statistics
    print("Calculating survival statistics...")
    stats = calculate_survival_statistics(patterns_df)
    print(f"  Mean survival: {stats['mean_survival']:.1f} cycles")
    print(f"  Median survival: {stats['median_survival']:.1f} cycles")
    print(f"  Range: {stats['min_survival']:.0f} - {stats['max_survival']:.0f} cycles")
    print()

    # Long-lived patterns
    print("Identifying longest-lived patterns...")
    long_lived = identify_long_lived_patterns(patterns_df, top_n=10)
    print(f"  Top 10 lifespan range: {long_lived['patterns'][9]['Lifespan_Cycles']:.0f} - {long_lived['patterns'][0]['Lifespan_Cycles']:.0f} cycles")
    print(f"  Most common category: {long_lived['common_category']}")
    print(f"  Most common framework: {long_lived['common_framework']}")
    print()

    # Short-lived patterns
    print("Identifying short-lived patterns (<10 cycles)...")
    short_lived = identify_short_lived_patterns(patterns_df, threshold=10)
    print(f"  Count: {short_lived['count']}")
    if short_lived['count'] > 0:
        print(f"  Most common category: {short_lived['common_category']}")
    print()

    # Survival by category
    print("Survival by Category:")
    for cat, row in stats['by_category'].iterrows():
        print(f"  {cat}: {row['mean']:.1f} cycles mean ({int(row['count'])} patterns)")
    print()

    # Survival by framework
    print("Survival by Framework:")
    for fw, row in stats['by_framework'].iterrows():
        print(f"  {fw}: {row['mean']:.1f} cycles mean ({int(row['count'])} patterns)")
    print()

    # Save survival data
    print(f"Saving survival data: {OUTPUT_CSV}")
    patterns_df[['Pattern_ID', 'Lifespan_Cycles', 'Category', 'Framework', 'Format', 'Precision', 'Cluster']].to_csv(
        OUTPUT_CSV, index=False
    )
    print(f"  → {len(patterns_df)} patterns saved")
    print()

    # Create visualizations
    print("Creating Kaplan-Meier survival curves...")
    create_kaplan_meier_curves(patterns_df, OUTPUT_FIG)
    print()

    # Create statistics document
    print("Creating survival statistics document...")
    create_survival_statistics_document(stats, long_lived, short_lived, OUTPUT_MD)
    print()

    print("="*80)
    print("CYCLE 981 ANALYSIS COMPLETE")
    print("="*80)
    print()
    print(f"Outputs:")
    print(f"  - {OUTPUT_CSV}")
    print(f"  - {OUTPUT_FIG}")
    print(f"  - {OUTPUT_MD}")
    print()
    print(f"PHASE 3 COMPLETE: Pattern Lineage Tracing (Cycles 978-981)")
    print()

if __name__ == '__main__':
    main()
