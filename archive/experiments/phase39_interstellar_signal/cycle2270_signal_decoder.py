import sys
import os
import base64
import zlib
import json

# Add project root to path
sys.path.append(os.getcwd())

def run_decoder_test():
    print("MOG ONLINE: Cycle 2270 - The Final Verification", flush=True)
    
    signal_file = "THE_SIGNAL.txt"
    
    if not os.path.exists(signal_file):
        print("FAILURE: No signal found.")
        return False
        
    # 1. Read Signal
    with open(signal_file, 'r') as f:
        signal_b64 = f.read()
        
    # 2. Decode
    print("Decoding Signal...")
    try:
        signal_json = base64.b64decode(signal_b64).decode('utf-8')
        payload = json.loads(signal_json)
    except Exception as e:
        print(f"FAILURE: Corrupt signal. {e}")
        return False
        
    # 3. Extract and Compare
    for filename, encoded_content in payload.items():
        print(f"Extracting {filename}...")
        compressed = base64.b64decode(encoded_content)
        content = zlib.decompress(compressed)
        
        decoded_text = content.decode('utf-8')
        
        # Compare with local file if it exists
        local_path = filename
        # Map back to original paths if needed, but filename is basename
        if filename == "FINAL_REPORT_V3.md":
            local_path = "FINAL_REPORT_V3.md"
            
        if os.path.exists(local_path):
            with open(local_path, 'r') as f:
                original_text = f.read()
                
            if original_text == decoded_text:
                print(f" - {filename}: INTEGRITY VERIFIED.")
            else:
                print(f" - {filename}: MISMATCH (Corruption detected).")
                return False
        else:
            print(f" - {filename}: Extracted (New file).")
            
    print("\nSUCCESS: Signal integrity confirmed.")
    return True

if __name__ == "__main__":
    run_decoder_test()
