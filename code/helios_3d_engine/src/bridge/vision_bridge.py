import os
import imageio.v3 as iio
import numpy as np
from PIL import Image

# Try to import local Apple Vision bridge
try:
    from src.bridge.apple_vision import AppleVisionAnalyzer
    HAS_APPLE_VISION = True
except ImportError:
    print("Vision Bridge: Apple Vision Framework not available (Not on macOS?). Using Mock.")
    HAS_APPLE_VISION = False

class VisionBridge:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.export_dir = os.path.join(self.base_dir, "assets", "vision_export")
        os.makedirs(self.export_dir, exist_ok=True)
        
        if HAS_APPLE_VISION:
            self.local_eye = AppleVisionAnalyzer()

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
        2. Send to Vision Model (Gemini)
        3. Parse Parameters
        """
        print(f"Vision Bridge: Analyzing scene in {frames_dir}...")
        sheet_path = self.create_contact_sheet(frames_dir)
        if not sheet_path:
            return {}
            
        # 1. Pilot Override (Manual Injection)
        # If I (The Pilot) have placed a JSON file here, use it.
        override_path = os.path.join(frames_dir, "pilot_override.json")
        if os.path.exists(override_path):
            try:
                import json
                print(f"Vision Bridge: PILOT OVERRIDE DETECTED at {override_path}")
                with open(override_path, 'r') as f:
                    params = json.load(f)
                print(f"Vision Bridge: Injected Params: {params}")
                return params
            except Exception as e:
                print(f"Vision Bridge: Failed to load override: {e}")
        
        # 2. Local Apple Vision (The Local Eye)
        if HAS_APPLE_VISION:
            print("Vision Bridge: Invoking 'The Local Eye' (Apple Vision Framework)...")
            try:
                params = self.local_eye.get_semantic_params(sheet_path)
                print(f"Vision Bridge: Local Inference Params: {params}")
                return params
            except Exception as e:
                print(f"Vision Bridge: Local Eye Failed ({e}). Falling back to mock.")
        
        # 3. Mock Inference (Prototype)
        # For prototype/offline, we use mock inference
        response_text = self._mock_inference(sheet_path)
        
        params = self.parse_gemini_response(response_text)
        print(f"Vision Bridge: Inferred Params: {params}")
        return params

    def _mock_inference(self, image_path):
        """
        Simulates a Vision API response based on simple file heuristics 
        or random variation for testing UI feedback.
        """
        # In a real scenario, this sends the image to Gemini 1.5 Flash
        # and asks: "Analyze this object. Suggest Gyroid parameters."
        
        # Mock logic:
        import random
        styles = [
            "The object appears to be organic and curved. Suggesting concave gyroid structure.",
            "The object is tall and geometric. Suggesting vertical scaling.",
            "The object is dense and blocky. Suggesting wide scale."
        ]
        return random.choice(styles)

    def parse_gemini_response(self, response_text):
        """
        Parses structured text from Gemini into simulation parameters.
        Expected format: JSON or Key-Value lines.
        """
        # Placeholder: Simple keyword matching
        params = {}
        text = response_text.lower()
        
        if "concave" in text or "organic" in text:
            params['concavity'] = 0.5
            params['gyroid_type'] = 'gyroid'
        
        if "tall" in text or "vertical" in text:
            params['scale_y'] = 1.5
            params['scale'] = 2.5
            
        if "wide" in text or "blocky" in text:
            params['scale_x'] = 1.5
            params['scale'] = 1.2
            
        return params
