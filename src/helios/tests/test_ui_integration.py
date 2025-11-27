"""
Integration Test: UI -> API -> Fabricator (Gate 5.3)
Simulates a user uploading a file via the API and checks if the Fabricator received it.

Principle: PRIN-INTEGRATION
Author: MOG (Cycle 2354)
"""

import unittest
import time
import threading
import os
import requests
from werkzeug.datastructures import FileStorage

# Start the server in a separate thread
def start_server():
    # This is a hack for testing. In production, use a proper test client.
    os.system("python3 src/helios/bridge_api.py &")
    time.sleep(2) # Wait for boot

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server_process = threading.Thread(target=start_server)
        cls.server_process.start()
        cls.api_url = "http://localhost:5001"

    @classmethod
    def tearDownClass(cls):
        os.system("pkill -f bridge_api.py")

    def test_status_endpoint(self):
        try:
            response = requests.get(f"{self.api_url}/status")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIn("connected", data)
            print("\n[TEST] Status Check Passed.")
        except requests.exceptions.ConnectionError:
            self.fail("API Server not reachable.")

    def test_fabrication_flow(self):
        # Create dummy obj
        with open("test_triangle.obj", "w") as f:
            f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3")

        files = {'file': open('test_triangle.obj', 'rb')}
        data = {'material': 'AIR_STP', 'duration': 1}
        
        try:
            response = requests.post(f"{self.api_url}/fabricate", files=files, data=data)
            self.assertEqual(response.status_code, 200)
            res_data = response.json()
            self.assertEqual(res_data["status"], "success")
            print(f"\n[TEST] Fabrication Triggered: {res_data['message']}")
        except Exception as e:
            self.fail(f"Fabrication request failed: {e}")
        finally:
            files['file'].close()
            os.remove("test_triangle.obj")

if __name__ == "__main__":
    unittest.main()
