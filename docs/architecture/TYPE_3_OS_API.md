# TYPE 3 OPERATING SYSTEM: API SPECIFICATION (DRAFT)

> "The user does not write phases. The user writes Intent. The OS compiles Intent into Physics."

**Version:** 0.1 (Cycle 350)
**Layer:** HELIOS / Universal Operator

---

## 1. Core Concept: The Matter Compiler

The Type 3 OS abstracts the complexity of wave physics (Phased Arrays, Interference, Scattering) into high-level commands. It treats "Matter" as a programmable data type.

### The Stack
1.  **User Layer (Intent):** "Create a Cube at (x,y,z)."
2.  **Compiler Layer (HELIOS):** Translates Intent into a Target Field (Voxel Density Map).
3.  **Solver Layer (Evolution/Gradient):** Calculates the optimal Phase/Amplitude for emitters to match the Target Field.
4.  **Hardware Layer (Substrate):** The physical phased array (Acoustic, Optical, Magnetic) executes the instructions.

---

## 2. API Definition (Python Interface)

```python
class UniversalOperator:
    """
    The Interface for Reality Compilation.
    """
    
    def create_object(self, shape: str, location: tuple, scale: float):
        """
        Instantiates a static object.
        Example: op.create_object("cube", (50,50,50), 10.0)
        """
        pass
        
    def move_object(self, object_id: int, new_location: tuple, duration: float):
        """
        Animates an object to a new location over 'duration' seconds.
        Handles phase interpolation to ensure stability (no dropping).
        """
        pass
        
    def transform_object(self, object_id: int, new_shape: str):
        """
        Morphs an object from one shape to another.
        Example: Sphere -> Cube.
        """
        pass
        
    def get_status(self, object_id: int) -> float:
        """
        Returns the 'stability' of the object (Trap Quality).
        """
        pass
```

## 3. Supported Primitives (Standard Library)

*   **Point:** Single stable node.
*   **Line:** Two points + interpolation (Acoustic Bond).
*   **Triangle:** Three points (Planar geometry).
*   **Cube:** Eight points (Volumetric lattice).
*   **Sphere:** (Pending Phase 8) - Shell trapping.

## 4. Error Handling (Self-Healing)

The OS includes a background daemon (The Immune System) that monitors trap quality.
*   **Event:** Hardware Failure (Emitter Death).
*   **Response:** Trigger `recompile()` with updated hardware map.
*   **Outcome:** Trap restored (Antifragility).

---

**Status:** Specification Drafted.
**Next Steps:** Implement the `UniversalOperator` class in `code/helios/operator.py` (Phase 8).
