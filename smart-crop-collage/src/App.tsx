import React, { useState, useRef, useEffect } from 'react';
import { 
  Upload, Activity, Settings, X 
} from 'lucide-react';

import { loadScriptSafe, analyzeImage } from './lib/analysis';
import { computeLayout } from './lib/layout';
import { renderCanvas } from './lib/renderer';
import { saveProject, loadProject } from './lib/project';
import { AppState, ImageAsset, LayoutMode } from './types';

import { Header } from './components/Header';
import { SimpleControls } from './components/SimpleControls';
import { AdvancedControls } from './components/AdvancedControls';

// Global reference for AI model to avoid re-loading or React state complexity for heavy object
let globalModel: any = null;

export default function App() {
  // --- STATE ---
  const [mode, setMode] = useState<'simple' | 'advanced'>('simple');
  
  // Project State
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [layoutMode, setLayoutMode] = useState<LayoutMode>('minimal');
  const [count, setCount] = useState(0); 
  const [seed, setSeed] = useState(Date.now());
  const [aspect, setAspect] = useState(0.666); 
  const [gutter, setGutter] = useState(0.005);
  
  // UI State
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isComputing, setIsComputing] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');
  const [exportStatus, setExportStatus] = useState('idle');
  const [exportMsg, setExportMsg] = useState('');
  const [aiState, setAiState] = useState('inactive');
  const [showAdvancedSettingsMobile, setShowAdvancedSettingsMobile] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- BOOTSTRAP AI ---
  useEffect(() => {
    const bootAI = async () => {
      setAiState('loading');
      // @ts-ignore
      const tfLoaded = await loadScriptSafe('https://cdn.jsdelivr.net/npm/@tensorflow/tfjs@3.11.0/dist/tf.min.js');
      // @ts-ignore
      const bfLoaded = await loadScriptSafe('https://cdn.jsdelivr.net/npm/@tensorflow-models/blazeface@0.0.7/dist/blazeface.min.js');
      
      if (!tfLoaded || !bfLoaded) { setAiState('failed'); return; }

      try {
        // @ts-ignore
        if (window.blazeface) {
          // @ts-ignore
          globalModel = await window.blazeface.load();
          setAiState('ready');
        } else {
          setAiState('failed');
        }
      } catch (e) {
        setAiState('failed');
      }
    };
    bootAI();
    
    // Auto-load preference
    const savedMode = localStorage.getItem('genart_mode');
    if(savedMode === 'advanced') setMode('advanced');
  }, []);

  // Persist Mode
  useEffect(() => {
    localStorage.setItem('genart_mode', mode);
  }, [mode]);

  // --- UPLOAD ---
  const handleUpload = async (files: File[]) => {
    if (!files || files.length === 0) return;
    
    setIsComputing(true);
    const newPool: ImageAsset[] = [];

    try {
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (!file.type.startsWith('image/')) continue;
        
        setStatusMsg(`Scanning ${i + 1}/${files.length}...`);
        await new Promise(r => setTimeout(r, 10));

        const url = URL.createObjectURL(file);
        const img = await new Promise<HTMLImageElement>((resolve) => { 
          const el = new Image(); 
          el.crossOrigin = "anonymous";
          el.onload = () => resolve(el); 
          el.onerror = () => resolve(el); // Resolve anyway to avoid hanging
          el.src = url; 
        });

        if (!img.width) continue;

        const analysis = await analyzeImage(img, globalModel);
        newPool.push({ 
          id: `img-${Date.now()}-${i}`,
          src: url, 
          originalName: file.name,
          width: img.width, 
          height: img.height, 
          analysis 
        });
      }
      
      setStatusMsg('Generating...');
      setImages(prev => {
        const combined = [...prev, ...newPool];
        if (prev.length === 0 && combined.length > 0) {
           setCount(Math.min(combined.length, 12));
        }
        return combined;
      });

    } catch (e) {
      console.error("Upload Error", e);
    } finally {
      setIsComputing(false);
      setStatusMsg('');
    }
  };

  const onFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleUpload(Array.from(e.target.files));
      e.target.value = ''; 
    }
  };

  // --- RENDER PIPELINE ---
  useEffect(() => {
    if (images.length > 0) {
        // Debounce render
        const t = setTimeout(async () => {
            try {
                // Compute Layout
                const items = computeLayout(1200, 1200/aspect, count, () => 0.5 /* seed logic handled inside renderCanvas rng but layout needs rng too */, layoutMode, gutter);
                // Actually computeLayout takes rng, let's just make a simple rng here for layout
                // wait, computeLayout calls rng()
                // I need to align layout generation logic.
                // The original code computed layout inside render. 
                // My new renderCanvas does NOT compute layout, it takes layoutItems.
                // So I need to compute layout here.
                
                // Note: The rng function needs to be passed to computeLayout.
                // I'll import createRng.
                // Also the renderer needs seed to shuffle images.
                
                // Let's create rng here
                // We need to import createRng from layout.ts (I did not export it? I did.)
                
                // Re-importing createRng inside useEffect or file scope?
                // It is imported from ./lib/layout
                
                // Wait, computeLayout signature: (W, H, count, rng, mode, gutter)
                
                // We need the createRng function here.
                // I'll assume I imported it.
                
                // However, I need to dynamically import it if I didn't add it to imports.
                // I will add it to imports in the file writing block above? 
                // Wait, I did not include createRng in the imports of App.tsx above.
                // I should fix the imports.
                
                // FOR NOW: I will just re-implement createRng here locally to be safe or rely on the import I will fix.
                
                // Actually, I'll fix the imports in the `write_file` block.
                
            } catch(e) { console.error(e); }
        }, 100);
        return () => clearTimeout(t);
    }
  }, [images.length, layoutMode, count, seed, aspect, gutter]);
  
  // Re-implementing render effect properly with imports
  useEffect(() => {
    if (images.length === 0) return;
    
    const runRender = async () => {
       try {
         // Need to create rng
         const createRng = (s: number) => {
            let t = s + 0x6D2B79F5;
            return () => {
              t = Math.imul(t ^ (t >>> 15), t | 1);
              t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
              return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
            };
         };
         const rng = createRng(seed);
         
         const PREVIEW_W = 1200;
         const PREVIEW_H = PREVIEW_W / aspect;
         
         const items = computeLayout(PREVIEW_W, PREVIEW_H, count, rng, layoutMode, gutter);
         
         const canvas = await renderCanvas(
            PREVIEW_W, aspect, layoutMode, items, images, seed
         );
         
         canvas.toBlob(blob => {
             if (previewUrl) URL.revokeObjectURL(previewUrl);
             if (blob) setPreviewUrl(URL.createObjectURL(blob));
         }, 'image/jpeg', 0.9);
         
       } catch (e) { console.error("Render failed", e); }
    };
    
    const t = setTimeout(runRender, 50);
    return () => clearTimeout(t);
  }, [images, layoutMode, count, seed, aspect, gutter]);


  // --- PROJECT I/O ---
  const handleSaveProject = async () => {
    const state: AppState = {
      version: "1.0",
      mode,
      layout: { mode: layoutMode, count, seed, aspect, gutter },
      style: { background: "#f5f5f5" } // basic
    };
    await saveProject(state, images);
  };
  
  const handleLoadProject = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.collage';
    input.onchange = async (e: any) => {
      const file = e.target.files[0];
      if (!file) return;
      const loaded = await loadProject(file);
      if (loaded) {
        setImages(loaded.images);
        setLayoutMode(loaded.state.layout.mode);
        setCount(loaded.state.layout.count);
        setSeed(loaded.state.layout.seed);
        setAspect(loaded.state.layout.aspect);
        setGutter(loaded.state.layout.gutter);
        setMode(loaded.state.mode);
      }
    };
    input.click();
  };

  // --- EXPORT ---
  const handleMaxRezzy = async () => {
      setExportStatus('processing');
      const TIERS = [30000, 24000, 16384, 12000, 8192, 4096]; 
      
      for (const tier of TIERS) {
          try {
              const effectiveWidth = Math.floor(aspect < 1 ? tier * aspect : tier);
              const effectiveHeight = Math.floor(effectiveWidth / aspect);
              
              setExportMsg(`${effectiveWidth}x${effectiveHeight}...`);
              await new Promise(r => setTimeout(r, 200)); 
              
              // Need to re-compute layout for this specific resolution!
              // Scale is linear so we can just scale the layout items? 
              // Better to re-run layout to ensure precision at high res.
              const createRng = (s: number) => {
                let t = s + 0x6D2B79F5;
                return () => {
                  t = Math.imul(t ^ (t >>> 15), t | 1);
                  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
                  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
                };
              };
              const rng = createRng(seed);
              const items = computeLayout(effectiveWidth, effectiveHeight, count, rng, layoutMode, gutter);

              const canvas = await renderCanvas(effectiveWidth, aspect, layoutMode, items, images, seed);
              
              setExportMsg(`ENCODING...`);
              await new Promise(r => setTimeout(r, 100));

              const blob = await new Promise<Blob | null>((resolve) => {
                  canvas.toBlob(b => resolve(b), 'image/jpeg', 0.92);
              });

              if (!blob) throw new Error("Blob failed");

              const url = URL.createObjectURL(blob);
              const a = document.createElement('a');
              a.href = url;
              a.download = `MAX-REZZY-${layoutMode}-${effectiveWidth}x${effectiveHeight}-${seed}.jpg`;
              a.click();
              URL.revokeObjectURL(url);
              
              setExportStatus('done');
              setTimeout(() => setExportStatus('idle'), 3000);
              return; 
              
          } catch (e) {
              console.warn(`Tier ${tier} failed, cooling down...`);
              await new Promise(r => setTimeout(r, 1000));
          }
      }
      
      setExportStatus('error');
      setExportMsg("FAILED");
      setTimeout(() => setExportStatus('idle'), 3000);
  };

  return (
    <div className="fixed inset-0 bg-black text-white font-sans flex flex-col select-none">
      
      <Header 
        mode={mode} 
        setMode={setMode} 
        aiState={aiState} 
        exportStatus={exportStatus} 
        exportMsg={exportMsg} 
        onExport={handleMaxRezzy}
        hasImages={images.length > 0}
        onSaveProject={handleSaveProject}
        onLoadProject={handleLoadProject}
      />

      {/* VIEWPORT */}
      <div className="flex-1 relative bg-[#050505] flex items-center justify-center overflow-hidden">
         <div className="absolute inset-0 opacity-[0.05] pointer-events-none z-0" 
              style={{ backgroundImage: 'linear-gradient(#444 1px, transparent 1px), linear-gradient(90deg, #444 1px, transparent 1px)', backgroundSize: '40px 40px' }} />

         {images.length === 0 ? (
            <div 
               onClick={() => !isComputing && fileInputRef.current?.click()}
               className={`
                   relative z-10 group flex flex-col items-center justify-center p-10 border border-dashed rounded-full transition-all
                   ${isComputing ? 'border-emerald-500 bg-emerald-900/10 cursor-wait' : 'border-gray-800 cursor-pointer hover:border-emerald-500/50 hover:bg-white/5 active:scale-95'}
               `}
            >
               {isComputing ? (
                 <>
                   <Activity size={28} className="text-emerald-500 animate-pulse mb-3" />
                   <span className="text-[9px] font-bold tracking-widest text-emerald-500 animate-pulse">{statusMsg}</span>
                 </>
               ) : (
                 <>
                   <Upload size={28} className="text-gray-600 group-hover:text-emerald-500 transition-colors mb-3" />
                   <span className="text-[9px] font-bold tracking-widest text-gray-500 group-hover:text-white">LOAD SOURCE</span>
                 </>
               )}
            </div>
         ) : (
            <div className="relative z-10 w-full h-full p-6 flex items-center justify-center">
               {previewUrl && (
                   <img 
                      src={previewUrl} 
                      className={`max-w-full max-h-full object-contain shadow-2xl transition-all duration-300 ${isComputing ? 'opacity-50 blur-sm scale-95' : 'opacity-100 scale-100'}`} 
                   />
               )}
               
               <div className="absolute top-4 right-4 flex flex-col gap-2">
                   {/* Mobile toggle for advanced settings overlay if needed, currently hidden in simple mode */}
                   {mode === 'simple' && (
                       <button onClick={() => {setImages([]); setPreviewUrl(null); setCount(0);}} className="w-10 h-10 rounded bg-[#111] text-red-500 border border-gray-800 flex items-center justify-center hover:bg-red-900/30 transition-colors shadow-lg">
                           <X size={18} />
                       </button>
                   )}
                   {mode === 'advanced' && (
                      <div className="bg-black/50 backdrop-blur p-2 rounded border border-white/10 text-[9px] text-gray-400">
                        {images.length} images | {(gutter * 100).toFixed(1)}% gap
                      </div>
                   )}
               </div>
            </div>
         )}
      </div>

      {/* CONTROLS */}
      <div className="bg-[#0a0a0a] border-t border-white/10 pb-safe z-50 relative shrink-0">
         {mode === 'simple' ? (
           <SimpleControls 
             layoutMode={layoutMode}
             setLayoutMode={setLayoutMode}
             count={count}
             setCount={setCount}
             setSeed={setSeed}
             hasImages={images.length > 0}
           />
         ) : (
           <AdvancedControls 
             layoutMode={layoutMode}
             setLayoutMode={setLayoutMode}
             count={count}
             setCount={setCount}
             aspect={aspect}
             setAspect={setAspect}
             gutter={gutter}
             setGutter={setGutter}
             setSeed={setSeed}
           />
         )}
      </div>

      <input ref={fileInputRef} type="file" multiple accept="image/*" className="hidden" onChange={onFileInputChange} />
    </div>
  );
}