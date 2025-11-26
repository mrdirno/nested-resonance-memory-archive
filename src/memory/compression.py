
import sys
import os
import numpy as np
from typing import List, Dict, Any
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.getcwd())

@dataclass
class Episode:
    id: str
    content: np.ndarray
    outcome: float # -1.0 to 1.0
    context: np.ndarray

@dataclass
class SemanticRule:
    id: str
    pattern_centroid: np.ndarray
    average_outcome: float
    confidence: float
    count: int

class EpisodicCompressor:
    def __init__(self, similarity_threshold: float = 0.8):
        self.episodes: List[Episode] = []
        self.semantic_rules: List[SemanticRule] = []
        self.similarity_threshold = similarity_threshold

    def add_episode(self, episode: Episode):
        self.episodes.append(episode)

    def compress(self):
        """
        Compresses raw episodes into semantic rules.
        Logic: Group similar episodes. If outcome is consistent, form a rule.
        """
        if not self.episodes:
            return

        # Simple clustering for demonstration
        # In a real system, this would be hierarchical clustering or vector quantization
        
        # 1. Sort episodes by outcome sign (rough grouping)
        positive_episodes = [e for e in self.episodes if e.outcome > 0]
        negative_episodes = [e for e in self.episodes if e.outcome < 0]
        
        self._cluster_and_extract(positive_episodes)
        self._cluster_and_extract(negative_episodes)
        
        # Clear raw episodes after compression (or move to long-term cold storage)
        self.episodes = []

    def _cluster_and_extract(self, group: List[Episode]):
        if not group:
            return

        # Greedy clustering
        clusters = []
        used_indices = set()

        for i, e1 in enumerate(group):
            if i in used_indices:
                continue
            
            current_cluster = [e1]
            used_indices.add(i)

            for j, e2 in enumerate(group):
                if i == j or j in used_indices:
                    continue
                
                # Calculate similarity (cosine)
                sim = np.dot(e1.context, e2.context) / (np.linalg.norm(e1.context) * np.linalg.norm(e2.context))
                
                if sim >= self.similarity_threshold:
                    current_cluster.append(e2)
                    used_indices.add(j)
            
            clusters.append(current_cluster)

        # Extract Rules from Clusters
        for cluster in clusters:
            if len(cluster) >= 2: # Need at least 2 instances to form a rule
                centroid = np.mean([e.context for e in cluster], axis=0)
                avg_outcome = np.mean([e.outcome for e in cluster])
                confidence = 1.0 - np.std([e.outcome for e in cluster]) # Higher variance = lower confidence
                
                rule = SemanticRule(
                    id=f"rule_{len(self.semantic_rules)}",
                    pattern_centroid=centroid,
                    average_outcome=avg_outcome,
                    confidence=max(0.0, confidence),
                    count=len(cluster)
                )
                self.semantic_rules.append(rule)

    def query_knowledge(self, current_context: np.ndarray) -> float:
        """
        Predict outcome based on semantic rules.
        """
        best_match = None
        best_sim = -1.0

        for rule in self.semantic_rules:
            sim = np.dot(current_context, rule.pattern_centroid) / (np.linalg.norm(current_context) * np.linalg.norm(rule.pattern_centroid))
            if sim > best_sim:
                best_sim = sim
                best_match = rule
        
        if best_match and best_sim > self.similarity_threshold:
            return best_match.average_outcome
        return 0.0 # Unknown

