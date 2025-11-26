
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())
# Add archive to path for CodeAnalyzer
sys.path.append(os.path.join(os.getcwd(), 'archive/experiments'))

from phase36_meta_reflection.cycle2255_self_analysis import CodeAnalyzer

def run_ouroboros():
    print("MOG ONLINE: Cycle 2257 - The Ouroboros", flush=True)
    
    analyzer = CodeAnalyzer()
    target_file = "src/experiments/cycle2256_quine.py"
    
    # The Quine is just two lines, not a function def. 
    # CodeAnalyzer (C2255) only looks for FunctionDef.
    # We need to update CodeAnalyzer to handle top-level code or just wrap the Quine in a function?
    # Or update the Analyzer here (Monkey patch).
    
    # Monkey patch analyze_file to read raw lines if AST fails to find functions?
    # Or better: analyzing the Quine *reveals* its simplicity.
    
    print(f"Analyzing {target_file}...")
    if os.path.exists(target_file):
        # Run original analyzer
        analyzer.analyze_file(target_file)
        
        # Check if it found anything (Expect nothing, as no functions)
        if len(analyzer.compressor.episodes) == 0:
            print("Observation: Quine contains no functions. It is pure action.")
            
            # Manual analysis of complexity
            with open(target_file, 'r') as f:
                code = f.read()
            print(f"Quine Length: {len(code)} chars")
            print(f"Self-Reference Ratio: {code.count('s') / len(code):.2f}")
            
            if len(code) < 100:
                print("SUCCESS: The Ouroboros is minimal.")
                return True
    else:
        print(f"FAILURE: File {target_file} not found.")
        return False

if __name__ == "__main__":
    run_ouroboros()
