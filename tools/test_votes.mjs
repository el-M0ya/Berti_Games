/**
 * Tests de la logica de votos.
 *
 * Corre en Node sin navegador: se falsea un localStorage minimo para poder
 * probar la parte local, y la parte de la API se comprueba por separado.
 *
 * Uso: node tools/test_votes.mjs
 */

// Guardamos el codigo y ejecutamos el modulo con un localStorage falso.
const almacen = new Map()
globalThis.window = {
  localStorage: {
    getItem: (k) => (almacen.has(k) ? almacen.get(k) : null),
    setItem: (k, v) => almacen.set(k, String(v)),
    removeItem: (k) => almacen.delete(k),
  },
  dispatchEvent: () => {},
  addEventListener: () => {},
  removeEventListener: () => {},
}
globalThis.localStorage = globalThis.window.localStorage
globalThis.CustomEvent = class {}

// Node 24 ya trae crypto, pero randomUUID puede faltar en versiones viejas:
// lo definimos solo si no existe.
if (!globalThis.crypto?.randomUUID) {
  globalThis.crypto = { randomUUID: () => 'test-uuid-1234' }
}

const votes = await import('../src/lib/votes.js')

let fallos = 0
function eq(nombre, obtenido, esperado) {
  const a = JSON.stringify(obtenido)
  const b = JSON.stringify(esperado)
  if (a === b) {
    console.log(`  OK    ${nombre}`)
  } else {
    console.log(`  FALLA ${nombre}\n         esperado ${b}\n         obtenido  ${a}`)
    fallos += 1
  }
}

console.log('\nPuntaje y voto propio:')
eq('sin votos vale 0', votes.score({}, 'a'), 0)
eq('positivo', votes.score({ a: { total: 5, up: 5, down: 0, mine: 1 } }, 'a'), 5)
eq('negativo', votes.score({ a: { total: -3, up: 0, down: 3, mine: -1 } }, 'a'), -3)
eq('sin voto propio es 0', votes.myVote({ a: { total: 9, up: 9, down: 0 } }, 'a'), 0)
eq('formato viejo sin total', votes.score({ a: { up: 4, down: 1, mine: 1 } }, 'a'), 3)

console.log('\nUn clic (con la API caida, se queda en local):')
{
  // Sin fetch definido, la parte de la API falla y devuelve null.
  let v = await votes.votar({}, 'juego1', 1)
  eq('me gusta deja +1', [votes.score(v, 'juego1'), votes.myVote(v, 'juego1')], [1, 1])

  v = await votes.votar(v, 'juego1', 1)
  eq('segundo clic saca el voto', [votes.score(v, 'juego1'), votes.myVote(v, 'juego1')], [0, 0])

  v = await votes.votar(v, 'juego1', -1)
  eq('no me gusta deja -1', [votes.score(v, 'juego1'), votes.myVote(v, 'juego1')], [-1, -1])

  v = await votes.votar(v, 'juego1', 1)
  eq('cambiar de lado pasa de -1 a +1', [votes.score(v, 'juego1'), votes.myVote(v, 'juego1')], [1, 1])

  v = await votes.votar(v, 'juego1', -1)
  eq('y otra vez al otro lado', [votes.score(v, 'juego1'), votes.myVote(v, 'juego1')], [-1, -1])

  v = await votes.votar(v, 'juego1', -1)
  eq('sacar el voto', [votes.score(v, 'juego1'), votes.myVote(v, 'juego1')], [0, 0])
}

console.log('\nVotos de otra persona (los que baja la API):')
{
  almacen.clear()
  let v = await votes.votar({}, 'x', 1)
  // imagine que otro visitante vota +1 y este ya habia votado +1
  v = { x: { total: 2, up: 2, down: 0, mine: 1 } }
  eq('el total viene del servidor', votes.score(v, 'x'), 2)
  v = await votes.votar(v, 'x', -1)
  eq('cambiar de lado con votos ajenos', [votes.score(v, 'x'), votes.myVote(v, 'x')], [0, -1])
}

console.log('\nNunca queda en negativo y se limpia cuando llega a cero:')
{
  almacen.clear()
  let v = { y: { total: 0, up: 0, down: 1, mine: -1 } }
  v = await votes.votar(v, 'y', -1)
  // Cuando un juego queda en cero, la entrada se borra: no ocupa memoria.
  eq('la entrada se borra', 'y' in v, false)
  eq('y el total da 0 igual', votes.score(v, 'y'), 0)
}

console.log('\nSincronizar cuando la API no responde:')
{
  almacen.clear()
  const r = await votes.sincronizar()
  eq('avisa que no hay conexion', r.conectado, false)
  eq('devuelve los votos locales', r.votos, {})
}

console.log('\nGuarda y lee del local:')
{
  almacen.clear()
  const v = await votes.votar({}, 'z', 1)
  eq('lo que se vota se guarda', Object.keys(votes.cargar()).includes('z'), true)
}

console.log(fallos === 0 ? '\nTodos los tests pasaron.' : `\n${fallos} test(s) fallaron.`)
process.exit(fallos === 0 ? 0 : 1)