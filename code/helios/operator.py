"""
HELIOS Universal Operator
The Core Logic for the Type 3 Operating System.
Translates High-Level Intent (Shapes) into Low-Level Physics (Phases).

Author: Aldrin Payopay (aldrin.gdf@gmail.com)
Co-Authored-By: Gemini 3 Pro (MOG Pilot)
"""
import numpy as np
import random
import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from code.helios.substrate_3d import AcousticSubstrate3D

class Emitter:
    """
    Physical Emitter Definition.
    """
    def __init__(self, x, y, z, frequency=1.0, phase=0.0, amplitude=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.frequency = frequency
        self.phase = phase
        self.amplitude = amplitude

class UniversalOperator:
    """
    The Interface for Reality Compilation.
    Manages the Substrate and the Optimization Engine (GA).
    """
    
    def __init__(self, width_mm=100, height_mm=100, depth_mm=100, resolution_mm=2):
        self.substrate = AcousticSubstrate3D(width_mm, height_mm, depth_mm, resolution_mm)
        self.emitters = []
        self.resolution = resolution_mm
        
    def configure_array(self, rows=8, cols=8, spacing=10.0, z_plane=0.0):
        """
        Configures a standard planar phased array.
        """
        self.emitters = []
        center_offset_x = (rows - 1) * spacing / 2.0
        center_offset_y = (cols - 1) * spacing / 2.0
        
        # Center in the box
        box_center_x = (self.substrate.width * self.resolution) / 2.0
        box_center_y = (self.substrate.height * self.resolution) / 2.0
        
        for i in range(rows):
            for j in range(cols):
                x = box_center_x - center_offset_x + i * spacing
                y = box_center_y - center_offset_y + j * spacing
                self.emitters.append(Emitter(x, y, z_plane))
                
        print(f"[Operator] Array Configured: {len(self.emitters)} emitters.")
        
    def create_object(self, shape: str, location: tuple, scale: float = 10.0):
        """
        Instantiates a static object.
        Returns the optimal phases.
        """
        print(f"[Operator] Compiling Object: {shape} at {location}...")
        
        targets = self._get_targets(shape, location, scale)
        if not targets:
            raise ValueError(f"Unknown shape: {shape}")
            
        best_phases = self._optimize(targets)
        
        # Apply phases to emitters
        for i, e in enumerate(self.emitters):
            e.phase = best_phases[i]
            
        return best_phases
        
    def _get_targets(self, shape, location, scale):
        """
        Generates voxel coordinates for a given shape.
        """
        cx, cy, cz = location
        targets_mm = []
        
        if shape.lower() == "point":
            targets_mm.append([cx, cy, cz])
            
        elif shape.lower() == "cube":
            d = scale / 2.0
            # 8 Corners
            targets_mm = [
                [cx-d, cy-d, cz-d], [cx+d, cy-d, cz-d], [cx-d, cy+d, cz-d], [cx+d, cy+d, cz-d],
                [cx-d, cy-d, cz+d], [cx+d, cy-d, cz+d], [cx-d, cy+d, cz+d], [cx+d, cy+d, cz+d]
            ]
            
        else:
            return None
            
        # Convert to voxels
        targets_vox = [np.array(p) / self.resolution for p in targets_mm]
        return targets_vox

    def _optimize(self, targets, generations=50, pop_size=50):
        """
        Genetic Algorithm Backend.
        """
        num_emitters = len(self.emitters)
        population = [np.random.uniform(0, 2*np.pi, num_emitters) for _ in range(pop_size)]
        
        best_fitness = -9999.0
        best_genes = None
        
        for gen in range(generations):
            scores = []
            for individual in population:
                f = self._fitness_func(individual, targets)
                scores.append((f, individual))
                
            scores.sort(key=lambda x: x[0], reverse=True)
            if scores[0][0] > best_fitness:
                best_fitness = scores[0][0]
                best_genes = scores[0][1]
            
            # Simple Elitism
            elite = [x[1] for x in scores[:10]]
            new_pop = elite[:]
            while len(new_pop) < pop_size:
                p1 = random.choice(elite)
                p2 = random.choice(elite)
                cut = random.randint(1, num_emitters-1)
                child = np.concatenate((p1[:cut], p2[cut:]))
                if random.random() < 0.2:
                    idx = random.randint(0, num_emitters-1)
                    child[idx] = np.random.uniform(0, 2*np.pi)
                new_pop.append(child)
            population = new_pop
            
        return best_genes
        
    def _fitness_func(self, phases, targets):
        """
        Internal Fitness Function.
        """
        for i, e in enumerate(self.emitters):
            e.phase = phases[i]
            
        field = self.substrate.propagate(self.emitters)
        potential = field**2
        p_max = np.max(potential)
        
        if p_max < 0.001: return -100.0
        
        score = 0
        for t in targets:
            tx, ty, tz = int(t[0]), int(t[1]), int(t[2])
            # Bounds check
            if 0 <= tx < self.substrate.width and 0 <= ty < self.substrate.height and 0 <= tz < self.substrate.depth:
                p_target = potential[tz, ty, tx]
                score += (p_max - p_target)
            else:
                score -= 100.0
        return score

    def verify_stability(self, targets_vox):
        """
        Returns the average pressure ratio for the current configuration at target locations.
        """
        field = self.substrate.propagate(self.emitters)
        potential = field**2
        p_max = np.max(potential)
        
        if p_max == 0: return 1.0
        
        ratios = []
        for t in targets_vox:
            tx, ty, tz = int(t[0]), int(t[1]), int(t[2])
            if 0 <= tx < self.substrate.width and 0 <= ty < self.substrate.height and 0 <= tz < self.substrate.depth:
                p_val = potential[tz, ty, tx]
                ratios.append(p_val / p_max)
            else:
                ratios.append(1.0)
                
        return sum(ratios) / len(ratios)
