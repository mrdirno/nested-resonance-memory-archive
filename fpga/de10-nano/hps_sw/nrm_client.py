import socket
import sys
import time

HOST = '192.168.68.57'  # DE10-Nano IP
PORT = 5000

def send_command(cmd):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            s.sendall(cmd.encode() + b'\n')
            data = s.recv(1024)
            print(f"Sent: {cmd.strip()}")
            print(f"Received: {data.decode().strip()}")
        except ConnectionRefusedError:
            print(f"Connection refused to {HOST}:{PORT}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        send_command(cmd)
    else:
        print("Usage: python3 nrm_client.py <COMMAND>")
        print("Example: python3 nrm_client.py PING")
        print("Example: python3 nrm_client.py RD 0x0000")
        print("Example: python3 nrm_client.py WR 0x0000 0x1234")
