#!/usr/bin/env python3
import sys
import shutil
import platform
import os

def check_system_health():
    print("DUALITY-ZERO SYSTEM HEALTH CHECK")
    print("================================")
    
    # 1. Python Version
    print(f"[*] Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("[-] WARNING: Python version < 3.8")
    else:
        print("[+] Python version OK.")

    # 2. Disk Space
    total, used, free = shutil.disk_usage("/")
    free_gb = free // (2**30)
    print(f"[*] Disk Space Free: {free_gb} GB")
    if free_gb < 10:
        print("[-] WARNING: Low disk space (< 10 GB)")
    else:
        print("[+] Disk space OK.")

    # 3. Platform Info
    print(f"[*] System: {platform.system()} {platform.release()}")
    print(f"[*] Machine: {platform.machine()}")
    
    print("================================")
    print("[+] SYSTEM VITALS STABLE.")

if __name__ == "__main__":
    check_system_health()
