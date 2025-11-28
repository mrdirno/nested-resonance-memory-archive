import socket
import time
import math
import sys

# Configuration
HOST = '127.0.0.1'
PORT = 5000
DATA_ADDR = 0x1000  # Targeted Shared Memory Address
CTRL_ADDR = 0x0000  # Targeted Control Register

def generate_sine_wave(steps=64):
    """Generates a single period of a sine wave scaled to 0-255."""
    data = []
    for i in range(steps):
        val = int(127.5 + 127.5 * math.sin(2 * math.pi * i / steps))
        data.append(val)
    return data

def stream_data():
    """Streams generated pattern to the FPGA bridge."""
    print(f"Connecting to NRM Bridge at {HOST}:{PORT}...")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.settimeout(1.0)
            print("Connected. Starting stream...")

            pattern = generate_sine_wave()
            count = 0
            start_time = time.time()

            # Stream 10 cycles of the wave
            for cycle in range(10):
                print(f"Streaming Cycle {cycle+1}/10...")
                for val in pattern:
                    # Protocol: WR <ADDR> <VALUE>
                    # We are writing to the same address to simulate a FIFO push
                    cmd = f"WR 0x{DATA_ADDR:04X} 0x{val:02X}\n"
                    s.sendall(cmd.encode())
                    
                    # Wait for ACK (OK)
                    response = s.recv(1024).decode().strip()
                    if response != "OK":
                        print(f"Error: Bridge responded with {response}")
                        return

                    count += 1
                    
                    # Rate limiting (optional, to emulate real-time 1kHz)
                    # time.sleep(0.001) 

            duration = time.time() - start_time
            print(f"\nStream Complete.")
            print(f"Sent {count} samples in {duration:.2f} seconds.")
            print(f"Throughput: {count/duration:.2f} samples/sec")
            
            # Final check of status register
            s.sendall(f"RD 0x{CTRL_ADDR:04X}\n".encode())
            status = s.recv(1024).decode().strip()
            print(f"Final Status (Reg 0x{CTRL_ADDR:04X}): {status}")

    except ConnectionRefusedError:
        print("Failed to connect. Is bridge_server running on the DE10-Nano?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    stream_data()
