
import uuid
import time
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NEXUS")

class NexusMessage:
    def __init__(self, sender_id, type, payload, recipient_id="broadcast"):
        self.id = str(uuid.uuid4())
        self.sender = sender_id
        self.recipient = recipient_id
        self.timestamp = time.time()
        self.type = type
        self.payload = payload
        
    def to_json(self):
        return json.dumps(self.__dict__)
        
    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        msg = cls(data['sender'], data['type'], data['payload'], data['recipient'])
        msg.id = data['id']
        msg.timestamp = data['timestamp']
        return msg

class NexusNode:
    def __init__(self, node_id=None):
        self.node_id = node_id if node_id else str(uuid.uuid4())
        self.inbox = []
        self.outbox = []
        self.peers = set()
        logger.info(f"NexusNode initialized: {self.node_id}")
        
    def add_peer(self, peer_id):
        self.peers.add(peer_id)
        logger.info(f"Node {self.node_id} added peer: {peer_id}")
        
    def create_message(self, type, payload, recipient="broadcast"):
        msg = NexusMessage(self.node_id, type, payload, recipient)
        self.outbox.append(msg)
        return msg
        
    def receive_message(self, json_msg):
        try:
            msg = NexusMessage.from_json(json_msg)
            if msg.recipient == "broadcast" or msg.recipient == self.node_id:
                self.inbox.append(msg)
                logger.info(f"Node {self.node_id} received message {msg.id} from {msg.sender}")
                return True
            else:
                logger.debug(f"Node {self.node_id} ignored message for {msg.recipient}")
                return False
        except Exception as e:
            logger.error(f"Failed to parse message: {e}")
            return False
            
    def process_inbox(self):
        """
        Process all messages in inbox. In a real system, this would dispatch to handlers.
        """
        processed_count = 0
        while self.inbox:
            msg = self.inbox.pop(0)
            # Placeholder for message handling logic
            # e.g., if msg.type == 'state_update': self.merge_state(msg.payload)
            processed_count += 1
        return processed_count

if __name__ == "__main__":
    # Basic Test
    node1 = NexusNode()
    node2 = NexusNode()
    
    node1.add_peer(node2.node_id)
    node2.add_peer(node1.node_id)
    
    msg = node1.create_message("ping", {"content": "Hello World"})
    print(f"Node 1 created message: {msg.to_json()}")
    
    # Simulate network transmission
    node2.receive_message(msg.to_json())
    
    count = node2.process_inbox()
    print(f"Node 2 processed {count} messages.")
