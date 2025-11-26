
"""
Cycle 2334: The Holocron (Knowledge Graph Visualization)
Goal: Create an interactive visualization of the Knowledge Graph to enable intuitive exploration.
Method: Generate a standalone HTML file with D3.js.
"""

import json
import os
import sys

# Ensure src is in path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))

def generate_holocron(input_path="data/knowledge_graph.json", output_path="data/holocron.html"):
    """Generates a D3.js visualization from the knowledge graph JSON."""
    
    print(f"Loading Knowledge Graph from {input_path}...")
    try:
        with open(input_path, 'r') as f:
            graph_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_path} not found. Run Cycle 2333 first.")
        return

    nodes = []
    links = []
    
    # Process Nodes
    # We need to map node IDs to indices for D3 force simulation
    node_id_map = {}
    
    print(f"Processing {len(graph_data['nodes'])} nodes...")
    
    for idx, (node_id, attrs) in enumerate(graph_data["nodes"].items()):
        node_id_map[node_id] = idx
        group = 1 # Default group
        
        if attrs.get("type") == "principle":
            group = 2
        elif attrs.get("type") == "cycle":
            group = 3
        elif attrs.get("type") == "module":
            group = 4
            
        nodes.append({
            "id": node_id,
            "group": group,
            "type": attrs.get("type", "unknown")
        })

    # Process Edges
    print(f"Processing {len(graph_data['edges'])} edges...")
    for edge in graph_data["edges"]:
        source = edge["source"]
        target = edge["target"]
        
        if source in node_id_map and target in node_id_map:
            links.append({
                "source": source, # D3 will map this to the node object if we use IDs, but let's stick to IDs
                "target": target,
                "value": 1,
                "type": edge.get("relation", "related")
            })

    # HTML Template
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>The Holocron: DUALITY-ZERO Knowledge Graph</title>
    <style>
        body {{ margin: 0; background-color: #000; color: #eee; font-family: monospace; overflow: hidden; }}
        #graph {{ width: 100vw; height: 100vh; }}
        .node {{ stroke: #fff; stroke-width: 1.5px; cursor: pointer; }}
        .link {{ stroke: #999; stroke-opacity: 0.6; }}
        .label {{ pointer-events: none; font-size: 10px; fill: #ccc; }}
        #info {{ position: absolute; top: 20px; left: 20px; background: rgba(0,0,0,0.8); padding: 10px; border: 1px solid #444; max-width: 300px; display: none; }}
        h1 {{ position: absolute; bottom: 20px; left: 20px; margin: 0; font-size: 24px; color: #0f0; }}
    </style>
    <script src="https://d3js.org/d3.v7.min.js"></script>
</head>
<body>
    <h1>The Holocron</h1>
    <div id="info"></div>
    <div id="graph"></div>

    <script>
        const data = {{
            nodes: {json.dumps(nodes)},
            links: {json.dumps(links)}
        }};

        const width = window.innerWidth;
        const height = window.innerHeight;

        const color = d3.scaleOrdinal(d3.schemeCategory10);

        const simulation = d3.forceSimulation(data.nodes)
            .force("link", d3.forceLink(data.links).id(d => d.id).distance(50))
            .force("charge", d3.forceManyBody().strength(-50))
            .force("center", d3.forceCenter(width / 2, height / 2));

        const svg = d3.select("#graph").append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(d3.zoom().on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }}));

        const g = svg.append("g");

        const link = g.append("g")
            .attr("class", "links")
            .selectAll("line")
            .data(data.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.sqrt(d.value));

        const node = g.append("g")
            .attr("class", "nodes")
            .selectAll("circle")
            .data(data.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", 5)
            .attr("fill", d => {{
                if (d.type === 'principle') return '#ff0'; // Yellow
                if (d.type === 'cycle') return '#0ff'; // Cyan
                if (d.type === 'module') return '#f0f'; // Magenta
                return '#555'; // Grey (Files)
            }})
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));

        node.append("title")
            .text(d => d.id);
            
        // Hover interactions
        node.on("mouseover", (event, d) => {{
            const info = document.getElementById("info");
            info.style.display = "block";
            info.innerHTML = `<strong>${{d.id}}</strong><br>Type: ${{d.type}}`;
        }});

        simulation.on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);

            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
        }});

        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}

        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}

        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
    </script>
</body>
</html>
    """
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"Holocron generated at: {output_path}")

if __name__ == "__main__":
    generate_holocron()
