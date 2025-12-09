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
        files = sorted([f for f in os.listdir(frames_dir) if f.endswith('.jpg')])
        if not files:
            return None
            
        total_frames = len(files)
        step = total_frames // num_views
        
        selected_frames = []
        for i in range(num_views):
            idx = min(i * step, total_frames - 1)
            path = os.path.join(frames_dir, files[idx])
            selected_frames.append(iio.imread(path))
            
        # Create Grid (2x2)
        # Assuming all frames same size
        h, w, c = selected_frames[0].shape
        grid_h = h * 2
        grid_w = w * 2
        
        grid_img = np.zeros((grid_h, grid_w, c), dtype=np.uint8)
        
        grid_img[0:h, 0:w] = selected_frames[0] # Top Left
        grid_img[0:h, w:w*2] = selected_frames[1] # Top Right
        grid_img[h:h*2, 0:w] = selected_frames[2] # Bottom Left
        grid_img[h:h*2, w:w*2] = selected_frames[3] # Bottom Right
        
        output_path = os.path.join(self.export_dir, "contact_sheet.jpg")
        iio.imwrite(output_path, grid_img)
        print(f"Vision Bridge: Contact sheet saved to {output_path}")
        return output_path

    def parse_gemini_response(self, response_text):
        """
        Parses structured text from Gemini into simulation parameters.
        Expected format: JSON or Key-Value lines.
        """
        # Placeholder: Simple keyword matching
        params = {}
        if "concave" in response_text.lower():
            params['concavity'] = 0.5
        if "tall" in response_text.lower():
            params['scale_y'] = 1.5
        if "wide" in response_text.lower():
            params['scale_x'] = 1.5
            
        return params
