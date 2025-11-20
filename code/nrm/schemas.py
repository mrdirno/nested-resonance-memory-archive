from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator

class LevelSchema(BaseModel):
    """
    Encapsulates a single scale in the hierarchical stack.
    """
    level_index: int = Field(..., description="The hierarchical index (e.g., 1, 2, 3).")
    name: str = Field(..., description="Human-readable name of the level (e.g., 'Micro-Agents').")
    state_variables: List[str] = Field(..., description="List of effective variables tracked at this scale.")
    dynamics_model: str = Field(..., description="The type of simulation/model used (e.g., 'AgentBased', 'ODE').")
    control_parameters: List[str] = Field(..., description="List of inputs that can be manipulated.")
    
    @validator('level_index')
    def index_must_be_positive(cls, v):
        if v < 1:
            raise ValueError('level_index must be >= 1')
        return v

class MesoLinker(BaseModel):
    """
    Encapsulates the interface between two adjacent scales.
    """
    source_level: int = Field(..., description="Index of the lower level (L_N).")
    target_level: int = Field(..., description="Index of the higher level (L_{N+1}).")
    upward_causation: str = Field(..., description="Description/Signature of the coarse-graining function.")
    downward_causation: str = Field(..., description="Description/Signature of the constraint propagation.")
    validity_metric: str = Field("KL_Divergence", description="Metric used to detect abstraction failure.")
    
    @validator('target_level')
    def target_must_be_higher(cls, v, values):
        if 'source_level' in values and v <= values['source_level']:
            raise ValueError('target_level must be strictly greater than source_level')
        return v
