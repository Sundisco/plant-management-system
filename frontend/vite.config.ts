import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://1cff-89-150-165-188.ngrok-free.app',
        changeOrigin: true,
        secure: false,
        ws: true
      },
      '/watering-schedule': {
        target: 'https://1cff-89-150-165-188.ngrok-free.app',
        changeOrigin: true,
        secure: false
      }
    },
    allowedHosts: ['.ngrok-free.app']
  },
  build: {
    chunkSizeWarningLimit: 1000,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', '@mui/material', '@mui/icons-material'],
          charts: ['recharts'],
        }
      }
    }
  },
  preview: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'https://1cff-89-150-165-188.ngrok-free.app',
        changeOrigin: true,
        secure: false,
        ws: true
      },
      '/watering-schedule': {
        target: 'https://1cff-89-150-165-188.ngrok-free.app',
        changeOrigin: true,
        secure: false
      }
    }
  }
}) 