"""
Tests for nrm_core/vector.py
"""
import pytest
from nrm_core.vector import Vector

def test_vector_init():
    v = Vector([1, 2, 3])
    assert v.values == (1.0, 2.0, 3.0)

def test_vector_dot():
    v1 = Vector([1, 2, 3])
    v2 = Vector([4, 5, 6])
    assert v1.dot(v2) == 32.0

def test_vector_magnitude():
    v = Vector([3, 4])
    assert v.magnitude == 5.0

def test_vector_normalize():
    v = Vector([3, 4])
    norm_v = v.normalize()
    assert norm_v.magnitude == pytest.approx(1.0)
    assert norm_v.values == (0.6, 0.8)

def test_cosine_similarity():
    v1 = Vector([1, 0])
    v2 = Vector([0, 1])
    v3 = Vector([1, 1])
    assert v1.cosine_similarity(v2) == 0.0
    assert v1.cosine_similarity(v3) == pytest.approx(0.70710678)
