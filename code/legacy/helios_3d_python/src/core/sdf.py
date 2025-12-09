import numpy as np

def gyroid(x, y, z, scale=1.0, thickness=0.1):
    """
    Evaluates the Gyroid SDF.
    Equation: sin(x)cos(y) + sin(y)cos(z) + sin(z)cos(x)
    """
    x = x * scale
    y = y * scale
    z = z * scale
    
    val = np.sin(x)*np.cos(y) + np.sin(y)*np.cos(z) + np.sin(z)*np.cos(x)
    
    # Return absolute distance to surface (Shell)
    return np.abs(val) - thickness

def sphere(x, y, z, radius=1.0):
    return np.sqrt(x**2 + y**2 + z**2) - radius

def box(x, y, z, size=1.0):
    # Simplified box approximation
    return np.maximum(np.abs(x), np.maximum(np.abs(y), np.abs(z))) - size

def union(d1, d2):
    return np.minimum(d1, d2)

def intersect(d1, d2):
    return np.maximum(d1, d2)

def difference(d1, d2):
    return np.maximum(d1, -d2)
