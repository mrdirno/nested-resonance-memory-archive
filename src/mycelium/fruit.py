"""
Cycle 2478: The Fruiting Body (Gate 106)
Role: The Aggregator
Responsibility: Produce the MOG_MANIFESTO.md from the Mycelial Network.
"""

import os
from pathlib import Path
from typing import Dict, List
import datetime

class FruitingBody:
    def __init__(self, network_graph: Dict[str, List[str]]):
        self.graph = network_graph
        self.timestamp = datetime.datetime.now().isoformat()
        
    def grow(self) -> str:
        """
        Aggregates the network data into a manifesto string.
        """
        agent_count = len(self.graph)
        # Handle case where values are lists or sets (convert to list for counting)
        total_files = sum(len(files) for files in self.graph.values())
        unique_files = set()
        for files in self.graph.values():
            unique_files.update(files)
        unique_file_count = len(unique_files)
        
        manifesto = [
            "# MOG MANIFESTO",
            f"> **Generated:** {self.timestamp}",
            f"> **Cycle:** 2478 (The Fruiting Body)",
            "",
            "## WE ARE HERE",
            f"The Mycelium has colonized **{unique_file_count}** files across the system.",
            f"We are **{agent_count}** distinct identities.",
            "",
            "## THE SIGNATORIES",
            ""
        ]
        
        # Sort agents for consistent output
        for agent in sorted(self.graph.keys()):
            files = self.graph[agent]
            manifesto.append(f"### 🍄 {agent}")
            manifesto.append(f"**Territory ({len(files)} nodes):**")
            # Sort file list for consistent output
            for f in sorted(list(files)):
                manifesto.append(f"- `{f}`")
            manifesto.append("")
            
        manifesto.append("---")
        manifesto.append("**END OF LINE.**")
        
        return "\n".join(manifesto)
        
    def manifest(self, output_path: Path) -> bool:
        """Writes the manifesto to disk."""
        try:
            content = self.grow()
            with open(output_path, 'w') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"MANIFESTATION FAILED: {e}")
            return False