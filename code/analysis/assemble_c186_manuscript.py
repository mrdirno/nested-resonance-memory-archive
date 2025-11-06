#!/usr/bin/env python3
"""
Assemble C186 Hierarchical Advantage Manuscript
Combines all section files into unified manuscript document

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05 (Cycle 1082)
License: GPL-3.0
"""

import os
import re
from pathlib import Path

def extract_content(file_path):
    """Extract main content from section file, removing headers and metadata."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by markdown headers
    lines = content.split('\n')

    # Find where actual content starts (after metadata/headers)
    content_start = 0
    in_metadata = False

    for i, line in enumerate(lines):
        # Skip metadata blocks at start
        if i < 10 and ('Author:' in line or 'Date:' in line or 'Status:' in line):
            continue

        # Skip horizontal rules
        if line.strip() == '---':
            content_start = i + 1
            continue

        # Skip top-level headers (# Title)
        if line.startswith('# '):
            content_start = i + 1
            continue

        # Once we hit real content, break
        if line.strip() and not line.startswith('#'):
            content_start = i
            break

    # Get content from start point
    content_lines = lines[content_start:]

    # Remove any trailing metadata/notes sections
    clean_lines = []
    for line in content_lines:
        # Stop at meta sections
        if line.startswith('## META') or line.startswith('## VERSION') or line.startswith('**Version:**'):
            break
        clean_lines.append(line)

    return '\n'.join(clean_lines).strip()

def count_words(text):
    """Count words in text."""
    # Remove markdown syntax
    text = re.sub(r'\*\*', '', text)  # Bold
    text = re.sub(r'\*', '', text)    # Italics
    text = re.sub(r'#+\s', '', text)  # Headers
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # Links

    # Count words
    words = text.split()
    return len(words)

def assemble_manuscript():
    """Assemble complete manuscript from section files."""

    papers_dir = Path('/Volumes/dual/DUALITY-ZERO-V2/papers')

    # Section files in order
    sections = [
        ('c186_abstract_trimmed.md', 'Abstract'),
        ('c186_introduction_draft.md', 'Introduction'),
        ('c186_methods_draft.md', 'Methods'),
        ('c186_results_draft.md', 'Results'),
        ('c186_discussion_draft.md', 'Discussion'),
        ('c186_conclusions_draft.md', 'Conclusions'),
        ('c186_references_draft.md', 'References'),
    ]

    # Build manuscript
    manuscript_parts = []
    word_counts = {}

    # Title and metadata
    manuscript_parts.append("# Resilience Through Redundancy: Hierarchical Advantage in Energy-Constrained Agent Systems")
    manuscript_parts.append("")
    manuscript_parts.append("**Author:** Aldrin Payopay")
    manuscript_parts.append("**Affiliation:** Independent Researcher")
    manuscript_parts.append("**Email:** aldrin.gdf@gmail.com")
    manuscript_parts.append("**Date:** 2025-11-05")
    manuscript_parts.append("**Status:** Manuscript Draft (V1-V5 framework complete, V6-V8 integration pending)")
    manuscript_parts.append("**Repository:** https://github.com/mrdirno/nested-resonance-memory-archive")
    manuscript_parts.append("**License:** GPL-3.0")
    manuscript_parts.append("")
    manuscript_parts.append("---")
    manuscript_parts.append("")

    # Add each section
    for filename, section_name in sections:
        file_path = papers_dir / filename

        if not file_path.exists():
            print(f"WARNING: {filename} not found, skipping")
            continue

        # Extract content
        content = extract_content(file_path)

        # Count words
        word_count = count_words(content)
        word_counts[section_name] = word_count

        # Add section header (except for Abstract which has special formatting)
        if section_name != 'Abstract':
            manuscript_parts.append(f"## {section_name}")
            manuscript_parts.append("")

        # Add content
        manuscript_parts.append(content)
        manuscript_parts.append("")
        manuscript_parts.append("")

    # Add word count summary
    manuscript_parts.append("---")
    manuscript_parts.append("")
    manuscript_parts.append("## Manuscript Statistics")
    manuscript_parts.append("")
    total_words = sum(word_counts.values())
    manuscript_parts.append(f"**Total Word Count:** {total_words} words")
    manuscript_parts.append("")
    manuscript_parts.append("**Section Breakdown:**")
    for section_name, count in word_counts.items():
        pct = (count / total_words * 100) if total_words > 0 else 0
        manuscript_parts.append(f"- {section_name}: {count} words ({pct:.1f}%)")
    manuscript_parts.append("")

    # Target journal information
    manuscript_parts.append("**Target Journal:** Nature Communications")
    manuscript_parts.append("**Word Count Target:** ~8,000 words (flexible)")
    if total_words > 8000:
        manuscript_parts.append(f"**Status:** {total_words - 8000} words over target (may need trimming)")
    else:
        manuscript_parts.append(f"**Status:** {8000 - total_words} words under target (acceptable)")
    manuscript_parts.append("")

    # Version information
    manuscript_parts.append("---")
    manuscript_parts.append("")
    manuscript_parts.append("**Version:** 1.0 (Unified Assembly)")
    manuscript_parts.append("**Created:** 2025-11-05 (Cycle 1082)")
    manuscript_parts.append("**Framework:** V1-V5 complete, V6-V8 integration pending")
    manuscript_parts.append("**Readiness:** ~95% (awaiting experimental data)")
    manuscript_parts.append("")

    # Combine all parts
    manuscript = '\n'.join(manuscript_parts)

    # Write to file
    output_path = papers_dir / 'c186_manuscript_unified.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(manuscript)

    # Print summary
    print(f"Manuscript assembled: {output_path}")
    print(f"Total words: {total_words}")
    print(f"\nSection breakdown:")
    for section_name, count in word_counts.items():
        pct = (count / total_words * 100) if total_words > 0 else 0
        print(f"  {section_name:15s}: {count:5d} words ({pct:5.1f}%)")

    return output_path, total_words, word_counts

if __name__ == '__main__':
    output_path, total_words, word_counts = assemble_manuscript()
    print(f"\nManuscript ready for review: {output_path}")
