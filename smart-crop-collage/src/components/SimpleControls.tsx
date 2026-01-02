import React from 'react';
import { Layout, Grid, AlertCircle, Plus, Minus, RefreshCw } from 'lucide-react';
import { LayoutMode } from '../types';

interface SimpleControlsProps {
  layoutMode: LayoutMode;
  setLayoutMode: (m: LayoutMode) => void;
  count: number;
  setCount: (fn: (prev: number) => number) => void;
  setSeed: (s: number) => void;
  hasImages: boolean;
}

export const SimpleControls: React.FC<SimpleControlsProps> = ({
  layoutMode, setLayoutMode, count, setCount, setSeed, hasImages
}) => {
  
  const adjustCount = (delta: number) => {
    setCount(prev => {
        const step = prev > 25 ? (delta * 2) : delta;
        return Math.max(1, prev + step);
    });
  };

  return (
     <div className="p-4 flex flex-col gap-3">
         <div className="grid grid-cols-3 gap-2">
             {[
                 { id: 'minimal', label: 'MINIMAL', icon: Layout },
                 { id: 'balanced', label: 'BALANCED', icon: Grid },
                 { id: 'complex', label: 'COMPLEX', icon: AlertCircle }, 
             ].map(m => (
                 <button
                    key={m.id}
                    disabled={!hasImages}
                    onClick={() => setLayoutMode(m.id as LayoutMode)}
                    className={`h-20 border rounded-xl flex flex-col items-center justify-center gap-1 transition-all active:scale-95 ${layoutMode === m.id ? 'bg-white text-black border-white' : 'bg-[#111] border-[#222] text-gray-500 hover:bg-[#161616]'}`}
                 >
                    <m.icon size={20} />
                    <span className="text-[9px] font-black tracking-widest mt-1">{m.label}</span>
                 </button>
             ))}
         </div>

         <div className="flex gap-2 h-14">
             <div className="flex-1 bg-[#111] border border-[#222] rounded-xl flex items-center justify-between px-1">
                <button disabled={!hasImages} onClick={() => adjustCount(-1)} className="w-12 h-full flex items-center justify-center text-gray-500 hover:text-white"><Minus size={20}/></button>
                <div className="text-center">
                    <span className="block text-xl font-bold leading-none">{count}</span>
                    <span className="block text-[8px] text-gray-600 font-bold uppercase tracking-widest mt-0.5">FRAGMENTS</span>
                </div>
                <button disabled={!hasImages} onClick={() => adjustCount(1)} className="w-12 h-full flex items-center justify-center text-gray-500 hover:text-white"><Plus size={20}/></button>
             </div>
             
             <button 
                disabled={!hasImages}
                onClick={() => setSeed(Date.now())}
                className="w-1/3 bg-[#111] border border-[#222] rounded-xl flex flex-col items-center justify-center gap-1 text-white hover:bg-white hover:text-black transition-colors"
             >
                <RefreshCw size={20} />
                <span className="text-[10px] font-bold tracking-widest">REMIX</span>
             </button>
         </div>
     </div>
  );
};
