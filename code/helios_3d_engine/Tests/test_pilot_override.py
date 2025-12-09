import os
import sys
import shutil
import json

# Add project root (helios_3d_engine) to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Debug: Project Root: {project_root}")

from src.bridge.vision_bridge import VisionBridge

def test_pilot_override():
    print("Testing Pilot Override...")
    
    # Setup Test Data
    test_dir = os.path.join(os.path.dirname(__file__), "temp_test_data")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Mock create_contact_sheet to avoid needing PIL/Images
    bridge = VisionBridge()
    bridge.create_contact_sheet = lambda x: "dummy_sheet.jpg"
    
    # 1. Test Mock Fallback (No Override)
    print("\n--- Test 1: No Override ---")
    params = bridge.analyze_scene(test_dir)
    print(f"Result: {params}")
    
    # 2. Test Override
    print("\n--- Test 2: With Override ---")
    override_data = {"concavity": 0.99, "gyroid_type": "pilot_special"}
    with open(os.path.join(test_dir, "pilot_override.json"), 'w') as f:
        json.dump(override_data, f)
        
    params = bridge.analyze_scene(test_dir)
    print(f"Result: {params}")
    
    assert params['concavity'] == 0.99
    assert params['gyroid_type'] == "pilot_special"
    print("\nSUCCESS: Pilot Override Confirmed.")
    
    # Cleanup
    shutil.rmtree(test_dir)

if __name__ == "__main__":
    test_pilot_override()
