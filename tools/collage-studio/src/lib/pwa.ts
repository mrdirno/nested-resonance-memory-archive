// src/lib/pwa.ts

export const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const reg = await navigator.serviceWorker.register('./sw.js', { scope: './' });
      console.log('SW registered:', reg);
      
      // Request Periodic Sync (if supported)
      if ('periodicSync' in reg) {
        try {
          // @ts-ignore
          await reg.periodicSync.register('update-templates', {
            minInterval: 24 * 60 * 60 * 1000 // 1 day
          });
        } catch (e) {
          console.log('Periodic sync could not be registered');
        }
      }
    } catch (e) {
      console.error('SW registration failed:', e);
    }
  }
};
