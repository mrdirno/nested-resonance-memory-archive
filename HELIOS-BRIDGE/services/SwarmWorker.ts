import { useEffect, useRef, useState } from 'react';

// Define the Wasm interface
interface HeliosWasm {
    calculate_field: (emitters_ptr: number, count: number, x: number, y: number, z: number) => number;
    memory: WebAssembly.Memory;
    // Add other exports as needed
}

interface ComputeTask {
    task_id: number;
    emitters: Array<{ x: number, y: number, z: number, phase: number }>;
    targets: Array<{ x: number, y: number, z: number }>;
}

export const useSwarmWorker = (enabled: boolean = true) => {
    const ws = useRef<WebSocket | null>(null);
    const wasmInstance = useRef<WebAssembly.Instance | null>(null);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [tasksCompleted, setTasksCompleted] = useState<number>(0);

    useEffect(() => {
        if (!enabled) return;

        // 1. Load Wasm
        const loadWasm = async () => {
            try {
                const response = await fetch('/helios_physics.wasm');
                const bytes = await response.arrayBuffer();
                const results = await WebAssembly.instantiate(bytes, {
                    env: {
                        // Import any needed JS functions here (e.g. logging)
                        console_log: (arg: number) => console.log(arg)
                    }
                });
                wasmInstance.current = results.instance;
                console.log("[Swarm] Wasm Engine Loaded.");
                connectToCoordinator();
            } catch (err) {
                console.error("[Swarm] Failed to load Wasm:", err);
            }
        };

        // 2. Connect to Coordinator
        const connectToCoordinator = () => {
            const socket = new WebSocket('ws://localhost:8765');

            socket.onopen = () => {
                console.log("[Swarm] Connected to Coordinator.");
                setIsConnected(true);
                socket.send(JSON.stringify({ type: "ready" }));
            };

            socket.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'compute_task') {
                    handleTask(data, socket);
                }
            };

            socket.onclose = () => {
                console.log("[Swarm] Disconnected. Retrying in 5s...");
                setIsConnected(false);
                setTimeout(connectToCoordinator, 5000);
            };

            socket.onerror = (err) => {
                console.error("[Swarm] WebSocket Error:", err);
            };

            ws.current = socket;
        };

        loadWasm();

        return () => {
            if (ws.current) ws.current.close();
        };
    }, [enabled]);

    const handleTask = async (task: ComputeTask, socket: WebSocket) => {
        // console.log(`[Swarm] Computing Task ${task.task_id}...`);
        const start = performance.now();

        // Mock Computation for now (until we bind the Wasm memory correctly)
        // In a real implementation, we'd write emitters to Wasm memory, call calculate, read results.

        // Simulate work
        // await new Promise(r => setTimeout(r, 50));

        const results = task.targets.map(t => ({
            x: t.x, y: t.y, z: t.z,
            u: Math.random() * -100 // Mock Gorkov potential
        }));

        const end = performance.now();
        // console.log(`[Swarm] Task ${task.task_id} complete in ${(end - start).toFixed(2)}ms`);

        socket.send(JSON.stringify({
            type: "result",
            task_id: task.task_id,
            results: results
        }));
        setTasksCompleted(prev => prev + 1);
    };

    return { isConnected, tasksCompleted };
};
