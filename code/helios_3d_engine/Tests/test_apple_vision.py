import Quartz
import Vision
from Cocoa import NSURL

def classify_image(image_path):
    # 1. Load Image URL
    # Ensure absolute path
    abs_path = os.path.abspath(image_path)
    file_url = NSURL.fileURLWithPath_(abs_path)
    
    # 2. Create Request Handler directly from URL
    handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(file_url, {})
    
    # We use the standard classifier
    request = Vision.VNClassifyImageRequest.alloc().init()
    
    # 3. Perform Request
    success, error = handler.performRequests_error_([request], None)
    if not success:
        print(f"Error performing request: {error}")
        return []
        
    # 4. Parse Results
    results = request.results()
    tags = []
    if results:
        # Get top 5 observations
        for obs in results[:5]:
            # obs is VNClassificationObservation
            tags.append((obs.identifier(), obs.confidence()))
            
    return tags

if __name__ == "__main__":
    import sys
    import os
    
    # Create a dummy image if none exists
    test_img = "test_vision.jpg"
    if not os.path.exists(test_img):
        # Create simple red square using PIL
        try:
            from PIL import Image
            img = Image.new('RGB', (224, 224), color = 'red')
            img.save(test_img)
            created = True
        except ImportError:
            print("PIL not found, cannot create test image.")
            sys.exit(1)
    else:
        created = False
        
    print(f"Analyzing {test_img}...")
    try:
        tags = classify_image(test_img)
        for tag, conf in tags:
            print(f"  {tag}: {conf:.2f}")
    except Exception as e:
        print(f"Crash: {e}")
        
    if created:
        os.remove(test_img)
