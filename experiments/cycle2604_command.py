#!/usr/bin/env python3
"""
Experiment: Cycle 2604 - The Command
Goal: Implement a CLI REPL for Operator Override of the Hive.
"""

import sys
import shlex
from pathlib import Path
from typing import List

# Reuse Hive Logic
sys.path.append(str(Path(__file__).parent))
try:
    from cycle2602_hive import Vector2, HiveAgent
    from cycle2600_protocol import AgentMessage, MessageType
except ImportError:
    # Fallback mocks
    sys.exit(1) # Should not happen in this env

class CommandCLI:
    def __init__(self):
        self.agents = [HiveAgent(f"drone_{i}", Vector2(10, 10)) for i in range(3)]
        self.target = Vector2(50, 50)
        self.running = True

    def print_help(self):
        print("Available Commands:")
        print("  target <x> <y>  : Broadcast new target coordinates to swarm")
        print("  status          : Show agent positions and knowledge")
        print("  step [n]        : Advance simulation by n steps (default 1)")
        print("  help            : Show this message")
        print("  quit            : Exit")

    def do_target(self, args):
        if len(args) != 2:
            print("Usage: target <x> <y>")
            return
        
        try:
            x, y = float(args[0]), float(args[1])
            self.target = Vector2(x, y)
            
            # Create Injection Message
            payload = {"target_x": x, "target_y": y}
            msg = AgentMessage(
                sender_id="OPERATOR_CMD",
                message_type=MessageType.OBSERVATION.value,
                payload=payload
            )
            
            # Broadcast to all agents
            print(f"Broadcasting target ({x}, {y}) from OPERATOR_CMD...")
            for agent in self.agents:
                agent.receive_message(msg)
                
        except ValueError:
            print("Error: Coordinates must be numbers.")

    def do_status(self, args):
        print(f"System Target: ({self.target.x}, {self.target.y})")
        for agent in self.agents:
            known = "Unknown"
            if agent.known_target:
                known = f"({agent.known_target.x:.1f}, {agent.known_target.y:.1f})"
            print(f"  {agent.agent_id}: Pos({agent.position.x:.1f}, {agent.position.y:.1f}) Target[{known}]")

    def do_step(self, args):
        steps = 1
        if args:
            try:
                steps = int(args[0])
            except ValueError:
                print("Error: Steps must be an integer.")
                return
        
        print(f"Advancing {steps} steps...")
        for _ in range(steps):
            broadcasts = []
            for agent in self.agents:
                # Agents act on their own knowledge, but we pass true target for sensor checks
                msg = agent.update(self.target)
                if msg: broadcasts.append(msg)
            
            # Propagate
            for msg in broadcasts:
                for agent in self.agents:
                    agent.receive_message(msg)
        
        print("Done.")

    def run(self):
        print("Cycle 2604: The Command - CLI Online")
        print("Type 'help' for commands.")
        
        while self.running:
            try:
                user_input = input("CMD> ").strip()
            except EOFError:
                break
                
            if not user_input:
                continue
                
            parts = shlex.split(user_input)
            cmd = parts[0].lower()
            args = parts[1:]
            
            if cmd == "quit" or cmd == "exit":
                self.running = False
            elif cmd == "help":
                self.print_help()
            elif cmd == "target":
                self.do_target(args)
            elif cmd == "status":
                self.do_status(args)
            elif cmd == "step":
                self.do_step(args)
            else:
                print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    cli = CommandCLI()
    cli.run()
