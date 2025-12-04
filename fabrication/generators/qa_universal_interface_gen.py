import numpy as np
import math
import sys
import struct
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from fabrication.library import lamp_lib

def generate_interface_master(output_path, resolution=50):
    print(f"Generating QA INTERFACE MASTER: {output_path}")
    
    # Dimensions
    block_size = 100.0
    block_height = 15.0
    
    # QA Specs (from QA_PROTOCOL.md)
    base_socket_id = 40.5
    shaft_plug_od = 40.0
    rod_clearance_id = 15.0
    shade_mount_id = 42.0
    mating_depth = 3.0
    
    step = block_size / resolution
    res_xy = int(block_size / step) + 2
    res_z = int(block_height / step) + 2
    
    print(f"Grid: {res_xy}x{res_xy}x{res_z}")
    grid = np.zeros((res_xy, res_xy, res_z), dtype=bool)
    
    # Center coordinates
    c1 = (-25.0, -25.0) # Base Socket
    c2 = (25.0, -25.0)  # Shaft Plug
    c3 = (-25.0, 25.0)  # Rod Clearance
    c4 = (25.0, 25.0)   # Shade Mount
    
    for z_idx in range(res_z):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (block_size / 2.0)
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (block_size / 2.0)
                
                # Main Block Body
                if abs(x_mm) < (block_size/2) and abs(y_mm) < (block_size/2):
                    is_solid = True
                    
                    # Feature 1: Base Socket (Recess)
                    # Location: Bottom Left
                    d1 = math.sqrt((x_mm - c1[0])**2 + (y_mm - c1[1])**2)
                    if d1 < (base_socket_id / 2.0):
                        if z_mm >= (block_height - mating_depth): # Recess at top
                            is_solid = False
                            
                    # Feature 2: Shaft Plug (Boss)
                    # Location: Bottom Right
                    d2 = math.sqrt((x_mm - c2[0])**2 + (y_mm - c2[1])**2)
                    if d2 < (shaft_plug_od / 2.0):
                        if z_mm >= block_height: # Extrude upwards? 
                            # Wait, grid stops at block_height. 
                            # We need to modify z range or carve out surroundings.
                            # Let's carve out a ring AROUND the plug to simulate it rising?
                            # No, simpler: The block is the base. The plug rises FROM the block.
                            # Current grid z max is block_height.
                            pass
                    
                    # Feature 3: Rod Clearance (Hole)
                    # Location: Top Left
                    d3 = math.sqrt((x_mm - c3[0])**2 + (y_mm - c3[1])**2)
                    if d3 < (rod_clearance_id / 2.0):
                        is_solid = False
                        
                    # Feature 4: Shade Mount (Hole)
                    # Location: Top Right
                    d4 = math.sqrt((x_mm - c4[0])**2 + (y_mm - c4[1])**2)
                    if d4 < (shade_mount_id / 2.0):
                        is_solid = False
                        
                    grid[x_idx,y_idx,z_idx] = is_solid
                else:
                    grid[x_idx,y_idx,z_idx] = False

    # Add Shaft Plug Extension (Boss)
    # We need to extend the grid or add a second pass. 
    # Easier: Just make the block thicker and carve everything else away? No.
    # Let's define the block as Z=0 to 10. The plug goes to 13.
    
    # RE-RUN loop for correct Z logic
    grid.fill(False)
    
    res_z_total = int((block_height + mating_depth) / step) + 2
    grid = np.zeros((res_xy, res_xy, res_z_total), dtype=bool)
    
    for z_idx in range(res_z_total):
        z_mm = z_idx * step
        
        for x_idx in range(res_xy):
            x_mm = (x_idx * step) - (block_size / 2.0)
            for y_idx in range(res_xy):
                y_mm = (y_idx * step) - (block_size / 2.0)
                
                # Base Plate (0 to 10mm)
                if z_mm < 10.0:
                    if abs(x_mm) < 48.0 and abs(y_mm) < 48.0: # 96mm square
                        is_solid = True
                        
                        # C1: Base Socket (Recess) - Carve out top 3mm of base plate
                        d1 = math.sqrt((x_mm - c1[0])**2 + (y_mm - c1[1])**2)
                        if d1 < (base_socket_id / 2.0) and z_mm > 7.0:
                            is_solid = False
                            
                        # C3: Rod Hole
                        d3 = math.sqrt((x_mm - c3[0])**2 + (y_mm - c3[1])**2)
                        if d3 < (rod_clearance_id / 2.0):
                            is_solid = False
                            
                        # C4: Shade Hole
                        d4 = math.sqrt((x_mm - c4[0])**2 + (y_mm - c4[1])**2)
                        if d4 < (shade_mount_id / 2.0):
                            is_solid = False
                            
                        grid[x_idx,y_idx,z_idx] = is_solid
                        
                # Boss Extension (10mm to 13mm)
                elif z_mm < 13.0:
                    # C2: Shaft Plug (Boss)
                    d2 = math.sqrt((x_mm - c2[0])**2 + (y_mm - c2[1])**2)
                    if d2 < (shaft_plug_od / 2.0):
                        grid[x_idx,y_idx,z_idx] = True

    # Mesh Extraction
    vertices, faces = lamp_lib.extract_mesh_from_grid(grid, step, block_size, block_size)
    lamp_lib.write_binary_stl(output_path, vertices, faces)

if __name__ == "__main__":
    output_file = "qa_interface_master.stl"
    if len(sys.argv) > 1: output_file = sys.argv[1]
    generate_interface_master(output_file)
