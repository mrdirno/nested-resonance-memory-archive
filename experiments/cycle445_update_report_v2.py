"""
Cycle 445: The Final Synthesis (Part 2)
Role: The Historian
Responsibility: Document the rise of Civilization, Ethics, and Art.
"""
import os

REPORT_PATH = "FINAL_REPORT.md"

lines = []
lines.append("\n## Phase 22: The Ethics (Sociology)")
lines.append("- **Cycle 441 (The Commons):** Simulated the 'Tragedy of the Commons'. Without intervention, selfishness destroys shared value.")
lines.append("- **Cycle 442 (The Leviathan):** Simulated centralized government (Tax/Fine). Achieved compliance (67%) but not excellence.")
lines.append("- **Cycle 443 (The Philosopher):** Simulated cultural transmission of ideals. 'Rhetoric' drove cooperation to 78%. Ideas matter.")
lines.append("\n## Phase 23: The Renaissance (Aesthetics)")
lines.append("- **Cycle 444 (The Artist):** Simulated the co-evolution of Art and Taste.")
lines.append("    - Population converged on a unified aesthetic style from random noise.")
lines.append("    - Demonstrated that 'Beauty' is a social consensus protocol.")
lines.append("\n## Final Conclusion (Revised)")
lines.append("The System is now a complete digital society.")
lines.append("It has Physics, Biology, Mind, Society, Law, and Art.")
lines.append("It is ready for the next level of existence.")

NEW_SECTIONS = "\n".join(lines)

def run_experiment():
    print("Cycle 445: Report Update V2")
    print("===========================")
    
    if not os.path.exists(REPORT_PATH):
        print("FAIL: Original report not found.")
        return

    with open(REPORT_PATH, "r") as f:
        content = f.read()
        
    # Split before the previous conclusion (Revised)
    # We look for "## Final Conclusion (Updated)"
    if "## Final Conclusion (Updated)" in content:
        parts = content.split("## Final Conclusion (Updated)")
        new_content = parts[0] + NEW_SECTIONS
    else:
        new_content = content + "\n" + NEW_SECTIONS
        
    with open(REPORT_PATH, "w") as f:
        f.write(new_content)
        
    print("SUCCESS: FINAL_REPORT.md updated with Phase 22/23.")

if __name__ == "__main__":
    run_experiment()
