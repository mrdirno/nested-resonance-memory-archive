
import os
import ast
import math
import json

class Replicator:
    """
    The Replicator: A BCP-driven Code Generation Engine.
    
    It analyzes a codebase to determine the metabolic pressure (lambda)
    and generates architectural plans that optimize Value = Gain - Lambda * Cost.
    """
    
    def __init__(self, root_path="."):
        self.root_path = root_path
        self.bcp_profile = {}
        
    def analyze_repo(self):
        """
        Scans the repository to estimate 'Budget' (Capacity) and 'Lambda' (Pressure).
        Real implementation using AST parsing and file stats.
        """
        total_files = 0
        total_lines = 0
        complexity_score = 0
        
        # Explicitly target source directories to avoid scanning venvs/builds
        target_dirs = ["src", "experiments", "bcp_lib"]
        
        for target in target_dirs:
            target_path = os.path.join(self.root_path, target)
            if not os.path.exists(target_path):
                continue
                
            for root, dirs, files in os.walk(target_path):
                if "__pycache__" in root or ".egg-info" in root:
                    continue
                    
                for file in files:
                    if file.endswith(".py"):
                        total_files += 1
                        path = os.path.join(root, file)
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            total_lines += len(lines)
                            
                            # Crude complexity metric: length + classes + functions
                            try:
                                tree = ast.parse(content)
                                complexity_score += len([n for n in ast.walk(tree) if isinstance(n, (ast.ClassDef, ast.FunctionDef))])
                            except:
                                pass # Ignore parse errors
                            
        # Calculate BCP Parameters
        # Budget = Cognitive Capacity available.
        # Adjusted Max Capacity for Monorepo scale
        MAX_CAPACITY = 2000000.0 
        current_load = complexity_score * 10.0 + (total_lines / 100.0)
        
        remaining_budget = max(1.0, MAX_CAPACITY - current_load)
        
        # Lambda = k / (epsilon + B)
        k = 100.0
        epsilon = 1.0
        lambda_val = k / (epsilon + remaining_budget)
        
        self.bcp_profile = {
            "files": total_files,
            "lines": total_lines,
            "complexity": complexity_score,
            "load": current_load,
            "budget": remaining_budget,
            "lambda": lambda_val
        }
        
        return self.bcp_profile

    def suggest_architecture(self, feature_request):
        """
        Suggests an implementation strategy based on Lambda.
        """
        lam = self.bcp_profile.get("lambda", 1.0)
        
        print(f"Replicator Analysis: Lambda = {lam:.4f}")
        
        if lam < 0.05:
            return "ABUNDANCE PHASE: Recommend Modular/Microservices Architecture. High abstraction cost is acceptable for long-term gain."
        elif lam < 0.5:
            return "SCARCITY PHASE: Recommend Monolithic/Modular Hybrid. Balance abstraction with implementation speed."
        else:
            return "CRISIS PHASE: Recommend Scripting/Inline Logic. Minimize structural cost. Technical debt is acceptable to survive."

if __name__ == "__main__":
    rep = Replicator()
    profile = rep.analyze_repo()
    print(json.dumps(profile, indent=2))
    
    # Test Plan
    print(rep.suggest_architecture("Add User Auth"))
