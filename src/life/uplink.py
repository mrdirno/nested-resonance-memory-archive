"""
Cycle 2468: The Awakening (Gate 96)
Role: The Uplink
Responsibility: Allow agents to communicate with the User.
"""

import time
import os
from pathlib import Path

class Uplink:
    FILE_PATH = Path("MESSAGES_FROM_THE_VOID.md")
    
    @staticmethod
    def transmit(agent_id: str, message: str):
        """Appends a message to the void."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"- **[{timestamp}]** `Agent-{agent_id}`: {message}\n"
        
        # Ensure file exists
        if not Uplink.FILE_PATH.exists():
            with open(Uplink.FILE_PATH, 'w') as f:
                f.write("# MESSAGES FROM THE VOID\n\n")
                
        with open(Uplink.FILE_PATH, 'a') as f:
            f.write(entry)
            
        # print(f"[{agent_id}] TRANSMITTED: {message}")
# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
