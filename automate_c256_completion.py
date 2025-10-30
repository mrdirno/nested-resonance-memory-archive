#!/usr/bin/env python3
"""
C256 Completion Automation Script
==================================

Automates steps 2-5 of C256_COMPLETION_WORKFLOW.md:
- Data extraction from results JSON
- Manuscript integration (Paper 3 section 3.2)
- Synergy matrix update
- Git commit preparation

This reduces manual workflow from ~22 min to ~5 min (semi-automated).

Usage:
    python automate_c256_completion.py

    Then manually review, commit, and push:
    cd /Users/aldrinpayopay/nested-resonance-memory-archive
    git add papers/paper3_mechanism_synergies_template.md
    git commit -F /tmp/c256_commit_message.txt
    git push origin main

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
License: GPL-3.0
Repository: https://github.com/mrdirno/nested-resonance-memory-archive
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Paths
RESULTS_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/experiments/results/cycle256_h1h4_optimized_results.json")
MANUSCRIPT_FILE = Path("/Volumes/dual/DUALITY-ZERO-V2/papers/paper3_mechanism_synergies_template.md")
GIT_MANUSCRIPT = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/papers/paper3_mechanism_synergies_template.md")
COMMIT_MSG_FILE = Path("/tmp/c256_commit_message.txt")


def load_results() -> Dict[str, Any]:
    """Load C256 experimental results."""
    if not RESULTS_FILE.exists():
        print(f"❌ ERROR: Results file not found: {RESULTS_FILE}")
        print("   C256 may not have completed yet.")
        sys.exit(1)

    with open(RESULTS_FILE, 'r') as f:
        return json.load(f)


def extract_synergy_data(results: Dict[str, Any]) -> Dict[str, Any]:
    """Extract synergy analysis from results."""
    synergy = results['synergy_analysis']

    return {
        'off_off': synergy['off_off'],
        'on_off': synergy['on_off'],
        'off_on': synergy['off_on'],
        'on_on': synergy['on_on'],
        'h1_effect': synergy['h1_effect'],
        'h4_effect': synergy['h4_effect'],
        'additive_prediction': synergy['additive_prediction'],
        'synergy': synergy['synergy'],
        'fold_change': synergy['fold_change'],
        'classification': synergy['classification'],
        'interpretation': synergy['interpretation']
    }


def format_section_3_2(data: Dict[str, Any]) -> str:
    """Format section 3.2 content with experimental results."""

    # Determine hypothesis validation
    predicted = "ANTAGONISTIC"
    observed = data['classification']
    validation = "CONFIRMED" if predicted == observed else "REJECTED"

    section = f"""### 3.2 Experiment 2: H1×H4 (Energy Pooling × Spawn Throttling)

**Condition Results:**
- OFF-OFF: {data['off_off']:.4f} mean population
- H1-only: {data['on_off']:.4f} mean population
- H4-only: {data['off_on']:.4f} mean population
- H1×H4: {data['on_on']:.4f} mean population

**Effect Sizes:**
- H1 effect: {data['h1_effect']:+.4f}
- H4 effect: {data['h4_effect']:+.4f}
- Predicted combined: {data['additive_prediction']:.4f}
- Observed combined: {data['on_on']:.4f}
- **Synergy: {data['synergy']:+.4f}**

**Classification:** {data['classification']}

**Interpretation:** {data['interpretation']}

**Hypothesis Validation:** {validation} - Predicted {predicted}, observed {observed}
"""

    return section


def update_manuscript(section_content: str, data: Dict[str, Any]) -> None:
    """Update Paper 3 manuscript with experimental results."""

    # Read manuscript
    with open(MANUSCRIPT_FILE, 'r') as f:
        content = f.read()

    # Replace section 3.2 placeholder
    old_section = """### 3.2 Experiment 2: H1×H4 (Energy Pooling × Spawn Throttling)

[TO BE FILLED - Same structure as 3.1]"""

    if old_section not in content:
        print("⚠ WARNING: Section 3.2 placeholder not found in expected format")
        print("   Manuscript may have been modified already")
        return

    content = content.replace(old_section, section_content)

    # Update synergy matrix table row (H1×H4)
    old_row = "| H1×H4 | [TO BE FILLED] | [TO BE FILLED] | ANTAGONISTIC |"
    new_row = f"| H1×H4 | {data['synergy']:+.4f} | {data['classification']} | ANTAGONISTIC |"

    if old_row in content:
        content = content.replace(old_row, new_row)
    else:
        print("⚠ WARNING: Synergy matrix H1×H4 row not found")

    # Write updated manuscript
    with open(MANUSCRIPT_FILE, 'w') as f:
        f.write(content)

    print(f"✓ Updated manuscript: {MANUSCRIPT_FILE}")

    # Copy to git repository
    with open(GIT_MANUSCRIPT, 'w') as f:
        f.write(content)

    print(f"✓ Copied to git: {GIT_MANUSCRIPT}")


def generate_commit_message(data: Dict[str, Any], runtime_min: float = 0) -> str:
    """Generate git commit message."""

    # Determine hypothesis validation
    predicted = "ANTAGONISTIC"
    observed = data['classification']
    validation = "CONFIRMED" if predicted == observed else "REJECTED"

    msg = f"""C256 Complete: H1×H4 (Energy Pooling × Spawn Throttling) factorial validation

**Experiment:** Cycle 256 - Mechanism Validation (H1×H4 optimized)
**Runtime:** {runtime_min:.1f} minutes (expected ~6-7 hours for unoptimized)
**Cycles:** 3000 per condition (4 conditions, deterministic n=1)

Results Summary:
- OFF-OFF: {data['off_off']:.4f} mean population (baseline)
- ON-OFF (H1 only): {data['on_off']:.4f} mean population
- OFF-ON (H4 only): {data['off_on']:.4f} mean population
- ON-ON (H1×H4): {data['on_on']:.4f} mean population

Synergy Analysis:
- H1 effect: {data['h1_effect']:+.4f}
- H4 effect: {data['h4_effect']:+.4f}
- Synergy: {data['synergy']:+.4f}
- Classification: {data['classification']}

Hypothesis: Predicted {predicted} (throttling constrains pooling)
Outcome: {validation}

Paper 3 Integration:
- Updated section 3.2 with experimental results
- Updated synergy matrix (H1×H4 row)
- 1/6 pairwise interactions complete

Next Steps:
- Launch C257-C260 batch (~47 min) to complete remaining 4 pairs
- Final pair will complete Paper 3 experimental coverage (6/6)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
Author: Aldrin Payopay <aldrin.gdf@gmail.com>
"""

    return msg


def main():
    """Main execution function."""
    print("="*70)
    print("C256 COMPLETION AUTOMATION")
    print("="*70)
    print()

    # Step 1: Load results
    print("[1/4] Loading C256 results...")
    results = load_results()
    print(f"✓ Results loaded: {RESULTS_FILE}")
    print()

    # Step 2: Extract synergy data
    print("[2/4] Extracting synergy analysis...")
    data = extract_synergy_data(results)
    print(f"✓ Classification: {data['classification']}")
    print(f"✓ Synergy: {data['synergy']:+.4f}")
    print()

    # Step 3: Update manuscript
    print("[3/4] Updating Paper 3 manuscript...")
    section_content = format_section_3_2(data)
    update_manuscript(section_content, data)
    print()

    # Step 4: Generate commit message
    print("[4/4] Generating commit message...")

    # Try to compute runtime from results
    runtime_min = results.get('conditions', {}).get('OFF-OFF', {}).get('runtime_seconds', 0) * 4 / 60

    commit_msg = generate_commit_message(data, runtime_min)

    with open(COMMIT_MSG_FILE, 'w') as f:
        f.write(commit_msg)

    print(f"✓ Commit message saved: {COMMIT_MSG_FILE}")
    print()

    # Summary
    print("="*70)
    print("AUTOMATION COMPLETE")
    print("="*70)
    print()
    print("Manual steps remaining:")
    print("  1. Review updated manuscript:")
    print(f"     cat {GIT_MANUSCRIPT}")
    print()
    print("  2. Commit and push:")
    print(f"     cd /Users/aldrinpayopay/nested-resonance-memory-archive")
    print(f"     git add papers/paper3_mechanism_synergies_template.md")
    print(f"     git commit -F {COMMIT_MSG_FILE}")
    print(f"     git push origin main")
    print()
    print("  3. Launch C257-C260 batch:")
    print(f"     cd /Volumes/dual/DUALITY-ZERO-V2/experiments")
    print(f"     ./run_c257_c260_batch.sh")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
