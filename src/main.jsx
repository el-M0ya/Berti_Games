import React from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.jsx'
import './styles/global.css'

/**
 * GitHub Pages no reescribe URLs: entrar directo a /consola/ps2 devuelve el
 * 404.html, que redirige a index.html?p=/consola/ps2. Acá devolvemos la ruta
 * real al navegador para que React Router la vea bien.
 */
function restorePathFromRedirect() {
  const redirect = new URLSearchParams(window.location.search).get('p')
  if (!redirect) return

  const base = import.meta.env.BASE_URL.replace(/\/$/, '') // '/Berti_Games'
  const target = `${base}${redirect.startsWith('/') ? redirect : `/${redirect}`}`
  window.history.replaceState(null, '', target)
}

restorePathFromRedirect()

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL}>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
