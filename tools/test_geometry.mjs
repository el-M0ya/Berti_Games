/**
 * Tests de la geometria de la ficha de juego.
 *
 * Corre con:  node tools/test_geometry.mjs
 * No necesita framework: si algo falla, sale con codigo 1.
 */
import { computeGeometry, panelMaxHeight, panelMargin, overlaps, DESKTOP_MIN, PANEL_MAX_W } from '../src/components/detailGeometry.js'

let fallos = 0

function check(nombre, cond, detalle = '') {
  if (cond) {
    console.log(`  OK   ${nombre}`)
  } else {
    console.log(`  FALLA ${nombre} ${detalle}`)
    fallos += 1
  }
}

const VIEWPORTS = [
  { vw: 360, vh: 640, nombre: 'celular chico' },
  { vw: 390, vh: 844, nombre: 'iPhone' },
  { vw: 768, vh: 1024, nombre: 'tablet' },
  { vw: 1000, vh: 700, nombre: 'ventana angosta' },
  { vw: 1280, vh: 720, nombre: 'escritorio' },
  { vw: 1920, vh: 1080, nombre: 'pantalla grande' },
]

console.log('Geometria de la ficha:\n')

for (const { vw, vh, nombre } of VIEWPORTS) {
  // Tarjeta original en el medio de la grilla.
  const originRect = { left: 300, top: 500, width: 190, height: 253 }
  const geo = computeGeometry(vw, vh, originRect)
  const expectedDesktop = vw >= DESKTOP_MIN

  console.log(`${nombre} (${vw}x${vh})`)

  check('detecta el layout correcto', geo.desktop === expectedDesktop,
    `esperado ${expectedDesktop}, dio ${geo.desktop}`)

  // La carta final tiene que entrar completa en pantalla.
  check('la carta entra en el ancho', geo.end.x >= 0 && geo.end.x + geo.end.w <= vw,
    `x=${geo.end.x} w=${geo.end.w} vw=${vw}`)
  check('la carta entra en el alto', geo.end.y >= 0 && geo.end.y + geo.end.h <= vh,
    `y=${geo.end.y} h=${geo.end.h} vh=${vh}`)

  // Arranca exactamente donde estaba la tarjeta.
  check('arranca en la tarjeta', geo.start.x === originRect.left && geo.start.y === originRect.top)
  check('arranca con el tamano de la tarjeta',
    geo.start.w === originRect.width && geo.start.h === originRect.height)

  // En escritorio la carta va a la izquierda; en celular, centrada.
  if (geo.desktop) {
    check('la carta queda a la izquierda', geo.end.x <= 64, `x=${geo.end.x}`)
  } else {
    const centrado = Math.abs(geo.end.x + geo.end.w / 2 - vw / 2) <= 1
    check('la carta queda centrada', centrado, `x=${geo.end.x} w=${geo.end.w} vw=${vw}`)
  }

  // El panel no puede tapar la carta.
  const panelH = panelMaxHeight(vw, vh, geo)
  const margin = panelMargin(vw)
  const panelW = Math.min(PANEL_MAX_W, vw)
  const panelBox = geo.desktop
    ? { x: vw - margin - panelW, y: (vh - panelH) / 2, w: panelW, h: panelH }
    : { x: 0, y: vh - panelH, w: vw, h: panelH }
  check('el panel no tapa la carta', !overlaps(geo.end, panelBox),
    `carta=${JSON.stringify(geo.end)} panel=${JSON.stringify(panelBox)}`)
  check('el panel entra en pantalla', panelBox.x >= 0 && panelBox.x + panelBox.w <= vw)

  // Sin rectangulo de origen tiene que entrar desde arriba.
  const sinOrigen = computeGeometry(vw, vh, null)
  check('sin origen entra desde arriba', sinOrigen.start.y < 0, `y=${sinOrigen.start.y}`)
  check('sin origen mantiene el ancho final', sinOrigen.start.w === sinOrigen.end.w)

  console.log('')
}

console.log(fallos === 0 ? 'Todos los tests pasaron.' : `${fallos} test(s) fallaron.`)
process.exit(fallos === 0 ? 0 : 1)
