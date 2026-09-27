import GameCover from './GameCover.jsx'

/**
 * Tarjeta de juego: caratula de fondo y nombre abajo.
 * Al tocarla se anima hacia la izquierda y abre la ficha.
 */
export default function GameCard({ game, accent, onOpen, index = 0 }) {
  return (
    <button
      type="button"
      className="card"
      style={{ '--accent': accent, '--i': index }}
      onClick={() => onOpen(game)}
      aria-label={`Ver ficha de ${game.title}`}
    >
      <GameCover game={game} accent={accent} className="card__cover" />

      <span className="card__shade" />

      {game.year ? <span className="card__year">{game.year}</span> : null}

      {game.players?.includes('Multijugador') ? (
        <span className="card__badge" title="Multijugador">
          2+
        </span>
      ) : null}

      <span className="card__name">{game.title}</span>
    </button>
  )
}
