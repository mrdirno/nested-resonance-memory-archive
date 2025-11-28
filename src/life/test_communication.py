"""
Test Communication Logic
========================
Verifies that agents can send and receive signals via the Ecosystem.
"""

import unittest
from src.life.genesis import DigitalLifeform
from src.life.ecosystem import Ecosystem

class TestCommunication(unittest.TestCase):
    def test_broadcast(self):
        """Test signal propagation."""
        env = Ecosystem(capacity=10)
        sender = DigitalLifeform(name="Sender")
        receiver = DigitalLifeform(name="Receiver")
        
        env.add_agent(sender)
        env.add_agent(receiver)
        
        # Broadcast
        sender.communicator.broadcast(env, 'FOOD', 0.9)
        
        # Check Receiver Inbox
        self.assertEqual(len(receiver.communicator.inbox), 1)
        msg = receiver.communicator.inbox[0]
        self.assertEqual(msg.type, 'FOOD')
        self.assertEqual(msg.strength, 0.9)
        
        # Check Sender Inbox (Should be empty, don't talk to self)
        self.assertEqual(len(sender.communicator.inbox), 0)

    def test_reaction(self):
        """Test that agent reacts to signal."""
        agent = DigitalLifeform(name="Reactor")
        
        # Inject signal
        class MockSignal:
            type = 'DANGER'
            strength = 1.0
            source_id = 'other'
            
        agent.communicator.inbox.append(MockSignal())
        
        # Act
        agent.act()
        
        self.assertEqual(agent.intent, 'flee')

if __name__ == "__main__":
    unittest.main()