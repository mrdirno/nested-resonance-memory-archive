"""
Cycle 488: Analysis Cleanup
Role: The Janitor
Responsibility: Archive old analysis scripts.
"""
import os
import shutil
import glob

SOURCE_DIR = "analysis"
DEST_DIR = "archive/analysis"

def run_experiment():
    print("Cycle 488: Analysis Cleanup")
    print("===========================")
    
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        
    # Pattern: c[digit]*.py (e.g., c186_...) and mog_*.py
    patterns = ["c[0-9]*.py", "mog_*.py", "paper*.py", "generate_*.py", "analyze_*.py"]
    
    count = 0
    for pattern in patterns:
        files = glob.glob(os.path.join(SOURCE_DIR, pattern))
        for f in files:
            filename = os.path.basename(f)
            dest_path = os.path.join(DEST_DIR, filename)
            shutil.move(f, dest_path)
            count += 1
            
    print(f"SUCCESS: Moved {count} analysis files to archive.")

if __name__ == "__main__":
    run_experiment()
