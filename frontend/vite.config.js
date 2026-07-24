import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const BASE = '/Healing_Trip_Gyeonggi/'

export default defineConfig({
  base: BASE,
  plugins: [react()],
  server: {
    open: BASE,
  },
})
