import React from 'react';
import { LayoutMode } from '../types';
import { Minus, Plus, RefreshCw } from 'lucide-react';

interface AdvancedControlsProps {
  layoutMode: LayoutMode;
  setLayoutMode: (m: LayoutMode) => void;
  count: number;
  setCount: (n: number) => void;
  aspect: number;
  setAspect: (a: number) => void;
  gutter: number;
  setGutter: (g: number) => void;
  setSeed: (s: number) => void;
}

export const AdvancedControls: React.FC<AdvancedControlsProps> = ({
  layoutMode, setLayoutMode, count, setCount, aspect, setAspect, gutter, setGutter, setSeed
}) => {
  
  return (
    <div className="p-4 border-t border-white/10 bg-[#0e0e0e] grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 text-xs">
      
      {/* LAYOUT GROUP */}
      <div className="flex flex-col gap-2">
        <h3 className="text-gray-500 font-bold tracking-widest uppercase text-[9px]">Layout Mode</h3>
        <div className="flex rounded bg-[#111] p-1 border border-[#222]">
          {(['minimal', 'balanced', 'complex'] as const).map(m => (
            <button
              key={m}
              onClick={() => setLayoutMode(m)}
              className={`flex-1 py-2 rounded uppercase font-bold text-[9px] ${layoutMode === m ? 'bg-emerald-600 text-white' : 'text-gray-500 hover:text-white'}`}
            >
              {m}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between mt-2">
           <span className="text-gray-400">Fragment Count</span>
           <div className="flex items-center gap-2 bg-[#111] border border-[#222] rounded px-2 py-1">
             <button onClick={() => setCount(Math.max(1, count - 1))}><Minus size={12}/></button>
             <span className="w-6 text-center font-bold">{count}</span>
             <button onClick={() => setCount(count + 1)}><Plus size={12}/></button>
           </div>
        </div>
        
        <button 
           onClick={() => setSeed(Date.now())}
           className="mt-2 w-full bg-[#111] border border-[#222] py-2 rounded flex items-center justify-center gap-2 hover:bg-white hover:text-black transition-colors"
        >
          <RefreshCw size={12}/> REMIX SEED
        </button>
      </div>

      {/* DIMENSIONS GROUP */}
      <div className="flex flex-col gap-2">
        <h3 className="text-gray-500 font-bold tracking-widest uppercase text-[9px]">Canvas</h3>
        <div className="grid grid-cols-4 gap-1">
             {[{v:0.666, l:'2:3'}, {v:1, l:'1:1'}, {v:1.77, l:'16:9'}, {v:0.5625, l:'9:16'}].map(a => (
                 <button 
                   key={a.l} 
                   onClick={() => setAspect(a.v)} 
                   className={`py-2 rounded font-bold ${Math.abs(aspect - a.v) < 0.01 ? 'bg-emerald-600 text-white' : 'bg-[#111] border border-[#222] text-gray-500'}`}
                 >
                     {a.l}
                 </button>
             ))}
        </div>
        
        <div className="mt-2">
           <div className="flex justify-between mb-1">
             <span className="text-gray-400">Gutter / Padding</span>
             <span className="text-gray-500">{(gutter * 100).toFixed(1)}%</span>
           </div>
           <input 
             type="range" 
             min="0" max="0.05" step="0.001" 
             value={gutter} 
             onChange={(e) => setGutter(parseFloat(e.target.value))}
             className="w-full accent-emerald-500 h-1 bg-gray-800 rounded-lg appearance-none cursor-pointer"
           />
        </div>
      </div>

      {/* STYLE GROUP (Placeholder for now) */}
      <div className="flex flex-col gap-2 opacity-50 pointer-events-none">
        <h3 className="text-gray-500 font-bold tracking-widest uppercase text-[9px]">Style (Coming Soon)</h3>
        <div className="flex gap-2">
           <div className="w-8 h-8 rounded-full bg-white border border-gray-600"></div>
           <div className="w-8 h-8 rounded-full bg-black border border-gray-600"></div>
           <div className="w-8 h-8 rounded-full bg-[#f5f5f5] border border-gray-600"></div>
        </div>
      </div>
      
    </div>
  );
};
