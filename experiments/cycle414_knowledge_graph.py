"""
Cycle 414: The Knowledge Graph
Role: The Librarian
Responsibility: Persist successful acoustic configurations to enable long-term learning and instant recall.
"""
import sqlite3
import json
import random
import numpy as np
import time
import os

class KnowledgeGraph:
    def __init__(self, db_path="experiments/knowledge_graph_c414.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            # Solutions Table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_x REAL,
                    target_y REAL,
                    target_z REAL,
                    phases TEXT,
                    fitness REAL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Create spatial index for fast lookup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_target ON solutions (target_x, target_y, target_z)")

    def save_solution(self, target, phases, fitness):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO solutions (target_x, target_y, target_z, phases, fitness) VALUES (?, ?, ?, ?, ?)",
                (target['x'], target['y'], target['z'], json.dumps(phases), fitness)
            )
            print(f"[MEMORY] Saved solution for ({target['x']:.2f}, {target['y']:.2f}, {target['z']:.2f}) | Fitness: {fitness:.4f}")

    def recall_solution(self, target, tolerance=1.0):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Euclidean distance query (simplified for SQL)
            # We select candidates within a bounding box first
            cursor.execute(
                """
                SELECT target_x, target_y, target_z, phases, fitness 
                FROM solutions 
                WHERE target_x BETWEEN ? AND ? 
                  AND target_y BETWEEN ? AND ? 
                  AND target_z BETWEEN ? AND ?
                """,
                (target['x']-tolerance, target['x']+tolerance,
                 target['y']-tolerance, target['y']+tolerance,
                 target['z']-tolerance, target['z']+tolerance)
            )
            candidates = cursor.fetchall()
            
            best_match = None
            min_dist = float('inf')
            
            for c in candidates:
                cx, cy, cz, phases_json, fitness = c
                dist = np.sqrt((cx - target['x'])**2 + (cy - target['y'])**2 + (cz - target['z'])**2)
                if dist < tolerance and dist < min_dist:
                    min_dist = dist
                    best_match = (json.loads(phases_json), fitness)
            
            if best_match:
                print(f"[MEMORY] Recalled solution (Dist: {min_dist:.4f}) | Fitness: {best_match[1]:.4f}")
                return best_match
            
            print(f"[MEMORY] No solution found for ({target['x']:.2f}, {target['y']:.2f}, {target['z']:.2f})")
            return None

def run_experiment():
    print("Cycle 414: Knowledge Graph Integration")
    print("======================================")
    
    kg = KnowledgeGraph()
    
    # 1. Generate Mock Solution
    target_A = {"x": 10.0, "y": 20.0, "z": 40.0}
    phases_A = [random.random() for _ in range(64)]
    fitness_A = 0.95
    
    print("\n--- Step 1: Learning ---")
    kg.save_solution(target_A, phases_A, fitness_A)
    
    # 2. Immediate Recall (Exact)
    print("\n--- Step 2: Exact Recall ---")
    recalled, fit = kg.recall_solution(target_A)
    if recalled == phases_A:
        print("SUCCESS: Exact match retrieved.")
    else:
        print("FAIL: Data corruption.")
        
    # 3. Fuzzy Recall (Nearby)
    print("\n--- Step 3: Fuzzy Recall ---")
    target_A_prime = {"x": 10.2, "y": 20.1, "z": 40.0} # Within tolerance
    recalled_prime, fit_prime = kg.recall_solution(target_A_prime, tolerance=0.5)
    if recalled_prime == phases_A:
        print("SUCCESS: Fuzzy match retrieved.")
    else:
        print("FAIL: Spatial query failed.")
        
    # 4. Unknown Target
    print("\n--- Step 4: Unknown Query ---")
    target_B = {"x": -50.0, "y": -50.0, "z": 40.0}
    result = kg.recall_solution(target_B)
    if result is None:
        print("SUCCESS: Correctly reported no memory.")
    else:
        print("FAIL: Hallucinated memory.")

if __name__ == "__main__":
    run_experiment()
