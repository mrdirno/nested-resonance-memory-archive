import os
import cv2
import numpy as np
from PIL import Image

def process_video():
    video_path = "code/helios_3d_engine/assets/test_data/subject.mp4"
    frames_dir = "code/helios_3d_engine/assets/test_data/frames_subject"
    
    if os.path.exists(frames_dir):
        import shutil
        shutil.rmtree(frames_dir)
    os.makedirs(frames_dir)
    
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Processing {total_frames} frames from {video_path}...")
    
    # Extract 4 equidistant frames
    indices = [0, total_frames // 4, total_frames // 2, (total_frames * 3) // 4]
    saved_frames = []
    
    for i, idx in enumerate(indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out_path = os.path.join(frames_dir, f"frame_{i}.jpg")
            img = Image.fromarray(frame)
            img = img.resize((512, 512)) # Standardize
            img.save(out_path)
            saved_frames.append(np.array(img))
            print(f"Saved {out_path}")
            
    cap.release()
    
    # Generate Contact Sheet
    if len(saved_frames) == 4:
        top = np.hstack((saved_frames[0], saved_frames[1]))
        bottom = np.hstack((saved_frames[2], saved_frames[3]))
        sheet = np.vstack((top, bottom))
        
        sheet_path = "code/helios_3d_engine/assets/vision_export/contact_sheet_subject.jpg"
        Image.fromarray(sheet).save(sheet_path)
        print(f"Contact Sheet Saved: {sheet_path}")

if __name__ == "__main__":
    process_video()
