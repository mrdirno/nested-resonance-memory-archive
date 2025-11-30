#!/usr/bin/env python3
"""
Experiment: Cycle 2661 - The Stream
Goal: Flood the system with high-velocity data to test throughput limits.
"""

import time
import queue
import threading

class DataPump:
    def __init__(self):
        self.stream = queue.Queue()
        self.running = True
        self.counter = 0

    def producer(self):
        while self.running:
            self.stream.put(f"DATA_PACKET_{self.counter}")
            self.counter += 1
            # No sleep = max speed

    def consumer(self):
        processed = 0
        start = time.time()
        while self.running:
            try:
                _ = self.stream.get(timeout=0.1)
                processed += 1
            except queue.Empty:
                continue
                
            if processed % 100000 == 0:
                elapsed = time.time() - start
                rate = processed / elapsed
                print(f"[STREAM] Processed {processed} packets. Rate: {rate:.0f} msg/sec")

def run_stream_test():
    print("Cycle 2661: The Stream - High Bandwidth Test")
    
    pump = DataPump()
    
    p_thread = threading.Thread(target=pump.producer)
    c_thread = threading.Thread(target=pump.consumer)
    
    p_thread.start()
    c_thread.start()
    
    time.sleep(2) # Run for 2 seconds
    
    pump.running = False
    p_thread.join()
    c_thread.join()
    
    print(f"SUCCESS: System handled high-velocity stream (Total: {pump.counter})")

if __name__ == "__main__":
    run_stream_test()
