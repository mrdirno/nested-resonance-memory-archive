# NRM Core API Reference

## nrm_core.vector

### class Vector
A simple immutable vector class for NRM calculations.

#### `__init__(self, values)`
Initialize a new Vector.
- `values` (iterable): The components of the vector.

#### `dot(self, other)`
Calculate the dot product with another vector.
- `other` (Vector): The other vector.
- **Returns**: (float) The dot product.
- **Raises**: `ValueError` if dimensions do not match.

#### `magnitude`
(property) The Euclidean magnitude (length) of the vector.

#### `normalize(self)`
Return a normalized (unit length) copy of this vector.
- **Returns**: (Vector) The normalized vector.

#### `cosine_similarity(self, other)`
Calculate the cosine similarity with another vector.
- `other` (Vector): The other vector.
- **Returns**: (float) The cosine similarity (0.0 to 1.0 for non-negative vectors).

#### Operators
- `v1 + v2`: Vector addition.
- `v * scalar`: Scalar multiplication.
- `v[index]`: Access component by index.

---

## nrm_core.resonance

### class ResonantNode
A single node in the resonant field.

#### `__init__(self, node_id, vector)`
- `node_id` (str): Unique identifier for the node.
- `vector` (Vector or list): The semantic vector associated with this node.

#### `resonate(self, input_vector)`
Stimulate the node with an input vector. Energy increases based on cosine similarity.
- `input_vector` (Vector or list): The stimulus vector.

#### `decay(self, rate=0.1)`
Decay the node's energy.
- `rate` (float): Decay rate (0.0 to 1.0). Default is 0.1.

### class ResonantField
The field managing multiple resonant nodes.

#### `__init__(self)`
Initialize an empty field.

#### `add_node(self, node_id, vector)`
Add a node to the field.
- `node_id` (str): Unique identifier.
- `vector` (Vector or list): Semantic vector.

#### `stimulate(self, vector)`
Stimulate all nodes in the field with an input vector.
- `vector` (Vector or list): The stimulus vector.

#### `get_active_nodes(self, threshold=0.5)`
Retrieve nodes with energy above a threshold.
- `threshold` (float): Energy threshold. Default 0.5.
- **Returns**: (dict) Mapping of `node_id` to `energy`.

#### `decay(self)`
Apply decay to all nodes in the field.
