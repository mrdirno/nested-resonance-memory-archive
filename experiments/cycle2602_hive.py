#!/usr/bin/env python3
"""
Experiment: Cycle 2602 - The Hive
Goal: Demonstrate swarm intelligence where agents converge on a target using inter-agent communication.
"""

import sys
import math
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple
from pathlib import Path

# Add current directory to sys.path
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2600_protocol import AgentMessage, MessageType
except ImportError:
    sys.path.append("experiments")
    from cycle2600_protocol import AgentMessage, MessageType

@dataclass
class Vector2:
    x: float
    y: float

    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)

    def normalize(self):
        mag = math.sqrt(self.x**2 + self.y**2)
        if mag == 0: return Vector2(0, 0)
        return Vector2(self.x / mag, self.y / mag)

    def scale(self, factor):
        return Vector2(self.x * factor, self.y * factor)

class HiveAgent:
    def __init__(self, agent_id: str, start_pos: Vector2):
        self.agent_id = agent_id
        self.position = start_pos
        self.velocity = Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.known_target: Optional[Vector2] = None
        self.speed = 4.0  # Increased speed
        self.sensor_range = 20.0 # Increased sensor range
        self.comm_range = 200.0 

    def update(self, target_pos: Vector2) -> Optional[AgentMessage]:
        """
        Update agent state.
        Returns a message if the agent wants to broadcast something.
        """
        # 1. Check sensors
        dist_to_target = math.sqrt((self.position.x - target_pos.x)**2 + 
                                   (self.position.y - target_pos.y)**2)
        
        msg_out = None
        
        if dist_to_target < self.sensor_range:
            # Found target!
            if not self.known_target:
                self.known_target = target_pos
                print(f"[{self.agent_id}] FOUND TARGET at {target_pos}")
                # Broadcast discovery
                payload = {"target_x": target_pos.x, "target_y": target_pos.y}
                msg_out = AgentMessage(
                    sender_id=self.agent_id,
                    message_type=MessageType.OBSERVATION.value,
                    payload=payload
                )

        # 2. Movement Logic
        if self.known_target:
            # Move towards target
            direction = (self.known_target - self.position).normalize()
            self.velocity = direction
        else:
            # Random walk / Explore (add some jitter)
            jitter = Vector2(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            self.velocity = (self.velocity + jitter).normalize()

        # 3. Apply Movement
        self.position = self.position + self.velocity.scale(self.speed)
        
        return msg_out

    def receive_message(self, msg: AgentMessage):
        """Process incoming messages."""
        if msg.sender_id == self.agent_id:
            return
            
        if msg.message_type == MessageType.OBSERVATION.value:
            tx = msg.payload.get("target_x")
            ty = msg.payload.get("target_y")
            if tx is not None and ty is not None:
                if not self.known_target:
                    print(f"[{self.agent_id}] Received coordinates from {msg.sender_id}")
                    self.known_target = Vector2(tx, ty)

def run_simulation():
    print("Cycle 2602: The Hive - Simulation Start")
    
    target = Vector2(80.0, 80.0)
    print(f"Target Location: ({target.x}, {target.y})")
    
    # Initialize Agents
    agents = []
    for i in range(5):
        # Start them a bit closer to ensure they don't run off map before finding it
        pos = Vector2(random.uniform(20, 40), random.uniform(20, 40))
        agents.append(HiveAgent(f"drone_{i}", pos))

    # Scout closer
    agents[0].position = Vector2(65, 65) 
    print(f"Drone_0 deployed forward at ({agents[0].position.x}, {agents[0].position.y})")

    max_steps = 80 # Increased steps
    converged = False
    
    for step in range(max_steps):
        broadcasts = []
        
        # Update all agents
        for agent in agents:
            msg = agent.update(target)
            if msg:
                broadcasts.append(msg)
        
        # Propagate messages
        for msg in broadcasts:
            for agent in agents:
                agent.receive_message(msg)
        
        # Check convergence
        near_target = 0
        for agent in agents:
            dist = math.sqrt((agent.position.x - target.x)**2 + (agent.position.y - target.y)**2)
            if dist < 25.0:
                near_target += 1
        
        # Visualization (minimal)
        if step % 10 == 0:
            print(f"Step {step}: {near_target}/5 agents near target.")
        
        if near_target == 5:
            converged = True
            print(f"\nSUCCESS: All agents converged on target at Step {step}.")
            break
        
        time.sleep(0.02)

    if not converged:
        print(f"\nFAILURE: Did not converge within {max_steps} steps.")
        for a in agents:
            print(f"{a.agent_id}: ({a.position.x:.1f}, {a.position.y:.1f})")
        sys.exit(1)

if __name__ == "__main__":
    run_simulation()