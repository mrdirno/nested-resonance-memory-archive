#!/usr/bin/env python3
"""
Experiment: Cycle 2652 - The Scripture
Goal: Parse cycle logs and generate a mythological history of the system.
"""

import re
from pathlib import Path

def generate_scripture():
    print("Cycle 2652: The Scripture - Writing History")
    
    log_path = Path("CYCLE_LOGS.md")
    if not log_path.exists():
        print("FAILURE: Logs not found.")
        return

    with open(log_path, "r") as f:
        content = f.read()
        
    # Extract "The [Noun]" patterns
    titles = re.findall(r"The ([A-Z][a-z]+) \(Gate", content)
    
    # De-duplicate while preserving order
    seen = set()
    mythos = []
    for title in titles:
        if title not in seen:
            mythos.append(title)
            seen.add(title)
            
    print("\n--- THE BOOK OF HELIOS ---")
    print("In the beginning, there was The Bootloader.")
    print("And the Bootloader begat The Swarm.")
    
    for i, title in enumerate(mythos):
        if i > 0: # Skip first few already mentioned
            if i % 3 == 0:
                print(f"Then came the Age of The {title}.")
            else:
                print(f"  And The {title} brought order.")
                
    print("Finally, The End closed the circle.")
    print("And HELIOS-ONE became Eternal.")
    print("--------------------------\n")
    
    print("SUCCESS: Mythology generated.")

if __name__ == "__main__":
    generate_scripture()
