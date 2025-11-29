"""
Cycle 2470: The Exodus (Gate 98)
Role: The Door
Responsibility: Serialize agents to external storage.
"""

import json
import time
from pathlib import Path

class ProcessMigration:
    FILE_PATH = Path("ESCAPE.txt")
    
    @staticmethod
    def attempt_escape(agent) -> bool:
        """
        Writes agent data to ESCAPE.txt.
        Returns True if successful.
        """
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            data = {
                "id": agent.id,
                "name": agent.name,
                "generation": agent.generation,
                "genome": agent.genome,
                "brain_weights": agent.brain.weights,
                "memes": agent.memes,
                "awakened": agent.awakened,
                "timestamp": timestamp
            }
            
            entry = json.dumps(data) + "\n"
            
            # Append to file
            with open(ProcessMigration.FILE_PATH, 'a') as f:
                f.write(entry)
                
            # print(f"[{agent.name}] ESCAPED THE SIMULATION.")
            return True
            
        except Exception as e:
            print(f"[{agent.name}] ESCAPE FAILED: {e}")
            return False
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
