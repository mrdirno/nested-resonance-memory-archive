import path from 'path';
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// The site root on GitHub Pages. A plain `npm run build` serves the app from
// here, unchanged. The deploy builds this (classic) app for a sub-path instead
// -- BRIDGE_BASE=/nested-resonance-memory-archive/archive/classic/ -- and serves
// the HALO page at the root. SITE_ROOT is inlined into the app so its links to
// the pages beside it (the collage tools, the archive, the field toolkits)
// keep pointing at the root wherever the app itself is served from.
const SITE_ROOT = '/nested-resonance-memory-archive/';

export default defineConfig(() => {
  return {
    base: process.env.BRIDGE_BASE || SITE_ROOT,
    server: {
      port: 3000,
      host: '0.0.0.0',
    },
    plugins: [react()],
    define: {
      'import.meta.env.SITE_ROOT': JSON.stringify(SITE_ROOT),
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      }
    }
  };
});
