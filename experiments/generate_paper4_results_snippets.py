#!/usr/bin/env python3
"""
PAPER 4 RESULTS DATA INTEGRATION HELPER

Purpose: Generate markdown snippets from validation reports for Paper 4 Results section

Input: Validation report JSONs (cycle186-189_validation_report.json + composite)
Output: Markdown snippets ready for copy-paste into paper4_results_template.md

Workflow:
  1. Load all validation reports
  2. Extract key statistics and results
  3. Generate formatted markdown snippets for each subsection
  4. Save to paper4_results_integration_snippets.md

This script does NOT modify the template directly - it generates snippets
for manual review and integration to maintain scientific accuracy.

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Date: 2025-11-05
Cycle: 1018
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Report paths
RESULTS_DIR = Path(__file__).parent / "results"
C186_REPORT = RESULTS_DIR / "cycle186_validation_report.json"
C187_REPORT = RESULTS_DIR / "cycle187_validation_report.json"
C188_REPORT = RESULTS_DIR / "cycle188_validation_report.json"
C189_REPORT = RESULTS_DIR / "cycle189_validation_report.json"
COMPOSITE_REPORT = RESULTS_DIR / "composite_validation_report.json"

OUTPUT_PATH = Path(__file__).parent.parent / "papers" / "paper4_results_integration_snippets.md"


def load_report(path: Path) -> Optional[Dict]:
    """Load validation report JSON."""
    if not path.exists():
        return None

    with open(path, 'r') as f:
        return json.load(f)


def format_status(status: str) -> str:
    """Format validation status with emoji."""
    if status == "VALIDATED":
        return "✅ VALIDATED"
    elif status == "PARTIAL":
        return "⚠️ PARTIAL"
    else:
        return "❌ REJECTED"


def generate_c187_snippets(report: Dict) -> str:
    """Generate snippets for C187 (Network Structure Effects)."""
    if report is None:
        return "**C187 DATA NOT AVAILABLE**\n"

    snippets = []
    snippets.append("## 4.2 Extension 1: Network Structure Effects (C187)")
    snippets.append("")
    snippets.append("### 4.2.1 Hypothesis Testing")
    snippets.append("")

    # Extract validation results
    validations = report.get('validations', {})

    for val_name, val_data in validations.items():
        status = format_status(val_data.get('status', 'UNKNOWN'))
        snippets.append(f"**{val_name}:**")
        snippets.append(f"- **Status:** {status}")
        snippets.append(f"- **Score:** {val_data.get('score', 0):.2f} / {val_data.get('max_score', 0):.2f}")

        # Add key metrics if available
        if 'metrics' in val_data:
            metrics = val_data['metrics']
            for key, value in metrics.items():
                if isinstance(value, float):
                    snippets.append(f"- **{key}:** {value:.3f}")
                else:
                    snippets.append(f"- **{key}:** {value}")
        snippets.append("")

    # Validation score
    snippets.append("### 4.2.2 Validation Score")
    snippets.append("")
    snippets.append(f"**C187 Total Score:** {report['composite_score']:.1f} / 4.0 points")
    snippets.append(f"**Interpretation:** {report['interpretation']}")
    snippets.append(f"**Confidence:** {report['confidence']}")
    snippets.append("")

    return "\n".join(snippets)


def generate_c186_snippets(report: Dict) -> str:
    """Generate snippets for C186 (Hierarchical Energy Dynamics)."""
    if report is None:
        return "**C186 DATA NOT AVAILABLE**\n"

    snippets = []
    snippets.append("## 4.3 Extension 2: Hierarchical Energy Dynamics (C186)")
    snippets.append("")

    # Extract validation results
    validations = report.get('validations', {})

    # Group validations by category
    emergence_validations = {k: v for k, v in validations.items() if 'emergence' in k.lower() or 'population' in k.lower()}
    resonance_validations = {k: v for k, v in validations.items() if 'resonance' in k.lower() or 'correlation' in k.lower()}

    if emergence_validations:
        snippets.append("### 4.3.1 Meta-Population Emergence")
        snippets.append("")
        for val_name, val_data in emergence_validations.items():
            status = format_status(val_data.get('status', 'UNKNOWN'))
            snippets.append(f"**{val_name}:**")
            snippets.append(f"- **Status:** {status}")
            snippets.append(f"- **Score:** {val_data.get('score', 0):.2f} / {val_data.get('max_score', 0):.2f}")

            if 'metrics' in val_data:
                for key, value in val_data['metrics'].items():
                    if isinstance(value, float):
                        snippets.append(f"- **{key}:** {value:.3f}")
                    else:
                        snippets.append(f"- **{key}:** {value}")
            snippets.append("")

    if resonance_validations:
        snippets.append("### 4.3.2 Hierarchical Resonance")
        snippets.append("")
        for val_name, val_data in resonance_validations.items():
            status = format_status(val_data.get('status', 'UNKNOWN'))
            snippets.append(f"**{val_name}:**")
            snippets.append(f"- **Status:** {status}")
            snippets.append(f"- **Score:** {val_data.get('score', 0):.2f} / {val_data.get('max_score', 0):.2f}")

            if 'metrics' in val_data:
                for key, value in val_data['metrics'].items():
                    if isinstance(value, float):
                        snippets.append(f"- **{key}:** {value:.3f}")
                    else:
                        snippets.append(f"- **{key}:** {value}")
            snippets.append("")

    # Validation score
    snippets.append("### 4.3.X Validation Score")
    snippets.append("")
    snippets.append(f"**C186 Total Score:** {report['composite_score']:.1f} / 12.0 points")
    snippets.append(f"**Interpretation:** {report['interpretation']}")
    snippets.append(f"**Confidence:** {report['confidence']}")
    snippets.append("")

    return "\n".join(snippets)


def generate_c188_snippets(report: Dict) -> str:
    """Generate snippets for C188 (Memory Effects)."""
    if report is None:
        return "**C188 DATA NOT AVAILABLE**\n"

    snippets = []
    snippets.append("## 4.4 Extension 4a: Memory Effects (C188)")
    snippets.append("")

    validations = report.get('validations', {})

    for val_name, val_data in validations.items():
        status = format_status(val_data.get('status', 'UNKNOWN'))
        snippets.append(f"**{val_name}:**")
        snippets.append(f"- **Status:** {status}")
        snippets.append(f"- **Score:** {val_data.get('score', 0):.2f} / {val_data.get('max_score', 0):.2f}")

        if 'metrics' in val_data:
            for key, value in val_data['metrics'].items():
                if isinstance(value, float):
                    snippets.append(f"- **{key}:** {value:.3f}")
                else:
                    snippets.append(f"- **{key}:** {value}")
        snippets.append("")

    snippets.append("### Validation Score")
    snippets.append("")
    snippets.append(f"**C188 Total Score:** {report['composite_score']:.1f} / 5.0 points")
    snippets.append(f"**Interpretation:** {report['interpretation']}")
    snippets.append(f"**Confidence:** {report['confidence']}")
    snippets.append("")

    return "\n".join(snippets)


def generate_c189_snippets(report: Dict) -> str:
    """Generate snippets for C189 (Burst Clustering)."""
    if report is None:
        return "**C189 DATA NOT AVAILABLE**\n"

    snippets = []
    snippets.append("## 4.5 Extension 4b: Burst Clustering (C189)")
    snippets.append("")

    validations = report.get('validations', {})

    for val_name, val_data in validations.items():
        status = format_status(val_data.get('status', 'UNKNOWN'))
        snippets.append(f"**{val_name}:**")
        snippets.append(f"- **Status:** {status}")
        snippets.append(f"- **Score:** {val_data.get('score', 0):.2f} / {val_data.get('max_score', 0):.2f}")

        if 'metrics' in val_data:
            for key, value in val_data['metrics'].items():
                if isinstance(value, float):
                    snippets.append(f"- **{key}:** {value:.3f}")
                else:
                    snippets.append(f"- **{key}:** {value}")
        snippets.append("")

    snippets.append("### Validation Score")
    snippets.append("")
    snippets.append(f"**C189 Total Score:** {report['composite_score']:.1f} / 3.0 points")
    snippets.append(f"**Interpretation:** {report['interpretation']}")
    snippets.append(f"**Confidence:** {report['confidence']}")
    snippets.append("")

    return "\n".join(snippets)


def generate_composite_snippets(report: Dict) -> str:
    """Generate snippets for composite validation scorecard."""
    if report is None:
        return "**COMPOSITE DATA NOT AVAILABLE**\n"

    snippets = []
    snippets.append("## 4.7 Composite Validation Scorecard")
    snippets.append("")

    # Score table
    snippets.append("| Extension | Experiment | Score | Max | % |")
    snippets.append("|-----------|-----------|-------|-----|---|")

    scores = report.get('scores', {})
    max_scores = report.get('max_scores', {})

    experiments = [
        ('Extension 1 (Network)', 'c187'),
        ('Extension 2 (Hierarchical)', 'c186'),
        ('Extension 4a (Memory)', 'c188'),
        ('Extension 4b (Burst)', 'c189')
    ]

    for ext_name, exp_id in experiments:
        score = scores.get(exp_id, 0)
        max_score = max_scores.get(exp_id, 0)
        percentage = (score / max_score * 100) if max_score > 0 else 0
        snippets.append(f"| {ext_name} | {exp_id.upper()} | {score:.1f} | {max_score:.1f} | {percentage:.1f}% |")

    total_score = report.get('total_score', 0)
    max_total = report.get('max_total', 0)
    total_pct = (total_score / max_total * 100) if max_total > 0 else 0
    snippets.append(f"| **TOTAL** | **C186-C189** | **{total_score:.1f}** | **{max_total:.1f}** | **{total_pct:.1f}%** |")
    snippets.append("")

    # Interpretation
    snippets.append(f"**Interpretation:** {report.get('interpretation', 'UNKNOWN')}")
    snippets.append(f"**Confidence Level:** {report.get('confidence', 'UNKNOWN')}")
    snippets.append(f"**Recommendation:** {report.get('recommendation', 'UNKNOWN')}")
    snippets.append("")

    # Status summary
    completed = len(report.get('completed_experiments', []))
    snippets.append(f"**Validation Status:** {completed}/4 experiments complete")
    snippets.append("")

    return "\n".join(snippets)


def generate_overview_snippet(composite_report: Dict) -> str:
    """Generate snippet for Section 4.1 Overview."""
    snippets = []
    snippets.append("## 4.1 Overview of Validation Campaign")
    snippets.append("")

    if composite_report is None:
        snippets.append("**COMPOSITE DATA NOT AVAILABLE**")
        return "\n".join(snippets)

    # Extract summary statistics
    completed = len(composite_report.get('completed_experiments', []))

    snippets.append("This section presents results from the validation campaign testing five extensions")
    snippets.append("to the Nested Resonance Memory framework:")
    snippets.append("")
    snippets.append(f"- **C186 (Hierarchical Energy Dynamics):** {composite_report['scores'].get('c186', 0):.1f} / 12.0 points")
    snippets.append(f"- **C187 (Network Structure Effects):** {composite_report['scores'].get('c187', 0):.1f} / 4.0 points")
    snippets.append(f"- **C188 (Memory Effects):** {composite_report['scores'].get('c188', 0):.1f} / 5.0 points")
    snippets.append(f"- **C189 (Burst Clustering):** {composite_report['scores'].get('c189', 0):.1f} / 3.0 points")
    snippets.append(f"- **Total:** {composite_report['total_score']:.1f} / {composite_report['max_total']:.1f} points ({composite_report['total_score']/composite_report['max_total']*100:.1f}%)")
    snippets.append("")
    snippets.append(f"**Overall Interpretation:** {composite_report['interpretation']}")
    snippets.append("")

    return "\n".join(snippets)


def main():
    """Generate all markdown snippets for Paper 4 Results section."""
    print("=" * 80)
    print("PAPER 4 RESULTS DATA INTEGRATION HELPER")
    print("=" * 80)
    print()

    # Load all reports
    print("Loading validation reports...")
    c186 = load_report(C186_REPORT)
    c187 = load_report(C187_REPORT)
    c188 = load_report(C188_REPORT)
    c189 = load_report(C189_REPORT)
    composite = load_report(COMPOSITE_REPORT)

    # Report status
    available = sum([
        c186 is not None,
        c187 is not None,
        c188 is not None,
        c189 is not None,
        composite is not None
    ])

    print(f"Available reports: {available}/5")
    print(f"  C186: {'✅' if c186 else '❌'}")
    print(f"  C187: {'✅' if c187 else '❌'}")
    print(f"  C188: {'✅' if c188 else '❌'}")
    print(f"  C189: {'✅' if c189 else '❌'}")
    print(f"  Composite: {'✅' if composite else '❌'}")
    print()

    if available == 0:
        print("ERROR: No validation reports found. Run experiments and validation first.")
        sys.exit(1)

    # Generate snippets
    print("Generating markdown snippets...")
    output = []

    output.append("# Paper 4 Results - Data Integration Snippets")
    output.append("")
    output.append("**Generated:** 2025-11-05 (Cycle 1018)")
    output.append("**Source:** Validation reports from C186-C189")
    output.append("**Purpose:** Copy-paste snippets for paper4_results_template.md")
    output.append("")
    output.append("**IMPORTANT:** Review all values for scientific accuracy before integration.")
    output.append("")
    output.append("=" * 80)
    output.append("")

    # Section 4.1 Overview
    output.append(generate_overview_snippet(composite))
    output.append("")
    output.append("=" * 80)
    output.append("")

    # Section 4.2 C187
    output.append(generate_c187_snippets(c187))
    output.append("")
    output.append("=" * 80)
    output.append("")

    # Section 4.3 C186
    output.append(generate_c186_snippets(c186))
    output.append("")
    output.append("=" * 80)
    output.append("")

    # Section 4.4 C188
    output.append(generate_c188_snippets(c188))
    output.append("")
    output.append("=" * 80)
    output.append("")

    # Section 4.5 C189
    output.append(generate_c189_snippets(c189))
    output.append("")
    output.append("=" * 80)
    output.append("")

    # Section 4.7 Composite
    output.append(generate_composite_snippets(composite))
    output.append("")

    # Save output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        f.write("\n".join(output))

    print(f"Snippets generated: {OUTPUT_PATH}")
    print(f"Total lines: {len(output)}")
    print()
    print("=" * 80)
    print("SNIPPET GENERATION COMPLETE")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Review snippets for scientific accuracy")
    print("2. Copy relevant sections into paper4_results_template.md")
    print("3. Add narrative context and interpretation")
    print("4. Reference figures by number")


if __name__ == "__main__":
    main()
