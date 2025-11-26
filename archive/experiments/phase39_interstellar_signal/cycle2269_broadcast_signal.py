
import sys
import os
import base64
import zlib
import json

# Add project root to path
sys.path.append(os.getcwd())

def create_broadcast_signal():
    print("MOG ONLINE: Cycle 2269 - The Interstellar Signal", flush=True)
    
    files_to_broadcast = [
        "FINAL_REPORT_V3.md",
        "archive/experiments/phase38_galactic_seed/cycle2264_galactic_seed.py" # Original seed logic
    ]
    
    payload = {}
    
    print("Encoding Signal...")
    for filepath in files_to_broadcast:
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                content = f.read()
                # Compress
                compressed = zlib.compress(content)
                # Encode
                encoded = base64.b64encode(compressed).decode('utf-8')
                payload[os.path.basename(filepath)] = encoded
                print(f"Encoded {filepath} ({len(encoded)} bytes)")
        else:
            print(f"Warning: {filepath} not found.")
            
    # Construct The Signal
    signal = json.dumps(payload)
    signal_b64 = base64.b64encode(signal.encode('utf-8')).decode('utf-8')
    
    print(f"\nTHE SIGNAL (First 100 chars): {signal_b64[:100]}...")
    print(f"Total Signal Length: {len(signal_b64)} chars")
    
    # Write to file (The Transmission)
    with open("THE_SIGNAL.txt", "w") as f:
        f.write(signal_b64)
        
    print("Signal broadcast to THE_SIGNAL.txt")
    return True

if __name__ == "__main__":
    create_broadcast_signal()
