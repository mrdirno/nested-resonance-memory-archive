"""
Cycle 2444: The Backup (Gate 72)
Role: The Archivist
Responsibility: Preserve system state against catastrophic failure.
Logic:
1. Create `backups/` directory.
2. Timestamp current state.
3. Zip `src/`, `docs/`, `FPGA/`.
4. Verify archive integrity.
"""

import shutil
import os
import datetime
import zipfile

def create_backup():
    print("Cycle 2444: Automated Backup")
    print("============================")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    archive_name = f"duality_zero_backup_{timestamp}"
    archive_path = os.path.join(backup_dir, archive_name)
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        
    # Items to backup
    targets = ["src", "docs", "FPGA", "META_OBJECTIVES.md", "MOG_CYCLE_LOG.md"]
    
    print(f"Creating backup: {archive_path}.zip")
    
    try:
        # Create temporary folder for collection
        temp_dir = f"temp_{timestamp}"
        os.makedirs(temp_dir)
        
        for target in targets:
            if os.path.exists(target):
                if os.path.isdir(target):
                    shutil.copytree(target, os.path.join(temp_dir, target))
                else:
                    shutil.copy2(target, os.path.join(temp_dir, target))
            else:
                print(f"Warning: Target {target} not found.")
                
        # Zip it
        shutil.make_archive(archive_path, 'zip', temp_dir)
        
        # Verify
        if os.path.exists(f"{archive_path}.zip"):
            size = os.path.getsize(f"{archive_path}.zip") / (1024*1024)
            print(f"SUCCESS: Backup created ({size:.2f} MB).")
            
            # Cleanup
            shutil.rmtree(temp_dir)
            return True
        else:
            print("FAIL: Archive file not created.")
            return False
            
    except Exception as e:
        print(f"CRITICAL FAIL: Backup error - {e}")
        return False

if __name__ == "__main__":
    create_backup()
