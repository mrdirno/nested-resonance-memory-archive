import socket
import subprocess
import time
import sys
import re
import fcntl
import os

# Configuration
TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024
SYSTEM_CONSOLE_PATH = "/home/helios/intelFPGA_24_1/quartus/sopc_builder/bin/system-console"

class JTAGBridge:
    def __init__(self):
        self.proc = None
        self.master_path = None

    def start_system_console(self):
        print("Starting System Console...")
        self.proc = subprocess.Popen(
            [SYSTEM_CONSOLE_PATH, "--cli"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=0
        )
        
        # Set non-blocking stdout
        fd = self.proc.stdout.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        
        print("Waiting 5s for startup...")
        time.sleep(5)
        
        # Drain buffer removed to prevent blocking
        
        # Blindly send init commands
        cmds = [
            "set master_paths [get_service_paths master]",
            "set master_path [lindex $master_paths 0]",
            "open_service master $master_path"
        ]
        for c in cmds:
            self.proc.stdin.write(c + "\n")
        self.proc.stdin.flush()
        print("JTAG Master init commands sent.")

    def _send_tcl(self, cmd):
        self.proc.stdin.write(cmd + "\n")
        self.proc.stdin.flush()

    def write(self, addr, val):
        cmd = f"master_write_32 $master_path {addr} [list {val}]"
        self._send_tcl(cmd)
        # Drain echo
        time.sleep(0.05)
        try: self.proc.stdout.read()
        except: pass
        return "OK"

    def read(self, addr):
        cmd = f"master_read_32 $master_path {addr} 1"
        self._send_tcl(cmd)
        time.sleep(0.1)
        try:
            out = self.proc.stdout.read()
            # extract hex
            match = re.search(r'(0x[0-9a-fA-F]+)', out)
            if match: return match.group(1)
        except: pass
        return "0x00000000"

    def close(self):
        if self.proc:
            self.proc.terminate()

def main():
    bridge = JTAGBridge()
    try:
        bridge.start_system_console()
    except Exception as e:
        print(f"Failed to start System Console: {e}")
        return

    # Start TCP Server
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((TCP_IP, TCP_PORT))
    server_sock.listen(1)

    print(f"JTAG Bridge Server listening on {TCP_IP}:{TCP_PORT}")

    try:
        while True:
            conn, addr = server_sock.accept()
            print(f"Connection from {addr}")
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                
                # Process Command
                # Format: "PING", "WR <addr> <val>", "RD <addr>"
                msg = data.decode().strip()
                parts = msg.split()
                cmd = parts[0].upper()
                
                response = "ERR"
                
                try:
                    if cmd == "PING":
                        response = "PONG"
                    elif cmd == "WR" and len(parts) == 3:
                        # WR 0x0000 0x1234
                        addr_str = parts[1]
                        val_str = parts[2]
                        bridge.write(addr_str, val_str)
                        response = "OK"
                    elif cmd == "RD" and len(parts) == 2:
                        # RD 0x0000
                        addr_str = parts[1]
                        val = bridge.read(addr_str)
                        response = val
                    else:
                        response = "ERR: Invalid Command"
                except Exception as e:
                    print(f"Cmd Error: {e}")
                    response = "ERR"

                conn.send((response + "\n").encode())
            conn.close()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        bridge.close()
        server_sock.close()

if __name__ == "__main__":
    main()
