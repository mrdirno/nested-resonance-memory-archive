import subprocess
import re
import sys

def find_hps():
    print("Scanning for DE10-Nano (Terasic)...")
    try:
        # Quick scan of local subnet
        # Assuming 192.168.68.0/24 based on history
        cmd = ["nmap", "-sn", "192.168.68.0/24"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        # Look for Terasic MAC OUI: 00:07:ED (Altera/Terasic often show up as Altera or Terasic)
        # Or look for hostname "de10-nano"
        
        # Simple parsing
        ip = None
        lines = res.stdout.split('\n')
        for i, line in enumerate(lines):
            if "Nmap scan report for" in line:
                parts = line.split()
                current_ip = parts[-1].strip('()')
            if "MAC Address" in line and ("Terasic" in line or "Altera" in line or "00:07:ED" in line):
                print(f"FOUND TARGET: {current_ip} ({line})")
                return current_ip
                
        return None
    except FileNotFoundError:
        print("Error: nmap not found. Please install nmap.")
        return None

if __name__ == "__main__":
    ip = find_hps()
    if ip:
        print(ip)
        sys.exit(0)
    else:
        sys.exit(1)

