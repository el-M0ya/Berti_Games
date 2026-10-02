/**
 * Filtrado y orden del catalogo.
 *
 * Todo puro: recibe la lista de juegos y las opciones, devuelve la lista
 * filtrada y ordenada. Sin React ni del DOM, asi se puede probar con Node
 * (ver tools/test_catalog.mjs).
 */

import { buildSearchIndex, parseQuery, sortKey, splitTerms } from './text.js'
import { score } from './votes.js'

/** Los tres ordenes disponibles. El primero es el de por defecto. */
export const SORTS = [
  { id: 'destacados', label: 'Destacados' },
  { id: 'alfabetico', label: 'A-Z' },
  { id: 'votos', label: 'Mas votados' },
]

export const DEFAULT_SORT = 'destacados'

/** Los valores de `players` que existen, de menor a mayor cantidad. */
export const PLAYER_ORDER = ['1 jugador', '2 jugadores', '4 jugadores']

/** Los generos mas comunes van primero en el filtro. */
const GENEROS_COMUNES = [
  'Accion',
  'Aventura',
  'Rol',
  'Disparadores',
  'Deportes',
  'Carreras',
  'Estrategia',
  'Peleas',
  'Plataformas',
  'Simulacion',
  'Arcade',
  'Logica',
  'MMORPG',
  'Tablero',
  'Cartas',
  'Educativo',
  'Familiar',
  'Casual',
  'Indie',
  'Variado',
]

/** Generos disponibles en una consola, ordenados y con la cuenta de cada uno. */
export function genresDisponibles(games) {
  const cuenta = new Map()
  for (const g of games) {
    for (const genero of g.genres || []) {
      if (!cuenta.has(genero)) cuenta.set(genero, 0)
      cuenta.set(genero, cuenta.get(genero) + 1)
    }
  }
  const lista = [...cuenta.entries()].map(([nombre, total]) => ({ nombre, total }))
  lista.sort((a, b) => {
    const ia = GENEROS_COMUNES.indexOf(a.nombre)
    const ib = GENEROS_COMUNES.indexOf(b.nombre)
    if (ia !== -1 && ib !== -1) return ia - ib
    if (ia !== -1) return -1
    if (ib !== -1) return 1
    return a.nombre.localeCompare(b.nombre, 'es')
  })
  return lista
}

/** Valores de jugadores disponibles en una consola. */
export function playersDisponibles(games) {
  const presentes = new Set()
  for (const g of games) {
    for (const p of g.players || []) presentes.add(p)
  }
  return PLAYER_ORDER.filter((p) => presentes.has(p))
}

function coincidePorBusqueda(game, indice, palabras, anos) {
  for (const term of palabras) {
    if (
      !indice.titulo.includes(term) &&
      !indice.id.includes(term) &&
      !indice.generos.includes(term)
    ) {
      return false
    }
  }
  // Los anios se buscan solo en el anio del juego, no en el titulo.
  if (anos.length && !anos.includes(indice.ano)) return false
  return true
}

function compararAlfabetico(a, b) {
  return sortKey(a).localeCompare(sortKey(b), 'es')
}

/**
 * Aplica filtros y orden.
 *
 * @param {Array} games       Catalogo de una consola
 * @param {object} opciones   { texto, jugador, genero, orden, votos, indice }
 * @returns {Array} La lista ya filtrada y ordenada
 */
export function filtrarYOrdenar(games, opciones) {
  const { texto = '', jugador = '', genero = '', orden = DEFAULT_SORT, votos = {} } = opciones
  const indice = opciones.indice || buildSearchIndex(games)

  const { palabras, anos } = splitTerms(parseQuery(texto))

  let lista = games.filter((g, i) => {
    if (jugador && !(g.players || []).includes(jugador)) return false
    if (genero && !(g.genres || []).includes(genero)) return false
    if (palabras.length || anos.length) {
      if (!coincidePorBusqueda(g, indice[i], palabras, anos)) return false
    }
    return true
  })

  // Copia antes de ordenar: `games` viene de un modulo compartido y no se debe
  // mutar, o el orden se quedaria pegado entre navegaciones.
  lista = [...lista]

  if (orden === 'votos') {
    lista.sort((a, b) => {
      const sa = score(votos, a.id)
      const sb = score(votos, b.id)
      if (sa !== sb) return sb - sa
      return compararAlfabetico(a, b)
    })
    return lista
  }

  if (orden === 'alfabetico') {
    lista.sort(compararAlfabetico)
    return lista
  }

  // Destacados: los favoritos primero, y dentro de cada grupo, alfabeto.
  lista.sort((a, b) => {
    const fa = a.favorite ? 0 : 1
    const fb = b.favorite ? 0 : 1
    if (fa !== fb) return fa - fb
    return compararAlfabetico(a, b)
  })
  return lista
}