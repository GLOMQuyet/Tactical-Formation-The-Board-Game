import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Relative paths, so the same build works on GitHub Pages (under
// /Tactical-Formation-The-Board-Game/) and on itch.io (inside an iframe).
export default defineConfig({
  base: './',
  plugins: [react()],
  worker: { format: 'es' },
  build: { outDir: 'dist', target: 'es2020' },
});
