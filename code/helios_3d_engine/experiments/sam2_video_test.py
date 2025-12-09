import torch
import os
import shutil
import imageio.v3 as iio
from sam2.build_sam import build_sam2_video_predictor

def extract_frames(video_path, output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    print(f"Reading video from {video_path}")
    try:
        # Read all frames (memory intensive but fine for short clips)
        # Using index=None reads all frames
        frames = iio.imread(video_path, plugin="pyav", index=None)
        
        print(f"Video loaded. Shape: {frames.shape}")
        
        for i, frame in enumerate(frames):
             # Save as JPEG using imageio
             iio.imwrite(os.path.join(output_dir, f"{i:05d}.jpg"), frame, plugin="pillow")
             
        print(f"Extracted {len(frames)} frames to {output_dir}")
        
    except Exception as e:
        print(f"Frame extraction failed: {e}")
        import traceback
        traceback.print_exc()

def test_sam2_video():
    # 1. Setup
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_path = os.path.join(base_dir, "assets", "test_data", "default_subject.mp4")
    frame_dir = os.path.join(base_dir, "assets", "test_data", "frames")
    model_dir = os.path.join(base_dir, "assets", "models")
    checkpoint_path = os.path.join(model_dir, "sam2_hiera_tiny.pt")
    model_cfg = "sam2_hiera_t.yaml"
    
    # 2. Extract Frames
    print("Extracting frames...")
    extract_frames(video_path, frame_dir)
    
    # 3. Load Video Predictor
    print("Loading SAM 2 Video Predictor...")
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    try:
        predictor = build_sam2_video_predictor(model_cfg, checkpoint_path, device=device)
        
        # 4. Init State
        print("Initializing Inference State...")
        inference_state = predictor.init_state(video_path=frame_dir)
        
        # 5. Add Click (Center of first frame)
        # Assuming 1280x720, center is 640, 360
        print("Adding point click...")
        ann_frame_idx = 0
        ann_obj_id = 1
        points = torch.tensor([[640, 360]], dtype=torch.float32)
        labels = torch.tensor([1], dtype=torch.int32) # 1 = positive click
        
        _, out_obj_ids, out_mask_logits = predictor.add_new_points_or_box(
            inference_state=inference_state,
            frame_idx=ann_frame_idx,
            obj_id=ann_obj_id,
            points=points,
            labels=labels,
        )
        
        # 6. Propagate
        print("Propagating mask...")
        # Propagate through first 10 frames for testing
        count = 0
        for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(inference_state):
            count += 1
            if count >= 10:
                break
        
        print(f"Propagation successful for {count} frames.")
        
    except Exception as e:
        print(f"Video Inference Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sam2_video()
