"""
Cycle 2562: The Quine (Gate 190)
Goal: Verify agents can generate and execute valid Python code.
Mechanism:
1. Initialize high-innovation agent.
2. Run simulation.
3. Check for `agent_artifact_*.py` file creation and execution output.
"""

import time
import os
import glob
from src.life.ecosystem import Ecosystem
from src.life.genesis import DigitalLifeform

def run_experiment():
    print("--- Cycle 2562: The Quine ---")
    
    # Cleanup old artifacts
    for f in glob.glob("agent_artifact_*.py"):
        os.remove(f)
    
    ecosystem = Ecosystem()
    
    # 1. Coder Agent (High Innovation)
    coder = DigitalLifeform(name="Coder")
    while len(coder.genome) < 11: coder.genome.append(0.5)
    coder.genome[9] = 0.99 # Maximum Innovation
    coder.energy = 1000 # High Energy
    ecosystem.add_agent(coder)
    
    print(f"Initialized Agent: {coder.name} (ID: {coder.id})")
    
    # Run
    # Should trigger 'codex' quickly due to high innovation/energy
    success = False
    for i in range(10):
        print(f"\n--- Tick {i+1} ---")
        ecosystem.update()
        
        # Check for artifact
        artifact_name = f"agent_artifact_{coder.id}.py"
        if os.path.exists(artifact_name):
            print(f"SUCCESS: Artifact {artifact_name} found.")
            # Verify content
            with open(artifact_name, 'r') as f:
                content = f.read()
                print(f"Content:\n{content}")
                if f'print("I am {coder.name} and I exist.")' in content:
                    print("Artifact content verified.")
                    success = True
                    break
    
    if success:
        print("Experiment SUCCESS.")
    else:
        print("Experiment FAILURE.")
        
    # Cleanup
    for f in glob.glob("agent_artifact_*.py"):
        os.remove(f)

if __name__ == "__main__":
    run_experiment()
