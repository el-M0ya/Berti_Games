/**
 * Definicion de las consolas que existen en el catalogo.
 * `slug` se usa en la URL: /consola/ps2
 */
export const CONSOLES = [
  {
    slug: 'ps1',
    name: 'PlayStation',
    short: 'PS1',
    brand: 'Sony',
    year: 1994,
    accent: '#b07cff',
    accentSoft: 'rgba(176, 124, 255, 0.18)',
    tagline: 'La consola que abrio la era de los 3D en casa.',
  },
  {
    slug: 'ps2',
    name: 'PlayStation 2',
    short: 'PS2',
    brand: 'Sony',
    year: 2000,
    accent: '#2f6fe4',
    accentSoft: 'rgba(47, 111, 228, 0.18)',
    tagline: 'La consola mas vendida de la Historia.',
  },
  {
    slug: 'psp',
    name: 'PlayStation Portable',
    short: 'PSP',
    brand: 'Sony',
    year: 2004,
    accent: '#00c2a8',
    accentSoft: 'rgba(0, 194, 168, 0.18)',
    tagline: 'La consola portatil de Sony, con UMD y pantalla de 16:9.',
  },
  {
    slug: 'ps3',
    name: 'PlayStation 3',
    short: 'PS3',
    brand: 'Sony',
    year: 2006,
    accent: '#4a9eff',
    accentSoft: 'rgba(74, 158, 255, 0.18)',
    tagline: 'Larga Vida al Gameplay',
  },
  {
    slug: 'xbox360',
    name: 'Xbox 360',
    short: 'XBOX 360',
    brand: 'Microsoft',
    year: 2005,
    accent: '#7dc82f',
    accentSoft: 'rgba(125, 200, 47, 0.18)',
    tagline: 'La reina del Multijugador',
  },
  {
    slug: 'ps4',
    name: 'PlayStation 4',
    short: 'PS4',
    brand: 'Sony',
    year: 2013,
    accent: '#1f6feb',
    accentSoft: 'rgba(31, 111, 235, 0.18)',
    tagline: 'La grandeza aguarda. This is for the players',
  },
  {
    slug: 'ps5',
    name: 'PlayStation 5',
    short: 'PS5',
    brand: 'Sony',
    year: 2020,
    accent: '#e8f1ff',
    accentSoft: 'rgba(232, 241, 255, 0.14)',
    tagline: 'Play has no limits',
  },
]

export const CONSOLE_SLUGS = CONSOLES.map((c) => c.slug)

export function getConsole(slug) {
  return CONSOLES.find((c) => c.slug === slug)
}
