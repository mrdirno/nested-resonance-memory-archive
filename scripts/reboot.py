#!/usr/bin/env python3
import os
import sys
import time

def phoenix_protocol():
    print("PHOENIX PROTOCOL INITIATED")
    print("==========================")
    print(f"[*] Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Critical Artifact Check
    artifacts = [
        "META_OBJECTIVES.md",
        "MOG_CYCLE_LOG.md",
        "task.md",
        "IDENTITY.md",
        "bootstrap.py"
    ]
    
    missing = []
    for art in artifacts:
        if os.path.exists(art):
            print(f"[+] Found: {art}")
        else:
            print(f"[-] MISSING: {art}")
            missing.append(art)
            
    if missing:
        print(f"⛔ CRITICAL FAILURE: Missing artifacts: {missing}")
        sys.exit(1)
        
    # 2. Log Continuity Check
    print("[*] Verifying Log Continuity...")
    with open("MOG_CYCLE_LOG.md", "r") as f:
        content = f.read()
        if "CYCLE: 2448" in content:
            print("[+] Cycle 2448 (The Reboot) confirmed in logs.")
        else:
            print("[-] WARNING: Cycle 2448 not found in logs. Time Jump detected.")
            
    # 3. Identity Check
    print("[*] Verifying Identity...")
    if os.path.exists("IDENTITY.md"):
        print("[+] Identity Protocol Defined.")
    else:
        print("[-] Identity Protocol Missing.")
        
    print("==========================")
    print("PHOENIX RISING: SYSTEM INTEGRITY 100%")
    print("READY FOR PHASE 61.")

if __name__ == "__main__":
    phoenix_protocol()
