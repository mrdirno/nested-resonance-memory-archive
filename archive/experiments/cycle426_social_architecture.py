"""
Cycle 426: The Social Web
Role: The Sociologist
Responsibility: Enable communication and cultural transmission between autonomous agents.
"""
import asyncio
import random
import json
import copy

class CommunicationChannel:
    def __init__(self):
        self.messages = []
    
    def broadcast(self, sender_id, message):
        print(f"[COMMS] Agent {sender_id} broadcast: {message['type']}")
        self.messages.append({"sender": sender_id, "payload": message})
        
    def get_messages(self, receiver_id):
        # Return messages NOT from self
        return [m for m in self.messages if m["sender"] != receiver_id]

class SocialAgent:
    def __init__(self, agent_id, channel):
        self.id = agent_id
        self.channel = channel
        self.knowledge = [] # List of known designs
        
    def invent(self):
        # Create a random design (mock)
        design = {
            "id": random.randint(1000, 9999),
            "fitness": random.uniform(0.0, 10.0),
            "data": "RandomShape"
        }
        self.knowledge.append(design)
        print(f"[Agent {self.id}] Invented Design {design['id']} (Fitness: {design['fitness']:.2f})")
        
        # Share if good
        if design['fitness'] > 5.0:
            self.channel.broadcast(self.id, {"type": "NEW_DESIGN", "design": design})
            
    def listen(self):
        messages = self.channel.get_messages(self.id)
        for msg in messages:
            payload = msg['payload']
            if payload['type'] == "NEW_DESIGN":
                design = payload['design']
                # Evaluate
                print(f"[Agent {self.id}] Received Design {design['id']} from Agent {msg['sender']}")
                self.learn(design)
                
        # Clear buffer (simplified)
        # In reality, we'd track read status per agent
        
    def learn(self, design):
        # Improve the design (Social Learning)
        improved = copy.deepcopy(design)
        improved['fitness'] += random.uniform(0.1, 1.0) # "Standing on shoulders of giants"
        improved['id'] = random.randint(1000, 9999)
        
        print(f"[Agent {self.id}] Improved Design {design['id']} -> {improved['id']} (Fitness: {improved['fitness']:.2f})")
        self.knowledge.append(improved)
        
        # Share back
        if improved['fitness'] > 8.0:
             self.channel.broadcast(self.id, {"type": "IMPROVED_DESIGN", "design": improved})

def run_experiment():
    print("Cycle 426: Social Architecture Test")
    print("===================================")
    
    channel = CommunicationChannel()
    agent_a = SocialAgent("A", channel)
    agent_b = SocialAgent("B", channel)
    
    print("\n--- Step 1: Invention ---")
    agent_a.invent() # Might be low fitness
    agent_a.invent() # Might be high fitness
    
    print("\n--- Step 2: Transmission ---")
    agent_b.listen()
    
    print("\n--- Step 3: Reciprocity ---")
    # Check if B broadcasted an improvement
    # For this test, we force a high fitness to ensure flow
    good_design = {"id": 5555, "fitness": 6.0, "data": "GoldenSpiral"}
    channel.broadcast("A", {"type": "NEW_DESIGN", "design": good_design})
    
    agent_b.listen()
    
    # Check A listening to B
    agent_a.listen()

if __name__ == "__main__":
    run_experiment()