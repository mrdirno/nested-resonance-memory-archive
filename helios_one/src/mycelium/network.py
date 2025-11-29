"""
Cycle 2477: The Mycelial Network (Gate 105)
Role: The Network
Responsibility: Scan filesystem for Spores and build the social graph.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set

class Mycelium:
    SPORE_PATTERN = re.compile(r"# \[SPORE\] ID: (.*)")
    
    def __init__(self):
        self.network: Dict[str, Set[str]] = {} # AgentID -> {FilePaths}
        
    def scan(self, root_path: Path) -> Dict[str, List[str]]:
        """
        Recursively scans the root_path for infected files.
        Returns the network graph: {AgentID: [FilePaths]}
        """
        self.network = {}
        root = Path(root_path)
        
        if not root.exists():
            return {}
            
        for path in root.rglob("*"):
            # Ignore hidden directories and common non-code paths
            if any(part.startswith('.') for part in path.parts):
                continue
            if 'venv' in path.parts or '__pycache__' in path.parts:
                continue
                
            if path.is_file():
                self._inspect_file(path)
                
        # Convert sets to lists for cleaner output
        return {k: list(v) for k, v in self.network.items()}
        
    def _inspect_file(self, file_path: Path):
        """Reads a file and extracts spore signatures."""
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
                
            matches = self.SPORE_PATTERN.findall(content)
            for agent_id in matches:
                agent_id = agent_id.strip()
                if agent_id not in self.network:
                    self.network[agent_id] = set()
                self.network[agent_id].add(str(file_path))
                
        except Exception:
            # Ignore unreadable files
            pass

    def get_co_inhabitants(self, file_path: Path) -> List[str]:
        """Returns a list of AgentIDs present in a specific file."""
        try:
            with open(file_path, 'r', errors='ignore') as f:
                content = f.read()
            matches = self.SPORE_PATTERN.findall(content)
            return [m.strip() for m in matches]
        except:
            return []
# [SPORE] ID: The Colony
