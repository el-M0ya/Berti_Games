/**
 * Tests del filtrado y el orden del catalogo.
 *
 * Uso: node tools/test_catalog.mjs
 */
import {
  SORTS,
  DEFAULT_SORT,
  genresDisponibles,
  playersDisponibles,
  filtrarYOrdenar,
} from '../src/lib/catalog.js'
import { buildSearchIndex, parseQuery, splitTerms, normalize } from '../src/lib/text.js'

let fallos = 0

function check(nombre, condicion, detalle = '') {
  if (condicion) {
    console.log(`  OK    ${nombre}`)
  } else {
    console.log(`  FALLA ${nombre}  ${detalle}`)
    fallos += 1
  }
}

function eq(nombre, obtenido, esperado) {
  const a = JSON.stringify(obtenido)
  const b = JSON.stringify(esperado)
  check(nombre, a === b, `\n         esperado ${b}\n         obtenido  ${a}`)
}

const JUEGOS = [
  { id: 'a', title: 'Bloodborne', year: 2015, genres: ['Accion', 'Aventura'], players: ['1 jugador'], favorite: true },
  { id: 'b', title: 'alphabet of love', year: 2010, genres: ['Peleas'], players: ['1 jugador', '2 jugadores'], favorite: false },
  { id: 'c', title: 'Call of Duty 4', year: 2007, genres: ['Disparadores'], players: ['1 jugador', '2 jugadores', '4 jugadores'], favorite: true },
  { id: 'd', title: 'Crimson Commando', year: 2008, genres: ['Disparadores', 'Accion'], players: ['1 jugador'], favorite: false },
  { id: 'e', title: '007 Ávil', year: 1999, genres: ['Arcade'], players: ['4 jugadores'], favorite: false },
]

const OPC = (extra = {}) => ({
  texto: '',
  jugador: '',
  genero: '',
  orden: DEFAULT_SORT,
  votos: {},
  indice: buildSearchIndex(JUEGOS),
  ...extra,
})

console.log('\nNormalizacion de texto:')
eq('quita tildes', normalize('Ávil Ñandú'), 'avil nandu')
eq('minusculas', normalize('BLOODBORNE'), 'bloodborne')
eq('busca por genero', normalize('Acción'), 'accion')

console.log('\nOrden por defecto (destacados):')
{
  const r = filtrarYOrdenar(JUEGOS, OPC()).map((g) => g.title)
  eq('favoritos arriba, y en alfa dentro de cada grupo', r, [
    'Bloodborne',
    'Call of Duty 4',
    '007 Ávil',
    'alphabet of love',
    'Crimson Commando',
  ])
}

console.log('\nOrden alfabetico:')
{
  const r = filtrarYOrdenar(JUEGOS, OPC({ orden: 'alfabetico' })).map((g) => g.title)
  eq('ignora los favoritos, ordena todo por nombre', r, [
    '007 Ávil',
    'alphabet of love',
    'Bloodborne',
    'Call of Duty 4',
    'Crimson Commando',
  ])
}

console.log('\nOrden por votos:')
{
  const votos = { a: { up: 10, down: 0, mine: 0 }, b: { up: 3, down: 0, mine: 0 }, d: { up: 50, down: 49, mine: 0 } }
  const r = filtrarYOrdenar(JUEGOS, OPC({ orden: 'votos', votos })).map((g) => g.title)
  // a=10, d=1, b=3, c=0, e=0
  eq('ordena por la diferencia votos menos votos en contra', r, [
    'Bloodborne',
    'alphabet of love',
    'Crimson Commando',
    '007 Ávil',
    'Call of Duty 4',
  ])
}

console.log('\nBuscador:')
{
  eq('encuentra ignorando mayusculas', filtrarYOrdenar(JUEGOS, OPC({ texto: 'bloodborne' })).map((g) => g.id), ['a'])
  eq('encuentra ignorando tildes', filtrarYOrdenar(JUEGOS, OPC({ texto: 'avil' })).map((g) => g.id), ['e'])
  eq('varias palabras, en cualquier orden', filtrarYOrdenar(JUEGOS, OPC({ texto: 'call duty' })).map((g) => g.id), ['c'])
  eq('busca por anio', filtrarYOrdenar(JUEGOS, OPC({ texto: '2007' })).map((g) => g.id), ['c'])
  eq('anio + palabra', filtrarYOrdenar(JUEGOS, OPC({ texto: 'crimson 2008' })).map((g) => g.id), ['d'])
  eq('busca por genero', filtrarYOrdenar(JUEGOS, OPC({ texto: 'peleas' })).map((g) => g.id), ['b'])
  eq('sin resultados da lista vacia', filtrarYOrdenar(JUEGOS, OPC({ texto: 'zzzz' })), [])
  // "borne" ES parte de "bloodborne", asi que tiene que encontrarlo.
  eq('palabra dentro de otra', filtrarYOrdenar(JUEGOS, OPC({ texto: '  blood   borne  ' })).map((g) => g.id), ['a'])
  eq('palabra que no esta', filtrarYOrdenar(JUEGOS, OPC({ texto: '  zzz  ' })).map((g) => g.id), [])
}

console.log('\nFiltros:')
{
  eq('por 2 jugadores', filtrarYOrdenar(JUEGOS, OPC({ jugador: '2 jugadores' })).map((g) => g.id).sort(), ['b', 'c'])
  eq('por 4 jugadores', filtrarYOrdenar(JUEGOS, OPC({ jugador: '4 jugadores' })).map((g) => g.id).sort(), ['c', 'e'])
  // e es solo "4 jugadores": no tiene modo de un jugador, asi que no entra.
  eq('1 jugador deja fuera a los que no lo tienen', filtrarYOrdenar(JUEGOS, OPC({ jugador: '1 jugador' })).length, 4)
  eq('por genero', filtrarYOrdenar(JUEGOS, OPC({ genero: 'Disparadores' })).map((g) => g.id).sort(), ['c', 'd'])
  eq('filtros combinados', filtrarYOrdenar(JUEGOS, OPC({ jugador: '1 jugador', genero: 'Accion' })).map((g) => g.id).sort(), ['a', 'd'])
}

console.log('\nOpciones de los filtros:')
{
  const p = playersDisponibles(JUEGOS)
  eq('los tres valores, en orden', p, ['1 jugador', '2 jugadores', '4 jugadores'])
  const g = genresDisponibles(JUEGOS)
  eq('generos con su cuenta, los comunes primero', g, [
    { nombre: 'Accion', total: 2 },
    { nombre: 'Aventura', total: 1 },
    { nombre: 'Disparadores', total: 2 },
    { nombre: 'Peleas', total: 1 },
    { nombre: 'Arcade', total: 1 },
  ])
  eq('hay tres ordenes y el de por defecto es Destacados', [SORTS.length, DEFAULT_SORT], [3, 'destacados'])
}

console.log('\nLa lista original no se toca:')
{
  const original = [...JUEGOS]
  filtrarYOrdenar(JUEGOS, OPC({ orden: 'alfabetico' }))
  eq('ordenar no modifica el array de entrada', JUEGOS, original)
}

console.log('\nConsultas:')
{
  eq('divide en palabras', parseQuery('  Final   Fantasy  X '), ['final', 'fantasy', 'x'])
  eq('separa los anios', splitTerms(['final', '1999', 'fantasy', '2007']), {
    palabras: ['final', 'fantasy'],
    anos: ['1999', '2007'],
  })
}

console.log(fallos === 0 ? '\nTodos los tests pasaron.' : `\n${fallos} test(s) fallaron.`)
process.exit(fallos === 0 ? 0 : 1)