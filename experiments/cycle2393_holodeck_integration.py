"""
Cycle 2393: Holodeck Integration Test (Gate 17)
Verifies that the Flask API correctly triggers the FPGA Driver.
"""

import requests
import json
import sys
import time
import os # Moved to global scope
from multiprocessing import Process

# API Endpoint
BASE_URL = "http://127.0.0.1:5001"

def test_simulation_endpoint():
    print("[Test] Testing /simulate endpoint...")
    
    # Payload: 64 phases (0) and Target (0,0,0)
    # From Cycle 2388, we know Result should be 1248616634
    payload = {
        "phases": [0] * 64,
        "target": [0, 0, 0]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/simulate", json=payload)
        if response.status_code == 200:
            data = response.json()
            potential = data.get('potential')
            print(f"[Test] Response: {data}")
            
            if potential == 1248616634:
                print("[Test] PASS: Potential matches expected value.")
                return True
            else:
                print(f"[Test] FAIL: Expected 1248616634, got {potential}")
                return False
        else:
            print(f"[Test] FAIL: API returned {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"[Test] FAIL: Connection error - {e}")
        return False

def run_server():
    # This is a bit hacky for a test, usually we'd use pytest-flask
    # But adhering to "No Framework Assumption"
    os.system("python3 src/helios/api/server.py > server.log 2>&1")

if __name__ == "__main__":
    
    # Start Server in Background
    print("[Test] Starting Server...")
    p = Process(target=run_server)
    p.start()
    
    time.sleep(5) # Wait for boot
    
    try:
        # Check Status first
        print("[Test] Checking Status...")
        try:
            r = requests.get(f"{BASE_URL}/status")
            print(f"[Test] Status: {r.json()}")
        except:
            print("[Test] Server not reachable.")
            
        # Run Test
        success = test_simulation_endpoint()
        
    finally:
        print("[Test] Stopping Server...")
        p.terminate()
        p.join()
        # Force kill just in case os.system spawned a detached child
        os.system("pkill -f src/helios/api/server.py")
        
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
