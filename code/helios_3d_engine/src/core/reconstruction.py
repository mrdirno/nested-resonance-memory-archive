import torch
import numpy as np
import math
from skimage.measure import marching_cubes

class VoxelReconstructor:
    def __init__(self, resolution=64, device="mps"):
        self.resolution = resolution
        self.device = device if torch.backends.mps.is_available() else "cpu"
        self.grid = None
        self.bounds = (-1.0, 1.0) # Normalized cube
        
    def create_grid(self):
        """Creates a coordinate grid on the GPU."""
        res = self.resolution
        x = torch.linspace(self.bounds[0], self.bounds[1], res, device=self.device)
        y = torch.linspace(self.bounds[0], self.bounds[1], res, device=self.device)
        z = torch.linspace(self.bounds[0], self.bounds[1], res, device=self.device)
        
        # (X, Y, Z) grid points
        grid_x, grid_y, grid_z = torch.meshgrid(x, y, z, indexing='ij')
        
        # Stack into (N, 3) list of points
        # Shape: (Res^3, 3)
        self.points = torch.stack([grid_x.flatten(), grid_y.flatten(), grid_z.flatten()], dim=1)
        return self.points

    def get_turntable_cameras(self, num_frames):
        """
        Generates camera matrices for a 360 degree turntable.
        Assumes object is at (0,0,0) and camera rotates around Y axis.
        """
        cameras = []
        radius = 3.5 # Distance from center (tunable)
        
        for i in range(num_frames):
            angle = (2 * math.pi * i) / num_frames
            
            # Camera Position (Polar coordinates)
            cam_x = radius * math.sin(angle)
            cam_y = 0.0 # Eye level
            cam_z = radius * math.cos(angle)
            
            # Look At Matrix construction
            eye = torch.tensor([cam_x, cam_y, cam_z], device=self.device)
            at = torch.tensor([0.0, 0.0, 0.0], device=self.device)
            up = torch.tensor([0.0, 1.0, 0.0], device=self.device)
            
            z_axis = torch.nn.functional.normalize(eye - at, dim=0)
            x_axis = torch.nn.functional.normalize(torch.cross(up, z_axis), dim=0)
            y_axis = torch.cross(z_axis, x_axis)
            
            # View Matrix (World -> Camera)
            view = torch.eye(4, device=self.device)
            view[:3, 0] = x_axis
            view[:3, 1] = y_axis
            view[:3, 2] = z_axis
            view[:3, 3] = -torch.tensor([torch.dot(x_axis, eye), torch.dot(y_axis, eye), torch.dot(z_axis, eye)], device=self.device)
            
            cameras.append(view)
            
        return torch.stack(cameras) # (F, 4, 4)

    def project_and_carve(self, masks, fov=45.0):
        """
        masks: (F, H, W) float tensor (0.0 or 1.0)
        Carves the visual hull.
        """
        num_frames, H, W = masks.shape
        masks = masks.to(self.device)
        
        # 1. Setup Grid
        points = self.create_grid() # (N, 3)
        N = points.shape[0]
        
        # Add homogeneous coord
        points_h = torch.cat([points, torch.ones(N, 1, device=self.device)], dim=1) # (N, 4)
        
        # 2. Get Cameras
        view_matrices = self.get_turntable_cameras(num_frames) # (F, 4, 4)
        
        # 3. Projection Matrix (Perspective)
        aspect = W / H
        near = 0.1
        far = 100.0
        f = 1.0 / math.tan(math.radians(fov) / 2.0)
        
        proj = torch.zeros(4, 4, device=self.device)
        proj[0, 0] = f / aspect
        proj[1, 1] = f
        proj[2, 2] = (far + near) / (near - far)
        proj[2, 3] = (2 * far * near) / (near - far)
        proj[3, 2] = -1.0
        
        # MVP Matrix: Proj * View
        # (F, 4, 4)
        mvp = torch.matmul(proj.unsqueeze(0), view_matrices)
        
        # 4. Project Points (Vectorized Batch Processing)
        # We can't do all frames * all points at once (OOM risk). 
        # Loop through frames, accumulate "votes".
        
        # Start with all voxels "Solid" (1.0)
        voxels = torch.ones(N, dtype=torch.bool, device=self.device)
        
        print(f"Carving {N} voxels from {num_frames} masks...")
        
        for i in range(num_frames):
            # Project points into this camera
            # (N, 4) x (4, 4).T -> (N, 4)
            img_coords = torch.matmul(points_h, mvp[i].T)
            
            # Perspective Divide
            x = img_coords[:, 0] / img_coords[:, 3]
            y = img_coords[:, 1] / img_coords[:, 3] # Inverted Y? Standard GL is Y up. Image is Y down.
            # GL NDCs: [-1, 1]. Image UVs: [0, 1]
            
            # NDC to UV
            u = (x * 0.5 + 0.5) * W
            v = (-y * 0.5 + 0.5) * H # Flip Y for image coords
            
            # Check bounds
            valid_uv = (u >= 0) & (u < W) & (v >= 0) & (v < H) & (img_coords[:, 3] > 0)
            
            # Sample Mask
            # Nearest neighbor sampling
            u_idx = u.long().clamp(0, W-1)
            v_idx = v.long().clamp(0, H-1)
            
            mask_val = masks[i, v_idx, u_idx] > 0.5
            
            # Carve
            # A voxel is KEPT if it projects to a valid mask pixel OR is out of bounds (conservative)
            # Actually, standard visual hull: if it projects to BACKGROUND, it is REMOVED.
            # Our masks: 1=Foreground, 0=Background.
            
            # Keep if (Valid Projection AND Mask=1) OR (Invalid Projection)
            # Remove if (Valid Projection AND Mask=0)
            
            should_keep = ~valid_uv | mask_val
            
            voxels = voxels & should_keep
            
        print(f"Carving complete. Remaining voxels: {voxels.sum()}")
        
    def extract_mesh(self, voxels):
        """
        Converts binary voxel grid to mesh using Marching Cubes.
        voxels: (Res, Res, Res) bool/float tensor
        """
        print("Extracting mesh from voxels...")
        # Move to CPU and convert to numpy
        vol = voxels.cpu().numpy().astype(float)
        
        # Pad with 0 to close mesh
        vol = np.pad(vol, 1, 'constant', constant_values=0)
        
        try:
            verts, faces, normals, values = marching_cubes(vol, level=0.5)
            
            # Normalize verts to -1..1 range
            # Grid size is now Res + 2 due to padding
            res = self.resolution + 2
            
            # Map 0..Res to -1..1
            # v' = (v / (res-1)) * 2 - 1
            verts = (verts / (res - 1)) * 2.0 - 1.0
            
            return verts, normals, faces
            
        except RuntimeError:
            print("Marching Cubes failed (Empty volume?)")
            return None, None, None
