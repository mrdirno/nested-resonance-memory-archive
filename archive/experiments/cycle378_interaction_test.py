import requests
import time
import json

BASE_URL = "http://localhost:5001/api"

def test_interaction():
    print("Cycle 378: Holodeck Interaction Test")
    print("====================================")
    
    # 1. Create Cube
    print("\n[1] Testing Creation...")
    cmd = {"command": "Create a cube at 50 50 50"}
    try:
        res = requests.post(f"{BASE_URL}/command", json=cmd)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        
        if res.status_code != 200 or "object_id" not in res.json():
            print("FAIL: Creation failed.")
            return
            
        obj_id = res.json()["object_id"]
        print(f"SUCCESS: Created Object ID {obj_id}")
        
    except Exception as e:
        print(f"FAIL: Connection error - {e}")
        return

    time.sleep(1)

    # 2. Verify State
    print("\n[2] Verifying State...")
    try:
        res = requests.get(f"{BASE_URL}/state")
        state = res.json()
        objects = state.get("objects", [])
        found = False
        for obj in objects:
            if obj["id"] == obj_id:
                print(f"Found Object {obj_id} at {obj['location']}")
                if obj['location'] == [50.0, 50.0, 50.0]:
                    found = True
        
        if found:
            print("SUCCESS: State verified.")
        else:
            print("FAIL: Object not found in state.")
            
    except Exception as e:
        print(f"FAIL: State check error - {e}")

    time.sleep(1)

    # 3. Move Object
    print("\n[3] Testing Movement...")
    cmd = {"command": f"Move object {obj_id} to 60 60 60"}
    try:
        res = requests.post(f"{BASE_URL}/command", json=cmd)
        print(f"Response: {res.json()}")
        
        # Verify move
        res = requests.get(f"{BASE_URL}/state")
        state = res.json()
        for obj in state["objects"]:
            if obj["id"] == obj_id:
                print(f"Object {obj_id} is now at {obj['location']}")
                if obj['location'] == [60.0, 60.0, 60.0]:
                    print("SUCCESS: Movement verified.")
                else:
                    print("FAIL: Movement mismatch.")
                    
    except Exception as e:
        print(f"FAIL: Move error - {e}")

    time.sleep(1)
    
    # 4. Delete Object
    print("\n[4] Testing Deletion...")
    cmd = {"command": f"Delete object {obj_id}"}
    try:
        res = requests.post(f"{BASE_URL}/command", json=cmd)
        print(f"Response: {res.json()}")
        
        # Verify delete
        res = requests.get(f"{BASE_URL}/state")
        state = res.json()
        found = False
        for obj in state["objects"]:
            if obj["id"] == obj_id:
                found = True
        
        if not found:
            print("SUCCESS: Deletion verified.")
        else:
            print("FAIL: Object still exists.")
            
    except Exception as e:
        print(f"FAIL: Delete error - {e}")

if __name__ == "__main__":
    test_interaction()
