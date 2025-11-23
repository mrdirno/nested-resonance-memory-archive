#!/usr/bin/env python3
"""
Cycle 978: Pattern Lineage Mapping

Traces 123 patterns through 1,178 git commits to identify:
- First commit where pattern appeared
- Evolution through subsequent commits
- Final commit (publication form)

Method:
1. Parse git history (commit_hash|author|date|subject format)
2. For each pattern, identify cycle from First_Occurrence field
3. Search commit messages for cycle references
4. Map pattern to earliest matching commit
5. Document evolution path

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Authored-By: Claude <noreply@anthropic.com>
"""

import pandas as pd
import re
from pathlib import Path
from datetime import datetime

# File paths
GIT_HISTORY = "/tmp/git_history.csv"
PATTERN_DB = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_DATABASE.csv"
OUTPUT = "/Volumes/dual/DUALITY-ZERO-V2/data/PAPER3_PATTERN_LINEAGE.csv"

def parse_git_history(filepath):
    """Parse git log output (hash|author|date|subject)"""
    commits = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('|')
            if len(parts) >= 4:
                commits.append({
                    'hash': parts[0],
                    'author': parts[1],
                    'date': parts[2],
                    'subject': '|'.join(parts[3:])  # Handle | in subject
                })
    return pd.DataFrame(commits)

def extract_cycle_number(occurrence_str):
    """Extract cycle number from 'CycleXXX' or 'Cycle168-170' format"""
    if pd.isna(occurrence_str):
        return None

    # Handle range format (e.g., "Cycle168-170" → 168)
    match = re.search(r'Cycle(\d+)', str(occurrence_str))
    if match:
        return int(match.group(1))

    # Handle "Paper1" → treat as very early (Cycle 1)
    if 'Paper' in str(occurrence_str):
        return 1

    return None

def find_pattern_commits(pattern_id, first_cycle, last_cycle, commits_df):
    """Find commits mentioning the pattern's cycle range"""
    matching_commits = []

    # Search for cycle number in commit messages
    if first_cycle:
        # Look for "Cycle XXX" or "cycle XXX" in subject
        pattern = re.compile(rf'\b[Cc]ycle\s*{first_cycle}\b')
        for idx, row in commits_df.iterrows():
            if pattern.search(row['subject']):
                matching_commits.append({
                    'commit_hash': row['hash'],
                    'commit_date': row['date'],
                    'commit_subject': row['subject'][:80]  # Truncate long subjects
                })

    return matching_commits

def main():
    print("="*80)
    print("CYCLE 978: PATTERN LINEAGE MAPPING")
    print("="*80)
    print()

    # Load data
    print(f"Loading git history: {GIT_HISTORY}")
    commits_df = parse_git_history(GIT_HISTORY)
    print(f"  → {len(commits_df)} commits loaded")
    print()

    print(f"Loading pattern database: {PATTERN_DB}")
    patterns_df = pd.read_csv(PATTERN_DB, quotechar='"', escapechar='\\')
    print(f"  → {len(patterns_df)} patterns loaded")
    print()

    # Extract cycle numbers
    print("Extracting cycle numbers from First_Occurrence...")
    patterns_df['First_Cycle'] = patterns_df['First_Occurrence'].apply(extract_cycle_number)
    patterns_df['Last_Cycle'] = patterns_df['Last_Occurrence'].apply(extract_cycle_number)

    # Count patterns with valid cycle numbers
    valid_cycles = patterns_df['First_Cycle'].notna().sum()
    print(f"  → {valid_cycles}/{len(patterns_df)} patterns have numeric cycle references")
    print()

    # Map patterns to commits
    print("Mapping patterns to commits...")
    lineage_data = []

    for idx, pattern in patterns_df.iterrows():
        pattern_id = pattern['Pattern_ID']
        first_cycle = pattern['First_Cycle']
        last_cycle = pattern['Last_Cycle']

        # Find commits
        commits = find_pattern_commits(pattern_id, first_cycle, last_cycle, commits_df)

        if commits:
            # Take earliest commit as "first appearance"
            first_commit = commits[0]
            lineage_data.append({
                'Pattern_ID': pattern_id,
                'First_Occurrence': pattern['First_Occurrence'],
                'Last_Occurrence': pattern['Last_Occurrence'],
                'First_Cycle_Num': first_cycle,
                'Last_Cycle_Num': last_cycle,
                'First_Commit_Hash': first_commit['commit_hash'][:7],
                'First_Commit_Date': first_commit['commit_date'],
                'First_Commit_Subject': first_commit['commit_subject'],
                'Evolution_Commits': len(commits),
                'Lifespan_Cycles': last_cycle - first_cycle if (first_cycle and last_cycle) else None,
                'Category': pattern['Category'],
                'Framework': pattern['Framework'],
                'Source_Location': pattern['Source_Location']
            })
        else:
            # No matching commits found
            lineage_data.append({
                'Pattern_ID': pattern_id,
                'First_Occurrence': pattern['First_Occurrence'],
                'Last_Occurrence': pattern['Last_Occurrence'],
                'First_Cycle_Num': first_cycle,
                'Last_Cycle_Num': last_cycle,
                'First_Commit_Hash': 'NOT_FOUND',
                'First_Commit_Date': None,
                'First_Commit_Subject': None,
                'Evolution_Commits': 0,
                'Lifespan_Cycles': last_cycle - first_cycle if (first_cycle and last_cycle) else None,
                'Category': pattern['Category'],
                'Framework': pattern['Framework'],
                'Source_Location': pattern['Source_Location']
            })

        # Progress indicator
        if (idx + 1) % 10 == 0:
            print(f"  → Processed {idx + 1}/{len(patterns_df)} patterns...")

    print(f"  → All {len(patterns_df)} patterns processed")
    print()

    # Create lineage dataframe
    lineage_df = pd.DataFrame(lineage_data)

    # Summary statistics
    print("="*80)
    print("LINEAGE MAPPING SUMMARY")
    print("="*80)
    print()

    patterns_found = (lineage_df['First_Commit_Hash'] != 'NOT_FOUND').sum()
    patterns_not_found = (lineage_df['First_Commit_Hash'] == 'NOT_FOUND').sum()

    print(f"Patterns Mapped to Commits: {patterns_found}/{len(lineage_df)} ({patterns_found/len(lineage_df)*100:.1f}%)")
    print(f"Patterns Not Found: {patterns_not_found}/{len(lineage_df)} ({patterns_not_found/len(lineage_df)*100:.1f}%)")
    print()

    # Lifespan statistics (patterns with valid cycle ranges)
    valid_lifespans = lineage_df[lineage_df['Lifespan_Cycles'].notna()]
    if len(valid_lifespans) > 0:
        print("Pattern Lifespan Statistics (cycles):")
        print(f"  Mean: {valid_lifespans['Lifespan_Cycles'].mean():.1f}")
        print(f"  Median: {valid_lifespans['Lifespan_Cycles'].median():.1f}")
        print(f"  Min: {valid_lifespans['Lifespan_Cycles'].min():.0f}")
        print(f"  Max: {valid_lifespans['Lifespan_Cycles'].max():.0f}")
        print()

    # Top 10 longest-lived patterns
    print("Top 10 Longest-Lived Patterns:")
    top_10 = lineage_df.nlargest(10, 'Lifespan_Cycles')[['Pattern_ID', 'Lifespan_Cycles', 'First_Occurrence', 'Category']]
    print(top_10.to_string(index=False))
    print()

    # Save lineage database
    print(f"Saving pattern lineage database: {OUTPUT}")
    lineage_df.to_csv(OUTPUT, index=False)
    print(f"  → {len(lineage_df)} patterns with lineage data saved")
    print()

    print("="*80)
    print("CYCLE 978 ANALYSIS COMPLETE")
    print("="*80)
    print()
    print(f"Output: {OUTPUT}")
    print(f"Next: Cycle 979 (Dependency Mapping)")
    print()

if __name__ == '__main__':
    main()
