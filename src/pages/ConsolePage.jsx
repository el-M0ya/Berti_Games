import { useEffect, useMemo, useRef, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getConsole } from '../data/consoles.js'
import { getCount, loadGames, loadDescriptions } from '../data/games/loader.js'
import GameCard from '../components/GameCard.jsx'
import GameDetail from '../components/GameDetail.jsx'
import ContactSection from '../components/ContactSection.jsx'
import NotFound from './NotFound.jsx'
import { cargar, subscribe, sincronizar, votar } from '../lib/votes.js'
import {
  DEFAULT_SORT,
  SORTS,
  filtrarYOrdenar,
  genresDisponibles,
  playersDisponibles,
} from '../lib/catalog.js'
import { buildSearchIndex } from '../lib/text.js'

/** Cuantas tarjetas se muestran antes de pedir "ver mas". */
const POR_PAGINA = 60

export default function ConsolePage() {
  const { slug } = useParams()
  const consola = getConsole(slug)

  const [juegos, setJuegos] = useState(null)
  const [texto, setTexto] = useState('')
  const [jugador, setJugador] = useState('')
  const [genero, setGenero] = useState('')
  const [orden, setOrden] = useState(DEFAULT_SORT)
  const [votos, setVotos] = useState(cargar)
  const [votosOnline, setVotosOnline] = useState(false)
  const [vistos, setVistos] = useState(POR_PAGINA)
  const [seleccionado, setSeleccionado] = useState(null)
  const grillaRef = useRef(null)
  const buscadorRef = useRef(null)

  // Los votos los puede cambiar otra pestana, asi que nos suscribimos.
  useEffect(() => subscribe(setVotos), [])

  // Al entrar probamos la API de Cloudflare. Si responde, los votos son de
  // todos; si no, seguimos con los de este navegador.
  useEffect(() => {
    let cancelado = false
    sincronizar().then((r) => {
      if (cancelado) return
      setVotos(r.votos)
      setVotosOnline(r.conectado)
    })
    return () => {
      cancelado = true
    }
  }, [])

  // El indice de esa consola se pide al entrar. Nada mas se descarga.
  useEffect(() => {
    let cancelado = false
    setJuegos(null)
    setVistos(POR_PAGINA)
    loadGames(slug).then((lista) => {
      if (!cancelado) setJuegos(lista)
    })
    return () => {
      cancelado = true
    }
  }, [slug])

  // Al cambiar cualquier filtro se vuelve a la primera pagina.
  useEffect(() => {
    setVistos(POR_PAGINA)
  }, [texto, jugador, genero, orden])

  // El indice de busqueda se arma una vez por consola, no en cada pulsacion.
  const indice = useMemo(() => (juegos ? buildSearchIndex(juegos) : []), [juegos])

  const jugadores = useMemo(() => (juegos ? playersDisponibles(juegos) : []), [juegos])
  const generos = useMemo(() => (juegos ? genresDisponibles(juegos) : []), [juegos])

  const filtrados = useMemo(() => {
    if (!juegos) return []
    return filtrarYOrdenar(juegos, { texto, jugador, genero, orden, votos, indice })
  }, [juegos, texto, jugador, genero, orden, votos, indice])

  if (!consola) return <NotFound />

  const total = getCount(slug)
  const visibles = filtrados.slice(0, vistos)
  const quedan = filtrados.length - visibles.length
  const hayFiltros = texto.trim() !== '' || jugador !== '' || genero !== ''

  const abrirJuego = (juego, indiceEnGrilla) => {
    const nodo = grillaRef.current?.querySelector(`[data-index="${indiceEnGrilla}"]`)
    setSeleccionado({ juego, rect: nodo?.getBoundingClientRect(), slug })
  }

  const limpiar = () => {
    setTexto('')
    setJugador('')
    setGenero('')
    buscadorRef.current?.focus()
  }

  return (
    <div className="console-page" style={{ '--accent': consola.accent }}>
      <header className="page-head">
        <nav className="crumbs">
          <Link to="/">Inicio</Link>
          <span aria-hidden="true">/</span>
          <span>{consola.name}</span>
        </nav>
        <h1 className="page-head__title">{consola.name}</h1>
        <p className="page-head__sub">{consola.tagline}</p>
        <p className="page-head__meta">
          {consola.brand} &middot; {consola.year} &middot; {total} juegos
        </p>
      </header>

      <div className="toolbar">
        <div className="toolbar__fila">
          <div className="buscador">
            <span className="buscador__lupa" aria-hidden="true">
              &#9906;
            </span>
            <input
              ref={buscadorRef}
              type="search"
              className="buscador__input"
              placeholder={`Buscar en ${consola.short} por nombre o anio`}
              value={texto}
              onChange={(e) => setTexto(e.target.value)}
              aria-label={`Buscar juegos de ${consola.name}`}
            />
            {texto !== '' ? (
              <button
                className="buscador__limpiar"
                onClick={() => setTexto('')}
                aria-label="Borrar la busqueda"
              >
                <span aria-hidden="true">x</span>
              </button>
            ) : null}
          </div>

          <label className="orden">
            <span className="orden__label">Ordenar por</span>
            <select
              className="orden__select"
              value={orden}
              onChange={(e) => setOrden(e.target.value)}
              aria-label="Ordenar los juegos"
            >
              {SORTS.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <div className="toolbar__fila toolbar__fila--filtros">
          <div className="grupo-filtros">
            <span className="grupo-filtros__titulo">Jugadores</span>
            <div className="grupo-filtros__chips">
              <button
                className={`chip${jugador === '' ? ' is-active' : ''}`}
                onClick={() => setJugador('')}
              >
                Todos
              </button>
              {jugadores.map((p) => (
                <button
                  key={p}
                  className={`chip${jugador === p ? ' is-active' : ''}`}
                  onClick={() => setJugador(jugador === p ? '' : p)}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <div className="grupo-filtros">
            <span className="grupo-filtros__titulo">Genero</span>
            <select
              className="grupo-filtros__select"
              value={genero}
              onChange={(e) => setGenero(e.target.value)}
              aria-label="Filtrar por genero"
            >
              <option value="">Todos los generos</option>
              {generos.map((g) => (
                <option key={g.nombre} value={g.nombre}>
                  {g.nombre} ({g.total})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="toolbar__resumen">
          <p className="toolbar__cuenta">
            {!juegos
              ? 'Cargando...'
              : filtrados.length === total
                ? `${total} juegos`
                : `${filtrados.length} de ${total} juegos`}
          </p>
          {hayFiltros ? (
            <button className="toolbar__limpiar" onClick={limpiar}>
              Limpiar filtros
            </button>
          ) : null}
        </div>
      </div>

      {!juegos ? (
        <p className="empty">Cargando el catalogo...</p>
      ) : filtrados.length === 0 ? (
        <p className="empty">
          No hay juegos que coincidan. Proba con menos palabras o{' '}
          <button className="empty__link" onClick={limpiar}>
            limpiar los filtros
          </button>
          .
        </p>
      ) : (
        <>
          <div className="grid" ref={grillaRef}>
            {visibles.map((juego, i) => (
              <div key={juego.id} data-index={i} className="grid__item">
                <GameCard
                  game={juego}
                  accent={consola.accent}
                  index={i}
                  onOpen={() => abrirJuego(juego, i)}
                />
              </div>
            ))}
          </div>

          {quedan > 0 ? (
            <div className="cargar-mas">
              <p className="cargar-mas__texto">
                Mostrando {visibles.length} de {filtrados.length}
              </p>
              <button
                className="btn btn--ghost"
                onClick={() => setVistos(vistos + POR_PAGINA)}
              >
                Ver mas juegos
              </button>
            </div>
          ) : null}
        </>
      )}

      <ContactSection />

      {seleccionado ? (
        <GameDetailLoader
          juego={seleccionado.juego}
          slug={seleccionado.slug}
          accent={consola.accent}
          originRect={seleccionado.rect}
          votos={votos}
          votosOnline={votosOnline}
          onVotar={(id, dir) => votar(votos, id, dir).then(setVotos)}
          onClose={() => setSeleccionado(null)}
        />
      ) : null}
    </div>
  )
}

/**
 * La ficha pide la descripcion recien cuando se abre, y recien entonces baja
 * el archivo de descripciones de esa consola.
 */
function GameDetailLoader({ juego, slug, votos, votosOnline, onVotar, ...props }) {
  const [descripcion, setDescripcion] = useState(null)

  useEffect(() => {
    let cancelado = false
    loadDescriptions(slug).then((mapa) => {
      if (!cancelado) setDescripcion(mapa[juego.id] ?? '')
    })
    return () => {
      cancelado = true
    }
  }, [slug, juego.id])

  // Hasta que llegue el texto se muestra el nombre solo, sin pantalla en blanco.
  const completo = descripcion !== null ? { ...juego, description: descripcion } : juego

  return <GameDetail game={completo} votos={votos} votosOnline={votosOnline} onVotar={onVotar} {...props} />
}