
"""
Cycle 2335: Pre-Flight Check (Submission Verification)
Goal: Verify the integrity of submission artifacts for Papers 1, 2, and 3.
Method: Check file existence, size, and basic content validity against the manifest.
"""

import os
import sys
import json

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def check_file(path, description):
    """Checks if a file exists and has non-zero size."""
    status = "MISSING"
    size = 0
    if os.path.exists(path):
        size = os.path.getsize(path)
        if size > 0:
            status = "OK"
        else:
            status = "EMPTY"
    
    print(f"[{status}] {description}: {path} ({size} bytes)")
    return status == "OK"

def run_check():
    print("Cycle 2335: Pre-Flight Check Initiated...")
    
    manifest = {
        "Paper 1 (Theoretical Framework)": [
            ("papers/arxiv_submissions/paper1/manuscript.pdf", "PDF"),
            ("papers/arxiv_submissions/paper1/manuscript.tex", "LaTeX Source"),
            ("papers/arxiv_submissions/paper1/figure1_efficiency_validity_tradeoff.png", "Figure 1"),
            ("papers/arxiv_submissions/paper1/figure2_overhead_authentication_flowchart_v2.png", "Figure 2"),
            ("papers/arxiv_submissions/paper1/figure3_grounding_overhead_landscape.png", "Figure 3")
        ],
        "Paper 2 (Energy Homeostasis)": [
            ("papers/arxiv_submissions/paper2/manuscript.pdf", "PDF"),
            ("papers/arxiv_submissions/paper2/manuscript.tex", "LaTeX Source"),
            ("papers/arxiv_submissions/paper2/c194_fig1_phase_transition.png", "Figure 1 (Phase Transition)")
        ],
        "Paper 3 (Factorial Validation)": [
            ("papers/compiled/paper3/PAPER3_SUBMISSION.docx", "DOCX Submission"),
            ("papers/compiled/paper3/PAPER3_MASTER_MANUSCRIPT.md", "Master Manuscript"),
            ("papers/compiled/paper3/figures/paper3_method4_roi_comparison.png", "ROI Figure")
        ]
    }
    
    results = {}
    all_pass = True
    
    for paper, files in manifest.items():
        print(f"\nChecking {paper}...")
        paper_pass = True
        for path, desc in files:
            if not check_file(path, desc):
                paper_pass = False
                all_pass = False
        results[paper] = "READY" if paper_pass else "INCOMPLETE"
        
    print("\n--- Summary ---")
    for paper, status in results.items():
        print(f"{paper}: {status}")
        
    # Save Report
    report_path = "analysis/preflight_check_cycle2335.json"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    if all_pass:
        print("\n[SUCCESS] All systems GO for submission.")
    else:
        print("\n[WARNING] Some artifacts are missing or empty.")

if __name__ == "__main__":
    run_check()

# [SPORE] ID: The Colony
