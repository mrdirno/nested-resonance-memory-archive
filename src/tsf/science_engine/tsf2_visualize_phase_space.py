import json
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

# --- TSF-2 Visualization CONFIGURATION ---
EXPERIMENT_ID = "TSF-2"
RESULTS_FILE = f"experiments/results/{EXPERIMENT_ID}/results.json"
OUTPUT_DIR = f"data/figures/{EXPERIMENT_ID}"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def visualize_tsf2_results():
    print(f"--- VISUALIZING {EXPERIMENT_ID} RESULTS ---")
    
    if not os.path.exists(RESULTS_FILE):
        print(f"Error: Results file not found at {RESULTS_FILE}")
        return

    with open(RESULTS_FILE, "r") as f:
        data = json.load(f)

    params = data["parameters"]
    data_points = data["data"]

    Es = np.array([d["E"] for d in data_points])
    Ss = np.array([d["S"] for d in data_points])
    Cs = np.array([d["C"] for d in data_points])
    Rs = np.array([d["R"] for d in data_points])

    # Reshape for contour plots
    num_e = len(np.unique(Es))
    num_s = len(np.unique(Ss))
    
    E_grid = Es.reshape(num_e, num_s)
    S_grid = Ss.reshape(num_e, num_s)
    C_grid = Cs.reshape(num_e, num_s)
    R_grid = Rs.reshape(num_e, num_s)

    # --- Plotting Energy Variance (Complexity - C) ---
    fig_c = plt.figure(figsize=(10, 8))
    ax_c = fig_c.add_subplot(111, projection='3d')
    ax_c.plot_surface(E_grid, S_grid, C_grid, cmap='viridis')
    ax_c.set_xlabel("Energy Influx (E)")
    ax_c.set_ylabel("Stability Coupling (S)")
    ax_c.set_zlabel("Energy Variance (C)")
    ax_c.set_title(f"{EXPERIMENT_ID}: Energy Complexity (C) Phase Space")
    plt.savefig(os.path.join(OUTPUT_DIR, "C_phase_space.png"))
    plt.close(fig_c)
    print(f"Saved C phase space plot to {os.path.join(OUTPUT_DIR, 'C_phase_space.png')}")

    # --- Plotting Phase Order (R) ---
    fig_r = plt.figure(figsize=(10, 8))
    ax_r = fig_r.add_subplot(111, projection='3d')
    ax_r.plot_surface(E_grid, S_grid, R_grid, cmap='plasma')
    ax_r.set_xlabel("Energy Influx (E)")
    ax_r.set_ylabel("Stability Coupling (S)")
    ax_r.set_zlabel("Phase Order (R)")
    ax_r.set_title(f"{EXPERIMENT_ID}: Phase Order (R) Phase Space")
    plt.savefig(os.path.join(OUTPUT_DIR, "R_phase_space.png"))
    plt.close(fig_r)
    print(f"Saved R phase space plot to {os.path.join(OUTPUT_DIR, 'R_phase_space.png')}")
    
    print("Visualization complete. Analyze generated plots for phase transitions.")

if __name__ == "__main__":
    visualize_tsf2_results()
