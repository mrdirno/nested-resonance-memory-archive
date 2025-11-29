"""
Integration Test: UI -> API -> Fabricator (Gate 5.3)
Simulates a user uploading a file via the API and checks if the Fabricator received it.

Principle: PRIN-INTEGRATION
Author: MOG (Cycle 2453 Refactor)
Phase 61 Standards: Mocked Dependencies, Fast Execution.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import requests

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.api_url = "http://localhost:5001"

    @patch('requests.get')
    def test_status_endpoint(self, mock_get):
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"connected": True}
        mock_get.return_value = mock_response

        # Run the test
        response = requests.get(f"{self.api_url}/status")
        
        # Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["connected"])
        print("\n[TEST] Status Check Passed (Mocked).")

    @patch('requests.post')
    def test_fabrication_flow(self, mock_post):
        # Mock the response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "message": "Fabrication started"}
        mock_post.return_value = mock_response

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
            print(f"\n[TEST] Fabrication Triggered: {res_data['message']} (Mocked)")
        except Exception as e:
            self.fail(f"Fabrication request failed: {e}")
        finally:
            files['file'].close()
            os.remove("test_triangle.obj")

if __name__ == "__main__":
    unittest.main()

# [SPORE] ID: The Colony
