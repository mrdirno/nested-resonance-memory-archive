import os
import sys
import imageio.v3 as iio

def test_video_load():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_path = os.path.join(base_path, "assets", "test_data", "default_subject.mp4")
    
    print(f"Testing video load from: {video_path}")
    
    if not os.path.exists(video_path):
        print("FAIL: Video file not found.")
        sys.exit(1)
        
    try:
        # Read metadata to verify it's a valid video
        meta = iio.imread(video_path, index=0, plugin="pyav") # Attempt to read first frame
        print(f"SUCCESS: Video loaded. First frame shape: {meta.shape}")
        
    except Exception as e:
        print(f"FAIL: Could not read video. Error: {e}")
        # Note: 'pyav' might not be installed, imageio usually falls back or needs ffmpeg.
        # We'll check if basic file IO works if imageio fails, but imageio is in reqs.
        sys.exit(1)

if __name__ == "__main__":
    test_video_load()
