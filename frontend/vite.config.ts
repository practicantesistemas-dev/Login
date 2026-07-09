import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // import desde '@/components/...'
    },
  },
  server: {
    host: '0.0.0.0',
    port: 5175,
    strictPort: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
      '/sistemassalud': {
        target: 'http://localhost:5176',
        changeOrigin: true,
        secure: false,
        rewrite: path => path.replace(/^\/sistemassalud/, ''),
      },
      '/tesoreri': {
        target: 'http://localhost:5177',
        changeOrigin: true,
        secure: false,
        rewrite: path => path.replace(/^\/tesoreri/, ''),
      },
    },
  },
});