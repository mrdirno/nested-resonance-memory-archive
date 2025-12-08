
import os
import sys
import argparse
import http.server
import socketserver
import webbrowser
import threading
import time

def create_viewer_html(directory, port):
    """
    Scans the directory for STLs and generates a viewer.html file.
    """
    
    files = [f for f in os.listdir(directory) if f.lower().endswith('.stl')]
    if not files:
        print(f"No STLs found in {directory}")
        return False
        
    print(f"Found {len(files)} STL files.")
    
    js_files_array = []
    
    for f in files:
        # Heuristic Color Assignment
        lower_f = f.lower()
        color = "0xaaaaaa" # Start grey
        opacity = "1.0"
        
        if "black" in lower_f: color = "0x111111"
        elif "white" in lower_f: 
            color = "0xffffff"
            opacity = "0.9" # Translucent
        elif "red" in lower_f: color = "0xff0000"
        elif "blue" in lower_f: color = "0x0000ff"
        elif "yellow" in lower_f: color = "0xffff00"
        elif "green" in lower_f: color = "0x00ff00"
        elif "cyan" in lower_f: color = "0x00ffff"
        elif "magenta" in lower_f: color = "0xff00ff"
        # Material mapping
        elif "shade" in lower_f: 
            color = "0xffffff"
            opacity = "0.9"
        
        js_obj = f"{{ path: '{f}', color: {color}, opacity: {opacity}, name: '{f}' }}"
        js_files_array.append(js_obj)
        
    js_content = ",\n            ".join(js_files_array)
    
    # NOTE: Double braces {{ }} form a single { or } in f-string.
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Visual Verification: {os.path.basename(os.path.abspath(directory))}</title>
    <style>
        body {{ margin: 0; background-color: #333; overflow: hidden; }}
        canvas {{ width: 100%; height: 100% }}
        #info {{
            position: absolute; top: 10px; width: 100%; text-align: center; color: white;
            font-family: monospace; font-size: 16px; pointer-events: none; text-shadow: 1px 1px 2px black;
        }}
    </style>
</head>
<body>
    <div id="info">Loading {len(files)} visual assets...</div>
    
    <!-- Load Three.js from CDN -->
    <script type="importmap">
        {{
            "imports": {{
                "three": "https://unpkg.com/three@0.160.0/build/three.module.js",
                "three/addons/": "https://unpkg.com/three@0.160.0/examples/jsm/"
            }}
        }}
    </script>

    <script type="module">
        import * as THREE from 'three';
        import {{ OrbitControls }} from 'three/addons/controls/OrbitControls.js';
        import {{ STLLoader }} from 'three/addons/loaders/STLLoader.js';

        // Scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x505050); // Lighter Grey Background to verify non-black output
        
        // Debug: Axes Helper
        scene.add(new THREE.AxesHelper(100));

        // Debug: Verification Box (Green Cube at origin)
        const boxGeo = new THREE.BoxGeometry(20, 20, 20);
        const boxMat = new THREE.MeshBasicMaterial({{ color: 0x00ff00, wireframe: true }});
        const debugBox = new THREE.Mesh(boxGeo, boxMat);
        debugBox.position.set(-50, -50, 10);
        scene.add(debugBox);
        
        // Camera (Hardcoded Position for Lamp)
        const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 5000);
        camera.position.set(0, -500, 300); // Front view
        camera.up.set(0, 0, 1);

        // Renderer
        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        // Controls
        const controls = new OrbitControls(camera, renderer.domElement);
         controls.target.set(0, 0, 140); // Center of Lamp
        controls.update();

        // Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(100, -200, 400);
        dirLight.castShadow = true;
        scene.add(dirLight);
        
        const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
        dirLight2.position.set(-100, 200, 200);
        scene.add(dirLight2);

        // Loader
        const loader = new STLLoader();

        // Files
        const files = [
            {js_content}
        ];

        let loadedCount = 0;
        const group = new THREE.Group();
        scene.add(group);
        
        const infoDiv = document.getElementById('info');

        files.forEach(file => {{
            loader.load(file.path, function (geometry) {{
                let material;
                if(file.opacity < 1.0) {{
                     material = new THREE.MeshPhongMaterial({{ 
                        color: file.color, 
                        specular: 0x111111, 
                        shininess: 50,
                        transparent: true,
                        opacity: file.opacity,
                        side: THREE.DoubleSide,
                        depthWrite: false
                    }});
                }} else {{
                     material = new THREE.MeshPhongMaterial({{ 
                        color: file.color, 
                        specular: 0x111111, 
                        shininess: 30,
                        side: THREE.DoubleSide
                    }});
                }}
                
                const mesh = new THREE.Mesh(geometry, material);
                group.add(mesh);

                loadedCount++;
                infoDiv.textContent = "Loading... " + loadedCount + "/" + files.length;
                
                if(loadedCount === files.length) {{
                    infoDiv.textContent = "Visual Verification Ready: " + files.length + " Objects";
                    
                    // Auto Center Check
                    const box = new THREE.Box3().setFromObject(group);
                    if( !box.isEmpty() ) {{
                         console.log("Bounds:", box);
                    }}
                }}
            }}, undefined, function (error) {{
                console.error(error);
                infoDiv.textContent = "Error loading " + file.path;
                infoDiv.style.color = "red";
            }});
        }});

        // Grid
        const gridHelper = new THREE.GridHelper(500, 50);
        gridHelper.rotation.x = Math.PI / 2;
        scene.add(gridHelper);

        // Animation
        function animate() {{
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }}
        animate();

        // Resize
        window.addEventListener('resize', onWindowResize, false);
        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

    </script>
</body>
</html>
    """
    
    with open(os.path.join(directory, "viewer.html"), "w") as f:
        f.write(html_content)
        
    return True

def serve_directory(directory, port):
    os.chdir(directory)
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), Handler) as httpd:
        print(f"Serving at http://localhost:{port}/viewer.html")
        httpd.serve_forever()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate 3D Viewer for STLs")
    parser.add_argument("--dir", default=".", help="Directory containing STLs")
    parser.add_argument("--port", type=int, default=8125, help="Port to serve on")
    
    args = parser.parse_args()
    
    target_dir = os.path.abspath(args.dir)
    print(f"Target Directory: {target_dir}")
    if not os.path.exists(target_dir):
        print(f"Error: Directory {target_dir} does not exist.")
        sys.exit(1)
    
    if create_viewer_html(target_dir, args.port):
        print("Viewer created.")
        serve_directory(target_dir, args.port)
    else:
        print("Failed to create viewer.")
