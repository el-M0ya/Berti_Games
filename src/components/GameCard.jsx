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

      {game.favorite ? (
        <span className="card__fav" title="Juego destacado">
          <span aria-hidden="true">&#9733;</span>
          <span className="sr-only">Destacado</span>
        </span>
      ) : null}

      {game.year ? <span className="card__year">{game.year}</span> : null}

      {game.players?.includes('4 jugadores') ? (
        <span className="card__badge" title="4 jugadores">
          4
        </span>
      ) : game.players?.includes('2 jugadores') ? (
        <span className="card__badge" title="2 jugadores">
          2
        </span>
      ) : null}

      <span className="card__name">{game.title}</span>
    </button>
  )
}
