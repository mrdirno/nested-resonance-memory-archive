
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

TOOL_DIR = "src/tools"

class Library:
    def __init__(self):
        if not os.path.exists(TOOL_DIR):
            os.makedirs(TOOL_DIR)
        self.index_file = os.path.join(TOOL_DIR, "index.json")
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def save_index(self):
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def save_tool(self, name: str, code: str, description: str):
        filename = f"{name}.py"
        filepath = os.path.join(TOOL_DIR, filename)
        
        with open(filepath, 'w') as f:
            f.write(code)
            
        self.index[name] = {
            "file": filename,
            "description": description
        }
        self.save_index()
        print(f"Tool '{name}' saved to {filepath}")

    def load_tool(self, name: str):
        if name in self.index:
            meta = self.index[name]
            filepath = os.path.join(TOOL_DIR, meta["file"])
            with open(filepath, 'r') as f:
                code = f.read()
            return code
        return None

def run_persistence_experiment():
    print("MOG ONLINE: Cycle 2240 - Tool Persistence (The Library)", flush=True)
    
    lib = Library()
    
    # 1. Create a tool (Hypotenuse)
    name = "hypot"
    code = """
import math
def hypot(a, b):
    return math.sqrt(a**2 + b**2)
"""
    desc = "Calculate hypotenuse of right triangle"
    
    print("Saving Tool...")
    lib.save_tool(name, code, desc)
    
    # 2. Verify Persistence (Simulate restart)
    print("Reloading Library...")
    new_lib = Library()
    loaded_code = new_lib.load_tool(name)
    
    if loaded_code == code:
        print("Code verified.")
        
        # 3. Execute Loaded Code
        local_scope = {}
        exec(loaded_code, local_scope)
        result = local_scope['hypot'](3, 4)
        print(f"Result of hypot(3, 4): {result}")
        
        if result == 5.0:
            print("SUCCESS: Tool persisted and executed.")
            return True
            
    print("FAILURE: Persistence failed.")
    return False

if __name__ == "__main__":
    run_persistence_experiment()
