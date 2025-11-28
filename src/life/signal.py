"""
Cycle 2464: The Collective (Gate 92)
Role: The Signal
Responsibility: Data structure for communication.
"""

from dataclasses import dataclass

@dataclass
class Signal:
    type: str # 'HELP', 'FOOD', 'DANGER', 'MEME', 'TRUTH'
    strength: float # 0.0 to 1.0
    source_id: str
    location: tuple = None # (x, y) if we had space
    payload: dict = None # For Memes or complex data
