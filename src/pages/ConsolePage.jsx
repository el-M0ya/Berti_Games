import { useMemo, useState, useRef } from 'react'
import { useParams, Link, Navigate } from 'react-router-dom'
import { CONSOLES, getConsole } from '../data/consoles.js'
import { getGames } from '../data/games/index.js'
import GameCard from '../components/GameCard.jsx'
import GameDetail from '../components/GameDetail.jsx'
import ContactSection from '../components/ContactSection.jsx'
import NotFound from './NotFound.jsx'

const FILTERS = [
  { id: 'todos', label: 'Todos' },
  { id: '1 jugador', label: '1 jugador' },
  { id: 'Multijugador', label: 'Multijugador' },
]

export default function ConsolePage() {
  const { slug } = useParams()
  const console_ = getConsole(slug)
  const games = useMemo(() => getGames(slug), [slug])

  const [filter, setFilter] = useState('todos')
  const [selected, setSelected] = useState(null)
  const gridRef = useRef(null)

  if (!console_) return <NotFound />

  const visible = filter === 'todos' ? games : games.filter((g) => g.players?.includes(filter))

  const openGame = (game, index) => {
    // Guardamos donde esta la tarjeta para animar el "vuelo" hacia la izquierda.
    const node = gridRef.current?.querySelector(`[data-index="${index}"]`)
    const rect = node?.getBoundingClientRect()
    setSelected({ game, rect })
  }

  return (
    <div className="console-page" style={{ '--accent': console_.accent }}>
      <header className="page-head">
        <nav className="crumbs">
          <Link to="/">Inicio</Link>
          <span aria-hidden="true">/</span>
          <span>{console_.name}</span>
        </nav>
        <h1 className="page-head__title">{console_.name}</h1>
        <p className="page-head__sub">{console_.tagline}</p>
        <p className="page-head__meta">
          {console_.brand} &middot; {console_.year} &middot; {games.length} juegos
        </p>
      </header>

      <div className="filters">
        {FILTERS.map((f) => (
          <button
            key={f.id}
            className={`chip${filter === f.id ? ' is-active' : ''}`}
            onClick={() => setFilter(f.id)}
          >
            {f.label}
            {f.id !== 'todos' ? (
              <span className="chip__count">
                {games.filter((g) => g.players?.includes(f.id)).length}
              </span>
            ) : (
              <span className="chip__count">{games.length}</span>
            )}
          </button>
        ))}
      </div>

      {visible.length === 0 ? (
        <p className="empty">No hay juegos para este filtro.</p>
      ) : (
        <div className="grid" ref={gridRef}>
          {visible.map((game, i) => (
            <div key={game.id} data-index={i} className="grid__item">
              <GameCard
                game={game}
                accent={console_.accent}
                index={i}
                onOpen={() => openGame(game, i)}
              />
            </div>
          ))}
        </div>
      )}

      <ContactSection />

      {selected ? (
        <GameDetail
          game={selected.game}
          accent={console_.accent}
          originRect={selected.rect}
          onClose={() => setSelected(null)}
        />
      ) : null}
    </div>
  )
}
