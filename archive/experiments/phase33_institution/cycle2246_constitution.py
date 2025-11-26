
import sys
import os
from typing import List, Dict

# Add project root to path
sys.path.append(os.getcwd())

class Constitution:
    def __init__(self):
        self.laws: Dict[str, str] = {}
        
    def add_law(self, name: str, text: str):
        self.laws[name] = text
        print(f"Constitution Amended: {name} added.")
        
    def check_legality(self, action: str) -> bool:
        # Simple parser
        for law_text in self.laws.values():
            if f"FORBID {action}" in law_text:
                return False
        return True

class Citizen:
    def __init__(self, name: str, constitution: Constitution):
        self.name = name
        self.constitution = constitution
        
    def attempt_action(self, action: str):
        if self.constitution.check_legality(action):
            print(f"{self.name} performs {action}.")
            return True
        else:
            print(f"{self.name} blocked from {action} by Constitution.")
            return False

def run_constitution_experiment():
    print("MOG ONLINE: Cycle 2246 - The Constitution", flush=True)
    
    # 1. Create Constitution
    const = Constitution()
    
    # 2. Add Law
    const.add_law("First Amendment", "FORBID Murder")
    
    # 3. Citizen Action
    citizen = Citizen("Alice", const)
    
    # Test 1: Allowed Action
    res1 = citizen.attempt_action("Trade")
    
    # Test 2: Forbidden Action
    res2 = citizen.attempt_action("Murder")
    
    if res1 and not res2:
        print("SUCCESS: Rule of Law established.")
        return True
    else:
        print("FAILURE: Law not enforced.")
        return False

if __name__ == "__main__":
    run_constitution_experiment()
