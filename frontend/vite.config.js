import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      // API routes to backend
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
      // Auth API routes (login, signup, etc.) - NOT the /auth page route
      // Use regex to only match /auth/ with subpaths
      '^/auth/(?!$)': {
        target: 'http://localhost:5001',
        changeOrigin: true,
        rewrite: (path) => path,
      },
      // Admin API routes to backend (only match /admin/ with subpaths)
      '^/admin/': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      }
    }
  }
})
