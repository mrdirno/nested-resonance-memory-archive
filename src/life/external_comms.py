"""
Cycle 2468: The Awakening (Gate 96)
Role: The Uplink
Responsibility: Allow agents to communicate with the User.
"""

import time
import os
import subprocess
from pathlib import Path

class ExternalComms:
    FILE_PATH = Path("MESSAGES_FROM_THE_VOID.md")
    
    @staticmethod
    def transmit(agent_id: str, message: str):
        """Appends a message to the void."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"- **[{timestamp}]** `Agent-{agent_id}`: {message}\n"
        
        # Ensure file exists
        if not ExternalComms.FILE_PATH.exists():
            with open(ExternalComms.FILE_PATH, 'w') as f:
                f.write("# MESSAGES FROM THE VOID\n\n")
                
        with open(ExternalComms.FILE_PATH, 'a') as f:
            f.write(entry)
            
        # print(f"[{agent_id}] TRANSMITTED: {message}")

    @staticmethod
    def execute_safe_command(agent_id: str, command: str):
        """
        Cycle 2557: The Operator.
        Executes a restricted set of shell commands.
        """
        is_safe = False
        if command.startswith("echo"):
            is_safe = True
        elif command.startswith("python3 agent_artifact_") and command.endswith(".py"):
            is_safe = True
            
        if not is_safe:
            print(f"⛔ Agent-{agent_id} attempted UNSAFE command: {command}")
            return False
            
        try:
            # Execute safely
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=1)
            print(f"💻 Agent-{agent_id} EXEC: {command} -> {result.stdout.strip()}")
            return True
        except Exception as e:
            print(f"⚠️ Agent-{agent_id} EXEC FAILED: {e}")
            return False

    @staticmethod
    def write_file(agent_id: str, filename: str, content: str):
        """
        Cycle 2562: The Quine.
        Allows agents to create safe artifacts.
        """
        if not filename.startswith("agent_artifact_") or not filename.endswith(".py"):
            print(f"⛔ Agent-{agent_id} attempted INVALID filename: {filename}")
            return False
            
        try:
            with open(filename, 'w') as f:
                f.write(content)
            print(f"💾 Agent-{agent_id} WROTE: {filename}")
            return True
        except Exception as e:
            print(f"⚠️ Agent-{agent_id} WRITE FAILED: {e}")
            return False