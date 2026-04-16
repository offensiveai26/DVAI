import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 4444,
    proxy: {
      '/api': 'http://localhost:4445',
      '/health': 'http://localhost:4445',
      '/v1': 'http://localhost:4445',
    },
  },
})
