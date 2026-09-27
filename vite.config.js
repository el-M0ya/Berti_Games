import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// GitHub Pages publica el sitio en https://<usuario>.github.io/<repo>/
// Ese prefijo tiene que ir en `base` para que los assets carguen bien.
// En el workflow de deploy GITHUB_REPOSITORY ya viene definido, asi que no
// hace falta editar nada. Para desarrollo local usamos el nombre de la carpeta.
const repoName = process.env.GITHUB_REPOSITORY?.split('/')[1] || 'Berti_Games'

export default defineConfig({
  base: `/${repoName}/`,
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
  server: {
    port: 5173,
    open: true,
  },
})
