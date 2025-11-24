"""
Tests for nrm_core/fractal.py
"""
import pytest
import math
from nrm_core.fractal import FractalAgent, Population

def test_agent_init():
    agent = FractalAgent("A1", energy=1.0)
    assert agent.energy == 1.0
    assert len(agent.phase_state.phases) == 3

def test_agent_coherence():
    a1 = FractalAgent("A1")
    a2 = FractalAgent("A2")
    # Force phases to be identical
    a2.phase_state.phases = a1.phase_state.phases
    assert a1.compute_coherence(a2) == pytest.approx(1.0)

def test_population_step():
    pop = Population()
    a1 = FractalAgent("A1", energy=1.0)
    a2 = FractalAgent("A2", energy=1.0)
    pop.add(a1)
    pop.add(a2)
    
    pop.step(0.1)
    
    # Energy should decrease
    assert a1.energy < 1.0
    assert a2.energy < 1.0
    
    # Phases should change (unless they were already synced, which is unlikely with random init)
    # We can't easily assert phase change value without mocking random, but we verify code runs.
