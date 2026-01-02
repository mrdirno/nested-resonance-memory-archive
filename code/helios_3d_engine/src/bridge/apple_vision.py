import os
import Vision
from Cocoa import NSURL

class AppleVisionAnalyzer:
    """
    Provides local, offline image classification using macOS Vision Framework.
    """
    
    def __init__(self):
        self.request = Vision.VNClassifyImageRequest.alloc().init()
        
    def analyze_image(self, image_path):
        """
        Returns a list of (tag, confidence) tuples for the given image.
        """
        if not os.path.exists(image_path):
            print(f"AppleVision: Image not found at {image_path}")
            return []
            
        abs_path = os.path.abspath(image_path)
        file_url = NSURL.fileURLWithPath_(abs_path)
        
        handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(file_url, {})
        
        success, error = handler.performRequests_error_([self.request], None)
        if not success:
            print(f"AppleVision Error: {error}")
            return []
            
        results = self.request.results()
        tags = []
        if results:
            for obs in results[:10]: # Top 10
                tags.append((obs.identifier(), obs.confidence()))
                
        return tags

    def get_semantic_params(self, image_path):
        """
        Maps visual tags to Helios Simulation Parameters.
        Returns: (params_dict, reasoning_string)
        """
        tags = self.analyze_image(image_path)
        print(f"AppleVision Tags: {tags}")
        
        params = {}
        reasoning_parts = []
        
        # Semantic Mapping Logic
        # This is where we "Reason" based on labels
        
        is_organic = False
        is_structural = False
        is_tool = False
        
        # Top 3 tags for display
        top_tags = [t[0] for t in tags[:3]]
        reasoning_parts.append(f"Visuals: {', '.join(top_tags)}")
        
        for tag, conf in tags:
            t = tag.lower()
            if any(x in t for x in ['plant', 'animal', 'flower', 'organic', 'leaf', 'organism']):
                is_organic = True
            if any(x in t for x in ['building', 'architecture', 'structure', 'house', 'furniture']):
                is_structural = True
            if any(x in t for x in ['tool', 'device', 'machine', 'electronics']):
                is_tool = True
                
        # Apply Logic
        if is_organic:
            params['gyroid_type'] = 'gyroid' # Smooth
            params['concavity'] = 0.8
            params['scale'] = 1.5
            reasoning_parts.append("-> Organic Logic (Smooth Gyroid)")
            
        elif is_structural:
            params['gyroid_type'] = 'schwarz_p' # Blocky
            params['concavity'] = 0.2
            params['scale'] = 2.5
            reasoning_parts.append("-> Structural Logic (Schwarz P)")
            
        elif is_tool:
            params['gyroid_type'] = 'schwarz_d' # Diamond
            params['concavity'] = 0.5
            params['scale'] = 1.0
            reasoning_parts.append("-> Tool Logic (Schwarz D)")
        
        # Default fallback if ambiguous
        if not params:
            params['gyroid_type'] = 'gyroid'
            params['scale'] = 1.0
            reasoning_parts.append("-> Ambiguous (Default Gyroid)")
            
        return params, " ".join(reasoning_parts)
