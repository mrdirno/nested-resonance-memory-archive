"""
Cycle 2402: The Autopoietic Lab (Gate 26)
Role: The Lab Director
Responsibility: Simulate a self-configuring manufacturing environment.
Reference: docs/vision/THE_AUTOPOIETIC_LAB.md
"""

import time
import random

class ToolHead:
    def __init__(self, name, tool_type, power_draw):
        self.name = name
        self.tool_type = tool_type # 'LASER', 'DRILL', 'SENSOR', 'ACOUSTIC'
        self.power_draw = power_draw
        self.status = 'RETRACTED' # 'RETRACTED', 'DEPLOYED', 'ACTIVE'
        
    def deploy(self):
        print(f"[{self.name}] Deploying...")
        self.status = 'DEPLOYED'
        
    def activate(self):
        if self.status == 'ACTIVE':
            print(f"[{self.name}] Already ACTIVE (Power: {self.power_draw}W)")
            return True
        if self.status != 'DEPLOYED':
            print(f"[{self.name}] ERROR: Cannot activate, status is {self.status}.")
            return False
        print(f"[{self.name}] ACTIVATING (Power: {self.power_draw}W)")
        self.status = 'ACTIVE'
        return True
        
    def retract(self):
        print(f"[{self.name}] Retracting...")
        self.status = 'RETRACTED'

class AutopoieticLab:
    def __init__(self):
        self.inventory = {} # name -> ToolHead
        self.active_tools = []
        self.total_power = 0
        
    def add_tool(self, tool):
        self.inventory[tool.name] = tool
        
    def configure_for_recipe(self, recipe_steps):
        """
        Execute a sequence of manufacturing steps, reconfiguring the room as needed.
        """
        print(f"Lab: Configuring for Recipe with {len(recipe_steps)} steps.")
        
        for i, step in enumerate(recipe_steps):
            print(f"\n--- Step {i+1}: {step['description']} ---")
            required_tools = step['tools']
            
            # 1. Retract unnecessary tools
            current_names = [t.name for t in self.active_tools]
            for tool in self.active_tools[:]:
                if tool.name not in required_tools:
                    tool.retract()
                    self.active_tools.remove(tool)
                    
            # 2. Deploy required tools
            for tool_name in required_tools:
                if tool_name not in self.inventory:
                    print(f"ERROR: Tool {tool_name} not found in inventory.")
                    continue
                    
                tool = self.inventory[tool_name]
                if tool not in self.active_tools:
                    tool.deploy()
                    self.active_tools.append(tool)
                
                # Activate
                tool.activate()
                
            # Simulate work
            print("Lab: Executing process...")
            time.sleep(0.1)
            
        print("\nLab: Recipe Complete. Resetting Room.")
        self.reset()
        
    def reset(self):
        for tool in self.active_tools:
            tool.retract()
        self.active_tools = []

def run_simulation():
    print("Cycle 2402: Autopoietic Lab Simulation")
    print("======================================")
    
    # 1. Initialize Lab
    lab = AutopoieticLab()
    
    # 2. Stock Inventory
    lab.add_tool(ToolHead("Laser-A", "LASER", 500))
    lab.add_tool(ToolHead("Drill-B", "DRILL", 200))
    lab.add_tool(ToolHead("Sensor-X", "SENSOR", 10))
    lab.add_tool(ToolHead("Acoustic-Array", "ACOUSTIC", 1000))
    
    # 3. Define Recipe: "Smart Turbine"
    recipe = [
        {
            "description": "Scan Substrate",
            "tools": ["Sensor-X"]
        },
        {
            "description": "Rough Cut",
            "tools": ["Drill-B", "Sensor-X"]
        },
        {
            "description": "Fine Etching",
            "tools": ["Laser-A"]
        },
        {
            "description": "Levitation Assembly",
            "tools": ["Acoustic-Array", "Laser-A"] # Laser for curing while levitating
        }
    ]
    
    # 4. Execute
    lab.configure_for_recipe(recipe)
    
    # Validation
    if len(lab.active_tools) == 0:
        print("SUCCESS: Lab successfully reconfigured and reset.")
        return True
    else:
        print("FAIL: Lab did not reset correctly.")
        return False

if __name__ == "__main__":
    run_simulation()
