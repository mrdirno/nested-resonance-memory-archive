from huggingface_hub import snapshot_download, login
import os

TOKEN = "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"
MODEL_ID = "stabilityai/stable-video-diffusion-img2vid-xt-1-1"

print(f"Logging in with token {TOKEN[:5]}...")
login(token=TOKEN)

print(f"Downloading {MODEL_ID}...")
snapshot_download(repo_id=MODEL_ID, allow_patterns=["*.fp16.safetensors", "*.json", "*.txt"])
print("Download complete.")
