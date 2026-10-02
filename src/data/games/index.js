/**
 * Indice de catalogos. El script Python `tools/scan_games.py` escribe los
 * archivos de cada consola dentro de esta carpeta.
 */
import { PS1_GAMES } from './ps1.js'
import { PS2_GAMES } from './ps2.js'
import { PSP_GAMES } from './psp.js'
import { PS3_GAMES } from './ps3.js'
import { XBOX360_GAMES } from './xbox360.js'
import { PS4_GAMES } from './ps4.js'
import { PS5_GAMES } from './ps5.js'

export const GAMES_BY_CONSOLE = {
  ps1: PS1_GAMES,
  ps2: PS2_GAMES,
  psp: PSP_GAMES,
  ps3: PS3_GAMES,
  xbox360: XBOX360_GAMES,
  ps4: PS4_GAMES,
  ps5: PS5_GAMES,
}

/** Devuelve el catalogo de una consola, o una lista vacia si no existe. */
export function getGames(slug) {
  return GAMES_BY_CONSOLE[slug] ?? []
}

/** Cuenta total de juegos de toda la web. */
export function totalGames() {
  return Object.values(GAMES_BY_CONSOLE).reduce((acc, list) => acc + list.length, 0)
}
