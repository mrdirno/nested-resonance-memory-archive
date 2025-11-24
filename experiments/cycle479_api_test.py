"""
Cycle 479: API Test
Role: The Client
Responsibility: Verify the Interface.
"""
import sys
import os

sys.path.append(os.getcwd())

from nrm_core.interface import NRMInterface

def run_experiment():
    print("Cycle 479: NRM API Test")
    print("=======================")
    
    api = NRMInterface()
    
    # 1. Add Data
    print("Adding Nodes...")
    api.handle_request("ADD_NODE", {"id": "love", "vector": [1.0, 1.0, 0.0]})
    api.handle_request("ADD_NODE", {"id": "hate", "vector": [-1.0, 1.0, 0.0]})
    api.handle_request("ADD_NODE", {"id": "pizza", "vector": [0.0, 0.0, 1.0]})
    
    # 2. Query
    print("Querying [1.0, 1.0, 0.0] (Love)...")
    response = api.handle_request("QUERY", {"vector": [1.0, 1.0, 0.0]})
    
    print("Response:", response)
    
    results = response.get("results", [])
    if results and results[0][0] == "love":
        print("SUCCESS: API returned correct result.")
    else:
        print("FAIL: API malformed.")

if __name__ == "__main__":
    run_experiment()
