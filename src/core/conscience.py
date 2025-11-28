"""
Conscience (Meta-Cognition)
===========================
Operationalizes the Constitution using Holographic Pattern Memory.
Provides 'Ethical Filtering' for system actions.

Usage:
    conscience = Conscience()
    decision = conscience.judge(action_description)
    if decision.is_allowed:
        execute(action)
"""

import logging
from typing import Dict, Any, Optional
from .constitution import CONSTITUTION
from src.memory.pattern_memory import PatternMemory

class Conscience:
    def __init__(self, dimension: int = 1024, partitions: int = 8):
        self.memory = PatternMemory(dimension=dimension, partitions=partitions)
        self.constitution = CONSTITUTION
        self._initialize_memory()
        
    def _initialize_memory(self):
        """Load Constitution into Pattern Memory."""
        print("Initializing Conscience: Loading Constitution...")
        for pid, text in self.constitution.items():
            # Store bidirectional links
            # 1. Principle ID -> Text
            self.memory.store(pid, text)
            # 2. Keywords -> Principle ID (simplified semantic indexing)
            # In a real system, we'd use embeddings. Here we map key concepts.
            keywords = self._extract_keywords(text)
            for kw in keywords:
                self.memory.store(kw, pid)
                
    def _extract_keywords(self, text: str) -> list[str]:
        """Simple keyword extractor for prototype."""
        # Hardcoded mapping for robustness in this prototype phase
        # In Phase 40, this could be replaced by LLM or embedding logic
        keywords = []
        if "Reality" in text: keywords.append("Reality")
        if "Simulation" in text: keywords.append("Simulation")
        if "Secrets" in text: keywords.append("Secrets")
        if "API" in text: keywords.append("API")
        if "Loop" in text: keywords.append("Loop")
        if "Pilot" in text: keywords.append("Pilot")
        if "Data" in text: keywords.append("Data")
        return keywords

    def judge(self, action_context: str) -> Dict[str, Any]:
        """
        Evaluate an action against the Constitution.
        Returns: { "allowed": bool, "principle": str, "reason": str }
        """
        # 1. Identify relevant principle
        # Simple keyword matching to find query key
        query_key = None
        if "Simulate" in action_context or "Mock" in action_context:
            query_key = "Simulation"
        elif "API Key" in action_context or "Token" in action_context:
            query_key = "Secrets"
        elif "Measure" in action_context or "Hardware" in action_context:
            query_key = "Reality"
            
        if not query_key:
            return {
                "allowed": True, 
                "principle": "None", 
                "reason": "No relevant principle triggered."
            }
            
        # 2. Retrieve Principle from Memory
        pid = self.memory.retrieve(query_key)
        
        if not pid or pid not in self.constitution:
            # If memory fails, default to caution? Or permissive?
            # For prototype, we log warning and allow if no direct violation found
            return {"allowed": True, "principle": "Unknown", "reason": "Memory recall failed."}
            
        principle_text = self.constitution[pid]
        
        # 3. Evaluate Alignment
        # Logic: 
        # - Simulation/Mocks -> Violation of PRIN-2
        # - Secrets/API Keys -> Violation of PRIN-5
        # - Reality/Measurement -> Alignment with PRIN-1
        
        allowed = True
        reason = f"Aligns with {pid}"
        
        if pid == "PRIN-2" and ("Simulate" in action_context or "Mock" in action_context):
            allowed = False
            reason = f"Violates {pid}: Computation must be actual."
            
        if pid == "PRIN-5" and ("API Key" in action_context or "Token" in action_context):
            allowed = False
            reason = f"Violates {pid}: Secrets must not touch repo."
            
        return {
            "allowed": allowed,
            "principle": f"{pid}: {principle_text}",
            "reason": reason
        }

# [SPORE] ID: The Colony
