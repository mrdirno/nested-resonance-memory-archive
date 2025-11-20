"""
Principle Card Definition: Standing Wave Physics
"""

import json
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

from code.tsf.core.principle_card import PrincipleCard
from code.tsf.core.principles.standing_wave import StandingWaveExpandingUniverse

def create_card():
    card = PrincipleCard(
        id="PRIN-001-STANDING-WAVE",
        title="Standing Wave Physics in Expanding Universe",
        domain="Cosmology / Wave Mechanics",
        status="Draft",
        claim_falsifiable="Standing waves in an expanding universe exhibit amplitude decay and frequency redshift proportional to the scale factor, with specific horizon crossing signatures.",
        
        discovery_protocol={
            "module": "code.tsf.core.principles.standing_wave",
            "class": "StandingWaveExpandingUniverse",
            "method": "evolve_standing_wave",
            "parameters": {
                "frequency_range": [1e-18, 1e-12],
                "redshift_range": [1100, 0]
            }
        },
        
        refutation_protocol={
            "method": "compare_with_cmb_power_spectrum",
            "threshold": 0.05 # 5% deviation allowed
        },
        
        safety={
            "no_network_required": True,
            "overhead_auth_pass": True,
            "resource_class": "Low-Compute"
        }
    )
    
    return card

if __name__ == "__main__":
    card = create_card()
    
    # Ensure library directory exists
    library_path = os.path.join(os.path.dirname(__file__), '../../library')
    os.makedirs(library_path, exist_ok=True)
    
    output_file = os.path.join(library_path, 'standing_wave_physics.json')
    with open(output_file, 'w') as f:
        f.write(card.to_json())
    
    print(f"Principle Card generated: {output_file}")
