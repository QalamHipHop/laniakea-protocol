import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  root: '.',
  publicDir: 'static',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'cosmic.html'),
        landing: resolve(__dirname, 'landing.html'),
        mobile: resolve(__dirname, 'mobile/index.html')
      }
    },
    target: 'es2020',
    minify: 'esbuild',
    sourcemap: true,
    cssCodeSplit: true
  },
  server: {
    port: 5173,
    open: '/cosmic.html',
    proxy: {
      '/api': {
        target: process.env.LANIAKEA_API || 'http://localhost:8000',
        changeOrigin: true
      },
      '/ws': {
        target: process.env.LANIAKEA_API || 'http://localhost:8000',
        ws: true
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, '.'),
      '@i18n': resolve(__dirname, 'i18n')
    }
  }
});
