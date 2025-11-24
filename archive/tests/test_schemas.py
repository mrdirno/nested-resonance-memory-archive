import unittest
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from code.nrm.schemas import LevelSchema, MesoLinker
from pydantic import ValidationError

class TestNRMSchemas(unittest.TestCase):
    
    def test_level_schema_valid(self):
        """Test creating a valid LevelSchema."""
        l1 = LevelSchema(
            level_index=1,
            name="Micro",
            state_variables=["x", "y", "v_x", "v_y"],
            dynamics_model="AgentBased",
            control_parameters=["friction", "temperature"]
        )
        self.assertEqual(l1.level_index, 1)
        self.assertEqual(l1.name, "Micro")
        
    def test_level_schema_invalid_index(self):
        """Test that level_index must be positive."""
        with self.assertRaises(ValidationError):
            LevelSchema(
                level_index=0,
                name="Invalid",
                state_variables=[],
                dynamics_model="None",
                control_parameters=[]
            )

    def test_meso_linker_valid(self):
        """Test creating a valid MesoLinker."""
        link = MesoLinker(
            source_level=1,
            target_level=2,
            upward_causation="mean(velocity)",
            downward_causation="set_boundary(temperature)"
        )
        self.assertEqual(link.source_level, 1)
        self.assertEqual(link.target_level, 2)
        
    def test_meso_linker_invalid_hierarchy(self):
        """Test that target_level must be > source_level."""
        with self.assertRaises(ValidationError):
            MesoLinker(
                source_level=2,
                target_level=1, # Invalid: Target must be higher
                upward_causation="...",
                downward_causation="..."
            )

if __name__ == '__main__':
    unittest.main()
