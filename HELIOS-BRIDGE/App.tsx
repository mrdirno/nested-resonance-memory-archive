
import React, { useState, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';
import { SimulationState, SimulationMode, TranscendentalNumber, CameraTarget } from './types';
import { ParticleSystem, Boundary } from './components/ParticleSystem';
import { UIOverlay } from './components/UIComponents';
import { useSwarmWorker } from './services/SwarmWorker';
import { EvolvedArray } from './components/EvolvedArray';
import { KaleidoscopeEffect, KALEIDO_MODES } from './components/KaleidoscopeEffect';

// Coarse pointer (phone/tablet) → tune the camera controls for touch.
const IS_TOUCH = typeof window !== 'undefined' &&
  ((window.matchMedia && window.matchMedia('(pointer: coarse)').matches) || 'ontouchstart' in window);

// Smooth Camera Controller
const CameraController: React.FC<{
  target: CameraTarget | null,
  setTarget: (t: null) => void
}> = ({ target, setTarget }) => {
  const { camera, controls } = useThree();
  const vec = new THREE.Vector3();

  useFrame(() => {
    if (target) {
      vec.set(...target.position);
      camera.position.lerp(vec, 0.05);
      if (controls) {
        // @ts-ignore
        controls.target.lerp(new THREE.Vector3(...target.target), 0.05);
      }
      if (camera.position.distanceTo(vec) < 0.1) {
        setTarget(null);
      }
    }
  });

  return (
    <OrbitControls
      makeDefault
      enableDamping
      dampingFactor={IS_TOUCH ? 0.12 : 0.05}
      // Touch: gentler rotate/zoom and disable two-finger pan so pinch-zoom
      // and one-finger orbit don't fight each other (the "funky mobile" feel).
      rotateSpeed={IS_TOUCH ? 0.55 : 1}
      zoomSpeed={IS_TOUCH ? 0.7 : 1}
      enablePan={!IS_TOUCH}
      touches={{ ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY }}
      minDistance={IS_TOUCH ? 3 : 1}
      maxDistance={100}
      onStart={() => setTarget(null)} // Stop auto-move on user interaction
    />
  );
};

// Component to handle dynamic exposure updates
const ExposureController: React.FC<{ exposure: number }> = ({ exposure }) => {
  const { gl } = useThree();
  useFrame(() => {
    gl.toneMappingExposure = exposure;
  });
  return null;
};

// Adjusts FOV based on aspect ratio to prevent "zoomed in" feel on mobile
const ResponsiveCamera: React.FC = () => {
  const { camera, size } = useThree();

  React.useEffect(() => {
    const aspect = size.width / size.height;
    if (aspect < 1) {
      // Portrait (Mobile): widen FOV, but not so much it looks fish-eye/funky
      (camera as THREE.PerspectiveCamera).fov = 82;
    } else {
      // Landscape (Desktop): Default FOV
      (camera as THREE.PerspectiveCamera).fov = 60;
    }
    camera.updateProjectionMatrix();
  }, [size, camera]);

  return null;
};

const CAMERA_CONFIG = { position: [20, 10, 20], fov: 60 } as const;

const App: React.FC = () => {
  const [activePanel, setActivePanel] = useState<string | null>(null);
  const [cameraTarget, setCameraTarget] = useState<CameraTarget | null>(null);
  const [showArray, setShowArray] = useState(false);
  const [kaleidoMode, setKaleidoMode] = useState<number>(-1); // default: Everything (raw resonance field, no fold)

  // Activate Swarm Worker (Background Compute)
  const { isConnected, tasksCompleted, gaStatus } = useSwarmWorker(true);

  // Refs for direct DOM manipulation of stats (High performance)
  const digitRefs = {
    m: useRef<HTMLElement>(null),
    n: useRef<HTMLElement>(null),
    p: useRef<HTMLElement>(null),
    pos: useRef<HTMLElement>(null),
    energy: useRef<HTMLElement>(null),
  };

  // DEFAULT VIEW = original default (350k · STANDARD · no fold) — rolled back from the Entangled/Holy-Trinity clone
  const [config, setConfig] = useState<SimulationState>({
    particleCount: 350000,
    isPlaying: true,
    speed: 1,
    quality: 2.0,
    amplitude: 1.0,
    exposure: 3.0,
    contrast: 1.0,
    mode: SimulationMode.STANDARD,
    mapping: {
      a: TranscendentalNumber.PHI,
      b: TranscendentalNumber.PHI,
      c: TranscendentalNumber.PI
    },
    stagger: { a: 0, b: 239, c: 478 },
    extensions: {
      crystal: { threeFold: 0, sixFold: 0, lattice: 0 },
      harmonic: { commaSpiral: 0, perfectFifths: 0, equalTemp: 0 },
      topology: { trefoil: 0, torus: 0, hopf: 0 }
    },
    cameraStats: { x: '0', y: '0', z: '0', dist: '25' },
    resetTrigger: 0
  });

  return (
    <div className="w-full h-screen relative overflow-hidden select-none">
      <Canvas
        camera={CAMERA_CONFIG}
        dpr={IS_TOUCH ? [1, 1.5] : 2} // adaptive on touch for smoother framerate; fixed hi-res on desktop
        gl={{
          antialias: false,
          powerPreference: "high-performance",
          toneMapping: THREE.AgXToneMapping,
          toneMappingExposure: 1.0
        }}
      >
        {/* Scene Environment */}
        <fog attach="fog" args={['#000000', 10, 80]} />
        <ambientLight intensity={0.4} color="#404080" />
        <directionalLight position={[10, 10, 5]} intensity={1} color="#8A2BE2" />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />

        {/* Core Systems */}
        <Boundary />
        <ParticleSystem config={config} digitRefs={digitRefs} />
        {showArray && <EvolvedArray phases={gaStatus?.best_genome || []} />}
        <CameraController target={cameraTarget} setTarget={setCameraTarget} />
        <ExposureController exposure={config.exposure} />
        <ResponsiveCamera />
        {/* Sacred-geometry kaleidoscope fold over the resonance field (KELIBRO) */}
        <KaleidoscopeEffect mode={kaleidoMode} />
      </Canvas>

      {/* Kaleidoscope geometry selector — positioned below the header link band (h-[100px]) */}
      <div className="absolute top-[108px] left-1/2 -translate-x-1/2 z-20 flex flex-wrap justify-center gap-1.5
                      px-2 py-1.5 rounded-full bg-black/40 backdrop-blur-md border border-fuchsia-500/20">
        {KALEIDO_MODES.map((m) => (
          <button
            key={m.id}
            onClick={() => setKaleidoMode(m.id)}
            title={m.hint}
            className={`px-3 py-1 text-xs rounded-full transition-colors ${
              kaleidoMode === m.id
                ? 'bg-fuchsia-500/90 text-white'
                : 'text-gray-300 hover:bg-white/10'
            }`}
          >
            {m.label}
          </button>
        ))}
      </div>

      {/* UI Layer */}
      <UIOverlay
        config={config}
        setConfig={setConfig}
        activePanel={activePanel}
        setActivePanel={setActivePanel}
        digitRefs={digitRefs}
        onCameraMove={setCameraTarget}
        onResetCamera={() => setCameraTarget({ position: [20, 10, 20], target: [0, 0, 0] })}
        isConnected={isConnected}
        tasksCompleted={tasksCompleted}
        gaStatus={gaStatus}
        showArray={showArray}
        setShowArray={setShowArray}
        setKaleidoMode={setKaleidoMode}
      />
    </div>
  );
};

export default App;