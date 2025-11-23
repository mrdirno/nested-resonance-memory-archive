
import React, { useState, useRef } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import * as THREE from 'three';
import { SimulationState, SimulationMode, TranscendentalNumber, CameraTarget } from './types';
import { ParticleSystem, Boundary } from './components/ParticleSystem';
import { UIOverlay } from './components/UIComponents';

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

  return <OrbitControls enableDamping dampingFactor={0.05} minDistance={1} maxDistance={100} />;
};

// Component to handle dynamic exposure updates
const ExposureController: React.FC<{ exposure: number }> = ({ exposure }) => {
  const { gl } = useThree();
  useFrame(() => {
    gl.toneMappingExposure = exposure;
  });
  return null;
};

const App: React.FC = () => {
  const [activePanel, setActivePanel] = useState<string | null>(null);
  const [cameraTarget, setCameraTarget] = useState<CameraTarget | null>(null);

  // Refs for direct DOM manipulation of stats (High performance)
  const digitRefs = {
    m: useRef<HTMLElement>(null),
    n: useRef<HTMLElement>(null),
    p: useRef<HTMLElement>(null),
    pos: useRef<HTMLElement>(null),
    energy: useRef<HTMLElement>(null),
  };

  const [config, setConfig] = useState<SimulationState>({
    particleCount: 350000,
    isPlaying: true,
    speed: 1,
    quality: 0.7,
    amplitude: 1.0,
    exposure: 1.0,
    contrast: 1.0,
    mode: SimulationMode.STANDARD,
    mapping: {
      a: TranscendentalNumber.PHI,
      b: TranscendentalNumber.PHI,
      c: TranscendentalNumber.PI
    },
    stagger: { a: 0, b: 239, c: 478 },
    extensions: {
      crystal: { threeFold: false, sixFold: false, lattice: false },
      harmonic: { commaSpiral: true, perfectFifths: true, equalTemp: false },
      topology: { trefoil: false, torus: false, hopf: false }
    },
    cameraStats: { x: '0', y: '0', z: '0', dist: '25' }
  });

  return (
    <div className="w-full h-screen relative overflow-hidden select-none">
      <Canvas
        camera={{ position: [20, 10, 20], fov: 60 }}
        dpr={2} // Fixed High Quality for Capture
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
        <CameraController target={cameraTarget} setTarget={setCameraTarget} />
        <ExposureController exposure={config.exposure} />
      </Canvas>

      {/* UI Layer */}
      <UIOverlay
        config={config}
        setConfig={setConfig}
        activePanel={activePanel}
        setActivePanel={setActivePanel}
        digitRefs={digitRefs}
        onCameraMove={setCameraTarget}
        onResetCamera={() => setCameraTarget({ position: [20, 10, 20], target: [0, 0, 0] })}
      />
    </div>
  );
};

export default App;