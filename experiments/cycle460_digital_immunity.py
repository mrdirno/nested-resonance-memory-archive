"""
Cycle 460: The Antibody (Digital Immunity)
Role: The Doctor
Responsibility: Protect the codebase from corruption (Entropy/Attack).
"""
import hashlib
import os
import time
import shutil

TARGET_FILE = "src/helios/operator.py"
BACKUP_FILE = "src/helios/operator.py.secure"

def calculate_hash(filepath):
    if not os.path.exists(filepath): return None
    with open(filepath, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def run_experiment():
    print("Cycle 460: Digital Immunity Test")
    print("================================")
    
    # 1. Establish Baseline (Vaccination)
    if not os.path.exists(TARGET_FILE):
        print(f"Target {TARGET_FILE} not found.")
        return
        
    print(f"Target: {TARGET_FILE}")
    baseline_hash = calculate_hash(TARGET_FILE)
    print(f"Baseline Hash: {baseline_hash[:8]}...")
    
    # Create secure backup
    shutil.copy(TARGET_FILE, BACKUP_FILE)
    
    # 2. Simulate Attack (Infection)
    print("\n[ATTACK] Injecting viral code...")
    with open(TARGET_FILE, "a") as f:
        f.write("\n# VIRUS: SYSTEM COMPROMISED\n")
        
    infected_hash = calculate_hash(TARGET_FILE)
    print(f"Infected Hash: {infected_hash[:8]}...")
    
    if infected_hash != baseline_hash:
        print("[ALERT] Integrity Violation Detected!")
    else:
        print("[FAIL] Attack failed to change hash (Impossible).")
        return

    # 3. Immune Response (Healing)
    print("\n[DEFENSE] Initiating Immune Response...")
    shutil.copy(BACKUP_FILE, TARGET_FILE)
    
    restored_hash = calculate_hash(TARGET_FILE)
    print(f"Restored Hash: {restored_hash[:8]}...")
    
    if restored_hash == baseline_hash:
        print("SUCCESS: System healed itself.")
    else:
        print("FAIL: Healing failed.")
        
    # Cleanup
    if os.path.exists(BACKUP_FILE):
        os.remove(BACKUP_FILE)

if __name__ == "__main__":
    run_experiment()
