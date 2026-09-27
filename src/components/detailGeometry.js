/**
 * Geometria de la ficha de juego (la carta que vuela).
 *
 * Vive aparte del componente para poder probarla sin montar React.
 * Trabaja con numeros en vez de tocar el DOM, asi el mismo codigo sirve
 * para el layout de escritorio y el de celular.
 */

/** Ancho minimo para el layout de escritorio (carta a la izquierda + panel). */
export const DESKTOP_MIN = 1180

/**
 * Calcula donde arranca y donde termina la caratula animada.
 *
 * @param {number} vw          Ancho del viewport
 * @param {number} vh          Alto del viewport
 * @param {{left:number,top:number,width:number,height:number}|null} originRect
 *        Posicion de la tarjeta original. Si es null, entra desde arriba.
 * @returns {{start: object, end: object, desktop: boolean}}
 */
export function computeGeometry(vw, vh, originRect) {
  const desktop = vw >= DESKTOP_MIN

  let w
  let h
  let x
  let y

  if (desktop) {
    // Carta a la izquierda, centrada verticalmente.
    w = 300
    h = 420
    x = 48
    y = Math.max(24, Math.round((vh - h) / 2))
  } else {
    // Celular: carta angosta arriba y panel abajo, sin superponerse.
    w = Math.round(Math.min(180, vw * 0.46))
    h = Math.round(w * 1.4)
    x = Math.round((vw - w) / 2)
    y = Math.max(16, Math.round(vh * 0.04))
  }

  const end = { x, y, w, h }

  const start = originRect
    ? { x: originRect.left, y: originRect.top, w: originRect.width, h: originRect.height }
    : { x, y: -h, w, h }

  return { start, end, desktop }
}

/** Margen que el panel deja alrededor en escritorio: clamp(24, 4vw, 64). */
export function panelMargin(vw) {
  return Math.round(Math.min(Math.max(vw * 0.04, 24), 64))
}

/** Ancho maximo del panel. */
export const PANEL_MAX_W = 520

/** El panel no debe tapar la carta. Devuelve el alto maximo del panel. */
export function panelMaxHeight(vw, vh, geo) {
  if (geo.desktop) {
    return vh - panelMargin(vw) * 2
  }
  // Celular: la hoja inferior arranca debajo de la carta.
  return Math.max(200, Math.round(vh * 0.54))
}

/** ¿Se superponen la carta y el panel? Sirve para los tests. */
export function overlaps(a, b) {
  return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y
}
