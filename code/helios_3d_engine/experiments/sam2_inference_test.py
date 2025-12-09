import torch
import os
import urllib.request
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
import numpy as np

def test_sam2_inference():
    # 1. Setup Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.join(base_dir, "assets", "models")
    os.makedirs(model_dir, exist_ok=True)
    
    checkpoint_name = "sam2_hiera_tiny.pt"
    checkpoint_path = os.path.join(model_dir, checkpoint_name)
    model_cfg = "sam2_hiera_t.yaml" # Config file name in the package
    
    # 2. Download Checkpoint
    url = "https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_tiny.pt"
    if not os.path.exists(checkpoint_path):
        print(f"Downloading {checkpoint_name}...")
        try:
            urllib.request.urlretrieve(url, checkpoint_path)
            print("Download complete.")
        except Exception as e:
            print(f"Failed to download checkpoint: {e}")
            return

    # 3. Load Model
    print("Loading SAM 2 Model...")
    try:
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Note: build_sam2 expects the config file to be reachable. 
        # The pip install typically bundles configs.
        predictor = SAM2ImagePredictor(build_sam2(model_cfg, checkpoint_path, device=device))
        print("Model loaded successfully.")
        
    except Exception as e:
        print(f"Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Dummy Inference
    print("Running Dummy Inference...")
    try:
        # Create a fake image (H, W, 3)
        image = np.zeros((512, 512, 3), dtype=np.uint8)
        predictor.set_image(image)
        
        # Point prompt (x, y)
        input_point = np.array([[256, 256]])
        input_label = np.array([1])
        
        masks, scores, logits = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True,
        )
        print(f"Inference Successful. Mask Shape: {masks.shape}")
        
    except Exception as e:
        print(f"Inference Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sam2_inference()
