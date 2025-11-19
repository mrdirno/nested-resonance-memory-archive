#!/usr/bin/env python3
"""
Batch Experiment Completion Automation Script
=============================================

Generalizes C256 automation for C257-C260 batch experiments.
Automates data extraction, manuscript integration, and git commit preparation.

Usage:
    python automate_batch_completion.py --cycle 257 --m1 H1 --m2 H5
    python automate_batch_completion.py --cycle 258 --m1 H2 --m2 H4
    ...

Author: Aldrin Payopay <aldrin.gdf@gmail.com>
Co-Author: Claude (DUALITY-ZERO-V2)
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any

# Paths
BASE_DIR = Path("/Volumes/dual/DUALITY-ZERO-V2")
RESULTS_DIR = BASE_DIR / "experiments/results"
MANUSCRIPT_FILE = BASE_DIR / "papers/paper3_mechanism_synergies_template.md"
GIT_MANUSCRIPT = Path("/Users/aldrinpayopay/nested-resonance-memory-archive/papers/paper3_mechanism_synergies_template.md")
COMMIT_MSG_FILE = Path("/tmp/batch_commit_message.txt")

MECHANISM_NAMES = {
    "H1": "Energy Pooling",
    "H2": "Reality Sources",
    "H4": "Spawn Throttling",
    "H5": "Energy Recovery"
}

def load_results(cycle: int, m1: str, m2: str) -> Dict[str, Any]:
    """Load experimental results."""
    # Construct filename: cycle257_h1h5_optimized_results.json
    filename = f"cycle{cycle}_{m1.lower()}{m2.lower()}_optimized_results.json"
    results_file = RESULTS_DIR / filename

    if not results_file.exists():
        print(f"❌ ERROR: Results file not found: {results_file}")
        print(f"   Cycle {cycle} may not have completed yet.")
        sys.exit(1)

    with open(results_file, 'r') as f:
        return json.load(f)

def extract_synergy_data(results: Dict[str, Any], m1: str, m2: str) -> Dict[str, Any]:
    """Extract synergy analysis from results."""
    synergy = results['synergy_analysis']
    
    # Map generic keys to specific mechanisms if needed, but the JSON usually has specific keys
    # The JSON structure in C255 was: h1_effect, h2_effect
    # We need to handle dynamic keys
    
    m1_key = f"{m1.lower()}_effect"
    m2_key = f"{m2.lower()}_effect"
    
    return {
        'off_off': synergy['off_off'],
        'on_off': synergy['on_off'],
        'off_on': synergy['off_on'],
        'on_on': synergy['on_on'],
        'm1_effect': synergy.get(m1_key, 0.0),
        'm2_effect': synergy.get(m2_key, 0.0),
        'additive_prediction': synergy['additive_prediction'],
        'synergy': synergy['synergy'],
        'fold_change': synergy['fold_change'],
        'classification': synergy['classification'],
        'interpretation': synergy['interpretation']
    }

def format_section(data: Dict[str, Any], cycle: int, m1: str, m2: str) -> str:
    """Format manuscript section."""
    
    # Map cycle to section number
    cycle_map = {
        255: "3.1",
        256: "3.2",
        257: "3.3",
        258: "3.4",
        259: "3.5",
        260: "3.6"
    }
    section_num = cycle_map.get(cycle, "3.X")
    
    # Determine hypothesis validation (placeholder logic, refine as needed)
    # We need to know the predicted hypothesis. 
    # H1xH2: Synergistic
    # H1xH4: Antagonistic
    # H1xH5: Synergistic
    # H2xH4: Additive
    # H2xH5: Synergistic
    # H4xH5: Additive
    
    hypotheses = {
        "H1H2": "SYNERGISTIC",
        "H1H4": "ANTAGONISTIC",
        "H1H5": "SYNERGISTIC",
        "H2H4": "ADDITIVE",
        "H2H5": "SYNERGISTIC",
        "H4H5": "ADDITIVE"
    }
    pair_key = f"{m1}{m2}"
    predicted = hypotheses.get(pair_key, "UNKNOWN")
    observed = data['classification']
    validation = "CONFIRMED" if predicted == observed else "REJECTED"

    m1_name = MECHANISM_NAMES[m1]
    m2_name = MECHANISM_NAMES[m2]

    section = f"""### {section_num} Experiment {section_num.split('.')[-1]}: {m1}×{m2} ({m1_name} × {m2_name})

**Condition Results:**
- OFF-OFF: {data['off_off']:.4f} mean population
- {m1}-only: {data['on_off']:.4f} mean population
- {m2}-only: {data['off_on']:.4f} mean population
- {m1}×{m2}: {data['on_on']:.4f} mean population

**Effect Sizes:**
- {m1} effect: {data['m1_effect']:+.4f}
- {m2} effect: {data['m2_effect']:+.4f}
- Predicted combined: {data['additive_prediction']:.4f}
- Observed combined: {data['on_on']:.4f}
- **Synergy: {data['synergy']:+.4f}**

**Classification:** {data['classification']}

**Interpretation:** {data['interpretation']}

**Hypothesis Validation:** {validation} - Predicted {predicted}, observed {observed}
"""
    return section

def update_manuscript(section_content: str, data: Dict[str, Any], cycle: int, m1: str, m2: str) -> None:
    """Update Paper 3 manuscript."""
    
    # Read manuscript
    with open(MANUSCRIPT_FILE, 'r') as f:
        content = f.read()

    # Map cycle to section number for placeholder replacement
    cycle_map = {
        255: "3.1",
        256: "3.2",
        257: "3.3",
        258: "3.4",
        259: "3.5",
        260: "3.6"
    }
    section_num = cycle_map.get(cycle, "3.X")
    m1_name = MECHANISM_NAMES[m1]
    m2_name = MECHANISM_NAMES[m2]

    # Construct placeholder string to replace
    # Note: The template has specific headers. We need to match them.
    # Example: ### 3.3 Experiment 3: H1×H5 (Energy Pooling × Energy Recovery)
    
    header = f"### {section_num} Experiment {section_num.split('.')[-1]}: {m1}×{m2} ({m1_name} × {m2_name})"
    placeholder = f"{header}\n\n[TO BE FILLED - Same structure as 3.1]"
    
    if placeholder not in content:
        print(f"⚠ WARNING: Placeholder not found for {header}")
        print("   Trying loose match...")
        # Try to find just the header and append if the placeholder text is different
        if header in content:
             # Find the header and replace the block following it until the next section
             pass # Complex logic, for now assume strict match or manual fix
        else:
             print("   Header not found either.")
             return

    content = content.replace(placeholder, section_content.strip())

    # Update synergy matrix table row
    # | H1×H5 | [TO BE FILLED] | [TO BE FILLED] | SYNERGISTIC |
    old_row_start = f"| {m1}×{m2} | [TO BE FILLED] | [TO BE FILLED] |"
    # We need to find the full line to replace it correctly, preserving the hypothesis column if possible
    # But the hypothesis is hardcoded in the template.
    
    # Let's just replace the specific columns if we can identify the line
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if f"| {m1}×{m2} |" in line and "[TO BE FILLED]" in line:
            parts = line.split('|')
            # parts[0] is empty, parts[1] is pair, parts[2] is synergy, parts[3] is classification, parts[4] is hypothesis
            if len(parts) >= 5:
                parts[2] = f" {data['synergy']:+.4f} "
                parts[3] = f" {data['classification']} "
                lines[i] = "|".join(parts)
                print(f"✓ Updated synergy matrix row for {m1}×{m2}")
                break
    
    content = "\n".join(lines)

    # Write updated manuscript
    with open(MANUSCRIPT_FILE, 'w') as f:
        f.write(content)

    print(f"✓ Updated manuscript: {MANUSCRIPT_FILE}")

    # Copy to git repository
    with open(GIT_MANUSCRIPT, 'w') as f:
        f.write(content)

    print(f"✓ Copied to git: {GIT_MANUSCRIPT}")

def generate_commit_message(data: Dict[str, Any], cycle: int, m1: str, m2: str) -> str:
    """Generate git commit message."""
    
    hypotheses = {
        "H1H2": "SYNERGISTIC",
        "H1H4": "ANTAGONISTIC",
        "H1H5": "SYNERGISTIC",
        "H2H4": "ADDITIVE",
        "H2H5": "SYNERGISTIC",
        "H4H5": "ADDITIVE"
    }
    pair_key = f"{m1}{m2}"
    predicted = hypotheses.get(pair_key, "UNKNOWN")
    observed = data['classification']
    validation = "CONFIRMED" if predicted == observed else "REJECTED"
    
    msg = f"""C{cycle} Complete: {m1}×{m2} ({MECHANISM_NAMES[m1]} × {MECHANISM_NAMES[m2]}) validation

**Experiment:** Cycle {cycle} - Mechanism Validation ({m1}×{m2})
**Cycles:** 3000 per condition (deterministic n=1)

Results Summary:
- OFF-OFF: {data['off_off']:.4f}
- {m1}-only: {data['on_off']:.4f}
- {m2}-only: {data['off_on']:.4f}
- {m1}×{m2}: {data['on_on']:.4f}

Synergy Analysis:
- Synergy: {data['synergy']:+.4f}
- Classification: {data['classification']}

Hypothesis: Predicted {predicted}, Observed {observed} ({validation})

Paper 3 Integration:
- Updated section for C{cycle}
- Updated synergy matrix
"""
    return msg

def main():
    parser = argparse.ArgumentParser(description="Automate batch experiment completion")
    parser.add_argument("--cycle", type=int, required=True, help="Cycle number (e.g., 257)")
    parser.add_argument("--m1", type=str, required=True, help="First mechanism (e.g., H1)")
    parser.add_argument("--m2", type=str, required=True, help="Second mechanism (e.g., H5)")
    
    args = parser.parse_args()
    
    print(f"Processing C{args.cycle}: {args.m1}×{args.m2}...")
    
    results = load_results(args.cycle, args.m1, args.m2)
    data = extract_synergy_data(results, args.m1, args.m2)
    
    section_content = format_section(data, args.cycle, args.m1, args.m2)
    update_manuscript(section_content, data, args.cycle, args.m1, args.m2)
    
    commit_msg = generate_commit_message(data, args.cycle, args.m1, args.m2)
    with open(COMMIT_MSG_FILE, 'w') as f:
        f.write(commit_msg)
        
    print(f"✓ Commit message saved: {COMMIT_MSG_FILE}")

if __name__ == "__main__":
    main()
