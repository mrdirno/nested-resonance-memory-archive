import { SimulationState, SimulationMode, TranscendentalNumber } from './types';

export type SimulationPreset = Partial<SimulationState>;

export const PRESETS: Record<string, SimulationPreset> = {
    DEFAULT: {
        particleCount: 350000,
        speed: 1,
        quality: 0.7,
        amplitude: 1.0,
        exposure: 1.0,
        contrast: 1.0,
        mode: SimulationMode.STANDARD,
        stagger: { a: 0, b: 239, c: 478 },
        mapping: {
            a: TranscendentalNumber.PHI,
            b: TranscendentalNumber.PHI,
            c: TranscendentalNumber.PI
        }
    },
    HIGH_ENERGY: {
        particleCount: 238999, // Prime-ish number for interference
        speed: 5,
        amplitude: 50.0,
        exposure: 0.4,
        quality: 0.5, // Lower quality for performance at high speed
        mode: SimulationMode.STANDARD
    },
    CRYSTAL_focus: {
        particleCount: 150000,
        speed: 0.5,
        amplitude: 2.0,
        exposure: 1.2,
        mode: SimulationMode.CRYSTAL,
        extensions: {
            crystal: { threeFold: true, sixFold: true, lattice: false },
            harmonic: { commaSpiral: false, perfectFifths: false, equalTemp: false },
            topology: { trefoil: false, torus: false, hopf: false }
        }
    }
};
