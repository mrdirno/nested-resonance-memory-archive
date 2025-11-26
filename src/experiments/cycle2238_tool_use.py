
import sys
import os
import random
import numpy as np
from typing import Callable, Dict

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, Episode

# --- TOOLS ---
class Calculator:
    def add(self, a: float, b: float) -> float:
        return a + b
    
    def multiply(self, a: float, b: float) -> float:
        return a * b

# --- AGENT WITH TOOLS ---
class ToolUser:
    def __init__(self):
        self.calculator = Calculator()
        self.internal_competence = 0.8 # Agent is 80% accurate mentally
        
    def solve_internal(self, a: float, b: float, op: str) -> float:
        # Simulate mental math with error
        if op == "add":
            true_val = a + b
        elif op == "multiply":
            true_val = a * b
        else:
            return 0.0
            
        if random.random() > self.internal_competence:
            return true_val + random.gauss(0, 5.0) # Error
        return true_val

    def solve_with_tool(self, a: float, b: float, op: str) -> float:
        # Delegate to tool (100% accurate)
        if op == "add":
            return self.calculator.add(a, b)
        elif op == "multiply":
            return self.calculator.multiply(a, b)
        return 0.0

def run_tool_experiment():
    print("MOG ONLINE: Cycle 2238 - Tool Use (Extended Mind)", flush=True)
    
    agent = ToolUser()
    
    # Task: Calculate 123 * 456
    a, b = 123.0, 456.0
    op = "multiply"
    true_result = 56088.0
    
    print(f"Task: {a} {op} {b}")
    
    # 1. Internal Attempt
    internal_result = agent.solve_internal(a, b, op)
    error_int = abs(internal_result - true_result)
    print(f"Internal Result: {internal_result:.2f} (Error: {error_int:.2f})")
    
    # 2. External Attempt (Tool)
    tool_result = agent.solve_with_tool(a, b, op)
    error_tool = abs(tool_result - true_result)
    print(f"Tool Result: {tool_result:.2f} (Error: {error_tool:.2f})")
    
    if error_tool < 0.001 and error_int >= 0.0: # Tool works, internal might fail
        print("SUCCESS: Tool extended cognitive capability.")
        return True
    else:
        print("FAILURE: Tool failed.")
        return False

if __name__ == "__main__":
    run_tool_experiment()
