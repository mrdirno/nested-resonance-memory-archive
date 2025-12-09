import torch
import numpy as np
import math
import subprocess
import os
from skimage.measure import marching_cubes

class VoxelReconstructor:
    def __init__(self, resolution=64, device="mps"):
        self.resolution = resolution
        self.device = device if torch.backends.mps.is_available() else "cpu"
        self.grid = None
        self.bounds = (-1.0, 1.0)
        self.cli_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            "../../../helios_native_bridge/.build/release/HeliosCLI"
        ))
        
    def run_native_photogrammetry(self, input_folder, output_path, progress_callback=None):
        print(f"Launching Native Bridge: {self.cli_path}")
        if not os.path.exists(self.cli_path):
            print("Error: HeliosCLI binary not found.")
            return False

        cmd = [self.cli_path, input_folder, output_path]
        
        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                text=True, bufsize=1, universal_newlines=True
            )
            
            for line in process.stdout:
                line = line.strip()
                if line.startswith("PROGRESS:"):
                    val = float(line.split(":")[1])
                    if progress_callback: progress_callback(val)
                elif line == "COMPLETE":
                    print("Native Photogrammetry Complete.")
                elif line.startswith("ERROR:"):
                    print(f"Native Error: {line}")
                    
            return process.wait() == 0
        except Exception as e:
            print(f"Bridge Failed: {e}")
            return False

    def load_obj(self, path):
        """
        Parses a simple OBJ file.
        RealityKit creates path/model.obj usually inside the folder if folder output is used.
        """
        # RealityKit OBJ export is often a folder if textures are involved.
        # If 'output_path' ends in .obj, it might be a folder named 'something.obj' containing 'model.obj'.
        
        target_file = path
        if os.path.isdir(path):
            # Look for .obj inside
            candidates = [f for f in os.listdir(path) if f.endswith('.obj')]
            if candidates:
                target_file = os.path.join(path, candidates[0])
            else:
                return None, None, None
        
        verts = []
        normals = []
        faces = []
        
        # Minimal OBJ parser
        try:
            with open(target_file, 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        verts.append(list(map(float, line.split()[1:4])))
                    elif line.startswith('vn '):
                        normals.append(list(map(float, line.split()[1:4])))
                    elif line.startswith('f '):
                        # Handle f v/vt/vn
                        face_idxs = []
                        for v in line.split()[1:]:
                            # OBJ is 1-indexed
                            idx = int(v.split('/')[0]) - 1
                            face_idxs.append(idx)
                        if len(face_idxs) == 3:
                            faces.append(face_idxs)
                        elif len(face_idxs) == 4:
                            # Triangulate quad
                            faces.append([face_idxs[0], face_idxs[1], face_idxs[2]])
                            faces.append([face_idxs[0], face_idxs[2], face_idxs[3]])
                            
            return np.array(verts, dtype=np.float32), np.array(normals, dtype=np.float32), np.array(faces, dtype=np.int32)
        except Exception as e:
            print(f"OBJ Load Error: {e}")
            return None, None, None

    # ... (Legacy Voxel Code omitted for brevity but assumed preserved) ...
    def create_grid(self):
        """Creates a coordinate grid on the GPU."""
        res = self.resolution
        x = torch.linspace(self.bounds[0], self.bounds[1], res, device=self.device)
        y = torch.linspace(self.bounds[0], self.bounds[1], res, device=self.device)
        z = torch.linspace(self.bounds[0], self.bounds[1], res, device=self.device)
        grid_x, grid_y, grid_z = torch.meshgrid(x, y, z, indexing='ij')
        self.points = torch.stack([grid_x.flatten(), grid_y.flatten(), grid_z.flatten()], dim=1)
        return self.points

    def get_turntable_cameras(self, num_frames):
        cameras = []
        radius = 3.5
        for i in range(num_frames):
            angle = (2 * math.pi * i) / num_frames
            cam_x = radius * math.sin(angle); cam_y = 0.0; cam_z = radius * math.cos(angle)
            eye = torch.tensor([cam_x, cam_y, cam_z], device=self.device)
            at = torch.tensor([0.0, 0.0, 0.0], device=self.device)
            up = torch.tensor([0.0, 1.0, 0.0], device=self.device)
            z_axis = torch.nn.functional.normalize(eye - at, dim=0)
            x_axis = torch.nn.functional.normalize(torch.cross(up, z_axis), dim=0)
            y_axis = torch.cross(z_axis, x_axis)
            view = torch.eye(4, device=self.device)
            view[:3, 0] = x_axis; view[:3, 1] = y_axis; view[:3, 2] = z_axis
            view[:3, 3] = -torch.tensor([torch.dot(x_axis, eye), torch.dot(y_axis, eye), torch.dot(z_axis, eye)], device=self.device)
            cameras.append(view)
        return torch.stack(cameras)

    def project_and_carve(self, masks, fov=45.0):
        num_frames, H, W = masks.shape
        masks = masks.to(self.device)
        points = self.create_grid()
        N = points.shape[0]
        points_h = torch.cat([points, torch.ones(N, 1, device=self.device)], dim=1)
        view_matrices = self.get_turntable_cameras(num_frames)
        aspect = W / H; near = 0.1; far = 100.0; f = 1.0 / math.tan(math.radians(fov) / 2.0)
        proj = torch.zeros(4, 4, device=self.device)
        proj[0, 0] = f / aspect; proj[1, 1] = f
        proj[2, 2] = (far + near) / (near - far); proj[2, 3] = (2 * far * near) / (near - far); proj[3, 2] = -1.0
        mvp = torch.matmul(proj.unsqueeze(0), view_matrices)
        voxels = torch.ones(N, dtype=torch.bool, device=self.device)
        for i in range(num_frames):
            img_coords = torch.matmul(points_h, mvp[i].T)
            x = img_coords[:, 0] / img_coords[:, 3]
            y = img_coords[:, 1] / img_coords[:, 3]
            u = (x * 0.5 + 0.5) * W; v = (-y * 0.5 + 0.5) * H
            valid_uv = (u >= 0) & (u < W) & (v >= 0) & (v < H) & (img_coords[:, 3] > 0)
            u_idx = u.long().clamp(0, W-1); v_idx = v.long().clamp(0, H-1)
            mask_val = masks[i, v_idx, u_idx] > 0.5
            should_keep = ~valid_uv | mask_val
            voxels = voxels & should_keep
        self.voxels = voxels.reshape(self.resolution, self.resolution, self.resolution)
        return self.voxels
        
    def extract_mesh(self, voxels):
        vol = voxels.cpu().numpy().astype(float)
        vol = np.pad(vol, 1, 'constant', constant_values=0)
        try:
            verts, faces, normals, values = marching_cubes(vol, level=0.5)
            res = self.resolution + 2
            verts = (verts / (res - 1)) * 2.0 - 1.0
            return verts, normals, faces
        except RuntimeError:
            return None, None, None
