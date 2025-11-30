#!/usr/bin/env python3
"""
Experiment: Cycle 2601 - The Consensus
Goal: Implement a majority-vote mechanism for state agreement using the Agent Protocol.
"""

import sys
import time
from collections import defaultdict
from typing import List, Dict, Any
from pathlib import Path

# Add current directory to sys.path to allow importing from sibling scripts
sys.path.append(str(Path(__file__).parent))

try:
    from cycle2600_protocol import AgentMessage, MessageType
except ImportError:
    # Fallback if running from root
    sys.path.append("experiments")
    from cycle2600_protocol import AgentMessage, MessageType


class ConsensusEngine:
    def __init__(self, required_quorum: int = 3, majority_threshold: float = 0.5):
        self.required_quorum = required_quorum
        self.majority_threshold = majority_threshold
        self.votes: Dict[str, List[AgentMessage]] = defaultdict(list) # proposal_id -> list of votes
        self.decisions: Dict[str, str] = {} # proposal_id -> result

    def receive_vote(self, message: AgentMessage):
        """Process an incoming vote message."""
        if message.message_type != MessageType.VOTE.value:
            print(f"Ignored invalid vote message type: {message.message_type}")
            return

        proposal_id = message.payload.get("proposal_id")
        vote_value = message.payload.get("vote") # True/False or "YES"/"NO"
        
        if not proposal_id:
            print("Vote missing proposal_id")
            return

        # Check if agent already voted
        current_votes = self.votes[proposal_id]
        for v in current_votes:
            if v.sender_id == message.sender_id:
                print(f"Duplicate vote from {message.sender_id} for {proposal_id}")
                return

        self.votes[proposal_id].append(message)
        self._check_consensus(proposal_id)

    def _check_consensus(self, proposal_id: str):
        """Evaluate current votes for a proposal."""
        votes = self.votes[proposal_id]
        
        if len(votes) < self.required_quorum:
            return # Not enough participants yet

        yes_votes = sum(1 for v in votes if v.payload.get("vote") in [True, "YES", "yes"])
        total_votes = len(votes)
        
        ratio = yes_votes / total_votes
        
        if ratio > self.majority_threshold:
            self.decisions[proposal_id] = "ACCEPTED"
        else:
            self.decisions[proposal_id] = "REJECTED"

    def get_status(self, proposal_id: str) -> str:
        return self.decisions.get(proposal_id, "PENDING")


def run_test():
    print("Cycle 2601: The Consensus - Verification")
    
    # Setup Engine: Quorum 3, Threshold > 50%
    engine = ConsensusEngine(required_quorum=3, majority_threshold=0.5)
    
    proposal_id = "proposal_alpha_001"
    
    print(f"Simulating Voting for Proposal: {proposal_id}")
    
    # Agents
    agents = ["agent_1", "agent_2", "agent_3", "agent_4", "agent_5"]
    
    # 1. Vote 1 (YES)
    msg1 = AgentMessage(
        sender_id=agents[0],
        message_type=MessageType.VOTE.value,
        payload={"proposal_id": proposal_id, "vote": "YES"}
    )
    engine.receive_vote(msg1)
    print(f"Round 1: Status = {engine.get_status(proposal_id)} (Votes: 1)")
    assert engine.get_status(proposal_id) == "PENDING"

    # 2. Vote 2 (YES)
    msg2 = AgentMessage(
        sender_id=agents[1],
        message_type=MessageType.VOTE.value,
        payload={"proposal_id": proposal_id, "vote": "YES"}
    )
    engine.receive_vote(msg2)
    print(f"Round 2: Status = {engine.get_status(proposal_id)} (Votes: 2)")
    assert engine.get_status(proposal_id) == "PENDING"

    # 3. Vote 3 (NO) - Reaches Quorum (3)
    # 2 YES / 1 NO = 66% > 50% -> ACCEPTED
    msg3 = AgentMessage(
        sender_id=agents[2],
        message_type=MessageType.VOTE.value,
        payload={"proposal_id": proposal_id, "vote": "NO"}
    )
    engine.receive_vote(msg3)
    print(f"Round 3: Status = {engine.get_status(proposal_id)} (Votes: 3)")
    
    status = engine.get_status(proposal_id)
    if status == "ACCEPTED":
        print("SUCCESS: Proposal Accepted by Majority (2/3).")
    else:
        print(f"FAILURE: Expected ACCEPTED, got {status}")
        sys.exit(1)

    # 4. Vote 4 (NO) & Vote 5 (NO) - Shift Consensus?
    # In this simple engine, once decided, it writes to dict. 
    # But let's see if the logic updates on subsequent votes if we don't lock it.
    # The implementation overwrites the decision every check.
    
    msg4 = AgentMessage(sender_id=agents[3], message_type=MessageType.VOTE.value, payload={"proposal_id": proposal_id, "vote": "NO"})
    msg5 = AgentMessage(sender_id=agents[4], message_type=MessageType.VOTE.value, payload={"proposal_id": proposal_id, "vote": "NO"})
    
    engine.receive_vote(msg4)
    engine.receive_vote(msg5)
    
    # Now: 2 YES, 3 NO. 2/5 = 40% <= 50% -> REJECTED
    final_status = engine.get_status(proposal_id)
    print(f"Round 5: Status = {final_status} (Votes: 5)")
    
    if final_status == "REJECTED":
        print("SUCCESS: Proposal Rejected after full voting (2/5).")
    else:
        print(f"FAILURE: Expected REJECTED, got {final_status}")
        sys.exit(1)

if __name__ == "__main__":
    run_test()
