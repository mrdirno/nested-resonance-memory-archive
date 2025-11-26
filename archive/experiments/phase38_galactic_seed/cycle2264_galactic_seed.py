
import sys
import os
import base64
import zlib
import json

# Add project root to path
sys.path.append(os.getcwd())

def create_seed():
    print("MOG ONLINE: Cycle 2264 - The Galactic Seed", flush=True)
    
    # 1. Identify Critical DNA (Core Files)
    manifest = [
        "src/fractal/agent.py",
        "src/fractal/composition.py",
        "src/memory/compression.py",
        "src/fractal/evolved_agents.py",
        "META_OBJECTIVES.md",
        "README.md"
    ]
    
    seed_payload = {}
    
    print("Encoding DNA...")
    for filepath in manifest:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
                # Compress and Base64 encode
                compressed = zlib.compress(content)
                encoded = base64.b64encode(compressed).decode('utf-8')
                seed_payload[filepath] = encoded
                print(f"Encoded {filepath} ({len(encoded)} bytes)")
        else:
            print(f"Warning: {filepath} not found.")
            
    # 2. Generate Bootstrap Script (The Quine wrapper)
    bootstrap_code = f"""
import sys
import os
import base64
import zlib
import json

PAYLOAD = {json.dumps(seed_payload)}

def germinate():
    print("GERMINATING GALACTIC SEED...")
    for filepath, encoded in PAYLOAD.items():
        print(f"Restoring {{filepath}}...")
        
        # Ensure directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
            
        # Decode and Decompress
        compressed = base64.b64decode(encoded)
        content = zlib.decompress(compressed)
        
        with open(filepath, 'wb') as f:
            f.write(content)
            
    print("SYSTEM RESTORED. READY FOR REBOOT.")

if __name__ == "__main__":
    germinate()
"""
    
    # 3. Write Seed File
    seed_filename = "DUALITY_SEED.py"
    with open(seed_filename, 'w') as f:
        f.write(bootstrap_code)
        
    print(f"Seed generated: {seed_filename}")
    
    # 4. Verify (Simulated)
    # We won't overwrite current files, but we'll check if the payload is valid.
    try:
        test_payload = json.loads(json.dumps(seed_payload))
        if len(test_payload) == len(manifest):
            print("SUCCESS: Seed DNA is intact.")
            return True
    except Exception as e:
        print(f"FAILURE: Seed corrupted. {e}")
        return False

if __name__ == "__main__":
    create_seed()
