"""
Cycle 569: The Holodeck Integration
Goal: Verify the Web Server correctly exposes the Universal Operator.
"""
import requests
import subprocess
import time
import sys
import os
import signal

def run_holodeck_test():
    print("Starting Holodeck Server...", flush=True)
    
    # Start server in background with PYTHONPATH set
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    process = subprocess.Popen(
        [sys.executable, "nrm_core/helios/server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("Waiting for server to initialize...", flush=True)
    server_url = "http://localhost:5001"
    
    max_retries = 20
    for i in range(max_retries):
        try:
            requests.get(server_url)
            print("Server is up!", flush=True)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            if i == max_retries - 1:
                print("Server failed to start.")
                # Print stderr
                outs, errs = process.communicate(timeout=5)
                print(errs)
                return False

    # Test Create Command
    print("Sending 'create cube' command...", flush=True)
    payload = {"command": "create cube at 50 50 50"}
    try:
        response = requests.post(f"{server_url}/api/command", json=payload)
        print(f"Response Code: {response.status_code}")
        print(f"Response Body: {response.json()}")
        
        if response.status_code == 200 and response.json().get("status") == "success":
            print("Success: Object created via API.")
        else:
            print("Failed to create object.")
            return False
            
    except Exception as e:
        print(f"API Request Failed: {e}")
        return False

    # Test State Retrieval
    print("Fetching System State...", flush=True)
    try:
        response = requests.get(f"{server_url}/api/state")
        data = response.json()
        print(f"State: {data}")
        
        objects = data.get("objects", [])
        if len(objects) > 0:
            print(f"Success: {len(objects)} object(s) found in state.")
        else:
            print("Error: State is empty.")
            return False
            
    except Exception as e:
        print(f"State Request Failed: {e}")
        return False

    # Cleanup
    print("Terminating Server...", flush=True)
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        
    return True

if __name__ == "__main__":
    if run_holodeck_test():
        print("CYCLE 569 COMPLETE: Holodeck Integration Verified.")
        sys.exit(0)
    else:
        print("CYCLE 569 FAILED.")
        sys.exit(1)
