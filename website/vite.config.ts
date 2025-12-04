import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Important: replace USERNAME and REPO with your GitHub username and repository name.
export default defineConfig({
  plugins: [react()],
  base: "/From-Words-to-Shields/",  // <-- critical for GitHub Pages
})
