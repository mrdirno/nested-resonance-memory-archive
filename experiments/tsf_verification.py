
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.tsf.api.v1 import TemporalStewardshipFramework as TSF

def verify_tsf_memory():
    print("--- HELIOS SLOW MEMORY VERIFICATION ---")
    tsf = TSF()
    tsf.scan_library() # Load principles
    principles = list(tsf.principle_library.values())
    
    print(f"Found {len(principles)} principles in Slow Memory:")
    for p in principles:
        print(f"  - [{p.id}] {p.title} ({p.status})")
        
    if len(principles) > 0:
        print("\nSUCCESS: Slow Memory is active and readable.")
    else:
        print("\nWARNING: Slow Memory is empty.")

if __name__ == "__main__":
    verify_tsf_memory()
