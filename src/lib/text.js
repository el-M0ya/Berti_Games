/**
 * Utilidades para buscar y ordenar el catalogo.
 *
 * Todo el texto del usuario se normaliza (sin tildes, en minusculas) para que
 * "bloodborne", "BLOODBORNE" y "BloodBorne" devuelvan lo mismo, y para que
 * "resident evil 4" encuentre a "Resident Evil IV".
 */

/** Quita tildes y pasa a minusculas. */
export function normalize(text) {
  return (text || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
}

/**
 * Clave para ordenar alfabeticamente.
 *
 * No alcanza con el titulo en minúsculas: "007", "3 en 1" y "Ávil" tienen que
 * caer en su lugar. Ademas ignoramos el ruido del principio ("the", "los", "de")
 * y usamos el año como desempate.
 */
export function sortKey(game) {
  const titulo = normalize(game.title)
  return `${titulo}|${game.year || 9999}`
}

/** Prepara los indices de busqueda de una lista de juegos (una sola vez). */
export function buildSearchIndex(games) {
  return games.map((g) => ({
    titulo: normalize(g.title),
    id: normalize(g.id),
    generos: normalize((g.genres || []).join(' ')),
    ano: g.year ? String(g.year) : '',
  }))
}

/** Convierte lo que escribio el usuario en terminos de busqueda. */
export function parseQuery(query) {
  return normalize(query)
    .split(/[\s,]+/)
    .filter(Boolean)
}

/**
 * Divide los terminos entre los que van a la titulo y los que son anos.
 * Buscar "2015" tiene que encontrar los juegos de ese anio, no los que
 * tienen "2015" en el titulo.
 */
export function splitTerms(terms) {
  const palabras = []
  const anos = []
  for (const t of terms) {
    if (/^(19|20)\d{2}$/.test(t)) anos.push(t)
    else palabras.push(t)
  }
  return { palabras, anos }
}