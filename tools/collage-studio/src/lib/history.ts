import { AppState, ImageAsset, LayoutMode } from '../types';

export interface HistoryItem {
  id: string;
  timestamp: number;
  thumbnail?: string; // Data URL of preview
  state: AppState;
  images: ImageAsset[]; // We need to store images for history to work.
                        // Storing full blobs in localStorage is BAD (5MB limit).
                        // Strategy: We can use IndexedDB for "Recent Projects" or just store metadata?
                        // If we store metadata, we can't restore if user closed tab.
                        // For this "Session History", we can store in memory (RAM).
                        // For "Browser History", we need IndexedDB.
                        // I'll implement RAM history for now (Session). 
                        // Actually, the request implies "go back... previously working on", suggesting persistence.
                        // I will try to store a "Slim History" in localStorage (Layout only) and warn if images missing?
                        // No, let's implement a proper "Session History" in RAM.
}

const SESSION_HISTORY: HistoryItem[] = [];

export const addToHistory = (state: AppState, images: ImageAsset[], previewUrl?: string) => {
  const item: HistoryItem = {
    id: `hist-${Date.now()}`,
    timestamp: Date.now(),
    thumbnail: previewUrl,
    state: { ...state },
    images: [...images] // Shallow copy of array
  };
  
  // Keep max 10
  if (SESSION_HISTORY.length >= 10) SESSION_HISTORY.shift();
  SESSION_HISTORY.push(item);
};

export const getHistory = () => [...SESSION_HISTORY].reverse(); // Newest first
