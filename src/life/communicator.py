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
        
    def process_signals(self):
        """Return processed signals and clear inbox."""
        # Simple logic: Return highest strength signal
        if not self.inbox:
            return None
            
        # Sort by strength
        self.inbox.sort(key=lambda x: x.strength, reverse=True)
        top_signal = self.inbox[0]
        self.inbox = []
        return top_signal
