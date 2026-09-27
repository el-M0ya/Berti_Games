import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

/** Vuelve arriba al cambiar de ruta (pero no al abrir la ficha de un juego). */
export default function ScrollToTop() {
  const { pathname } = useLocation()

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' })
  }, [pathname])

  return null
}
