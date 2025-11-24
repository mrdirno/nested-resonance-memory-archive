"""
Cycle 427: Theory of Mind (Recursive Modeling)
Role: The Empathic Architect
Responsibility: Model the internal state of peers to optimize social interaction.
"""
import asyncio
import random
import math
import time

# --- Mock Components (Reused/Simplified) ---

class AestheticCurator:
    def evaluate(self, shape, preference_profile):
        # Preference Profile defines what the agent likes
        # e.g., {"target_mode": "golden_spiral", "tolerance": 0.2}
        
        mode = shape['params']['mode']
        score = 0.0
        
        # 1. Mode Match
        if mode == preference_profile.get("target_mode"):
            score += 0.8
        elif mode == "random":
            score += 0.1
        else:
            score += 0.3
            
        # 2. Noise (Subjectivity)
        score += random.uniform(-0.1, 0.1)
        
        return max(0.0, min(1.0, score))

class GenerativeDesigner:
    def generate_batch(self, size=5):
        batch = []
        modes = ["random", "spherical_shell", "axis_aligned", "golden_spiral"]
        for _ in range(size):
            mode = random.choice(modes)
            batch.append({
                "id": random.randint(1000, 9999),
                "params": {"mode": mode},
                "data": "ShapeData"
            })
        return batch

# --- Theory of Mind Components ---

class MentalModel:
    def __init__(self, peer_id):
        self.peer_id = peer_id
        self.history = [] # List of (mode, score)
        self.preferences = {} # Inferred preferences (e.g., "golden_spiral": 0.8)

    def update(self, design, feedback):
        mode = design['params']['mode']
        score = feedback['score']
        self.history.append((mode, score))
        
        # Simple Average Learning
        if mode not in self.preferences:
            self.preferences[mode] = []
        self.preferences[mode].append(score)
        
        print(f"[MentalModel] Updated model for {self.peer_id}: {mode} avg = {self.predict_preference(mode):.2f}")

    def predict_preference(self, mode):
        if mode in self.preferences:
            scores = self.preferences[mode]
            return sum(scores) / len(scores)
        return 0.5 # Default uncertainty (Entropy)

class EmpathicAgent:
    def __init__(self, agent_id, preference_profile):
        self.id = agent_id
        self.profile = preference_profile
        self.designer = GenerativeDesigner()
        self.curator = AestheticCurator()
        self.mental_models = {} # peer_id -> MentalModel
        self.inbox = asyncio.Queue()

    def get_mental_model(self, peer_id):
        if peer_id not in self.mental_models:
            self.mental_models[peer_id] = MentalModel(peer_id)
        return self.mental_models[peer_id]

    async def receive(self, message):
        await self.inbox.put(message)

    async def process_inbox(self, channel):
        while not self.inbox.empty():
            msg = await self.inbox.get()
            sender = msg['from']
            content = msg['content']
            
            if content['type'] == 'DESIGN_SHARE':
                # Evaluate based on MY profile
                score = self.curator.evaluate(content['data'], self.profile)
                comment = "Love it!" if score > 0.7 else "Meh."
                
                reply = {
                    "type": "FEEDBACK",
                    "data": {"ref_id": content['data']['id'], "score": score, "comment": comment}
                }
                await channel.send(self.id, sender, reply)

            elif content['type'] == 'FEEDBACK':
                # Update Mental Model of the sender
                design_mode = content['meta']['mode'] # We cheat slightly and pass metadata back for simplicity
                self.get_mental_model(sender).update(
                    {"params": {"mode": design_mode}}, 
                    content['data']
                )

    async def invent_for(self, peer_id, channel):
        # 1. Generate Candidates
        batch = self.designer.generate_batch(size=5)
        
        # 2. Simulate Peer Reaction (Theory of Mind)
        model = self.get_mental_model(peer_id)
        scored_candidates = []
        for design in batch:
            predicted_score = model.predict_preference(design['params']['mode'])
            scored_candidates.append((design, predicted_score))
            
        # 3. Select Best
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        best_design, predicted_score = scored_candidates[0]
        
        print(f"[{self.id}] Inventing for {peer_id}. Selected {best_design['params']['mode']} (Predicted: {predicted_score:.2f})")
        
        # 4. Share
        msg = {
            "type": "DESIGN_SHARE",
            "data": best_design
        }
        # We attach metadata for the feedback loop to work easily in this mock
        msg_with_meta = {
            "type": "DESIGN_SHARE",
            "data": best_design,
        }
        
        # Hack: The channel needs to preserve metadata for the return trip, 
        # but in a real system the agent remembers what it sent.
        # For this simulation, we'll handle the memory in the 'run_experiment' loop or assume the agent tracks pending IDs.
        # To keep it simple, we'll just send it.
        
        await channel.send(self.id, peer_id, msg_with_meta)
        return best_design['params']['mode']

class CommunicationChannel:
    def __init__(self):
        self.agents = {}
        self.pending_feedback_meta = {} # msg_id -> mode (Hack for simulation tracking)

    def register(self, agent):
        self.agents[agent.id] = agent

    async def send(self, sender_id, recipient_id, content):
        if content['type'] == 'DESIGN_SHARE':
            # Store metadata for the return trip
            self.pending_feedback_meta[content['data']['id']] = content['data']['params']['mode']
            
        if content['type'] == 'FEEDBACK':
            # Attach metadata
            ref_id = content['data']['ref_id']
            if ref_id in self.pending_feedback_meta:
                content['meta'] = {"mode": self.pending_feedback_meta[ref_id]}

        print(f"[CHANNEL] {sender_id} -> {recipient_id}: {content['type']}")
        await self.agents[recipient_id].receive({"from": sender_id, "content": content})

async def main():
    print("Starting Cycle 427: Theory of Mind...")
    
    channel = CommunicationChannel()
    
    # Agent A: The Empathic Designer (No specific preference, wants to please B)
    agent_a = EmpathicAgent("AGENT_A", {"target_mode": "none"}) 
    
    # Agent B: The Strict Critic (Loves Golden Spirals)
    agent_b = EmpathicAgent("AGENT_B", {"target_mode": "golden_spiral"})
    
    channel.register(agent_a)
    channel.register(agent_b)
    
    # Simulation Loop
    history_of_choices = []
    
    for i in range(10):
        print(f"\n--- Interaction {i+1} ---")
        
        # A tries to please B
        chosen_mode = await agent_a.invent_for("AGENT_B", channel)
        history_of_choices.append(chosen_mode)
        
        # B processes and replies
        await agent_b.process_inbox(channel)
        
        # A learns
        await agent_a.process_inbox(channel)
        
        await asyncio.sleep(0.1)
        
    print("\n--- Results ---")
    print("Agent A's Design Choices over Time:")
    print(history_of_choices)
    
    spiral_count = history_of_choices.count("golden_spiral")
    print(f"Golden Spirals generated: {spiral_count}/10")
    
    if spiral_count >= 5:
        print("SUCCESS: Agent A learned Agent B's preference.")
    else:
        print("FAILURE: Agent A failed to adapt.")

if __name__ == "__main__":
    asyncio.run(main())
