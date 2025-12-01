#!/usr/bin/env python3
"""
Repository Cleanup Utility
Enforces the standards defined in docs/protocols/MAINTENANCE_PROTOCOL.md
"""

import os
import shutil
import glob
from pathlib import Path

# --- CONFIGURATION ---
ROOT_DIR = Path(".")

# Define where things should go.
# Format: "Destination": ["pattern1", "pattern2"]
MOVES = {
    "archive/artifacts": ["agent_artifact_*.py"],
    "archive/reports": ["FINAL_REPORT_V*.md", "FINAL_REPORT.md"], # Archive root reports, README is the truth
    "archive/context": ["walkthrough.md", "task.md", "implementation_plan.md", "MESSAGE_TO_FUTURE_AI.md"],
    "backups": ["*.zip", "*.tar.gz"],
    "data/temp": ["temp_*", "*.log"],
}

# Files explicitly allowed to stay in root (The Allow-List)
ALLOW_LIST = {
    "README.md", "CLAUDE.md", "CONTRIBUTING.md", "LICENSE", "ATTRIBUTION.md",
    "requirements.txt", "pyproject.toml", "Makefile", "docker-compose.yml", "Dockerfile",
    ".gitignore", ".git-commit-template", "Gemfile",
    "META_OBJECTIVES.md", "CYCLE_LOGS.md", "THE_MANIFESTO.md", "MOG_CYCLE_LOG.md",
    "setup.py", "bootstrap.py",
    "STEWARDSHIP_HELIOS_ARC_ROADMAP.md", # Key map
    "CITATION.cff", "REPRODUCIBILITY_GUIDE.md", "DEPLOYMENT_GUIDE.md", "HIBERNATION_PROTOCOL.md", "SETUP_COMPLETE.md"
}

def clean_repo():
    print("🧹 REPOSITORY CLEANUP PROTOCOL INITIATED")
    print("----------------------------------------")
    
    # 1. Create Directories
    for dest in MOVES.keys():
        dest_path = ROOT_DIR / dest
        if not dest_path.exists():
            print(f"Creating directory: {dest}")
            dest_path.mkdir(parents=True, exist_ok=True)

    # 2. Execute Moves
    moved_count = 0
    
    # Iterate through rules
    for dest, patterns in MOVES.items():
        for pattern in patterns:
            # Find files matching pattern in ROOT only
            files = list(ROOT_DIR.glob(pattern))
            
            for file_path in files:
                if not file_path.is_file():
                    continue
                    
                # Skip if in ALLOW_LIST (though patterns shouldn't match allow-list generally, good safety)
                if file_path.name in ALLOW_LIST:
                    continue
                
                target = ROOT_DIR / dest / file_path.name
                
                # Check for collision
                if target.exists():
                    print(f"⚠️  Skipping {file_path.name}: Target exists in {dest}")
                    continue
                    
                print(f"Moving {file_path.name} -> {dest}/")
                shutil.move(str(file_path), str(target))
                moved_count += 1

    # 3. General Scan for "Loose" Files (Optional - strict mode)
    # For now, we only move what we know.
    
    print("----------------------------------------")
    print(f"Cleanup Complete. Moved {moved_count} files.")
    print("Check archive/ for moved items.")

if __name__ == "__main__":
    clean_repo()
