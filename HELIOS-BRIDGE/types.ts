
export enum SimulationMode {
  STANDARD = 'standard',
  CRYSTAL = 'crystal',
  HARMONIC = 'harmonic',
  TOPOLOGY = 'topology'
}

export enum TranscendentalNumber {
  PI = 'pi',
  E = 'e',
  SQRT2 = 'sqrt2',
  PHI = 'phi'
}

export interface SimulationState {
  particleCount: number;
  isPlaying: boolean;
  speed: number; // Continuous value (Steps per second)
  quality: number; // 0.1 to 2.0
  amplitude: number; // Potential field force multiplier
  exposure: number; // New: Tone mapping exposure (The "Existence Threshold")
  contrast: number; // New: Visual hardness
  mode: SimulationMode;

  // Sequence Mapping
  mapping: {
    a: TranscendentalNumber;
    b: TranscendentalNumber;
    c: TranscendentalNumber;
  };

  // Stagger Offsets
  stagger: {
    a: number;
    b: number;
    c: number;
  };

  // Extensions
  extensions: {
    crystal: { threeFold: number; sixFold: number; lattice: number };
    harmonic: { commaSpiral: number; perfectFifths: number; equalTemp: number };
    topology: { trefoil: number; torus: number; hopf: number };
  };

  // Camera Stats (Read-only for UI)
  cameraStats: {
    x: string;
    y: string;
    z: string;
    dist: string;
  };

  // Signal to reset particle physics without changing config
  resetTrigger: number;
}

export interface CameraTarget {
  position: [number, number, number];
  target: [number, number, number];
}