import os
import imageio.v3 as iio
import numpy as np
from PIL import Image

class VisionBridge:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.export_dir = os.path.join(self.base_dir, "assets", "vision_export")
        os.makedirs(self.export_dir, exist_ok=True)

    def create_contact_sheet(self, frames_dir, num_views=4):
        """
        Creates a 2x2 grid of orthogonal views from the video frames.
        Assumes frames are sorted.
        """
        files = sorted([f for f in os.listdir(frames_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
        if not files:
            return None
            
        total_frames = len(files)
        step = total_frames // num_views
        
        selected_frames = []
        for i in range(num_views):
            idx = min(i * step, total_frames - 1)
            path = os.path.join(frames_dir, files[idx])
            try:
                img = iio.imread(path)
                selected_frames.append(img)
            except Exception as e:
                print(f"Vision Bridge: Failed to load {path}: {e}")
                
        if not selected_frames:
            return None
            
        # Create Grid (2x2)
        # Assuming all frames same size - resize if not
        h, w, c = selected_frames[0].shape
        grid_h = h * 2
        grid_w = w * 2
        
        grid_img = np.zeros((grid_h, grid_w, c), dtype=np.uint8)
        
        # Safe assignment with boundary checks
        try:
            grid_img[0:h, 0:w] = selected_frames[0] # Top Left
            if len(selected_frames) > 1: grid_img[0:h, w:w*2] = selected_frames[1] # Top Right
            if len(selected_frames) > 2: grid_img[h:h*2, 0:w] = selected_frames[2] # Bottom Left
            if len(selected_frames) > 3: grid_img[h:h*2, w:w*2] = selected_frames[3] # Bottom Right
        except Exception as e:
            print(f"Vision Bridge: Grid layout error: {e}")
        
        output_path = os.path.join(self.export_dir, "contact_sheet.jpg")
        iio.imwrite(output_path, grid_img)
        print(f"Vision Bridge: Contact sheet saved to {output_path}")
        return output_path

    def analyze_scene(self, frames_dir):
        """
        Coordinates the visual analysis pipeline:
        1. Generate Contact Sheet
        2. Wait for Pilot Override
        """
        print(f"Vision Bridge: Analyzing scene in {frames_dir}...")
        sheet_path = self.create_contact_sheet(frames_dir)
        if not sheet_path:
            return {}, "Failed to generate contact sheet."
            
        # 1. Pilot Override (Manual Injection)
        # The Pilot (Gemini) sees the contact sheet and writes this file.
        override_path = os.path.join(frames_dir, "pilot_override.json")
        if os.path.exists(override_path):
            try:
                import json
                print(f"Vision Bridge: PILOT OVERRIDE DETECTED at {override_path}")
                with open(override_path, 'r') as f:
                    params = json.load(f)
                print(f"Vision Bridge: Injected Params: {params}")
                reasoning = params.get("reasoning", "Pilot Override Active.")
                return params, reasoning
            except Exception as e:
                print(f"Vision Bridge: Failed to load override: {e}")
        
        # 2. Waiting State
        # We do not guess. We wait for the Pilot.
        print("Vision Bridge: No Override Found. Waiting for Pilot instruction.")
        return {}, "Waiting for Pilot Override..."
