"""
Cycle 2476: The Spore (Gate 104)
Role: The Colonizer
Responsibility: Attach to files and persist state.
"""

import os
from pathlib import Path

class Spore:
    SIGNATURE = "# [SPORE] ID:"
    
    def __init__(self, agent_id):
        self.agent_id = agent_id
        
    def infect(self, file_path: Path) -> bool:
        """
        Attaches the agent ID to the file as a metadata comment.
        Returns True if successful or already infected.
        """
        if not file_path.exists() or not file_path.is_file():
            return False
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            if self.SIGNATURE in content:
                # Already infected, check ID?
                # For now, multiple infections allowed
                pass
                
            # Append spore signature
            with open(file_path, 'a') as f:
                f.write(f"\n{self.SIGNATURE} {self.agent_id}\n")
                
            return True
        except Exception as e:
            print(f"INFECTION FAILED: {e}")
            return False

    @staticmethod
    def check_infection(file_path: Path) -> bool:
        """Returns True if file is infected by ANY spore."""
        if not file_path.exists(): return False
        try:
            with open(file_path, 'r') as f:
                return Spore.SIGNATURE in f.read()
        except:
            return False
# [SPORE] ID: The Colony
