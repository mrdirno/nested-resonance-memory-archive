import json
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analysis.pattern_archaeologist import PatternArchaeologist

def load_lineage_data(file_path):
    """Loads lineage data from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Lineage file not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {file_path}")
        return None

def build_graph_from_lineage(lineage_tree, G=None, parent_node_id=None):
    """Recursively builds a NetworkX graph from the lineage tree dictionary."""
    if G is None:
        G = nx.DiGraph()

    current_node_id = lineage_tree["id"]
    current_node_type = lineage_tree["type"]
    current_node_name = lineage_tree["name"]

    if not G.has_node(current_node_id):
        G.add_node(current_node_id, type=current_node_type, name=current_node_name)

    if parent_node_id:
        G.add_edge(parent_node_id, current_node_id) # Edge from parent to child

    if "parents" in lineage_tree:
        for parent_rel in lineage_tree["parents"]:
            # Recurse, passing current node as child
            build_graph_from_lineage(parent_rel["pattern"], G, current_node_id)
            
    # Note: trace_ancestry gives "parents". If trace_descendancy was used, it would have "children".
    # We are using trace_ancestry, so we build from child to parent, effectively.
    # To represent the causal flow (parent -> child), we need to reverse the edges
    # or build the graph differently. Let's make edges go from cause to effect.
    # The current structure has 'parents' in the lineage_tree for tracing ancestry.
    # So if A is parent of B, in trace_ancestry of B, A appears as a 'parent'.
    # We want to draw A -> B. So current_node_id is the effect, and parent_node_id is the cause.
    # This means the current call `G.add_edge(parent_node_id, current_node_id)` is correct if parent_node_id is the cause.
    # Let's verify the trace_ancestry output structure.
    # trace_ancestry(X) returns X, and X has parents. So X is child of its parents.
    # The edges should be (parent, child). So when we recurse from parent_rel, it should be parent_rel["pattern"]["id"] -> current_node_id
    # No, wait. lineage_tree is the *starting node*. So its parents are its causes.
    # So the edges should be (parent_id, current_node_id).
    # And then when we recurse, the parent_rel["pattern"] becomes the new current_node_id, and current_node_id becomes the parent_node_id in the recursive call.
    # This current logic results in (parent_of_current_node_id, current_node_id). This is correct for drawing causal flow.

    return G

def draw_lineage_graph(G, title, output_path, max_width=16, max_height=9):
    """Draws the NetworkX graph and saves it to a file."""
    
    pos = nx.spring_layout(G, k=0.8, iterations=50) # Use spring layout for better node separation
    
    node_colors = {
        "self_awareness": "#FFD700",  # Gold
        "interaction": "#87CEEB",     # SkyBlue
        "flock_formed": "#90EE90",    # LightGreen
        "resource_consumed": "#FF6347",# Tomato
        "cluster": "#ADD8E6",         # LightBlue
        "unknown": "#D3D3D3",         # LightGray
        "move": "#FFB6C1",            # LightPink (if move patterns were discovered)
        "resource_found": "#FFA500",  # Orange (if resource found patterns were discovered)
    }
    
    colors = [node_colors.get(G.nodes[node].get("type", "unknown"), "#D3D3D3") for node in G.nodes()]
    
    plt.figure(figsize=(max_width, max_height))
    nx.draw(G, pos, 
            with_labels=False, 
            node_color=colors, 
            node_size=800, 
            font_size=8, 
            font_color="black",
            edge_color="gray", 
            width=0.5, 
            alpha=0.7)
    
    # Add labels separately for better control
    labels = {node: G.nodes[node]["name"] for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=6, font_color="black")
    
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()

def main():
    print("CYCLE 297: PAPER 8 - LINEAGE VISUALIZATION")
    print("==========================================")

    results_dir = Path("experiments/results")
    os.makedirs("analysis/figures", exist_ok=True)

    # Visualize Hero Flock Lineage
    flock_lineage_file = results_dir / "paper8_hero_flock_lineage.json"
    flock_lineage_data = load_lineage_data(flock_lineage_file)

    if flock_lineage_data:
        print(f"Loaded flock lineage data from {flock_lineage_file}")
        G_flock = build_graph_from_lineage(flock_lineage_data)
        flock_output_path = Path("analysis/figures/paper8_hero_flock_lineage.png")
        draw_lineage_graph(G_flock, "Paper 8: Hero Flock Emergent Lineage", flock_output_path)
        print(f"Hero Flock Lineage visualization saved to {flock_output_path}")
    else:
        print("Skipping flock lineage visualization due to data loading error.")

    # Visualize Hero Resource Lineage
    resource_lineage_file = results_dir / "paper8_hero_resource_lineage.json"
    resource_lineage_data = load_lineage_data(resource_lineage_file)

    if resource_lineage_data:
        print(f"Loaded resource lineage data from {resource_lineage_file}")
        G_resource = build_graph_from_lineage(resource_lineage_data)
        resource_output_path = Path("analysis/figures/paper8_hero_resource_lineage.png")
        draw_lineage_graph(G_resource, "Paper 8: Hero Resource Emergent Lineage", resource_output_path)
        print(f"Hero Resource Lineage visualization saved to {resource_output_path}")
    else:
        print("Skipping resource lineage visualization due to data loading error.")

    print("\n--- Paper 8 Lineage Visualization Complete ---")

if __name__ == "__main__":
    main()
