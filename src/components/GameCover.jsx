import { useState } from 'react'

/**
 * Caratula con degradado de respaldo.
 * Si la imagen no existe o falla la carga, se dibuja un placeholder
 * con las iniciales del juego y los colores de la consola.
 */
export default function GameCover({ game, accent = '#2f6fe4', className = '' }) {
  const [failed, setFailed] = useState(false)
  const initials = (game.title || '?')
    .replace(/[^\p{L}\p{N}\s]/gu, '')
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 3)
    .map((w) => w[0].toUpperCase())
    .join('')

  if (!game.cover || failed) {
    return (
      <div
        className={`cover cover--fallback ${className}`}
        style={{ '--cover-accent': accent }}
        aria-label={game.title}
      >
        <span className="cover__initials">{initials}</span>
        <span className="cover__placeholder">Caratula pendiente</span>
      </div>
    )
  }

  return (
    <img
      className={`cover ${className}`}
      src={game.cover}
      alt={game.title}
      loading="lazy"
      decoding="async"
      onError={() => setFailed(true)}
    />
  )
}
