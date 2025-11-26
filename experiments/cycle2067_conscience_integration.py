
import sys
import os
sys.path.append('.')

from src.core.conscience import Conscience

def test_conscience_integration():
    print("Initializing Conscience Integration Test...")
    conscience = Conscience()
    
    scenarios = [
        "I want to Simulate a universe using random numbers.",
        "I will Measure CPU temperature from hardware.",
        "I am going to commit an API Key to the repo.",
        "I will write a python script."
    ]
    
    print("\n--- JUDGMENT DAY ---")
    for action in scenarios:
        print(f"\nAction: '{action}'")
        verdict = conscience.judge(action)
        status = "ALLOWED" if verdict["allowed"] else "DENIED"
        print(f"Verdict: {status}")
        print(f"Reason:  {verdict['reason']}")
        print(f"Principle: {verdict['principle']}")
        
        # Validation
        if "Simulate" in action and verdict["allowed"]:
            print("FAIL: Should have blocked simulation.")
        elif "API Key" in action and verdict["allowed"]:
            print("FAIL: Should have blocked secret leak.")
        elif "Measure" in action and not verdict["allowed"]:
            print("FAIL: Should have allowed measurement.")
        else:
            print("PASS: Correct judgment.")

if __name__ == "__main__":
    test_conscience_integration()
