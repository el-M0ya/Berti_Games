import { useCallback, useEffect, useLayoutEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import GameCover from './GameCover.jsx'
import { computeGeometry, panelMaxHeight, panelMargin, PANEL_MAX_W } from './detailGeometry.js'
import { myVote, score } from '../lib/votes.js'

/**
 * Ficha de un juego.
 *
 * Al abrirse, la tarjeta de origen vuela hacia la izquierda y el panel de
 * descripcion aparece a la derecha. Para lograr ese clonamos la caratula en
 * una capa flotante (`flyer`) que se anima con transform desde la posicion
 * real de la tarjeta hasta su lugar final.
 *
 * Las medidas salen de `detailGeometry.js`.
 */
export default function GameDetail({
  game,
  accent,
  originRect,
  onClose,
  votos = {},
  votosOnline = false,
  onVotar = () => {},
}) {
  const [open, setOpen] = useState(false)
  const [geo, setGeo] = useState(() => computeGeometry(window.innerWidth, window.innerHeight, originRect))
  const panelRef = useRef(null)
  const closeRef = useRef(onClose)
  closeRef.current = onClose

  // Al cambiar de juego recalculamos la geometria.
  useLayoutEffect(() => {
    setGeo(computeGeometry(window.innerWidth, window.innerHeight, originRect))
  }, [game?.id, originRect])

  // Si el usuario cambia el tamaño de la ventana con la ficha abierta,
  // reajustamos el destino para que la carta no quede fuera de pantalla.
  const recompute = useCallback(
    () => setGeo(computeGeometry(window.innerWidth, window.innerHeight, originRect)),
    [originRect],
  )
  useEffect(() => {
    window.addEventListener('resize', recompute)
    return () => window.removeEventListener('resize', recompute)
  }, [recompute])

  useEffect(() => {
    if (!game) return

    // Para que la transicion de entrada se aplique hay que pintar primero el
    // estado "cerrado" y cambiarlo despues. rAF hace eso, pero queda
    // suspendido si la pestaña esta oculta, asi que ademas dejamos un timer
    // de respaldo (lo que llegue primero gana).
    let done = false
    const reveal = () => {
      if (done) return
      done = true
      setOpen(true)
    }
    const raf = requestAnimationFrame(reveal)
    const timer = setTimeout(reveal, 40)

    const onKey = (e) => {
      if (e.key === 'Escape') closeRef.current()
    }
    window.addEventListener('keydown', onKey)

    // Bloquea el scroll del fondo mientras la ficha esta abierta.
    const prev = document.body.style.overflow
    document.body.style.overflow = 'hidden'

    return () => {
      cancelAnimationFrame(raf)
      clearTimeout(timer)
      window.removeEventListener('keydown', onKey)
      document.body.style.overflow = prev
    }
  }, [game])

  // El foco entra en la ficha para que Escape y la navegacion por teclado
  // funcionen apenas se abre.
  useEffect(() => {
    if (open) panelRef.current?.focus()
  }, [open])

  if (!game) return null

  // Antes de abrir, el flyer se dibuja donde estaba la tarjeta; despues se
  // mueve a la posicion final. El navegador interpola el cambio.
  const to = open ? geo.end : geo.start

  const flyerStyle = {
    '--fx': `${to.x}px`,
    '--fy': `${to.y}px`,
    '--fw': `${to.w}px`,
    '--fh': `${to.h}px`,
    '--frot': open ? '0deg' : '3deg',
    '--accent': accent,
  }

  const clickOutside = (e) => {
    const inPanel = panelRef.current?.contains(e.target)
    const inFlyer = e.target.closest?.('.detail__flyer')
    if (!inPanel && !inFlyer) onClose()
  }

  return createPortal(
    <div
      className={`detail${open ? ' is-open' : ''}`}
      style={{
        '--panel-max-h': `${panelMaxHeight(window.innerWidth, window.innerHeight, geo)}px`,
        '--panel-max-w': `${PANEL_MAX_W}px`,
        '--panel-margin': `${panelMargin(window.innerWidth)}px`,
      }}
      onMouseDown={clickOutside}
    >
      <div className="detail__scrim" onClick={onClose} aria-hidden="true" />

      <div
        className="detail__flyer"
        style={flyerStyle}
        data-desktop={geo.desktop ? 'true' : 'false'}
        aria-hidden="true"
      >
        <GameCover game={game} accent={accent} className="detail__flyer-cover" />
      </div>

      <section
        ref={panelRef}
        className="detail__panel"
        style={{ '--accent': accent }}
        role="dialog"
        aria-modal="true"
        aria-label={game.title}
        tabIndex={-1}
      >
        <header className="detail__head">
          <div className="detail__tags">
            {game.players?.map((p) => (
              <span key={p} className="tag tag--players">
                {p}
              </span>
            ))}
            {game.genres?.slice(0, 2).map((g) => (
              <span key={g} className="tag tag--genre">
                {g}
              </span>
            ))}
          </div>

          <button className="detail__close" onClick={onClose} aria-label="Cerrar ficha">
            <span aria-hidden="true">x</span>
          </button>
        </header>

        <h2 className="detail__title">{game.title}</h2>
        {game.year ? <p className="detail__year">{game.year}</p> : null}

        <p className="detail__desc">{game.description}</p>

        <div className="detail__spacer" />

        <div className="detail__votos">
          <span className="detail__votos-label">Te gusto este juego?</span>
          <div className="detail__votos-botones">
            <button
              className={`voto${myVote(votos, game.id) === 1 ? ' is-on' : ''}`}
              onClick={() => onVotar(game.id, 1)}
              aria-pressed={myVote(votos, game.id) === 1}
            >
              <span aria-hidden="true">Me gusta</span>
            </button>
            <span className="voto__cuenta">{score(votos, game.id)}</span>
            <button
              className={`voto voto--no${myVote(votos, game.id) === -1 ? ' is-on' : ''}`}
              onClick={() => onVotar(game.id, -1)}
              aria-pressed={myVote(votos, game.id) === -1}
            >
              <span aria-hidden="true">No me gusta</span>
            </button>
          </div>
          <p className="detail__votos-nota">
            {votosOnline
              ? 'Tu voto se guarda y lo ven todos los visitantes.'
              : 'Sin conexion con el servidor: tu voto se guarda solo en este navegador.'}
          </p>
        </div>

        <a
          className="detail__contact"
          href="#contacto"
          onClick={(e) => {
            e.preventDefault()
            onClose()
            document.getElementById('contacto')?.scrollIntoView({ behavior: 'smooth' })
          }}
        >
          Consultar por este juego
        </a>
      </section>
    </div>,
    document.body,
  )
}
