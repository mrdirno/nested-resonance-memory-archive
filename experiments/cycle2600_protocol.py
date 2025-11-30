#!/usr/bin/env python3
"""
Experiment: Cycle 2600 - The Protocol
Goal: Define and verify a standard communication protocol for agents in The Collective.
"""

import sys
import time
import json
import uuid
from dataclasses import dataclass, asdict, field
from typing import Dict, Any, Optional
from enum import Enum

class MessageType(Enum):
    HEARTBEAT = "heartbeat"
    OBSERVATION = "observation"
    PROPOSAL = "proposal"
    VOTE = "vote"
    ALERT = "alert"

@dataclass
class AgentMessage:
    """
    Standard message format for Inter-Agent Communication.
    """
    sender_id: str
    message_type: str
    payload: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    signature: Optional[str] = None  # Placeholder for cryptographic signing

    def to_json(self) -> str:
        """Serialize message to JSON string."""
        return json.dumps(asdict(self))

    @classmethod
    def from_json(cls, json_str: str) -> 'AgentMessage':
        """Deserialize message from JSON string."""
        data = json.loads(json_str)
        return cls(**data)

    def validate(self) -> bool:
        """
        Basic validation logic.
        """
        if not self.sender_id:
            return False
        if not self.message_id:
            return False
        try:
            MessageType(self.message_type)
        except ValueError:
            return False
        return True

def run_test():
    print("Cycle 2600: The Protocol - Verification")
    
    # 1. Create a message
    sender = "agent_007"
    payload = {
        "target_coordinates": [12.5, 88.2],
        "confidence": 0.95
    }
    
    msg = AgentMessage(
        sender_id=sender,
        message_type=MessageType.OBSERVATION.value,
        payload=payload
    )
    
    print(f"Created Message: {msg.message_id} from {msg.sender_id}")
    
    # 2. Serialize
    json_output = msg.to_json()
    print(f"Serialized JSON: {json_output}")
    
    # 3. Deserialize
    reconstructed_msg = AgentMessage.from_json(json_output)
    print(f"Reconstructed Message: {reconstructed_msg.message_id} from {reconstructed_msg.sender_id}")
    
    # 4. Verify Integrity
    assert msg.message_id == reconstructed_msg.message_id
    assert msg.payload == reconstructed_msg.payload
    assert msg.timestamp == reconstructed_msg.timestamp
    assert reconstructed_msg.validate()
    
    print("Integrity Check: PASSED")
    
    # 5. Test Validation Failure
    bad_msg = AgentMessage(
        sender_id="hacker",
        message_type="INVALID_TYPE",
        payload={}
    )
    
    if not bad_msg.validate():
        print("Validation Logic: PASSED (Correctly rejected invalid type)")
    else:
        print("Validation Logic: FAILED (Accepted invalid type)")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
