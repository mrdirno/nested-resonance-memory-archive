
import React, { useMemo, useRef, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { SimulationState, SimulationMode } from '../types';
import { DIGIT_SEQUENCES } from '../constants';

const SIMULATION_EXTENT = 15;
const WAVE_STRENGTH = 2.5;
const VELOCITY_DAMPING = 0.98;
const MAX_CYCLE = 2500;

interface ParticleSystemProps {
  config: SimulationState;
  // We pass refs for direct DOM updates to avoid React render cycles
  digitRefs?: {
    m: React.MutableRefObject<HTMLElement | null>;
    n: React.MutableRefObject<HTMLElement | null>;
    p: React.MutableRefObject<HTMLElement | null>;
    pos: React.MutableRefObject<HTMLElement | null>;
    energy: React.MutableRefObject<HTMLElement | null>;
  };
}

export const ParticleSystem: React.FC<ParticleSystemProps> = ({ config, digitRefs }) => {
  const meshRef = useRef<THREE.Points>(null);
  const velocitiesRef = useRef<Float32Array | null>(null);
  const currentPosRef = useRef(0);
  const lastFrameTimeRef = useRef(0);

  // -- Initialization --
  const { positions, colors, velocities } = useMemo(() => {
    const count = config.particleCount;
    const pos = new Float32Array(count * 3);
    const col = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);

    const gridSize = Math.ceil(Math.cbrt(count));
    
    for (let i = 0; i < count; i++) {
      const i3 = i * 3;
      const xi = i % gridSize;
      const yi = Math.floor(i / gridSize) % gridSize;
      const zi = Math.floor(i / (gridSize * gridSize));
      
      const spacing = (SIMULATION_EXTENT * 1.8) / gridSize;
      // Add some jitter like original
      pos[i3] = (xi - gridSize/2) * spacing + (Math.random() - 0.5) * spacing * 0.5;
      pos[i3+1] = (yi - gridSize/2) * spacing + (Math.random() - 0.5) * spacing * 0.5;
      pos[i3+2] = (zi - gridSize/2) * spacing + (Math.random() - 0.5) * spacing * 0.5;
      
      // Initial colors
      col[i3] = 0.4;
      col[i3+1] = 0.3;
      col[i3+2] = 0.7;
    }

    return { positions: pos, colors: col, velocities: vel };
  }, [config.particleCount]);

  // Reset logic
  useEffect(() => {
    velocitiesRef.current = velocities;
    currentPosRef.current = 0;
  }, [velocities]);

  // -- Physics Helpers --
  
  // Optimized digit retrieval to match original logic exactly
  const getDigit = (dimIndex: number, pos: number) => {
    let offset = 0;
    let seqKey = '';

    if (dimIndex === 0) { offset = config.stagger.a; seqKey = config.mapping.a; }
    else if (dimIndex === 1) { offset = config.stagger.b; seqKey = config.mapping.b; }
    else { offset = config.stagger.c; seqKey = config.mapping.c; }

    const staggeredPos = Math.max(0, (pos + offset) % MAX_CYCLE);
    const seq = DIGIT_SEQUENCES[seqKey];
    
    // Fallback matching original logic
    if (!seq) return (staggeredPos + dimIndex) % 10;
    
    const digitChar = seq[staggeredPos % seq.length];
    return parseInt(digitChar || '0');
  };

  // -- Main Loop --
  useFrame((state) => {
    if (!meshRef.current || !velocitiesRef.current) return;
    
    const now = state.clock.elapsedTime * 1000;
    const geometry = meshRef.current.geometry;
    const posAttr = geometry.attributes.position;
    const colAttr = geometry.attributes.color;
    const positions = posAttr.array as Float32Array;
    const colors = colAttr.array as Float32Array;
    const vels = velocitiesRef.current;

    // 1. Time Step & Sequence Update
    if (config.isPlaying && now - lastFrameTimeRef.current > (1000 / config.speed)) {
      currentPosRef.current++;
      lastFrameTimeRef.current = now;

      // Direct DOM update for UI to avoid React overhead
      if (digitRefs) {
        const m = getDigit(0, currentPosRef.current);
        const n = getDigit(1, currentPosRef.current);
        const p = getDigit(2, currentPosRef.current);
        const e = m*m + n*n + p*p;
        
        if(digitRefs.m.current) digitRefs.m.current.innerText = m.toString();
        if(digitRefs.n.current) digitRefs.n.current.innerText = n.toString();
        if(digitRefs.p.current) digitRefs.p.current.innerText = p.toString();
        if(digitRefs.pos.current) digitRefs.pos.current.innerText = currentPosRef.current.toLocaleString();
        if(digitRefs.energy.current) digitRefs.energy.current.innerText = e.toString();
      }
    }

    // 2. Physics Constants for this frame
    const mDigit = getDigit(0, currentPosRef.current);
    const nDigit = getDigit(1, currentPosRef.current);
    const pDigit = getDigit(2, currentPosRef.current);

    const energySum = mDigit*mDigit + nDigit*nDigit + pDigit*pDigit;
    const standardizedMode = energySum / 3;
    
    const waveNumber = Math.PI / SIMULATION_EXTENT;
    const phaseM = (mDigit / 9) * Math.PI;
    const phaseN = (nDigit / 9) * Math.PI;
    const phaseP = (pDigit / 9) * Math.PI;

    // Pre-calc commonly used values
    const activeMode = config.mode;
    const { crystal, harmonic, topology } = config.extensions;
    const isCrystal = activeMode === SimulationMode.CRYSTAL;
    const isHarmonic = activeMode === SimulationMode.HARMONIC;
    const isTopology = activeMode === SimulationMode.TOPOLOGY;

    // Analytical Gradient factors (Calculus based physics for better performance/smoothness)
    const forceMultiplier = WAVE_STRENGTH * standardizedMode * config.amplitude;

    // 3. Particle Loop
    for (let i = 0; i < config.particleCount; i++) {
      const i3 = i * 3;
      let x = positions[i3];
      let y = positions[i3+1];
      let z = positions[i3+2];

      let forceX = 0, forceY = 0, forceZ = 0;

      // --- Mode Specific Forces ---
      if (isCrystal) {
        if (crystal.threeFold) {
          const r = Math.sqrt(x*x+y*y);
          const angle = Math.atan2(y, x);
          const snap = Math.round(angle / 2.0944) * 2.0944; // 2pi/3
          forceX += (r * Math.cos(snap) - x) * 0.1;
          forceY += (r * Math.sin(snap) - y) * 0.1;
        }
        if (crystal.sixFold) {
           const r = Math.sqrt(x*x+y*y);
           const angle = Math.atan2(y, x);
           const snap = Math.round(angle / 1.0472) * 1.0472; // 2pi/6
           forceX += (r * Math.cos(snap) - x) * 0.05;
           forceY += (r * Math.sin(snap) - y) * 0.05;
        }
        if (crystal.lattice) {
           const a = SIMULATION_EXTENT / 3;
           const ni = Math.round(x / a);
           const nj = Math.round(y / (a * 0.866));
           forceX += (a * ni - x) * 0.02;
           forceY += (a * 0.866 * nj - y) * 0.02;
        }
      } else if (isHarmonic) {
        if (harmonic.commaSpiral) {
           const spiralPhase = currentPosRef.current * 0.0011;
           const sf = 0.1 * Math.sin(spiralPhase);
           forceX += y * sf;
           forceY += -x * sf;
        }
        if (harmonic.perfectFifths) {
           const ratio = 1.5;
           forceX += Math.sin(x * ratio * waveNumber) * 0.1;
           forceY += Math.sin(y * ratio * waveNumber) * 0.1;
           forceZ += Math.sin(z * ratio * waveNumber) * 0.1;
        }
      } else if (isTopology) {
        if (topology.trefoil) {
           const t = Math.atan2(y, x) * 0.15915;
           const s = SIMULATION_EXTENT * 0.5;
           const t2 = t * 6.283;
           const kx = s * (Math.sin(t2) + 2 * Math.sin(2*t2));
           const ky = s * (Math.cos(t2) - 2 * Math.cos(2*t2));
           const kz = s * (-Math.sin(3*t2));
           forceX += (kx - x) * 0.01;
           forceY += (ky - y) * 0.01;
           forceZ += (kz - z) * 0.01;
        }
        if (topology.torus) {
           const R = SIMULATION_EXTENT * 0.8;
           const r = SIMULATION_EXTENT * 0.3;
           const theta = Math.atan2(y, x);
           const d = Math.sqrt(x*x+y*y);
           const phi = Math.atan2(z, d - R);
           const tr = R + r * Math.cos(phi);
           const tx = tr * Math.cos(theta);
           const ty = tr * Math.sin(theta);
           const tz = r * Math.sin(phi);
           if ((x-tx)**2 + (y-ty)**2 + (z-tz)**2 > r*r) {
             forceX += (tx - x) * 0.02;
             forceY += (ty - y) * 0.02;
             forceZ += (tz - z) * 0.02;
           }
        }
      }

      // --- Wave Potential (The core logic - Analytical Gradient) ---
      // Potential V = cos(kx*x) * cos(ky*y) * cos(kz*z)
      // Force F = -Gradient(V)
      // Fx = -dV/dx = kx * sin(kx*x) * cos(ky*y) * cos(kz*z)
      
      const wx = mDigit * x * waveNumber + phaseM;
      const wy = nDigit * y * waveNumber + phaseN;
      const wz = pDigit * z * waveNumber + phaseP;
      
      const cx = Math.cos(wx);
      const cy = Math.cos(wy);
      const cz = Math.cos(wz);
      
      const sx = Math.sin(wx);
      const sy = Math.sin(wy);
      const sz = Math.sin(wz);

      // Apply analytical forces (Exact derivatives)
      // Fx = (m * k) * sin(...) * cos(...) * cos(...)
      // Using waveNumber as k factor
      const k = waveNumber * forceMultiplier * 0.1; // 0.1 scaling factor for stability

      forceX += (mDigit * sx * cy * cz) * k;
      forceY += (cx * nDigit * sy * cz) * k;
      forceZ += (cx * cy * pDigit * sz) * k;

      // --- Integration ---
      vels[i3]   += forceX;
      vels[i3+1] += forceY;
      vels[i3+2] += forceZ;

      vels[i3]   *= VELOCITY_DAMPING;
      vels[i3+1] *= VELOCITY_DAMPING;
      vels[i3+2] *= VELOCITY_DAMPING;

      x += vels[i3];
      y += vels[i3+1];
      z += vels[i3+2];

      // Boundary
      const d2 = x*x + y*y + z*z;
      if (d2 > SIMULATION_EXTENT*SIMULATION_EXTENT) {
        const scale = SIMULATION_EXTENT / Math.sqrt(d2);
        x *= scale; y *= scale; z *= scale;
        vels[i3] *= -0.5; vels[i3+1] *= -0.5; vels[i3+2] *= -0.5;
      }

      positions[i3] = x;
      positions[i3+1] = y;
      positions[i3+2] = z;

      // --- Coloring ---
      // Using the same aesthetic math as original
      const brightness = config.quality * 0.7;
      if (isCrystal) {
        const ang = Math.atan2(y, x);
        const an = (ang + Math.PI) * 0.15915;
        colors[i3] = 0.3 + an * brightness;
        colors[i3+1] = 0.2 + (1-an) * brightness * 0.8;
        colors[i3+2] = 0.4 + Math.abs(z/SIMULATION_EXTENT) * brightness;
      } else if (isHarmonic) {
         const ph = (x+y+z)*0.1;
         colors[i3] = 0.5 + 0.5*Math.sin(ph)*brightness;
         colors[i3+1] = 0.5 + 0.5*Math.sin(ph+2.09)*brightness;
         colors[i3+2] = 0.5 + 0.5*Math.sin(ph+4.18)*brightness;
      } else if (isTopology) {
         const r = Math.sqrt(x*x+y*y);
         const th = Math.atan2(y,x);
         colors[i3] = 0.3 + (r/SIMULATION_EXTENT)*brightness;
         colors[i3+1] = 0.3 + Math.abs(Math.sin(th*3))*brightness;
         colors[i3+2] = 0.3 + Math.abs(z/SIMULATION_EXTENT)*brightness;
      } else {
         // Standard mode colors based on coordinate resonance
         colors[i3] = 0.3 + Math.abs(Math.cos(mDigit * x * 0.2)) * brightness;
         colors[i3+1] = 0.2 + Math.abs(Math.cos(nDigit * y * 0.2)) * brightness * 0.8;
         colors[i3+2] = 0.4 + Math.abs(Math.cos(pDigit * z * 0.2)) * brightness * 0.9;
      }
    }

    posAttr.needsUpdate = true;
    colAttr.needsUpdate = true;
  });

  // Adjust opacity logic to be drastically lower for high particle counts (above 100k)
  // This ensures the additive blending doesn't result in a solid white screen.
  // Base opacity is around 0.02 for 350k particles.
  const baseOpacity = 0.6 + (config.quality * 0.2);
  // Inverse square root scaling is often better for density preservation
  const densityFactor = Math.sqrt(config.particleCount / 10000);
  const opacity = Math.max(0.02, baseOpacity / densityFactor);
  
  const size = 0.08 * Math.sqrt(50000 / config.particleCount) * config.quality;

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={positions.length / 3} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-color" count={colors.length / 3} array={colors} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial 
        vertexColors 
        size={size} 
        transparent 
        opacity={opacity} 
        blending={THREE.AdditiveBlending} 
        sizeAttenuation={true}
        depthWrite={false}
      />
    </points>
  );
};

export const Boundary = () => {
  return (
    <lineSegments>
      <edgesGeometry args={[new THREE.BoxGeometry(SIMULATION_EXTENT * 2, SIMULATION_EXTENT * 2, SIMULATION_EXTENT * 2)]} />
      <lineBasicMaterial color="#4A90E2" transparent opacity={0.3} />
    </lineSegments>
  );
};
