/**
 * Como se cargan los catalogos.
 *
 * Antes, los 7.800 juegos entraban todos en un solo archivo de 3,8 MB y el
 * visitante se lo bajaba entero antes de ver nada. Ahora estan partidos:
 *
 *   - counts.js + favorites.js  (~4 KB)  se cargan siempre
 *   - indices/ps4.js           (~360 KB) al entrar a esa consola
 *   - descriptions/ps4.js      (~537 KB) al abrir la ficha de un juego
 *
 * Los archivos de `src/data/generated/` los crea `tools/split_catalog.py`.
 *
 * Que un juego tenga `favorite` y una descripcion es cosa de este archivo,
 * no del .js de cada consola: asi el indice de cada tarjeta queda chico.
 */

import { CONSOLE_COUNTS, CONSOLE_PREVIEWS } from '../generated/counts.js'
import { FAVORITES } from '../generated/favorites.js'

/**
 * Los import() dinamicos de Vite:Promise y Webpack los convierte en
 * peticiones aparte. Cada consola queda en su propio archivo.
 */
const CARGAS_INDICE = {
  ps1: () => import('../generated/indices/ps1.js'),
  ps2: () => import('../generated/indices/ps2.js'),
  psp: () => import('../generated/indices/psp.js'),
  ps3: () => import('../generated/indices/ps3.js'),
  xbox360: () => import('../generated/indices/xbox360.js'),
  ps4: () => import('../generated/indices/ps4.js'),
  ps5: () => import('../generated/indices/ps5.js'),
}

const CARGAS_DESCRIPCION = {
  ps1: () => import('../generated/descriptions/ps1.js'),
  ps2: () => import('../generated/descriptions/ps2.js'),
  psp: () => import('../generated/descriptions/psp.js'),
  ps3: () => import('../generated/descriptions/ps3.js'),
  xbox360: () => import('../generated/descriptions/xbox360.js'),
  ps4: () => import('../generated/descriptions/ps4.js'),
  ps5: () => import('../generated/descriptions/ps5.js'),
}

const CONST_INDICE = {
  ps1: 'PS1_INDEX',
  ps2: 'PS2_INDEX',
  psp: 'PSP_INDEX',
  ps3: 'PS3_INDEX',
  xbox360: 'XBOX360_INDEX',
  ps4: 'PS4_INDEX',
  ps5: 'PS5_INDEX',
}

const CONST_DESCRIPCION = {
  ps1: 'PS1_DESCRIPCIONES',
  ps2: 'PS2_DESCRIPCIONES',
  psp: 'PSP_DESCRIPCIONES',
  ps3: 'PS3_DESCRIPCIONES',
  xbox360: 'XBOX360_DESCRIPCIONES',
  ps4: 'PS4_DESCRIPCIONES',
  ps5: 'PS5_DESCRIPCIONES',
}

/** Cache: si ya se cargo una consola, no se vuelve a pedir. */
const yaCargados = new Map()
const descripcionesCargadas = new Map()

/** Cuantos juegos hay en cada consola. Se sabe sin cargar nada. */
export function getCount(slug) {
  return CONSOLE_COUNTS[slug] ?? 0
}

export function totalCount() {
  return Object.values(CONSOLE_COUNTS).reduce((a, n) => a + n, 0)
}

/** Las tres caratulas de muestra de la portada. */
export function getPreviews(slug) {
  return CONSOLE_PREVIEWS[slug] ?? []
}

export function getFavorites(slug) {
  return FAVORITES[slug] ?? []
}

/**
 * Trae el catalogo de una consola, ya con favoritos puestos.
 * Devuelve `null` si esa consola no existe.
 */
export async function loadGames(slug) {
  if (yaCargados.has(slug)) return yaCargados.get(slug)

  const cargar = CARGAS_INDICE[slug]
  if (!cargar) return null

  const mod = await cargar()
  const indice = mod[CONST_INDICE[slug]] ?? []

  const favoritos = new Set(FAVORITES[slug] ?? [])
  const juegos = indice.map((j) => ({ ...j, favorite: favoritos.has(j.id) }))

  yaCargados.set(slug, juegos)
  return juegos
}

/** Trae solo las descripciones de una consola. */
export async function loadDescriptions(slug) {
  if (descripcionesCargadas.has(slug)) return descripcionesCargadas.get(slug)

  const cargar = CARGAS_DESCRIPCION[slug]
  if (!cargar) return {}

  const mod = await cargar()
  const mapa = mod[CONST_DESCRIPCION[slug]] ?? {}
  descripcionesCargadas.set(slug, mapa)
  return mapa
}

/**
 * Precalienta una consola: hace el import() sin esperar. Se llama al pasar
 * el mouse por el enlace, para que este cargado cuando llegue el clic.
 */
export function prefetch(slug) {
  if (CARGAS_INDICE[slug]) CARGAS_INDICE[slug]()
}