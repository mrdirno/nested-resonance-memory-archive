"""
Cycle 470: The Cleanup (Refactoring)
Role: The Janitor
Responsibility: Maintain directory hygiene.
"""
import os
import shutil
import glob

SOURCE_DIR = "experiments"
DEST_DIR = "archive/experiments"

def run_experiment():
    print("Cycle 470: Repository Cleanup")
    print("=============================")
    
    if not os.path.exists(DEST_DIR):
        os.makedirs(DEST_DIR)
        print(f"Created {DEST_DIR}")
        
    files = glob.glob(os.path.join(SOURCE_DIR, "cycle*.py"))
    count = 0
    
    for f in files:
        filename = os.path.basename(f)
        
        # Don't move self yet
        if "cycle470" in filename:
            continue
            
        dest_path = os.path.join(DEST_DIR, filename)
        shutil.move(f, dest_path)
        count += 1
        # print(f"Moved {filename}")
        
    print(f"SUCCESS: Moved {count} experiment files to archive.")

if __name__ == "__main__":
    run_experiment()
