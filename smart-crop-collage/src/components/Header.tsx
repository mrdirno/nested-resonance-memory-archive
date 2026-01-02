import React from 'react';
import { Download, RefreshCw, Check, AlertCircle, Loader2, BrainCircuit } from 'lucide-react';

interface HeaderProps {
  mode: 'simple' | 'advanced';
  setMode: (m: 'simple' | 'advanced') => void;
  aiState: string;
  exportStatus: string;
  exportMsg: string;
  onExport: () => void;
  hasImages: boolean;
  onSaveProject: () => void;
  onLoadProject: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  mode, setMode, aiState, exportStatus, exportMsg, onExport, hasImages,
  onSaveProject, onLoadProject
}) => {
  return (
    <div className="h-14 border-b border-white/10 flex items-center justify-between px-4 bg-[#0a0a0a] z-50 relative shrink-0">
       <div className="flex flex-col">
          <div className="font-bold tracking-[0.2em] text-[10px] text-gray-400">
              GEN<span className="text-white">ART</span>
          </div>
          <div className="flex items-center gap-2 mt-0.5">
              <button 
                onClick={() => setMode(mode === 'simple' ? 'advanced' : 'simple')}
                className="text-[8px] font-mono bg-gray-900 px-1.5 py-0.5 rounded text-emerald-500 hover:text-white hover:bg-emerald-900 transition-colors"
              >
                {mode === 'simple' ? 'SIMPLE' : 'ADVANCED'}
              </button>
              
              {aiState === 'loading' && <span className="text-[8px] text-yellow-500 flex items-center gap-1"><Loader2 size={6} className="animate-spin"/> AI BOOTING</span>}
              {aiState === 'ready' && <span className="text-[8px] text-emerald-500 flex items-center gap-1"><BrainCircuit size={8}/> AI READY</span>}
              {aiState === 'failed' && <span className="text-[8px] text-gray-500">MATH ONLY</span>}
          </div>
       </div>
       
       <div className="flex items-center gap-2">
         {mode === 'advanced' && (
           <>
              <button onClick={onSaveProject} className="text-[10px] bg-[#111] hover:bg-[#222] text-white px-3 py-2 rounded">
                SAVE PROJ
              </button>
              <button onClick={onLoadProject} className="text-[10px] bg-[#111] hover:bg-[#222] text-white px-3 py-2 rounded">
                LOAD PROJ
              </button>
           </>
         )}

         {hasImages && (
             <button 
               onClick={onExport} 
               disabled={exportStatus === 'processing'}
               className={`
                  flex items-center gap-2 text-[10px] font-bold px-4 py-2 rounded transition-all
                  ${exportStatus === 'processing' ? 'bg-yellow-500 text-black animate-pulse' : 
                    exportStatus === 'done' ? 'bg-green-500 text-black' :
                    exportStatus === 'error' ? 'bg-red-500 text-white' :
                    'bg-white text-black hover:bg-emerald-400'}
               `}
             >
                 {exportStatus === 'processing' ? (
                     <><RefreshCw size={12} className="animate-spin"/> {exportMsg}</>
                 ) : exportStatus === 'done' ? (
                     <><Check size={12}/> SAVED</>
                 ) : exportStatus === 'error' ? (
                     <><AlertCircle size={12}/> FAILED</>
                 ) : (
                     <><Download size={12}/> {mode === 'simple' ? 'SAVE JPG' : 'EXPORT'}</>
                 )}
             </button>
         )}
       </div>
    </div>
  );
};
