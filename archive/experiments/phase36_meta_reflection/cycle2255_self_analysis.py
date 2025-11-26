
import sys
import os
import ast
import numpy as np
from typing import List, Dict

# Add project root to path
sys.path.append(os.getcwd())

from src.memory.compression import EpisodicCompressor, Episode, SemanticRule

class CodeAnalyzer:
    def __init__(self):
        self.compressor = EpisodicCompressor(similarity_threshold=0.7)
        
    def analyze_file(self, filepath: str):
        with open(filepath, 'r') as f:
            code = f.read()
            
        tree = ast.parse(code)
        
        # Extract functions and classes as "Episodes"
        # Feature vector: [num_lines, num_args, num_returns] (Simplified)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                num_lines = len(node.body)
                num_args = len(node.args.args)
                
                # Heuristic for return
                has_return = any(isinstance(n, ast.Return) for n in ast.walk(node))
                
                # Normalize features roughly
                features = np.array([
                    min(num_lines / 20.0, 1.0),
                    min(num_args / 5.0, 1.0),
                    1.0 if has_return else 0.0
                ])
                
                # Outcome: Complexity? Or just "Is Function"?
                # Let's say outcome is "Complexity Score" (0-1)
                complexity = (num_lines + num_args) / 30.0
                complexity = min(complexity, 1.0)
                
                ep = Episode(
                    id=f"func_{node.name}",
                    content=np.zeros(1),
                    outcome=complexity,
                    context=features
                )
                self.compressor.add_episode(ep)
                
    def report(self):
        self.compressor.compress()
        print(f"Identified {len(self.compressor.semantic_rules)} types of functions.")
        for rule in self.compressor.semantic_rules:
            print(f"Type {rule.id}: Avg Complexity {rule.average_outcome:.2f}, Count {rule.count}")
            print(f"  Features (Len, Args, Ret): {rule.pattern_centroid}")

def run_self_analysis():
    print("MOG ONLINE: Cycle 2255 - Self-Analysis", flush=True)
    
    analyzer = CodeAnalyzer()
    target_file = "src/fractal/agent.py"
    
    print(f"Analyzing {target_file}...")
    if os.path.exists(target_file):
        analyzer.analyze_file(target_file)
        analyzer.report()
        
        # Check if we found structure
        if len(analyzer.compressor.semantic_rules) > 0:
            print("SUCCESS: System identified structural patterns in its own code.")
            return True
    else:
        print(f"FAILURE: File {target_file} not found.")
    
    return False

if __name__ == "__main__":
    run_self_analysis()
