# NRM Core Deployment Guide

## Overview
This guide details how to install, use, and distribute the `nrm_core` library.

## Installation

### From Source
You can install the package directly from the source code:

```bash
pip install .
```

### From Distribution Artifacts
After building (see below), you can install from the generated wheel:

```bash
pip install dist/nrm_core-0.0.1-py3-none-any.whl
```

## Building
To create the distribution artifacts (`.tar.gz` and `.whl`), run:

```bash
pip install build
python3 -m build
```

The artifacts will be placed in the `dist/` directory.

## Usage
Once installed, you can import `nrm_core` in your Python scripts:

```python
from nrm_core.resonance import ResonantField
from nrm_core.memory import PatternMemory

# Initialize a field
field = ResonantField()
# Note: ResonantField does not have a get_status() method in the current version, 
# refer to examples/hello_resonance.py for API usage.
```

## Examples
Check the `examples/` directory for complete usage scenarios:
- `examples/hello_resonance.py`: Basic field interaction.
- `examples/hello_memory.py`: Pattern storage and retrieval.
- `examples/associator.py`: CLI tool for concept association.
- `examples/web_server.py`: Simple HTTP API.

## Testing
Run the test suite to verify functionality:

```bash
pytest tests/
```
