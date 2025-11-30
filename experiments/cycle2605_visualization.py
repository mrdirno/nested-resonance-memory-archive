#!/usr/bin/env python3
"""
Experiment: Cycle 2605 - The Visualization
Goal: Generate a standalone HTML/JS visualization of a Hive simulation.
"""

import sys
import json
import random
from pathlib import Path

# Reuse Hive Logic
sys.path.append(str(Path(__file__).parent))
try:
    from cycle2602_hive import Vector2, HiveAgent
    from cycle2600_protocol import AgentMessage, MessageType
except ImportError:
    sys.exit(1)

def generate_simulation_data(steps=200):
    """Run a simulation and record agent positions per frame."""
    agents = [HiveAgent(f"drone_{i}", Vector2(random.uniform(0, 200), random.uniform(0, 200))) for i in range(10)]
    target = Vector2(400, 300) # Canvas 800x600
    
    # Set one agent to know target to start cascade
    agents[0].known_target = target
    
    frames = []
    
    for _ in range(steps):
        frame_data = []
        broadcasts = []
        
        for agent in agents:
            msg = agent.update(target)
            if msg: broadcasts.append(msg)
            
            frame_data.append({
                "id": agent.agent_id,
                "x": agent.position.x,
                "y": agent.position.y,
                "knowing": bool(agent.known_target)
            })
            
        for msg in broadcasts:
            for agent in agents:
                agent.receive_message(msg)
                
        frames.append(frame_data)
        
    return {
        "target": {"x": target.x, "y": target.y},
        "frames": frames
    }

def generate_html(data):
    json_str = json.dumps(data)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>HELIOS-ONE Hive Visualization</title>
    <style>
        body {{ background: #111; color: #eee; font-family: monospace; text-align: center; }}
        canvas {{ background: #000; border: 1px solid #333; }}
        #status {{ margin-top: 10px; }}
    </style>
</head>
<body>
    <h2>Cycle 2605: Hive Swarm Visualization</h2>
    <canvas id="simCanvas" width="800" height="600"></canvas>
    <div id="status">Frame: 0</div>

    <script>
        const data = {json_str};
        const canvas = document.getElementById('simCanvas');
        const ctx = canvas.getContext('2d');
        const status = document.getElementById('status');
        
        let frameIdx = 0;
        
        function draw() {{
            if (frameIdx >= data.frames.length) frameIdx = 0; // Loop
            
            const agents = data.frames[frameIdx];
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw Target
            ctx.fillStyle = '#f00';
            ctx.beginPath();
            ctx.arc(data.target.x, data.target.y, 10, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#fff';
            ctx.fillText("TARGET", data.target.x - 20, data.target.y - 15);
            
            // Draw Agents
            agents.forEach(a => {{
                ctx.fillStyle = a.knowing ? '#0f0' : '#666';
                ctx.beginPath();
                ctx.arc(a.x, a.y, 5, 0, Math.PI * 2);
                ctx.fill();
                
                // Draw ID
                ctx.fillStyle = '#aaa';
                ctx.font = '10px monospace';
                ctx.fillText(a.id, a.x + 8, a.y + 3);
            }});
            
            status.innerText = "Frame: " + frameIdx + " / " + data.frames.length;
            frameIdx++;
            
            requestAnimationFrame(draw);
        }}
        
        draw();
    </script>
</body>
</html>
"""
    return html

def main():
    print("Cycle 2605: The Visualization - Generating Data...")
    data = generate_simulation_data()
    
    print("Generating HTML...")
    html_content = generate_html(data)
    
    output_path = Path("experiments/cycle2605_hive_view.html")
    with open(output_path, "w") as f:
        f.write(html_content)
        
    print(f"SUCCESS: Visualization written to {output_path}")

if __name__ == "__main__":
    main()
