import torch
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import export_to_video
from PIL import Image

# Configuration
MODEL_ID = "stabilityai/stable-video-diffusion-img2vid"
TOKEN = "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"

def run_cpu_test():
    print("--- Testing CPU Execution (Slow but Safe) ---")
    
    # Load Pipeline on CPU
    pipe = StableVideoDiffusionPipeline.from_pretrained(
        MODEL_ID, 
        torch_dtype=torch.float32, # CPU usually prefers fp32
        variant=None, 
        use_safetensors=True,
        token=TOKEN
    )
    pipe.to("cpu")
    
    # Optimization: Sequential Offload still useful to keep peak RAM down? 
    # Actually, if we are on CPU, we rely on system RAM.
    # pipe.enable_sequential_cpu_offload() # Not needed if we just use RAM
    
    image = Image.open("test_input.png").resize((512, 512))
    
    print("Generating on CPU (this might take 5-10 mins)...")
    generator = torch.manual_seed(42)
    frames = pipe(
        image, 
        decode_chunk_size=1,
        generator=generator,
        num_inference_steps=5, # Minimal steps just to prove it works
    ).frames[0]
    
    export_to_video(frames, "test_output_cpu.mp4", fps=7)
    print("SUCCESS: CPU Generation complete.")

if __name__ == "__main__":
    run_cpu_test()
