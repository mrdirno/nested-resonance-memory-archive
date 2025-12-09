import torch
import sys

def check_sam2_readiness():
    print(f"Python: {sys.version}")
    print(f"PyTorch: {torch.__version__}")
    
    mps_available = torch.backends.mps.is_available()
    print(f"MPS Available: {mps_available}")
    
    if mps_available:
        device = torch.device("mps")
        x = torch.ones(5, device=device)
        print(f"Tensor on MPS: {x}")
    else:
        print("WARNING: MPS not available. SAM 2 will be slow on CPU.")

if __name__ == "__main__":
    check_sam2_readiness()
