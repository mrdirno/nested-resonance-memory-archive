"""
Cycle 2395: The Social Web (Phase 16 Resumption)
Role: The Sociologist
Responsibility: Verify communication and cultural transmission between autonomous agents.
"""
import random
import copy
import sys

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
        learned_count = 0
        for msg in messages:
            payload = msg['payload']
            if payload['type'] == "NEW_DESIGN" or payload['type'] == "IMPROVED_DESIGN":
                design = payload['design']
                # Evaluate
                print(f"[Agent {self.id}] Received Design {design['id']} from Agent {msg['sender']}")
                self.learn(design)
                learned_count += 1
        return learned_count
                
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
    print("Cycle 2395: Social Architecture Resumption")
    print("==========================================")
    
    channel = CommunicationChannel()
    agent_a = SocialAgent("A", channel)
    agent_b = SocialAgent("B", channel)
    
    print("\n--- Step 1: Invention ---")
    # Force a good invention for deterministic testing
    good_design = {"id": 1234, "fitness": 9.0, "data": "SeedShape"}
    agent_a.knowledge.append(good_design)
    channel.broadcast("A", {"type": "NEW_DESIGN", "design": good_design})
    
    print("\n--- Step 2: Transmission & Learning ---")
    learned_b = agent_b.listen()
    
    if learned_b > 0:
        print("PASS: Agent B learned from A.")
    else:
        print("FAIL: Agent B did not learn.")
        sys.exit(1)
        
    print("\n--- Step 3: Reciprocity ---")
    # B should have broadcasted an improvement if fitness > 8.0 (which it is, since 9.0 + boost > 8.0)
    learned_a = agent_a.listen()
    
    if learned_a > 0:
        print("PASS: Agent A received improvement from B.")
    else:
        # This might fail if random improvement didn't happen or threshold wasn't met
        # But given base 9.0, it should pass.
        print("FAIL: Agent A did not receive improvement.")
        sys.exit(1)

    print("\nSUCCESS: Social Web Operational.")

if __name__ == "__main__":
    run_experiment()