
import React, { useEffect } from 'react';
import { Settings, Waves, FlaskConical, Camera, Play, Pause, RotateCcw, Hash, Fingerprint, LayoutGrid, Activity, Eye, Timer } from 'lucide-react';
import { SimulationState, SimulationMode, TranscendentalNumber, CameraTarget } from '../types';
import { PRIME_NUMBERS } from '../constants';
import { PRESETS } from '../presets';

interface UIProps {
  config: SimulationState;
  setConfig: React.Dispatch<React.SetStateAction<SimulationState>>;
  activePanel: string | null;
  setActivePanel: (p: string | null) => void;
  digitRefs: any; // Passed from App
  onCameraMove: (target: CameraTarget) => void;
  onResetCamera: () => void;
}

const NavItem: React.FC<{ icon: React.ReactNode, label: string, active: boolean, onClick: () => void }> = ({ icon, label, active, onClick }) => (
  <button
    onClick={onClick}
    className={`flex flex-col items-center justify-center w-[60px] h-[60px] rounded-2xl transition-all duration-300 relative overflow-hidden group ${active ? 'bg-primary text-white shadow-[0_0_20px_rgba(124,58,237,0.5)] scale-110' : 'bg-glass text-white/70 hover:bg-white/10'}`}
  >
    <div className="z-10 flex flex-col items-center">
      {React.cloneElement(icon as React.ReactElement, { size: 24, className: 'mb-1' })}
      <span className="text-[10px] font-bold uppercase tracking-wide">{label}</span>
    </div>
    {/* Hover glow effect */}
    <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
  </button>
);

const IconButtonWithTooltip: React.FC<{ onClick: () => void, icon: React.ReactNode, label: string, colorClass: string }> = ({ onClick, icon, label, colorClass }) => (
  <div className="relative group">
    <button onClick={onClick} className={`p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors ${colorClass}`}>
      {icon}
    </button>
    <div className="absolute bottom-full right-0 mb-2 px-2 py-1 bg-black/90 backdrop-blur border border-white/10 rounded text-[10px] font-bold text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl z-50">
      {label}
    </div>
  </div>
);

const Panel: React.FC<{ title: string, subtitle: string, active: boolean, onClose: () => void, children: React.ReactNode, onResetParticles?: () => void, onResetDefaults?: () => void }> = ({ title, subtitle, active, onClose, children, onResetParticles, onResetDefaults }) => {
  if (!active) return null;
  return (
    <div className="fixed bottom-[90px] left-0 md:left-10 right-0 md:right-auto md:w-[400px] w-full md:max-h-[calc(100vh-120px)] max-h-[60vh] glass-panel rounded-t-2xl md:rounded-2xl overflow-y-auto z-40 animate-in slide-in-from-bottom-10 fade-in duration-300">
      <div className="sticky top-0 bg-black/80 backdrop-blur-xl p-5 border-b border-white/10 z-10 flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight">{title}</h2>
          <p className="text-xs text-white/60 font-medium">{subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          {onResetParticles && (
            <IconButtonWithTooltip
              onClick={onResetParticles}
              icon={<RotateCcw size={14} />}
              label="Reset Particles"
              colorClass="text-emerald-400 hover:text-emerald-300 hover:shadow-[0_0_10px_rgba(52,211,153,0.3)]"
            />
          )}
          {onResetDefaults && (
            <IconButtonWithTooltip
              onClick={onResetDefaults}
              icon={<RotateCcw size={14} />}
              label="Reset Defaults"
              colorClass="text-rose-400 hover:text-rose-300 hover:shadow-[0_0_10px_rgba(251,113,133,0.3)]"
            />
          )}
          <button onClick={onClose} className="p-2 text-white/50 hover:text-white transition-colors text-2xl leading-none ml-2">&times;</button>
        </div>
      </div>
      <div className="p-5 space-y-6">
        {children}

        {/* Panel Branding Footer */}
        <div className="mt-8 pt-6 border-t border-white/10 flex flex-col items-center gap-1 opacity-80">
          <a href="https://github.com/mrdirno/nested-resonance-memory-archive" target="_blank" rel="noopener noreferrer" className="text-[10px] font-mono text-white tracking-widest hover:underline drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]">
            github.com/mrdirno/nested-resonance-memory-archive
          </a>
        </div>
      </div>
    </div>
  );
};

const Button: React.FC<{ children: React.ReactNode, variant?: 'primary' | 'secondary' | 'tertiary' | 'success', onClick?: () => void, className?: string }> = ({ children, variant = 'primary', onClick, className = '' }) => {
  const gradients = {
    primary: 'bg-gradient-to-br from-primary to-violet-700',
    secondary: 'bg-gradient-to-br from-secondary to-pink-600',
    tertiary: 'bg-gradient-to-br from-tertiary to-cyan-600',
    success: 'bg-gradient-to-br from-success to-emerald-600',
  };
  return (
    <button
      onClick={onClick}
      className={`w-full py-4 rounded-xl font-bold text-sm text-white shadow-lg active:scale-98 transition-transform relative overflow-hidden ${gradients[variant]} ${className}`}
    >
      <div className="relative z-10 flex items-center justify-center gap-2">{children}</div>
      <div className="absolute inset-0 bg-white/20 opacity-0 hover:opacity-100 transition-opacity" />
    </button>
  );
};


const EffectSlider: React.FC<{ label: string, value: number, onChange: (val: number) => void }> = ({ label, value, onChange }) => {
  const isActive = value > 0;
  const displayValue = Math.abs(value);

  return (
    <div className={`p-3 rounded-xl border transition-all ${isActive ? 'bg-black/40 border-white/10' : 'bg-black/10 border-white/5 opacity-60'}`}>
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-2">
          <button
            onClick={() => {
              // Toggle polarity
              if (value === 0) onChange(0.1); // Default to 10% if 0
              else onChange(value * -1);
            }}
            className={`p-1 rounded-full transition-colors ${isActive ? 'bg-primary text-white shadow-[0_0_10px_rgba(124,58,237,0.5)]' : 'bg-white/10 text-white/30 hover:bg-white/20'}`}
          >
            <Settings size={12} className={isActive ? "animate-spin-slow" : ""} />
          </button>
          <span className={`text-xs font-bold ${isActive ? 'text-white' : 'text-white/40'}`}>{label}</span>
        </div>
        <span className={`font-mono text-xs ${isActive ? 'text-primary' : 'text-white/30'}`}>{Math.round(displayValue * 100)}%</span>
      </div>
      <input
        type="range" min="0" max="1" step="0.01"
        value={displayValue}
        onChange={(e) => {
          const newVal = parseFloat(e.target.value);
          // If it was disabled (negative), keep it negative (disabled) while sliding? 
          // No, dragging usually implies "I want to use this". Let's make dragging auto-enable.
          onChange(newVal);
        }}
        className={`w-full h-1 rounded-lg appearance-none cursor-pointer ${isActive ? 'bg-white/10 accent-primary' : 'bg-white/5 accent-white/20'}`}
      />
    </div>
  );
};
export const UIOverlay: React.FC<UIProps> = (props) => {
  const { config, setConfig, activePanel, setActivePanel, digitRefs, onCameraMove, onResetCamera } = props;

  // Helper to update sliders without lag
  const handleRange = (key: keyof SimulationState, val: number) => {
    setConfig(prev => ({ ...prev, [key]: val }));
  };

  return (
    <>
      {/* App Header & Branding */}
      <div className="fixed top-0 left-0 w-full h-[100px] flex flex-col items-center justify-center z-20 pointer-events-none bg-gradient-to-b from-black/90 to-transparent pt-2">
        <h1 className="text-3xl md:text-4xl font-black uppercase tracking-tighter text-white drop-shadow-[0_0_15px_rgba(255,255,255,0.4)]">
          HELIOS <span className="text-white/30 font-light">|</span> BRIDGE
        </h1>
        <div className="mt-2 pointer-events-auto">
          <a href="https://github.com/mrdirno/nested-resonance-memory-archive" target="_blank" rel="noopener noreferrer" className="text-xs md:text-sm font-mono font-bold tracking-widest text-white hover:text-white/80 transition-colors drop-shadow-[0_0_10px_rgba(255,255,255,0.8)]">
            github.com/mrdirno/nested-resonance-memory-archive
          </a>
        </div>
      </div>

      {/* Controls Panel */}
      <Panel
        title="System Controls"
        subtitle="Configure potential field dynamics"
        active={activePanel === 'controls'}
        onClose={() => setActivePanel(null)}
        onResetParticles={() => setConfig(c => ({ ...c, resetTrigger: c.resetTrigger + 1 }))}
        onResetDefaults={() => setConfig(c => ({
          ...c,
          speed: 1,
          quality: 1,
          amplitude: 1,
          exposure: 0.5,
          particleCount: 100000
        }))}
      >
        <div className="flex gap-3">
          <Button onClick={() => setConfig(c => ({ ...c, isPlaying: !c.isPlaying }))}>
            {config.isPlaying ? <Pause size={18} /> : <Play size={18} />}
            {config.isPlaying ? 'PAUSE' : 'RESUME'}
          </Button>
          <Button variant="secondary" onClick={() => window.location.reload()}>
            <RotateCcw size={18} /> RELOAD APP
          </Button>
        </div>

        {/* Phase Duration Slider */}
        <div className="bg-white/5 p-3 rounded-xl border border-white/10">
          <div className="flex justify-between text-sm font-bold mb-2 text-white/80">
            <span className="flex items-center gap-2"><Timer size={14} /> Phase Duration</span>
            <span className="font-mono text-primary">{(1000 / config.speed).toFixed(0)} ms</span>
          </div>
          <input
            type="range" min="16" max="3000" step="10"
            value={1000 / config.speed}
            onChange={(e) => handleRange('speed', 1000 / parseFloat(e.target.value))}
            className="w-full"
          />
          <div className="flex justify-between text-[10px] text-white/40 mt-1 uppercase font-bold">
            <span>Fast (16ms)</span>
            <span>Slow (3s)</span>
          </div>
        </div>

        <div className="flex gap-2 p-1 bg-black/30 rounded-xl border border-white/5">
          {[1, 5, 15].map(s => (
            <button
              key={s}
              onClick={() => setConfig(c => ({ ...c, speed: s }))}
              className={`flex-1 py-2 rounded-lg text-xs font-bold transition ${config.speed === s ? 'bg-tertiary text-black shadow-lg' : 'text-white/50 hover:text-white'}`}
            >
              {s === 1 ? 'SLOW' : s === 5 ? 'FAST' : 'ULTRA'}
            </button>
          ))}
        </div>

        <div className="space-y-5 mt-2">
          {/* The Reality Slider */}
          <div className="bg-white/5 p-3 rounded-xl border border-white/10">
            <div className="flex justify-between text-sm font-bold mb-2 text-secondary">
              <span className="flex items-center gap-2"><Eye size={14} /> Existence Threshold</span>
              <span className="font-mono">{config.exposure.toFixed(2)}</span>
            </div>
            <input
              type="range" min="0.0" max="3.0" step="0.05"
              value={config.exposure}
              onChange={(e) => handleRange('exposure', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-[10px] text-white/40 mt-1 uppercase font-bold">
              <span>Void</span>
              <span>Reality</span>
              <span>Overload</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-sm font-semibold mb-2">
              <span>Particle Density</span>
              <span className="text-primary font-mono">{config.particleCount.toLocaleString()}</span>
            </div>
            <input
              type="range" min="10000" max="1000000" step="10000"
              value={config.particleCount}
              onChange={(e) => handleRange('particleCount', parseInt(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <div className="flex justify-between text-sm font-semibold mb-2">
              <span>Visual Quality</span>
              <span className="text-primary font-mono">{config.quality.toFixed(1)}x</span>
            </div>
            <input
              type="range" min="0.1" max="2.0" step="0.1"
              value={config.quality}
              onChange={(e) => handleRange('quality', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>

          <div>
            <div className="flex justify-between text-sm font-semibold mb-2">
              <span>Field Amplitude</span>
              <span className="text-primary font-mono">{config.amplitude.toFixed(1)}x</span>
            </div>
            <input
              type="range" min="0.1" max="100" step="0.1"
              value={config.amplitude}
              onChange={(e) => handleRange('amplitude', parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 pt-2">
          {Object.values(SimulationMode).map(mode => (
            <button
              key={mode}
              onClick={() => setConfig(c => ({ ...c, mode }))}
              className={`py-3 rounded-xl text-xs font-bold uppercase border transition-all ${config.mode === mode ? 'bg-success/20 border-success text-success' : 'bg-black/30 border-transparent text-white/60'}`}
            >
              {mode}
            </button>
          ))}
        </div>
      </Panel>

      {/* Waves Panel */}
      <Panel
        title="Potential Field"
        subtitle="2500-digit sequences driving Ψ(r,t)"
        active={activePanel === 'waves'}
        onClose={() => setActivePanel(null)}
        onResetParticles={() => setConfig(c => ({ ...c, resetTrigger: c.resetTrigger + 1 }))}
        onResetDefaults={() => setConfig(c => ({
          ...c,
          mapping: { a: TranscendentalNumber.PHI, b: TranscendentalNumber.PHI, c: TranscendentalNumber.PI },
          stagger: { a: 0, b: 239, c: 478 }
        }))}
      >
        <div className="relative overflow-hidden rounded-xl bg-black/50 border border-white/10 p-4 font-mono text-sm leading-relaxed">
          {/* The gradient background for wave display */}
          <div className="absolute inset-0 bg-gradient-to-tr from-primary/20 via-secondary/20 to-tertiary/20 opacity-50 animate-pulse" />
          <div className="relative z-10 space-y-2">
            <div className="flex items-center gap-3">
              <span className="text-primary font-bold w-6">A:</span>
              <span ref={digitRefs.m} className="bg-primary text-black font-bold px-2 rounded shadow-[0_0_10px_rgba(124,58,237,0.5)]">0</span>
              <span className="text-white/40 text-xs truncate">...Sequence A...</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-secondary font-bold w-6">B:</span>
              <span ref={digitRefs.n} className="bg-secondary text-black font-bold px-2 rounded shadow-[0_0_10px_rgba(236,72,153,0.5)]">0</span>
              <span className="text-white/40 text-xs truncate">...Sequence B...</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-tertiary font-bold w-6">C:</span>
              <span ref={digitRefs.p} className="bg-tertiary text-black font-bold px-2 rounded shadow-[0_0_10px_rgba(6,182,212,0.5)]">0</span>
              <span className="text-white/40 text-xs truncate">...Sequence C...</span>
            </div>
          </div>
        </div>

        <div className="bg-black/30 rounded-xl p-4 border border-white/5 space-y-4">
          <div className="text-sm font-bold text-tertiary mb-2">Transcendental Mapping</div>
          {['a', 'b', 'c'].map(dim => (
            <div key={dim} className="flex justify-between items-center">
              <span className="uppercase text-xs font-bold text-white/70">Dimension {dim}</span>
              <select
                value={config.mapping[dim as keyof typeof config.mapping]}
                onChange={(e) => setConfig(c => ({ ...c, mapping: { ...c.mapping, [dim]: e.target.value } }))}
                className="bg-black border border-white/20 rounded px-3 py-1 text-xs text-white outline-none focus:border-primary"
              >
                {Object.values(TranscendentalNumber).map(t => <option key={t} value={t}>{t.toUpperCase()}</option>)}
              </select>
            </div>
          ))}
        </div>

        <div className="bg-black/30 rounded-xl p-4 border border-white/5">
          <div className="flex justify-between text-sm font-bold mb-2">
            <span>Prime Spacing</span>
            <span className="text-primary">{config.stagger.b}</span>
          </div>
          <input
            type="range" min="0" max={PRIME_NUMBERS.length - 1}
            onChange={(e) => {
              const val = PRIME_NUMBERS[parseInt(e.target.value)];
              setConfig(c => ({ ...c, stagger: { a: 0, b: val, c: val * 2 } }));
            }}
            className="w-full"
          />
          <div className="mt-4 grid grid-cols-2 gap-3 text-center">
            <div className="bg-white/5 rounded p-2">
              <div className="text-[10px] uppercase text-white/50">Total Energy</div>
              <div ref={digitRefs.energy} className="text-xl font-mono font-bold text-secondary">0</div>
            </div>
            <div className="bg-white/5 rounded p-2">
              <div className="text-[10px] uppercase text-white/50">Cycle Pos</div>
              <div ref={digitRefs.pos} className="text-xl font-mono font-bold text-primary">0</div>
            </div>
          </div>
        </div>
      </Panel>

      {/* Labs Panel */}
      <Panel
        title="Research Labs"
        subtitle="Advanced N-particle dynamics experiments"
        active={activePanel === 'labs'}
        onClose={() => setActivePanel(null)}
        onResetParticles={() => setConfig(c => ({ ...c, resetTrigger: c.resetTrigger + 1 }))}
        onResetDefaults={() => setConfig(c => ({
          ...c,
          extensions: {
            crystal: { threeFold: 0, sixFold: 0, lattice: 0 },
            harmonic: { commaSpiral: 0, perfectFifths: 0, equalTemp: 0 },
            topology: { trefoil: 0, torus: 0, hopf: 0 }
          }
        }))}
      >
        <div className="space-y-6">
          <div className="bg-black/30 p-4 rounded-xl border border-white/5">
            <div className="text-tertiary font-bold text-sm mb-3 flex items-center gap-2"><Fingerprint size={16} /> Crystallographic Symmetry</div>
            <div className="space-y-2">
              <EffectSlider label="3-Fold (120°) Symmetry" value={config.extensions.crystal.threeFold} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.CRYSTAL : c.mode, extensions: { ...c.extensions, crystal: { ...c.extensions.crystal, threeFold: v } } }))} />
              <EffectSlider label="6-Fold (60°) Symmetry" value={config.extensions.crystal.sixFold} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.CRYSTAL : c.mode, extensions: { ...c.extensions, crystal: { ...c.extensions.crystal, sixFold: v } } }))} />
              <EffectSlider label="Hexagonal Lattice" value={config.extensions.crystal.lattice} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.CRYSTAL : c.mode, extensions: { ...c.extensions, crystal: { ...c.extensions.crystal, lattice: v } } }))} />
            </div>
          </div>

          <div className="bg-black/30 p-4 rounded-xl border border-white/5">
            <div className="text-secondary font-bold text-sm mb-3 flex items-center gap-2"><Activity size={16} /> Pythagorean Harmonics</div>
            <div className="space-y-2">
              <EffectSlider label="Comma Spiral (23.46¢)" value={config.extensions.harmonic.commaSpiral} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.HARMONIC : c.mode, extensions: { ...c.extensions, harmonic: { ...c.extensions.harmonic, commaSpiral: v } } }))} />
              <EffectSlider label="Perfect Fifth Stack" value={config.extensions.harmonic.perfectFifths} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.HARMONIC : c.mode, extensions: { ...c.extensions, harmonic: { ...c.extensions.harmonic, perfectFifths: v } } }))} />
            </div>
          </div>

          <div className="bg-black/30 p-4 rounded-xl border border-white/5">
            <div className="text-primary font-bold text-sm mb-3 flex items-center gap-2"><Hash size={16} /> Topological Forms</div>
            <div className="space-y-2">
              <EffectSlider label="Trefoil Knot (3,2)" value={config.extensions.topology.trefoil} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.TOPOLOGY : c.mode, extensions: { ...c.extensions, topology: { ...c.extensions.topology, trefoil: v } } }))} />
              <EffectSlider label="Toroidal Attractor" value={config.extensions.topology.torus} onChange={(v) => setConfig(c => ({ ...c, mode: v > 0 ? SimulationMode.TOPOLOGY : c.mode, extensions: { ...c.extensions, topology: { ...c.extensions.topology, torus: v } } }))} />
            </div>
          </div>
        </div>
      </Panel>

      {/* Camera Panel */}
      <Panel title="Camera Control" subtitle="Navigate N-particle phase space" active={activePanel === 'camera'} onClose={() => setActivePanel(null)}>
        <div className="grid grid-cols-2 gap-3 mb-6">
          <button onClick={() => onCameraMove({ position: [0, 30, 0.1], target: [0, 0, 0] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Top View</button>
          <button onClick={() => onCameraMove({ position: [30, 0, 0], target: [0, 0, 0] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Side View</button>
          <button onClick={() => onCameraMove({ position: [20, 20, 20], target: [0, 0, 0] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Isometric</button>
          <button onClick={() => onCameraMove({ position: [0.1, 0.1, 0.1], target: [10, 10, 10] })} className="p-4 bg-white/5 border border-white/10 hover:bg-primary/20 hover:border-primary/50 rounded-xl text-sm font-bold transition">Core View</button>
        </div>

        <Button variant="secondary" onClick={onResetCamera}>Reset Camera</Button>

        <div className="mt-6 p-4 bg-black/30 rounded-xl border border-white/5">
          <div className="text-xs text-white/40 uppercase mb-2">Camera Telemetry</div>
          <div className="grid grid-cols-2 gap-4 font-mono text-sm">
            <div>X: <span className="text-tertiary">0.00</span></div>
            <div>Y: <span className="text-tertiary">0.00</span></div>
            <div>Z: <span className="text-tertiary">0.00</span></div>
            <div>D: <span className="text-primary">25.0</span></div>
          </div>
        </div>
      </Panel>

      {/* Navigation Bar */}
      <div className="fixed bottom-0 left-0 w-full h-[80px] bg-glass backdrop-blur-xl border-t border-white/10 flex justify-around items-center px-4 z-50">
        <NavItem icon={<Settings />} label="Control" active={activePanel === 'controls'} onClick={() => setActivePanel(activePanel === 'controls' ? null : 'controls')} />
        <NavItem icon={<Waves />} label="Fields" active={activePanel === 'waves'} onClick={() => setActivePanel(activePanel === 'waves' ? null : 'waves')} />
        <NavItem icon={<FlaskConical />} label="Labs" active={activePanel === 'labs'} onClick={() => setActivePanel(activePanel === 'labs' ? null : 'labs')} />
        <NavItem icon={<Camera />} label="Camera" active={activePanel === 'camera'} onClick={() => setActivePanel(activePanel === 'camera' ? null : 'camera')} />
      </div>
    </>
  );
};