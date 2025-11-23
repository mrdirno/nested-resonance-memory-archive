import React, { useMemo } from 'react';
import * as THREE from 'three';
import { Instance, Instances } from '@react-three/drei';

interface EvolvedArrayProps {
  phases: number[]; // 0 to 2pi
}

export const EvolvedArray: React.FC<EvolvedArrayProps> = ({ phases }) => {
  // Define the 8x8 grid geometry
  const emitters = useMemo(() => {
    const items = [];
    for (let i = 0; i < 64; i++) {
      const row = Math.floor(i / 8);
      const col = i % 8;
      // Center the 8x8 grid around (0,0,0)
      // Spacing 10mm
      const x = (col - 3.5) * 10;
      const y = (row - 3.5) * 10;
      const z = 0;
      items.push({ position: [x, y, z], index: i });
    }
    return items;
  }, []);

  return (
    <group>
        <Instances range={64}>
            <sphereGeometry args={[2, 16, 16]} />
            <meshStandardMaterial />
            {emitters.map((emitter, i) => {
                // Color based on phase (0 to 2pi) -> Hue
                // Normalize phase 0-2pi to 0-1
                const phase = phases && phases[i] !== undefined ? phases[i] : 0;
                const normalizedPhase = phase / (2 * Math.PI);
                const color = new THREE.Color().setHSL(normalizedPhase, 1.0, 0.5);

                return (
                    <Instance
                        key={i}
                        position={[emitter.position[0] as number, emitter.position[1] as number, emitter.position[2] as number]}
                        color={color}
                    />
                );
            })}
        </Instances>
    </group>
  );
};