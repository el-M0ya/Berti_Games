/**
 * API de votos, como Cloudflare Pages Function.
 *
 * Se deploya sola junto con el sitio: no hay que configurar nada extra
 * porque la funcion vive en /functions/api/votes.js.
 *
 * Endpoints:
 *   GET  /api/votes              -> { total: { juegoId: votos }, yo: { juegoId: voto } }
 *   POST /api/votes              { gameId, direction }  (direction: 1, -1 o 0)
 *
 * La base de datos es D1 (SQLite) y laConnecta la variable de entorno
 * VOTOS. Se crea con los comandos del README.
 */

const MAX_ID = 120
const MAX_CLIENT = 64
// Pausa minima entre dos votos del mismo navegador para el mismo juego.
// NO es una proteccion contra spam (de eso se encarga Cloudflare por
// separado): es para que un doble clic no mande dos peticiones.
//
// Tiene que ser CORTO. Con 2 segundos, cambiar "me gusta" por "no me gusta"
// al momento se perdia, y la persona creia que el boton no funcionaba.
const ESPERA_MINIMA_MS = 300

function json(datos, estado = 200, cabeceras = {}) {
  return new Response(JSON.stringify(datos), {
    status: estado,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      ...cabeceras,
    },
  })
}

/**
 * Solo dejamos escribir desde el sitio de verdad. Sin esto, cualquiera
 * podria usar su pagina para mandar votos falsos desde el navegador de la
 * gente.
 */
function permitido(request, env) {
  const origen = request.headers.get('Origin')
  // Peticiones sin Origin (curl, health checks) se permiten.
  if (!origen) return true
  const permitido_ = env.SITIO_ORIGIN
  if (!permitido_) return true // en desarrollo
  return origen === permitido_
}

function idValido(valor) {
  return (
    typeof valor === 'string' &&
    valor.length > 0 &&
    valor.length <= MAX_ID &&
    /^[a-z0-9._-]+$/i.test(valor)
  )
}

function clientValido(valor) {
  return typeof valor === 'string' && valor.length > 0 && valor.length <= MAX_CLIENT
}

export async function onRequestOptions() {
  return new Response(null, { status: 204 })
}

export async function onRequestGet({ request, env }) {
  if (!permitido(request, env)) {
    return json({ error: 'origen no permitido' }, 403)
  }

  const { results } = await env.VOTOS.prepare(
    `SELECT game_id, SUM(direction) AS total FROM votes GROUP BY game_id`,
  ).all()

  const total = {}
  for (const fila of results) {
    total[fila.game_id] = fila.total
  }

  // Cache corta: los votos cambian poco y asi no golpeamos la base por todo.
  return json(
    { total },
    200,
    { 'Cache-Control': 'public, max-age=60, s-maxage=60' },
  )
}

export async function onRequestPost({ request, env }) {
  if (!permitido(request, env)) {
    return json({ error: 'origen no permitido' }, 403)
  }

  let cuerpo
  try {
    cuerpo = await request.json()
  } catch {
    return json({ error: 'json invalido' }, 400)
  }

  const gameId = cuerpo?.gameId
  const direction = cuerpo?.direction
  const clientId = request.headers.get('X-Berti-Client')

  if (!idValido(gameId)) return json({ error: 'gameId invalido' }, 400)
  if (!clientValido(clientId)) return json({ error: 'falta el id del cliente' }, 400)
  if (![1, -1, 0].includes(direction)) {
    return json({ error: 'direction debe ser 1, -1 o 0' }, 400)
  }

  const ahora = Date.now()

  // Freno simple: no mas de un voto por juego cada 2 segundos.
  // Chica la idea, pero evita que un clic repetido llene la base de basura.
  const previo = await env.VOTOS.prepare(
    `SELECT updated_at FROM votes WHERE game_id = ? AND client_id = ?`,
  )
    .bind(gameId, clientId)
    .first()

  if (previo && ahora - previo.updated_at < ESPERA_MINIMA_MS) {
    const total = await totalDeJuego(env, gameId)
    return json({ ok: true, gameId, total, ignorado: true })
  }

  if (direction === 0) {
    // Voto 0 = sacar el voto (el boton pulsado dos veces).
    await env.VOTOS.prepare(
      `DELETE FROM votes WHERE game_id = ? AND client_id = ?`,
    )
      .bind(gameId, clientId)
      .run()
  } else {
    await env.VOTOS.prepare(
      `INSERT INTO votes (game_id, client_id, direction, updated_at)
       VALUES (?, ?, ?, ?)
       ON CONFLICT (game_id, client_id)
       DO UPDATE SET direction = excluded.direction, updated_at = excluded.updated_at`,
    )
      .bind(gameId, clientId, direction, ahora)
      .run()
  }

  const total = await totalDeJuego(env, gameId)
  return json({ ok: true, gameId, total })
}

async function totalDeJuego(env, gameId) {
  const fila = await env.VOTOS.prepare(
    `SELECT COALESCE(SUM(direction), 0) AS total FROM votes WHERE game_id = ?`,
  )
    .bind(gameId)
    .first()
  return fila?.total ?? 0
}