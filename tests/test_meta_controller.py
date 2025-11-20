import unittest
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from code.nrm.schemas import LevelSchema, MesoLinker
from code.nrm.meta_controller import NRMMetaController

class TestNRMMetaController(unittest.TestCase):
    
    def setUp(self):
        self.controller = NRMMetaController()
        
        # Define standard levels
        self.l1 = LevelSchema(
            level_index=1, name="Micro", state_variables=["x"], dynamics_model="ABM", control_parameters=["p"]
        )
        self.l2 = LevelSchema(
            level_index=2, name="Meso", state_variables=["y"], dynamics_model="ODE", control_parameters=["q"]
        )
        self.l3 = LevelSchema(
            level_index=3, name="Macro", state_variables=["z"], dynamics_model="PDE", control_parameters=["r"]
        )
        
        # Define linkers
        self.link12 = MesoLinker(
            source_level=1, target_level=2, upward_causation="f(x)", downward_causation="g(y)"
        )
        self.link23 = MesoLinker(
            source_level=2, target_level=3, upward_causation="h(y)", downward_causation="k(z)"
        )

    def test_registration(self):
        self.controller.register_level(self.l1)
        self.controller.register_level(self.l2)
        self.assertEqual(len(self.controller.levels), 2)
        
        self.controller.register_linker(self.link12)
        self.assertEqual(len(self.controller.linkers), 1)

    def test_path_resolution(self):
        # Build full stack
        self.controller.register_level(self.l1)
        self.controller.register_level(self.l2)
        self.controller.register_level(self.l3)
        self.controller.register_linker(self.link12)
        self.controller.register_linker(self.link23)
        
        # Resolve path L1 -> L3
        path = self.controller.resolve_path(1, 3)
        self.assertEqual(len(path), 2)
        self.assertEqual(path[0].source_level, 1)
        self.assertEqual(path[1].source_level, 2)
        self.assertEqual(path[1].target_level, 3)

    def test_invalid_path(self):
        self.controller.register_level(self.l1)
        self.controller.register_level(self.l3)
        # No linkers
        with self.assertRaises(ValueError):
            self.controller.resolve_path(1, 3)

if __name__ == '__main__':
    unittest.main()
