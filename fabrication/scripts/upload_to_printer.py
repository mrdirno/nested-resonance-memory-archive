import requests
import sys
import os

def upload_file(filepath, printer_ip="192.168.68.88", port=7125):
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        return False

    filename = os.path.basename(filepath)
    url = f"http://{printer_ip}:{port}/server/files/upload"
    
    print(f"Uploading {filename} to {printer_ip}...")
    
    try:
        with open(filepath, 'rb') as f:
            files = {'file': f}
            # Moonraker upload often takes an optional 'path' arg to specify subfolder, default is root (gcodes)
            response = requests.post(url, files=files)
            
        if response.status_code in [200, 201]:
            print(f"Success! Uploaded {filename}.")
            print(f"Server Response: {response.json()}")
            return True
        else:
            print(f"Failed to upload {filename}. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python upload_to_printer.py <filepath> [printer_ip]")
        sys.exit(1)
        
    fpath = sys.argv[1]
    ip = sys.argv[2] if len(sys.argv) > 2 else "192.168.68.88"
    
    upload_file(fpath, ip)
