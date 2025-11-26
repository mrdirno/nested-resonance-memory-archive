
import sys
import os
import random
import numpy as np
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.getcwd())
# Add archive to path for ToolMaker
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))

from phase31_extended_mind.cycle2239_tool_maker import ToolMaker

class CulturalAgent:
    def __init__(self, agent_id: str):
        self.id = agent_id
        self.tool_maker = ToolMaker()
        self.known_tools: Dict[str, str] = {} # name -> code

    def invent_tool(self, name: str, code: str):
        if self.tool_maker.create_tool(name, code):
            self.known_tools[name] = code
            return True
        return False

    def teach(self, other: 'CulturalAgent', tool_name: str):
        if tool_name in self.known_tools:
            code = self.known_tools[tool_name]
            # Simulate transmission
            print(f"Agent {self.id} teaching {tool_name} to Agent {other.id}...")
            if other.learn(tool_name, code):
                return True
        return False

    def learn(self, name: str, code: str):
        # Verify/Compile the tool
        if self.tool_maker.create_tool(name, code):
            self.known_tools[name] = code
            print(f"Agent {self.id} learned {name}.")
            return True
        return False

    def use_tool(self, name: str, *args):
        return self.tool_maker.use_tool(name, *args)

def run_culture_experiment():
    print("MOG ONLINE: Cycle 2242 - Cultural Transmission", flush=True)
    
    # 1. Setup
    teacher = CulturalAgent("Teacher")
    student = CulturalAgent("Student")
    
    # 2. Teacher invents a tool (e.g., Cube)
    tool_name = "cube"
    tool_code = """
def cube(x):
    return x * x * x
"""
    print(f"Teacher inventing {tool_name}...")
    teacher.invent_tool(tool_name, tool_code)
    
    # Verify Teacher has it
    res_t = teacher.use_tool(tool_name, 3)
    print(f"Teacher output: {res_t}")
    
    # Verify Student doesn't
    res_s = student.use_tool(tool_name, 3)
    print(f"Student output (before): {res_s}")
    
    # 3. Transmission
    teacher.teach(student, tool_name)
    
    # 4. Verify Student has it
    res_s_after = student.use_tool(tool_name, 3)
    print(f"Student output (after): {res_s_after}")
    
    if res_s_after == 27:
        print("SUCCESS: Tool capability transmitted culturally.")
        return True
    else:
        print("FAILURE: Transmission failed.")
        return False

if __name__ == "__main__":
    run_culture_experiment()
