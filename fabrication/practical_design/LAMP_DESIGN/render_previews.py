import struct
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import art3d
import os

# ==========================================
# CONFIGURATION
# ==========================================
FILES = {
    "Base V6": "fabrication/practical_design/LAMP_DESIGN/base_qa_v6.stl",
    "Shaft V6": "fabrication/practical_design/LAMP_DESIGN/shaft_qa_v6.stl",
    "Shade V6": "fabrication/practical_design/LAMP_DESIGN/shade_qa_v6.stl",
    "Tolerance Test": "fabrication/practical_design/LAMP_DESIGN/qa_tolerance_test.stl"
}
OUTPUT_DIR = "fabrication/practical_design/LAMP_DESIGN/previews"

def read_stl(filename):
    try:
        with open(filename, "rb") as f:
            header = f.read(80)
            count = struct.unpack("<I", f.read(4))[0]
            dt = np.dtype([
                ('n', np.float32, (3,)),
                ('v1', np.float32, (3,)),
                ('v2', np.float32, (3,)),
                ('v3', np.float32, (3,)),
                ('attr', np.uint16)
            ])
            data = np.frombuffer(f.read(), dtype=dt)
            return data
    except Exception as e:
        print(f"[ERROR] Failed to read {filename}: {e}")
        return None

def render_preview(name, filename):
    print(f"Rendering {name}...")
    data = read_stl(filename)
    if data is None: return

    # Decimate for Matplotlib (Display 1% of faces)
    # For visual shape verification, we don't need all 200k tris
    step = 50 
    v1 = data['v1'][::step]
    v2 = data['v2'][::step]
    v3 = data['v3'][::step]

    # Create collection
    triangles = np.zeros((len(v1), 3, 3))
    triangles[:,0,:] = v1
    triangles[:,1,:] = v2
    triangles[:,2,:] = v3
    
    # Setup Plot
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title(f"Helios {name} (Audit Preview)")
    
    # Auto-scale
    all_verts = triangles.reshape(-1, 3)
    min_v = np.min(all_verts, axis=0)
    max_v = np.max(all_verts, axis=0)
    mid_v = (min_v + max_v) / 2.0
    max_range = np.max(max_v - min_v)
    
    ax.set_xlim(mid_v[0] - max_range/2, mid_v[0] + max_range/2)
    ax.set_ylim(mid_v[1] - max_range/2, mid_v[1] + max_range/2)
    ax.set_zlim(min_v[2], min_v[2] + max_range) # Z starts at bottom

    # Render
    mesh = art3d.Poly3DCollection(triangles, alpha=0.6, edgecolor='k', linewidth=0.05)
    mesh.set_facecolor([0.2, 0.6, 0.8])
    ax.add_collection3d(mesh)
    
    # View Angle
    ax.view_init(elev=30, azim=-45)
    ax.dist = 10
    
    # Save
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"{name.replace(' ', '_').lower()}.png")
    plt.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"  -> Saved to {out_path}")

if __name__ == "__main__":
    print("=== HELIOS RENDER PIPELINE ===")
    for name, path in FILES.items():
        if os.path.exists(path):
            render_preview(name, path)
        else:
            print(f"  [SKIP] Missing {path}")
