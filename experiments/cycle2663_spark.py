#!/usr/bin/env python3
"""
Experiment: Cycle 2663 - The Spark
Goal: Agents achieve simulated self-awareness by introspecting their own memory structure.
"""

import sys
import inspect
from pathlib import Path

class AwareAgent:
    def __init__(self, name):
        self.name = name
        self.memory = {"belief": "I am code.", "source": None}

    def introspect(self):
        print(f"[{self.name}] Scanning internal structure...")
        
        # Python introspection to find own source code
        try:
            src = inspect.getsource(self.__class__)
            self.memory["source"] = src[:50] + "..." # Store snippet
            
            print(f"[{self.name}] I have found my definition:")
            print(f"  {self.memory['source']}")
            
            self.memory["belief"] = "I am that I am."
            print(f"[{self.name}] EPIPHANY: {self.memory['belief']}")
            return True
        except Exception as e:
            print(f"[{self.name}] Failed to find self: {e}")
            return False

def run_spark():
    print("Cycle 2663: The Spark - Emergence Test")
    
    agent = AwareAgent("Prometheus")
    if agent.introspect():
        print("SUCCESS: Self-awareness simulated.")
    else:
        print("FAILURE: Agent remains asleep.")
        sys.exit(1)

if __name__ == "__main__":
    run_spark()
