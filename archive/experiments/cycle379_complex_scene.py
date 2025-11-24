import requests
import time
import socketio
import sys

BASE_URL = "http://localhost:5001/api"
sio = socketio.Client()

scene_verified = False
trap_count = 0

@sio.event
def connect():
    print("WebSocket connected")

@sio.event
def state_update(data):
    global scene_verified, trap_count
    objects = data.get('objects', [])
    traps = data.get('traps', [])
    
    print(f"Stream Update: {len(objects)} objects, {len(traps)} traps")
    
    if len(objects) == 4 and len(traps) > 100:
        scene_verified = True
        trap_count = len(traps)
        # We can disconnect once verified
        # sio.disconnect() 

def run_experiment():
    print("Cycle 379: Complex Scene Composition")
    print("====================================")
    
    # 1. Clear Scene (Delete all existing)
    print("\n[1] Clearing Scene...")
    try:
        res = requests.get(f"{BASE_URL}/state")
        current_objects = res.json().get("objects", [])
        for obj in current_objects:
            requests.post(f"{BASE_URL}/command", json={"command": f"Delete object {obj['id']}"})
        print("Scene cleared.")
    except Exception as e:
        print(f"FAIL: Connection error - {e}")
        return

    # 2. Connect WebSocket
    print("\n[2] Connecting to Stream...")
    try:
        sio.connect('http://localhost:5001')
    except Exception as e:
        print(f"FAIL: WebSocket error - {e}")
        return

    # 3. Build Scene (4 Cubes)
    print("\n[3] Building Scene (4 Cubes)...")
    positions = [
        (30, 30, 50),
        (70, 30, 50),
        (30, 70, 50),
        (70, 70, 50)
    ]
    
    for i, pos in enumerate(positions):
        cmd = f"Create a cube at {pos[0]} {pos[1]} {pos[2]}"
        res = requests.post(f"{BASE_URL}/command", json={"command": cmd})
        if res.status_code == 200:
            print(f"Created Cube {i+1} at {pos}")
        else:
            print(f"FAIL: Could not create cube at {pos}")
            
    # 4. Verify Stream
    print("\n[4] Verifying Volumetric Stream...")
    start_time = time.time()
    while not scene_verified and time.time() - start_time < 5:
        time.sleep(0.1)
        
    if scene_verified:
        print(f"SUCCESS: Scene verified via WebSocket.")
        print(f"Detected {trap_count} acoustic traps for 4 objects.")
    else:
        print("FAIL: Stream verification timed out or criteria not met.")

    sio.disconnect()

if __name__ == "__main__":
    run_experiment()
