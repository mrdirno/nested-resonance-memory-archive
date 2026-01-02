import torch
import gradio as gr
from diffusers import StableVideoDiffusionPipeline
from diffusers.utils import load_image, export_to_video
from PIL import Image
from huggingface_hub import login
import os
import uuid
import sys

# --- Configuration ---
MODELS = {
    "SVD-XT (25 frames) - High Memory": "stabilityai/stable-video-diffusion-img2vid-xt-1-1",
    "SVD (14 frames) - Low Memory": "stabilityai/stable-video-diffusion-img2vid",
}
OUTPUT_DIR = "generated_videos"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Global State
pipe = None
load_error = None
current_model_id = None

# --- Helper: Device Selection ---
def get_device_config():
    if torch.cuda.is_available():
        return "cuda", torch.float16, "fp16"
    elif torch.backends.mps.is_available():
        return "mps", torch.float16, "fp16" # MPS supports fp16
    else:
        return "cpu", torch.float32, None

# --- Model Loading Logic ---
def load_model(model_selection, token=None):
    global pipe, load_error, current_model_id
    
    target_model_id = MODELS[model_selection]
    
    # Avoid reloading if already loaded
    if pipe is not None and current_model_id == target_model_id:
        return f"Model {target_model_id} already loaded."

    print(f"Attempting to load model: {target_model_id}...", flush=True)
    
    # Authenticate if token is provided
    if token and token.strip():
        print("Token provided. Authenticating...", flush=True)
        try:
            login(token=token.strip())
            print("Authentication successful.", flush=True)
        except Exception as e:
            print(f"Authentication warning: {e}", flush=True)
    
    device, dtype, variant = get_device_config()
    print(f"Device: {device}, Dtype: {dtype}, Variant: {variant}", flush=True)

    try:
        # If token is provided, pass it. Otherwise use cached/env token.
        kwargs = {}
        if token and token.strip():
            kwargs["token"] = token.strip()
            
        pipe = StableVideoDiffusionPipeline.from_pretrained(
            target_model_id, 
            torch_dtype=dtype, 
            variant=variant, 
            use_safetensors=True,
            **kwargs
        )
        pipe.to(device)
        
        # Optimization 1: Sequential CPU Offload (Saves VRAM)
        try:
            pipe.enable_sequential_cpu_offload()
            print("Enabled sequential CPU offload.", flush=True)
        except Exception as offload_err:
            print(f"Could not enable sequential offload: {offload_err}", flush=True)
            pipe.enable_attention_slicing()

        # Optimization 2: Force VAE to float32 (Fixes MPS 16-bit Buffer Limit)
        # MPS often fails with >4GB allocations in fp16, but fp32 is sometimes handled better or falls back to CPU cleanly.
        try:
            pipe.vae.to(dtype=torch.float32)
            print("Forced VAE to float32 for stability.", flush=True)
        except Exception as vae_err:
            print(f"Could not cast VAE to float32: {vae_err}", flush=True)

        current_model_id = target_model_id
        load_error = None
        print("Model loaded successfully.", flush=True)
        return f"Success: Loaded {target_model_id}"
    except Exception as e:
        load_error = str(e)
        print(f"Error loading model: {e}", flush=True)
        return f"Error: {e}"

# Attempt initial load (Default to XT)
initial_model_key = "SVD-XT (25 frames) - High Memory"
load_model(initial_model_key, token="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")

# --- Helper Functions ---

def resize_image_for_model(image: Image.Image, strict_division=64):
    width, height = image.size
    
    # Cap max dimension to 576 (Base resolution for SVD) to prevent memory explosion on Mac
    # SVD native is 1024x576 or 576x1024. Sticking closer to 576 helps a lot.
    max_dim = 768
    if width > max_dim or height > max_dim:
        scale = max_dim / max(width, height)
        width = int(width * scale)
        height = int(height * scale)
        print(f"Downscaling input to ({width}, {height}) for memory safety.", flush=True)
        image = image.resize((width, height), Image.LANCZOS)

    new_width = (width // strict_division) * strict_division
    new_height = (height // strict_division) * strict_division
    
    if new_width < 512 or new_height < 512:
        scale = 512 / min(new_width, new_height)
        new_width = int((new_width * scale) // strict_division) * strict_division
        new_height = int((new_height * scale) // strict_division) * strict_division

    if new_width != width or new_height != height:
        print(f"Resizing image from ({width}, {height}) to ({new_width}, {new_height})", flush=True)
        image = image.resize((new_width, new_height), Image.LANCZOS)
    
    return image

def generate_video(image, prompt, negative_prompt, motion_bucket_id, noise_aug_strength, fps):
    global pipe
    if pipe is None:
        raise gr.Error(f"Model not loaded. Error: {load_error}")

    if image is None:
        raise gr.Error("Please upload an image.")

    print(f"Generating video...", flush=True)
    
    try:
        input_image = resize_image_for_model(Image.fromarray(image))
        generator = torch.manual_seed(42)

        # Extreme Memory Optimization: Decode Chunk Size = 1
        # This decodes 1 frame at a time.
        frames = pipe(
            input_image, 
            decode_chunk_size=1,
            generator=generator,
            motion_bucket_id=motion_bucket_id,
            noise_aug_strength=noise_aug_strength,
            num_inference_steps=20, # Reduced steps slightly for speed/stability
        ).frames[0]


        unique_filename = f"{uuid.uuid4()}.mp4"
        output_path = os.path.join(OUTPUT_DIR, unique_filename)
        export_to_video(frames, output_path, fps=fps)
        
        print(f"Video saved to {output_path}", flush=True)
        return output_path
    except Exception as e:
        print(f"Generation Error: {e}", flush=True)
        raise gr.Error(f"Generation failed: {e}")

# --- UI Layout ---

with gr.Blocks(title="SVD-XT Standalone") as demo:
    gr.Markdown("# 🎥 Stable Video Diffusion (SVD-XT) Standalone UI")
    
    # Status Block
    with gr.Row():
        status_box = gr.Textbox(label="Model Status", value="Checking...", interactive=False)
    
    # Auth / Reload Block
    with gr.Row(visible=True) as auth_row:
        model_dropdown = gr.Dropdown(
            label="Select Model", 
            choices=list(MODELS.keys()), 
            value=initial_model_key,
            interactive=True
        )
        token_input = gr.Textbox(label="Hugging Face Token (Optional if saved)", type="password", value="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")
        load_btn = gr.Button("Load / Reload Model")

    def update_status():
        if pipe is not None:
            return f"Loaded: {current_model_id} ✅"
        else:
            return f"Model Not Loaded ❌. Error: {load_error}"

    load_btn.click(fn=load_model, inputs=[model_dropdown, token_input], outputs=[status_box])
    demo.load(fn=update_status, inputs=None, outputs=[status_box])

    # Main Interface
    with gr.Row():
        with gr.Column():
            image_input = gr.Image(label="Upload Input Image")
            prompt_input = gr.Textbox(label="Prompt (Intent)", value="Cinematic motion")
            neg_prompt_input = gr.Textbox(label="Negative Prompt", value="low quality, artifacts")
            
            with gr.Accordion("Advanced Settings", open=False):
                motion_bucket = gr.Slider(1, 255, 127, step=1, label="Motion Bucket ID")
                noise_aug = gr.Slider(0.0, 1.0, 0.02, step=0.01, label="Noise Augmentation")
                fps_slider = gr.Slider(5, 30, 7, step=1, label="FPS")

            generate_btn = gr.Button("Generate Video", variant="primary")

        with gr.Column():
            video_output = gr.Video(label="Generated Video")

    generate_btn.click(
        fn=generate_video,
        inputs=[image_input, prompt_input, neg_prompt_input, motion_bucket, noise_aug, fps_slider],
        outputs=video_output
    )

if __name__ == "__main__":
    demo.queue().launch(share=False, inbrowser=True)