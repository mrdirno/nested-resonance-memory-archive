# API Documentation: helios

# Module: `helios.bridge_api`

HELIOS Bridge API (Gate 5.1)
Exposes the Fabricator via a Flask REST API.

Principle: PRIN-ACCESSIBILITY
Author: MOG (Cycle 2352)

## Function: `fabricate`

```python
fabricate()
```

## Function: `simulate`

Trigger FPGA Simulation (Gorkov Potential).
Input: JSON { "target": [x, y, z], "phases": [p0, p1, ... p63] }
Output: JSON { "potential": <int> }

```python
simulate()
```

## Function: `status`

```python
status()
```

---

# Module: `helios.camera`

HELIOS Optical Grounding (Gate 7)
Provides headless camera feedback for closed-loop control.
Uses OpenCV to detect markers and return coordinates.
Gate 7 Compliant.

## Class: `Camera`

### Method: `connect`

Connects to the camera.

```python
Camera.connect(self)
```

### Method: `detect_marker`

Detects the brightest spot in the frame (simple marker tracking).
Returns (x, y) normalized coordinates (-1..1).

```python
Camera.detect_marker(self)
```

### Method: `disconnect`

```python
Camera.disconnect(self)
```

### Method: `get_frame`

Captures a frame.

```python
Camera.get_frame(self)
```

---

# Module: `helios.cli`

HELIOS Command Line Interface (Gate 6)
The Headless Control Surface for the Reality Compiler.
Gate 6 Compliant.

Usage:
    python3 src/helios/cli.py materialize --input data/triangle.obj --duration 5
    python3 src/helios/cli.py status

## Function: `cmd_materialize`

```python
cmd_materialize(args)
```

## Function: `cmd_status`

```python
cmd_status(args)
```

## Function: `main`

```python
main()
```

---

# Module: `helios.compiler`

HELIOS Matter Compiler (Gate 3.4)
The High-Level API for Reality Compilation.
Integrates Voxelizer, Solver, and Materials into a single pipeline.

Principle: PRIN-REALITY-COMPILATION
Author: MOG (Cycle 2344)

## Class: `MatterCompiler`

### Method: `compile_object`

Compiles a 3D mesh into acoustic phase instructions.
:param mesh_path: Path to .obj file.
:param material_name: Substrate material (e.g., "AIR_STP", "WATER_20C").
:return: Dictionary containing phases, frequencies, and metadata.

```python
MatterCompiler.compile_object(self, mesh_path, material_name='AIR_STP')
```

---

# Module: `helios.control`

HELIOS Control Module (Gate 8)
The Brain of the Physical Loop.
Integrates Fabricator (Output) and Camera (Input) into a cohesive controller.
Gate 8 Compliant.

## Class: `ClosedLoopController`

### Method: `connect`

Connect to both Camera and Fabricator.

```python
ClosedLoopController.connect(self)
```

### Method: `disconnect`

Disconnect from hardware.

```python
ClosedLoopController.disconnect(self)
```

### Method: `run_loop`

Execute the control loop.
:param duration: Total runtime in seconds.
:param interval: Loop interval in seconds.

```python
ClosedLoopController.run_loop(self, duration=10, interval=0.1)
```

---

# Module: `helios.fabricator`

HELIOS Fabricator (Gate 4.3)
The Top-Level Controller for the Physical Loop.
Orchestrates the Compiler -> HAL -> Hardware pipeline.
Gate 4.3 Compliant.

## Class: `Fabricator`

### Method: `connect`

```python
Fabricator.connect(self)
```

### Method: `disconnect`

```python
Fabricator.disconnect(self)
```

### Method: `materialize`

Full pipeline execution: Compile -> Upload -> Hold.
:param mesh_path: Path to .obj file.
:param material: Target material name.
:param duration: Time to hold the field (seconds).

```python
Fabricator.materialize(self, mesh_path, material='AIR_STP', duration=10)
```

---

# Module: `helios.hal`

HELIOS HAL (Hardware Abstraction Layer)
Interface for physical acoustic arrays.
Gate 4.1 Compliant.

## Class: `EmitterArray`

Abstract Base Class for Physical Emitter Arrays.

### Method: `connect`

Connects to the physical hardware.

```python
EmitterArray.connect(self, port: str)
```

### Method: `disconnect`

Disconnects from the hardware.

```python
EmitterArray.disconnect(self)
```

### Method: `get_status`

Returns hardware health status.

```python
EmitterArray.get_status(self) -> dict
```

### Method: `set_phases`

Sends phase instructions to the array.
:param phases: Numpy array of phase delays (0..2pi).

```python
EmitterArray.set_phases(self, phases: numpy.ndarray)
```

## Class: `VirtualArray`

Virtual implementation for testing/simulation.

### Method: `connect`

```python
VirtualArray.connect(self, port: str = 'VIRTUAL')
```

### Method: `disconnect`

```python
VirtualArray.disconnect(self)
```

### Method: `get_status`

```python
VirtualArray.get_status(self) -> dict
```

### Method: `set_phases`

```python
VirtualArray.set_phases(self, phases: numpy.ndarray)
```

---

# Module: `helios.materials`

HELIOS Material Library (Gate 3.3)
Standardized physics properties for substrate definition.

Principle: PRIN-MATERIAL-AGNOSTICISM
Author: MOG (Cycle 2343)

## Class: `MaterialProperties`

## Function: `get_material`

```python
get_material(name)
```

---

# Module: `helios.sdr_bridge`

HELIOS SDR Bridge (Gate 6.1)
Interfaces with RTL-SDR hardware to provide physical RF entropy and spectral data to the NRM.
Acts as a 'SensorArray' for the Reality Injection loop.

## Class: `SDRInterface`

### Method: `close`

```python
SDRInterface.close(self)
```

### Method: `connect`

Connects to the physical SDR or initializes the virtual one.

```python
SDRInterface.connect(self)
```

### Method: `get_psd`

Calculates Power Spectral Density (PSD) for visualization.

```python
SDRInterface.get_psd(self, n_fft=1024)
```

### Method: `read_samples`

Reads raw complex samples.

```python
SDRInterface.read_samples(self, count=1024)
```

---

# Module: `helios.serial_bridge`

HELIOS Serial Bridge (Gate 4.2)
High-performance serial communication protocol for driving physical emitter arrays.
Gate 4.2 Compliant.

## Class: `SerialArray`

Physical implementation of EmitterArray using Serial/USB.
Protocol:
[HEADER: 0xAA 0xBB] [CMD: 1 byte] [PAYLOAD_LEN: 2 bytes] [PAYLOAD] [CHECKSUM: 1 byte]

### Method: `connect`

```python
SerialArray.connect(self, port: str = None)
```

### Method: `disconnect`

```python
SerialArray.disconnect(self)
```

### Method: `get_status`

```python
SerialArray.get_status(self) -> dict
```

### Method: `set_phases`

Sends 8-bit phase data to the hardware.
Phases 0..2pi are mapped to 0..255.

```python
SerialArray.set_phases(self, phases: numpy.ndarray)
```

---

# Module: `helios.solver`

HELIOS Waveform Solver (Gate 3.2)
Inverse Physics Engine: Calculates emitter parameters (Phase/Frequency) to match a Target Density Field.

Principle: PRIN-INVERSE-DESIGN
Author: MOG (Cycle 2342)

## Class: `InverseSolver`

### Method: `evolve`

Run Genetic Algorithm to find optimal phases.

```python
InverseSolver.evolve(self)
```

### Method: `get_field`

Calculate the volumetric pressure field for the given phases.
Returns: 3D numpy array (Potential)

```python
InverseSolver.get_field(self, phases)
```

---

# Module: `helios.voxelizer`

HELIOS Voxelizer (Gate 3.1)
Converts 3D Wavefront .obj meshes into discrete Target Density Fields.

Principle: PRIN-DIGITAL-MATTER (Voxelization)
Author: MOG (Cycle 2341)

## Class: `Voxelizer`

### Method: `load_obj`

Parses a standard .obj file (vertices and faces).

```python
Voxelizer.load_obj(self, file_path)
```

### Method: `normalize_mesh`

Centers the mesh and scales it to fit within the unit sphere (0.0 to 1.0 normalized coordinates).
Scales to 90% of grid size to leave padding.

```python
Voxelizer.normalize_mesh(self)
```

### Method: `sample_triangle`

Uniformly samples points on a triangle surface.

```python
Voxelizer.sample_triangle(self, v0, v1, v2, num_samples)
```

### Method: `save_field`

Saves the voxel grid as a .npy file.

```python
Voxelizer.save_field(self, output_path)
```

### Method: `voxelize`

Converts the mesh into a voxel grid by sampling faces.
:param density: Value to assign to occupied voxels.
:param surface_samples: Number of samples per face (adjust based on resolution).
:return: The voxel grid.

```python
Voxelizer.voxelize(self, density=1.0, surface_samples=1000)
```

---
