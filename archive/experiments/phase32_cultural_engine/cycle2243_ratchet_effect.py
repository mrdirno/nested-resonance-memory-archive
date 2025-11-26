
import sys
import os
import random
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())
# Add archive to path for ToolMaker
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))

from phase31_extended_mind.cycle2239_tool_maker import ToolMaker
from src.experiments.cycle2242_cultural_transmission import CulturalAgent

class InnovativeAgent(CulturalAgent):
    def improve_tool(self, name: str, current_code: str) -> str:
        """
        Simulate innovation by modifying the code string.
        Goal: Make 'cube' into 'power4' (x^4).
        Simplified: We just replace the operation string if we are 'smart' enough.
        """
        # Simulate trial and error
        print(f"Agent {self.id} attempting to improve {name}...")
        
        # Naive mutation: Replace * * * with * * * *
        if "x * x * x" in current_code:
            new_code = current_code.replace("x * x * x", "x * x * x * x")
            # Rename function to match new tool name
            new_code = new_code.replace(f"def {name}(x):", f"def {name}_v2(x):")
            
            # Verify it works
            if self.tool_maker.create_tool(name + "_v2", new_code):
                # Test it: 2^4 = 16. Old was 2^3 = 8.
                res = self.tool_maker.use_tool(name + "_v2", 2)
                if res == 16:
                    print(f"Innovation SUCCESS: {name} upgraded.")
                    return new_code
        
        print("Innovation FAILED.")
        return current_code

def run_ratchet_experiment():
    print("MOG ONLINE: Cycle 2243 - The Ratchet Effect", flush=True)
    
    # 1. Setup
    gen1 = InnovativeAgent("Gen1")
    gen2 = InnovativeAgent("Gen2")
    
    # 2. Gen1 invents Base Tool (Cube)
    tool_name = "math_op"
    code_v1 = """
def math_op(x):
    return x * x * x
"""
    gen1.invent_tool(tool_name, code_v1)
    
    # 3. Transmit to Gen2
    gen1.teach(gen2, tool_name)
    
    # 4. Gen2 Innovates (Ratchet)
    code_v2 = gen2.improve_tool(tool_name, gen2.known_tools[tool_name])
    
    if code_v2 != code_v1:
        # Update Gen2's toolset
        gen2.known_tools[tool_name] = code_v2
        
        # 5. Transmit back (or to Gen3)
        # Let's verify Gen2 has the better tool
        res = gen2.use_tool(tool_name + "_v2", 2) # ToolMaker registered it as _v2
        if res == 16:
            print("SUCCESS: Culture ratcheted up (x^3 -> x^4).")
            return True
            
    print("FAILURE: Ratchet stuck.")
    return False

if __name__ == "__main__":
    run_ratchet_experiment()
