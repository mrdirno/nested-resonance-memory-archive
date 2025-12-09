import numpy as np

class AIGenerator:
    def __init__(self):
        pass
        
    def generate_from_text(self, prompt):
        """
        Parses a text prompt and returns SDF parameters for the Helios Engine.
        In Phase 6, this will connect to an LLM/Shap-E.
        For now, it uses keyword matching.
        """
        prompt = prompt.lower()
        params = {
            'type': 'gyroid',
            'scale': 1.0,
            'thickness': 0.1,
            'bias': 0.0
        }
        
        if 'sphere' in prompt:
            params['type'] = 'sphere'
        elif 'cube' in prompt:
            params['type'] = 'cube'
        elif 'gyroid' in prompt:
            params['type'] = 'gyroid'
            
        if 'large' in prompt:
            params['scale'] = 2.0
        elif 'small' in prompt:
            params['scale'] = 0.5
            
        if 'thick' in prompt:
            params['thickness'] = 0.3
        elif 'thin' in prompt:
            params['thickness'] = 0.05
            
        return params
