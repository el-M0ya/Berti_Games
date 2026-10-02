/**
 * Tests de la API de votos contra una base SQLite de verdad.
 *
 * Node 24 trae `node:sqlite`, asi que se puede probar el SQL y los handlers
 * reales sin tener una cuenta de Cloudflare. Se arma un adaptador chiquito
 * con la misma interfaz que usa D1 (prepare / bind / run / first / all).
 *
 * Uso: node tools/test_votes_api.mjs
 */
import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
// node:sqlite aparece en Node 22.5. Si no esta, avisamos bien en vez de
// reventar con un error de modulo que no dice nada.
let DatabaseSync
try {
  ;({ DatabaseSync } = await import('node:sqlite'))
} catch {
  console.log('\nEste test necesita Node 22.5 o superior (usa node:sqlite).')
  console.log(`Version actual: ${process.version}. No se ejecuta.\n`)
  process.exit(0)
}

const RAIZ = join(dirname(fileURLToPath(import.meta.url)), '..')
const votes = await import('../functions/api/votes.js')

let fallos = 0
function eq(nombre, obtenido, esperado) {
  const a = JSON.stringify(obtenido)
  const b = JSON.stringify(esperado)
  if (a === b) console.log(`  OK    ${nombre}`)
  else {
    console.log(`  FALLA ${nombre}\n         esperado ${b}\n         obtenido  ${a}`)
    fallos += 1
  }
}

// --- Base y adaptador estilo D1 ---------------------------------------------

const db = new DatabaseSync(':memory:')
db.exec(readFileSync(join(RAIZ, 'schema.sql'), 'utf8'))

const env = {
  VOTOS: {
    prepare(sql) {
      return {
        bind(...valores) {
          const args = valores.map(String)
          return {
            async run() {
              // node:sqlite no tiene exec con argumentos: hay que pasar por
              // prepare().run(), que es lo mismo que hace D1 por debajo.
              db.prepare(sql).run(...args)
              return { success: true }
            },
            async first() {
              const fila = db.prepare(sql).get(...valores.map(String))
              return fila ?? null
            },
            async all() {
              return { results: db.prepare(sql).all(...valores.map(String)) }
            },
          }
        },
        async all() {
          return { results: db.prepare(sql).all() }
        },
        async first() {
          return db.prepare(sql).get() ?? null
        },
      }
    },
  },
  SITIO_ORIGIN: 'https://ejemplo.github.io',
}

function pedir(metodo, url, { cuerpo, origen, cliente } = {}) {
  // Ojo: si un header vale undefined, la API de Headers lo convierte en el
  // texto "undefined". Hay que ponerlos solo si existen.
  const cabeceras = { 'Content-Type': 'application/json' }
  if (origen !== undefined) cabeceras.Origin = origen
  if (cliente !== undefined) cabeceras['X-Berti-Client'] = cliente

  return {
    request: new Request(`https://sitio.test${url}`, {
      method: metodo,
      headers: cabeceras,
      body: metodo === 'POST' ? JSON.stringify(cuerpo) : undefined,
    }),
    env,
  }
}

async function get(extra = {}) {
  const res = await votes.onRequestGet(pedir('GET', '/api/votes', { cliente: 'cliente-1', ...extra }))
  return { status: res.status, datos: await res.json() }
}

async function post(juego, direction, extra = {}) {
  const res = await votes.onRequestPost(
    pedir('POST', '/api/votes', {
      cuerpo: { gameId: juego, direction },
      cliente: 'cliente-1',
      ...extra,
    }),
  )
  return { status: res.status, datos: await res.json() }
}

// --- Tests -------------------------------------------------------------------

console.log('\nEmpezando con la base vacia:')
{
  const r = await get()
  eq('GET responde 200', r.status, 200)
  eq('sin votos todavia', r.datos.total, {})
}

console.log('\nVotar:')
{
  const r = await post('bloodborne', 1)
  eq('POST responde 200', r.status, 200)
  eq('total del juego en 1', r.datos.total, 1)
  eq('y viene en el listado', (await get()).datos.total, { bloodborne: 1 })
}

console.log('\nDos personas votan lo mismo:')
{
  await post('bloodborne', 1, { cliente: 'cliente-2' })
  eq('el total sube a 2', (await get()).datos.total.bloodborne, 2)
}

console.log('\nCambiar de lado:')
{
  // La pausa minima son 300 ms: hay que esperar antes de que el mismo
  // navegador vuelva a votar el mismo juego.
  await new Promise((r) => setTimeout(r, 350))
  await post('bloodborne', -1, { cliente: 'cliente-2' })
  // cliente-1 (+1) y cliente-2 (-1) = 0
  eq('queda en 0', (await get()).datos.total.bloodborne, 0)
}

console.log('\nSacar el voto (direction 0):')
{
  await post('bloodborne', 0, { cliente: 'cliente-1' })
  eq('solo queda el voto de cliente-2 (-1)', (await get()).datos.total.bloodborne, -1)
}

console.log('\nLa misma persona no puede votar dos veces:')
{
  db.exec("DELETE FROM votes")
  await post('juego-a', 1, { cliente: 'mismo' })
  await new Promise((r) => setTimeout(r, 350)) // espera el freno de 2 s
  await post('juego-a', 1, { cliente: 'mismo' })
  eq('el segundo voto REPLACE, no suma', (await get()).datos.total['juego-a'], 1)
}

console.log('\nFreno de spam (dos votos seguidos muy rapido):')
{
  db.exec("DELETE FROM votes")
  const uno = await post('juego-b', 1, { cliente: 'rapido' })
  const dos = await post('juego-b', -1, { cliente: 'rapido' })
  eq('el segundo se ignora', dos.datos.ignorado, true)
  eq('y avisa que se ignoro', dos.datos.ok, true)
  eq('el total queda como estaba', (await get()).datos.total['juego-b'], uno.datos.total)
}

console.log('\nDatos invalidos:')
{
  eq('gameId que no es texto', (await post('', 1)).status, 400)
  eq('gameId con caracteres raros', (await post('mal id; DROP TABLE', 1)).status, 400)
  eq('gameId demasiado largo', (await post('a'.repeat(200), 1)).status, 400)
  eq('direction invalida', (await post('juego-c', 7)).status, 400)
  eq('sin id de cliente', (await post('juego-c', 1, { cliente: undefined })).status, 400)
}

console.log('\nControl de origen:')
{
  eq('origen permitido', (await post('juego-d', 1, { origen: 'https://ejemplo.github.io' })).status, 200)
  eq('origen raro rechazado', (await post('juego-e', 1, { origen: 'https://malo.com' })).status, 403)
  eq('GET tambien', (await get({ origen: 'https://malo.com' })).status, 403)
  eq('sin Origin se permite (curl, health checks)', (await post('juego-f', 1)).status, 200)
}

console.log('\nVarios juegos:')
{
  db.exec('DELETE FROM votes')
  for (const [j, d] of [['j1', 1], ['j2', 1], ['j3', -1]]) {
    await post(j, d, { cliente: 'gente-' + j })
  }
  const t = (await get()).datos.total
  eq('solo devuelve los que tienen votos', t, { j1: 1, j2: 1, j3: -1 })
}

console.log('\nCache:')
{
  const res = await votes.onRequestGet(pedir('GET', '/api/votes'))
  eq('dice que se puede cachear', res.headers.get('Cache-Control'), 'public, max-age=60, s-maxage=60')
}

console.log(fallos === 0 ? '\nTodos los tests pasaron.' : `\n${fallos} test(s) fallaron.`)
process.exit(fallos === 0 ? 0 : 1)