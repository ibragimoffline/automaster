import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dev proxy: frontend (5173) -> Django (8000). API yo'llari /api/* va /media/* backendga uzatiladi.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/media': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
