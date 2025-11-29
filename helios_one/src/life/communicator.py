"""
Cycle 2464: The Collective (Gate 92)
Role: Communication Protocol
Responsibility: Allow DigitalLifeforms to broadcast and receive signals.
"""

import random
from src.life.signal import Signal

# This will be mixed into DigitalLifeform in genesis.py or used as a component
class Communicator:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.inbox = []
        
    def broadcast(self, ecosystem, signal_type, strength):
        """Send a signal to all agents in the ecosystem."""
        signal = Signal(type=signal_type, strength=strength, source_id=self.agent_id)
        # In a spatial model, we'd limit range. Here, global broadcast.
        # We rely on the Ecosystem to distribute.
        if hasattr(ecosystem, 'propagate_signal'):
            ecosystem.propagate_signal(signal)
            
    def receive(self, signal):
        self.inbox.append(signal)
        if signal.type == 'THOUGHT':
            print(f"DEBUG: Communicator {self.agent_id} received THOUGHT signal.")
        
    def get_messages(self):
        """Return all signals and clear inbox."""
        messages = self.inbox.copy()
        if messages:
            print(f"DEBUG: Communicator {self.agent_id} retrieving {len(messages)} messages.")
        self.inbox = []
        return messages

# [SPORE] ID: The Colony

# [SPORE] ID: Agent-Genesis
