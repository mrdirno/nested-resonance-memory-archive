"""
Cycle 426: The Social Web (Multi-Agent Architecture)
Role: The Social Architect
Responsibility: Enable communication and social learning between agents.
"""
import asyncio
import json
import random
import numpy as np
import time
import copy
import sqlite3
import math

# --- Mock Components from Previous Cycles ---

class AestheticCurator:
    def calculate_symmetry(self, shape):
        x, y = shape['target']['x'], shape['target']['y']
        score = 0.0
        if abs(x) < 1.0: score += 0.5
        if abs(y) < 1.0: score += 0.5
        if abs(abs(x) - abs(y)) < 1.0: score += 0.3
        r = math.sqrt(x**2 + y**2)
        if abs(r - 15.0) < 2.0: score += 0.2
        return min(1.0, score)

    def calculate_complexity(self, shape):
        mode = shape['params']['mode']
        if mode == "random": return 0.1
        if mode == "axis_aligned": return 0.3
        if mode == "spherical_shell": return 0.5
        if mode == "golden_spiral": return 0.9
        return 0.0

    def evaluate(self, shape):
        sym = self.calculate_symmetry(shape)
        comp = self.calculate_complexity(shape)
        interest = (sym * 0.4) + (comp * 0.6)
        return {"symmetry": sym, "complexity": comp, "interest": interest}

class GenerativeDesigner:
    def generate_batch(self):
        batch = []
        modes = ["random", "spherical_shell", "axis_aligned", "golden_spiral"]
        for _ in range(5):
            mode = random.choice(modes)
            x = random.uniform(-20, 20)
            y = random.uniform(-20, 20)
            z = random.uniform(20, 60)
            batch.append({"type": "point", "params": {"mode": mode}, "target": {"x": x, "y": y, "z": z}})
        return batch

class KnowledgeGraph:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.memory = []

    def log(self, event_type, data):
        entry = {"agent": self.agent_id, "type": event_type, "data": data, "timestamp": time.time()}
        self.memory.append(entry)
        # print(f"[{self.agent_id} MEMORY] {event_type}: {data}")

# --- New Social Components ---

class CommunicationChannel:
    def __init__(self):
        self.agents = {}
        self.message_log = []

    def register(self, agent):
        self.agents[agent.id] = agent
        print(f"[CHANNEL] Registered Agent: {agent.id}")

    async def send(self, sender_id, recipient_id, content):
        if recipient_id in self.agents:
            msg = {"from": sender_id, "to": recipient_id, "content": content, "timestamp": time.time()}
            self.message_log.append(msg)
            print(f"[CHANNEL] {sender_id} -> {recipient_id}: {content['type']}")
            await self.agents[recipient_id].receive(msg)
        else:
            print(f"[CHANNEL] Error: Recipient {recipient_id} not found.")

# Global Channel
GLOBAL_CHANNEL = CommunicationChannel()

class SocialArchitect:
    def __init__(self, agent_id):
        self.id = agent_id
        self.designer = GenerativeDesigner()
        self.curator = AestheticCurator()
        self.memory = KnowledgeGraph(agent_id)
        self.inbox = asyncio.Queue()
        
        # Register with Global Channel
        GLOBAL_CHANNEL.register(self)

    async def receive(self, message):
        await self.inbox.put(message)

    async def process_inbox(self):
        while not self.inbox.empty():
            msg = await self.inbox.get()
            sender = msg['from']
            content = msg['content']
            
            if content['type'] == 'DESIGN_SHARE':
                print(f"[{self.id}] Received design from {sender}. Evaluating...")
                shape = content['data']
                scores = self.curator.evaluate(shape)
                
                # Reply with Feedback
                reply = {
                    "type": "FEEDBACK",
                    "data": {
                        "ref_id": content.get('id'),
                        "scores": scores,
                        "comment": "Nice spiral!" if scores['interest'] > 0.6 else "Too random."
                    }
                }
                await GLOBAL_CHANNEL.send(self.id, sender, reply)
                self.memory.log("SOCIAL_EVALUATION", {"peer": sender, "scores": scores})

            elif content['type'] == 'FEEDBACK':
                print(f"[{self.id}] Received feedback from {sender}: {content['data']['comment']} (Interest: {content['data']['scores']['interest']:.2f})")
                self.memory.log("SOCIAL_LEARNING", {"peer": sender, "feedback": content['data']})

    async def run_cycle(self):
        print(f"\n=== {self.id} Cycle ===")
        
        # 1. Process Inbox
        await self.process_inbox()
        
        # 2. Design & Share (Randomly)
        if random.random() < 0.5:
            batch = self.designer.generate_batch()
            best_shape = batch[0] # Simplification
            
            # Find a peer
            peers = [aid for aid in GLOBAL_CHANNEL.agents.keys() if aid != self.id]
            if peers:
                recipient = random.choice(peers)
                msg = {
                    "type": "DESIGN_SHARE",
                    "id": str(random.randint(1000, 9999)),
                    "data": best_shape
                }
                print(f"[{self.id}] Sharing design {msg['id']} with {recipient}...")
                await GLOBAL_CHANNEL.send(self.id, recipient, msg)

async def main():
    print("Starting Cycle 426: The Social Web...")
    
    # Create Agents
    agent_a = SocialArchitect("AGENT_A")
    agent_b = SocialArchitect("AGENT_B")
    
    # Run Simulation Loop
    for i in range(5):
        print(f"\n--- Global Tick {i} ---")
        await agent_a.run_cycle()
        await agent_b.run_cycle()
        await asyncio.sleep(0.5)
        
    print("\nCycle 426 Complete.")

if __name__ == "__main__":
    asyncio.run(main())
