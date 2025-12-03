import numpy as np
import math
import sys
import struct
import os
import random

# Add project root to path for library import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from fabrication.library import lamp_lib

# -----------------------------------------------------------------------------
# HELIOS LAMP SERIES 07: THE NEURAL NET (SHADE)
# -----------------------------------------------------------------------------
# Logic: Connection Weights / Synaptic Firing.
# Method: Dense web of nodes and edges (Network Graph).
# Standard: V7 (Spider Fitter, 14mm Hole, 25.4mm Wall).
# -----------------------------------------------------------------------------

def generate_shade(output_path, diameter=200.0, height=180.0, resolution=120, hole_diameter=14.0):
    print(f"Generating THE NEURAL NET SHADE: {output_path}")
    
    # Mount Parameters
    mount_hole_radius = hole_diameter / 2.0 
    hub_radius = 20.0 
    spoke_width = 8.0 
    top_plate_height = 4.0
    bottom_rim_height = 4.0
    
    # Shell Parameters
    wall_thickness = 25.4 
    hand_access_radius = 45.0 
    
    # Grid Setup
    max_dim = max(diameter, height)
    step = max_dim / resolution
    
    res_x = int(diameter / step) + 5
    res_y = int(diameter / step) + 5
    res_z = int(height / step) + 1
    
    print(f"Grid: {res_x}x{res_y}x{res_z} (Voxel size: {step:.2f}mm)")
    
    grid = np.zeros((res_x, res_y, res_z), dtype=bool)
    
    # Neural Net Logic
    # 3D Graph: Nodes (Neurons) connected by Edges (Synapses).
    # To ensure printability, we need density.
    
    random.seed(2049)
    
    # Generate Nodes
    # Distribute on the shell surface mostly? Or volume?
    # Volume filled but hollow center.
    
    nodes = []
    num_nodes = 150
    
    radius = diameter / 2.0
    
    for _ in range(num_nodes):
        # Random pos in shell
        # Cylinder bounds
        r = random.uniform(hand_access_radius + 5, radius - 2)
        theta = random.uniform(0, 2*math.pi)
        z = random.uniform(5, height - 5)
        
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        nodes.append(np.array([x, y, z]))
        
    # Generate Edges (K-Nearest Neighbors)
    edges = []
    for i in range(num_nodes):
        # Find 3 nearest
        dists = []
        for j in range(num_nodes):
            if i == j: continue
            d = np.linalg.norm(nodes[i] - nodes[j])
            dists.append((d, j))
        
        dists.sort(key=lambda x: x[0])
        
        # Connect to nearest 3
        for k in range(min(3, len(dists))):
            edges.append((i, dists[k][1]))
            
    print(f"Training Network... {len(nodes)} Neurons, {len(edges)} Synapses")
    
    # Helper: Dist to segment
    def dist_to_segment(p, v1, v2):
        ab = v2 - v1
        ap = p - v1
        t = np.dot(ap, ab) / np.dot(ab, ab)
        t = max(0.0, min(1.0, t))
        closest = v1 + t * ab
        return np.linalg.norm(p - closest)
        
    # Voxelize
    # This is computationally heavy for brute force.
    # Optimization: Spatial binning or just accept slowness for prototype.
    # Resolution 120 is okay.
    
    synapse_radius = 3.5 # Thickened (was 2.5)
    neuron_radius = 6.0 # Thickened (was 5.0)
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        # Optimization: Filter nodes/edges by Z height
        relevant_nodes = [n for n in nodes if abs(n[2] - z_mm) < (neuron_radius + 5.0)]
        relevant_edges = []
        for e in edges:
            v1 = nodes[e[0]]
            v2 = nodes[e[1]]
            # Z bounds check
            min_z = min(v1[2], v2[2]) - synapse_radius
            max_z = max(v1[2], v2[2]) + synapse_radius
            if z_mm >= min_z and z_mm <= max_z:
                relevant_edges.append((v1, v2))
        
        for x_idx in range(res_x):
            x_mm = (x_idx * step) - (diameter / 2.0)
            
            for y_idx in range(res_y):
                y_mm = (y_idx * step) - (diameter / 2.0)
                
                dist_xy = math.sqrt(x_mm**2 + y_mm**2)
                p_curr = np.array([x_mm, y_mm, z_mm])
                
                # --- PRIORITY 1: SPIDER FITTER (Dynamic) ---
                current_shell_radius = radius
                fitter_override = lamp_lib.apply_spider_fitter(
                    x_mm, y_mm, z_mm, dist_xy,
                    mount_z_start=(height - top_plate_height),
                    mount_hole_radius=mount_hole_radius,
                    hub_radius=hub_radius,
                    spoke_width=spoke_width,
                    outer_radius=current_shell_radius
                )
                
                if fitter_override is not None:
                    grid[x_idx,y_idx,z_idx] = fitter_override
                    continue

                # --- PRIORITY 2: BOTTOM RIM ---
                if z_mm < bottom_rim_height:
                    if dist_xy < radius and dist_xy > hand_access_radius:
                         grid[x_idx,y_idx,z_idx] = True
                         continue

                # --- PRIORITY 3: NEURAL SHELL (Anisotropic) ---
                
                if dist_xy > (radius + 5.0):
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Hand Access (Strict)
                if dist_xy < hand_access_radius:
                    grid[x_idx,y_idx,z_idx] = False
                    continue
                    
                # Anisotropy: Stretch Nodes/Edges in Z
                # We don't move the nodes, we stretch the distance metric?
                # Or we just distribute nodes with Z bias?
                # The nodes are already distributed.
                # Let's thicken vertical connections?
                
                # Distance Metric Anisotropy
                # d = sqrt(dx^2 + dy^2 + (dz/stretch)^2)
                
                z_stretch = 2.0
                
                # Check Nodes
                is_solid = False
                for n in relevant_nodes:
                    # Ellipsoid neurons
                    dx = p_curr[0] - n[0]
                    dy = p_curr[1] - n[1]
                    dz = p_curr[2] - n[2]
                    d_ani = math.sqrt(dx**2 + dy**2 + (dz/z_stretch)**2)
                    
                    if d_ani < neuron_radius:
                        is_solid = True
                        break
                
                if is_solid:
                    grid[x_idx,y_idx,z_idx] = True
                    continue
                    
                # Check Edges
                # This is hard to anisotropize efficiently without complex math on segment distance
                # Just use standard thickness for edges, maybe slightly thicker?
                
                for e in relevant_edges:
                    if dist_to_segment(p_curr, e[0], e[1]) < synapse_radius:
                        is_solid = True
                        break
                        
                grid[x_idx,y_idx,z_idx] = is_solid

    # Clean Dust (QA)
    grid = lamp_lib.clean_voxel_grid(grid)

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, diameter, diameter, 0.0)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "neural_net_shade.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_shade(output_file)
