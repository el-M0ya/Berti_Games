/**
 * Votos de los visitantes.
 *
 * Hay dos almacenes y la web no sabe cual esta usando:
 *
 *   1. La API de Cloudflare D1 (`/api/votes`), que comparten todos.
 *   2. `localStorage`, que solo ve la persona que vota.
 *
 * Se usa la API y, si no esta disponible (la web abierta desde un archivo,
 * sin internet, o antes de haber configurado Cloudflare), se cae al
 * localStorage sin romper nada. Los votos se guardan siempre en local al
 * instante, asi que la interfaz nunca se siente lenta.
 *
 * Este archivo es la unica frontera entre la web y el almacen. Cambiar de
 * tecnologia mas adelante es modificar aca y nada mas.
 */

const CLAVE_VOTOS = 'berti-games:votos'
const CLAVE_CLIENTE = 'berti-games:cliente'
const EVENTO = 'berti-games:voto-cambiado'
const API = '/api/votes'

/** Quantas veces se reintenta si la API falla. */
const REINTENTOS = 2

// ---------------------------------------------------------------------------
// Almacen local
// ---------------------------------------------------------------------------

function leerLocal() {
  try {
    const raw = window.localStorage.getItem(CLAVE_VOTOS)
    const parsed = raw ? JSON.parse(raw) : null
    return parsed && typeof parsed === 'object' ? parsed : {}
  } catch {
    return {}
  }
}

function guardarLocal(votos) {
  try {
    window.localStorage.setItem(CLAVE_VOTOS, JSON.stringify(votos))
  } catch {
    // Modo privado o cuota llena: el voto igual se ve en esta sesion.
  }
  window.dispatchEvent(new CustomEvent(EVENTO))
}

// ---------------------------------------------------------------------------
// Identidad del visitante
// ---------------------------------------------------------------------------

/**
 * Un id aleatorio que se guarda en este navegador. NO es la IP ni ningun
 * dato personal: solo sirve para que una persona vote una vez por juego.
 */
function clienteId() {
  try {
    let id = window.localStorage.getItem(CLAVE_CLIENTE)
    if (!id) {
      id = crypto.randomUUID()
      window.localStorage.setItem(CLAVE_CLIENTE, id)
    }
    return id
  } catch {
    return 'anonimo'
  }
}

// ---------------------------------------------------------------------------
// La API
// ---------------------------------------------------------------------------

/** Trae los votos de todos. Devuelve { juegoId: total } o null si falla. */
async function pedirTotales() {
  for (let intento = 0; intento <= REINTENTOS; intento++) {
    try {
      const res = await fetch(API, { headers: { Accept: 'application/json' } })
      if (!res.ok) throw new Error(`HTTP ${res.status}`)
      const datos = await res.json()
      return datos?.total ?? null
    } catch {
      if (intento < REINTENTOS) {
        // Espera corta y se reintenta: puede ser un problema de red pasajero.
        await new Promise((r) => setTimeout(r, 400 * (intento + 1)))
      }
    }
  }
  return null
}

/** Manda un voto a la API. Devuelve el total del juego, o null si falla. */
async function enviarVoto(gameId, direction) {
  try {
    const res = await fetch(API, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Berti-Client': clienteId(),
      },
      body: JSON.stringify({ gameId, direction }),
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const datos = await res.json()
    return typeof datos?.total === 'number' ? datos.total : null
  } catch {
    return null
  }
}

// ---------------------------------------------------------------------------
// Interfaz que usa el resto de la web
// ---------------------------------------------------------------------------

/** Voto neto de un juego: positivos menos negativos. */
export function score(votos, id) {
  const v = votos[id]
  if (!v) return 0
  return (v.total ?? (v.up | 0) - (v.down | 0))
}

/** Que voto esta persona: 1, -1 o 0. */
export function myVote(votos, id) {
  const v = votos[id]
  if (!v) return 0
  if (v.mine === 1 || v.mine === -1) return v.mine
  return v.mine === 0 ? 0 : 0
}

/** Lee lo que hay guardado en este navegador, al instante. */
export function cargar() {
  return leerLocal()
}

/**
 * Se suscribe a los cambios de voto (otra pestana, o este mismo tab).
 * Devuelve la baja.
 */
export function subscribe(alCambiar) {
  const enVentana = (e) => {
    if (e.key === CLAVE_VOTOS || e.type === EVENTO) alCambiar(leerLocal())
  }
  window.addEventListener('storage', enVentana)
  window.addEventListener(EVENTO, enVentana)
  return () => {
    window.removeEventListener('storage', enVentana)
    window.removeEventListener(EVENTO, enVentana)
  }
}

/**
 * Cuando la web arranca, baja los votos de todos y los mezcla con los
 * locales. Si la API no responde, no pasa nada: seguimos con local.
 *
 * Devuelve { votos, conectado } para que la interfaz pueda avisarle a la
 * persona de si su voto se esta guardando en el servidor o solo aqui.
 */
export async function sincronizar() {
  const totales = await pedirTotales()
  if (!totales) {
    return { votos: leerLocal(), conectado: false }
  }

  const mios = leerLocal()
  const mezclados = {}

  for (const [gameId, total] of Object.entries(totales)) {
    mezclados[gameId] = {
      total,
      up: total > 0 ? total : 0,
      down: total < 0 ? -total : 0,
      mine: mios[gameId]?.mine ?? 0,
    }
  }

  // Los votos que aun no llegaron a la API (si votamos sin conexion).
  for (const [gameId, mio] of Object.entries(mios)) {
    if (!mezclados[gameId]) {
      mezclados[gameId] = {
        total: (mio.up | 0) - (mio.down | 0),
        up: mio.up | 0,
        down: mio.down | 0,
        mine: mio.mine ?? 0,
      }
    }
  }

  guardarLocal(mezclados)
  return { votos: mezclados, conectado: true }
}

/**
 * Registra un voto. Volver a pulsar el mismo boton lo saca; pulsar el
 * contrario cambia de lado.
 *
 * Devuelve los votos ya actualizados, para que la interfaz los pinte al
 * instante sin esperar a la red.
 */
export async function votar(votos, gameId, direction) {
  const actuales = { ...votos }
  const previo = actuales[gameId] || { total: 0, up: 0, down: 0, mine: 0 }

  const desarmado = {
    total: (previo.total ?? (previo.up | 0) - (previo.down | 0)),
    up: previo.up | 0,
    down: previo.down | 0,
    mine: previo.mine ?? 0,
  }

  if (desarmado.mine === direction) {
    // Segundo clic en el mismo boton: se anula.
    desarmado.up -= direction === 1 ? 1 : 0
    desarmado.down -= direction === -1 ? 1 : 0
    desarmado.mine = 0
  } else {
    // Si venia del otro lado, primero se saca ese voto.
    desarmado.up -= desarmado.mine === 1 ? 1 : 0
    desarmado.down -= desarmado.mine === -1 ? 1 : 0
    desarmado.up += direction === 1 ? 1 : 0
    desarmado.down += direction === -1 ? 1 : 0
    desarmado.mine = direction
  }

  desarmado.up = Math.max(0, desarmado.up)
  desarmado.down = Math.max(0, desarmado.down)
  desarmado.total = desarmado.up - desarmado.down

  if (desarmado.up === 0 && desarmado.down === 0) delete actuales[gameId]
  else actuales[gameId] = desarmado

  guardarLocal(actuales)

  // Ahora si, a la API. Si no hay, aqui se acaba y el voto queda local.
  const directionApi = desarmado.mine === 0 ? 0 : desarmado.mine
  const totalServidor = await enviarVoto(gameId, directionApi)
  if (totalServidor !== null) {
    const ajustados = { ...leerLocal() }
    const base = ajustados[gameId] || { up: 0, down: 0, mine: 0 }
    ajustados[gameId] = {
      total: totalServidor,
      up: totalServidor > 0 ? totalServidor : 0,
      down: totalServidor < 0 ? -totalServidor : 0,
      mine: base.mine,
    }
    guardarLocal(ajustados)
    return ajustados
  }

  return actuales
}