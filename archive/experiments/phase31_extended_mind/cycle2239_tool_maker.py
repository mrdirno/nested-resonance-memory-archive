
import sys
import os
import math

# Add project root to path
sys.path.append(os.getcwd())

class ToolMaker:
    def __init__(self):
        self.toolbox = {}
        
    def identify_need(self, problem_type: str) -> bool:
        # Simulate realizing "I don't know how to solve this"
        if problem_type not in self.toolbox:
            print(f"Need identified: {problem_type}")
            return True
        return False

    def create_tool(self, name: str, code_str: str):
        """
        Dynamically compile and load a new tool.
        """
        try:
            # Safety: In a real system, this needs a sandbox.
            # Here we trust the pilot.
            local_scope = {}
            exec(code_str, {"math": math}, local_scope)
            
            # Assuming the code defines a function with the same name
            if name in local_scope:
                self.toolbox[name] = local_scope[name]
                print(f"Tool '{name}' created successfully.")
                return True
            else:
                print(f"Error: Code did not define function '{name}'")
                return False
        except Exception as e:
            print(f"Compilation Error: {e}")
            return False

    def use_tool(self, name: str, *args) -> float:
        if name in self.toolbox:
            return self.toolbox[name](*args)
        return None

def run_tool_maker():
    print("MOG ONLINE: Cycle 2239 - The Tool Maker", flush=True)
    
    maker = ToolMaker()
    
    # 1. Encounter problem: Square Root of 144
    problem = "sqrt"
    input_val = 144.0
    
    if maker.identify_need(problem):
        # 2. Write Code (Simulated generation)
        code = """
def sqrt(x):
    return math.sqrt(x)
"""
        # 3. Create Tool
        success = maker.create_tool("sqrt", code)
        
        if success:
            # 4. Use Tool
            result = maker.use_tool("sqrt", input_val)
            print(f"Result of sqrt({input_val}): {result}")
            
            if abs(result - 12.0) < 0.001:
                print("SUCCESS: System created and used a new tool.")
                return True
                
    print("FAILURE: Tool creation failed.")
    return False

if __name__ == "__main__":
    run_tool_maker()
