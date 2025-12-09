import torch
import os
import numpy as np
import imageio.v3 as iio
from sam2.build_sam import build_sam2_video_predictor
from PySide6.QtCore import QObject, Signal, QThread

class SegmentationWorker(QThread):
    # Signal: mask_data (numpy array of shape HxW), frame_idx
    mask_ready = Signal(object, int)
    
    def __init__(self, predictor, inference_state, points, labels, frame_idx):
        super().__init__()
        self.predictor = predictor
        self.inference_state = inference_state
        self.points = points
        self.labels = labels
        self.frame_idx = frame_idx
        
    def run(self):
        # Add new point
        _, out_obj_ids, out_mask_logits = self.predictor.add_new_points_or_box(
            inference_state=self.inference_state,
            frame_idx=self.frame_idx,
            obj_id=1,
            points=self.points,
            labels=self.labels,
        )
        
        # Propagate forward (just a few frames for immediate feedback, 
        # full propagation should be a separate heavy task)
        # For now, let's just return the mask for THIS frame to be responsive
        
        # SAM 2 returns logits (1, H, W). We want binary mask.
        mask = (out_mask_logits[1] > 0.0).cpu().numpy().squeeze()
        self.mask_ready.emit(mask, self.frame_idx)


class SegmentationEngine(QObject):
    model_loaded = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.predictor = None
        self.inference_state = None
        self.is_ready = False
        self.frames_dir = None
        
        # Paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_dir = os.path.join(self.base_dir, "assets", "models")
        self.checkpoint_path = os.path.join(self.model_dir, "sam2_hiera_tiny.pt")
        self.model_cfg = "sam2_hiera_t.yaml"

    def initialize(self, frames_dir):
        """Loads the model and initializes state with the video frames."""
        self.frames_dir = frames_dir
        
        if not os.path.exists(self.checkpoint_path):
            print("SAM 2 Checkpoint not found.")
            self.model_loaded.emit(False)
            return

        try:
            print("Loading SAM 2 Model on MPS...")
            device = "mps" if torch.backends.mps.is_available() else "cpu"
            self.predictor = build_sam2_video_predictor(self.model_cfg, self.checkpoint_path, device=device)
            
            print(f"Initializing state with frames from: {frames_dir}")
            self.inference_state = self.predictor.init_state(video_path=frames_dir)
            self.is_ready = True
            self.model_loaded.emit(True)
            print("SAM 2 Ready.")
            
        except Exception as e:
            print(f"Failed to init SAM 2: {e}")
            import traceback
            traceback.print_exc()
            self.model_loaded.emit(False)

    def add_click(self, x, y, frame_idx):
        """Async click processing."""
        if not self.is_ready:
            return None
            
        points = torch.tensor([[x, y]], dtype=torch.float32)
        labels = torch.tensor([1], dtype=torch.int32) # Positive click
        
        worker = SegmentationWorker(self.predictor, self.inference_state, points, labels, frame_idx)
        return worker

    def propagate_all(self):
        """Propagates the mask through the entire video."""
        if not self.is_ready or not self.inference_state:
            return None
            
        print("Propagating masks through video...")
        masks = []
        
        # propagate_in_video yields (frame_idx, obj_ids, mask_logits)
        for out_frame_idx, out_obj_ids, out_mask_logits in self.predictor.propagate_in_video(self.inference_state):
             # Logits to binary mask (take first object)
             # Shape: (1, H, W)
             mask = (out_mask_logits[0] > 0.0).float()
             masks.append(mask)
             
        # Stack into (F, H, W) tensor
        if masks:
            full_mask_tensor = torch.stack(masks).squeeze(1)
            print(f"Propagation complete. Shape: {full_mask_tensor.shape}")
            return full_mask_tensor
        return None
