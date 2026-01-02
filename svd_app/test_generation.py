import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video
from PIL import Image
import os
import sys

# Configuration
MODEL_ID_14 = "stabilityai/stable-video-diffusion-img2vid"
MODEL_ID_XT = "stabilityai/stable-video-diffusion-img2vid-xt-1-1"
TOKEN = "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"

def run_test(model_id=MODEL_ID_14, decode_chunk_size=1, height=512, width=512):
    print(f"\n--- Testing Configuration ---")
    print(f"Model: {model_id}")
    print(f"Chunk Size: {decode_chunk_size}")
    print(f"Resolution: {width}x{height}")
    
    try:
        # Load Pipeline
        print("Loading pipeline...")
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            model_id, 
            torch_dtype=torch.float16, 
            variant="fp16", 
            use_safetensors=True,
            token=TOKEN
        )
        
        # MPS Optimization
        if torch.backends.mps.is_available():
            device = "mps"
            print("Using MPS device.")
        else:
            device = "cpu"
            print("Using CPU.")

        pipe.to(device)
        
        # Enable Sequential Offload (Critical for Mac)
        print("Enabling sequential cpu offload...")
        pipe.enable_sequential_cpu_offload()
        
        # Load Image
        image = Image.open("test_input.png").resize((width, height))
        
        # Generate
        print("Starting generation...")
        generator = torch.manual_seed(42)
        frames = pipe(
            image, 
            decode_chunk_size=decode_chunk_size,
            generator=generator,
            motion_bucket_id=127, 
            noise_aug_strength=0.1,
            num_inference_steps=10 # Reduced for speed testing
        ).frames[0]
        
        output_path = f"test_output_{width}x{height}.mp4"
        export_to_video(frames, output_path, fps=7)
        print(f"SUCCESS! Video saved to {output_path}")
        return True

    except Exception as e:
        print(f"FAILURE: {e}")
        return False

if __name__ == "__main__":
    # Test 1: SVD 14-frame, 512x512, chunk=1 (Most conservative)
    success = run_test(MODEL_ID_14, decode_chunk_size=1, height=512, width=512)
    
    if not success:
        print("\nRetrying with even stricter settings...")
        # Test 2: If that failed, maybe try even smaller resolution? 
        # But 512 is standard. 
        # We might need to force VAE to CPU if MPS fails.
