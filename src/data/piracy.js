/**
 * ============================================================================
 *  SECCION "PIRATEO"  --  EDITA SOLO ESTE ARCHIVO
 * ============================================================================
 *  Informacion de los servicios de modificacion de consolas y sus precios.
 *  Para ocultar la seccion entera: pon `visible: false` en la constante de abajo.
 */

export const PIRACY_VISIBLE = true

export const PIRACY = {
  intro:
    'Modificamos consolas para poder jugar tus copias de seguridad. Trabajo prolijo, con garantia y sin perderte los juegos digitales ni los saves originales.',

  disclaimer:
    'Servicio tecnico de modificacion de consolas. Los precios de los servicios se confirman por WhatsApp segun el modelo exacto de la consola.',

  /** Grupos de servicios: cada uno tiene sus versiones/precios. */
  services: [
    {
      id: 'modchips',
      title: 'Modchip / JTAG',
      console: 'PS2 · PS3',
      icon: 'chip',
      description:
        'Instalacion de modchip para jugar backups en disco duro o memoria. Incluye instalacion y configuracion inicial.',
      versions: [
        { name: 'PS2 Slim', price: 'Consultar', notes: 'Incluye mano y switch de alimentacion.' },
        { name: 'PS2 Fat', price: 'Consultar', notes: 'Version original 4GB/8GB.' },
        { name: 'PS3 Fat (allslim)', price: 'Consultar', notes: 'Copia de NAND incluida.' },
        { name: 'PS3 Slim', price: 'Consultar', notes: 'Solo para modelos NOR flash.' },
      ],
    },
    {
      id: 'softmod',
      title: 'Softmod / Homebrew',
      console: 'PS2 · PS3 · Xbox 360',
      icon: 'wrench',
      description:
        'Software modification sin cambiar hardware. Ideal si solo queres backups en un pendrive o disco externo.',
      versions: [
        { name: 'FreeMCBoot (PS2)', price: 'Consultar', notes: 'Instalacion con pendrive.' },
        { name: 'OtherOS + launcher (PS3)', price: 'Consultar', notes: 'Requiere consola con HDMI o chip distinto.' },
        { name: 'Linux Booting (Xbox 360)', price: 'Consultar', notes: 'Para modelos con exploit y DVD viable.' },
      ],
    },
    {
      id: 'full-mod',
      title: 'Mod Completa',
      console: 'PS3 · Xbox 360 · PS4 · PS5',
      icon: 'star',
      description:
        'Servicio integral: apertura, modificacion, lodgeo del juego en disco interno y verificacion de que todo funciona.',
      versions: [
        { name: 'PS3 Slim (E3 / NOR)', price: 'Consultar', notes: 'Mod completa con prueba de arranque.' },
        { name: 'Xbox 360 Slim', price: 'Consultar', notes: 'Incluye ventilacion y limpieza.' },
        { name: 'PS4 Slim / Pro', price: 'Consultar', notes: 'Mod de firmware seguro.' },
        { name: 'PS5 Digital', price: 'Consultar', notes: 'Solo modelos con disco.' },
      ],
    },
    {
      id: 'services',
      title: 'Servicio Tecnico',
      console: 'Todas las consolas',
      icon: 'wrench',
      description:
        'Limpieza profunda, cambio de fuente, reparacion de lectora, cambio de pasta termica y recambio de bateria interna.',
      versions: [
        { name: 'Limpieza completa', price: 'Consultar', notes: 'Desarmado, aspirado y repaste.' },
        { name: 'Cambio de fuente', price: 'Consultar', notes: 'Incluye fuente nueva.' },
        { name: 'Cambio de lectora', price: 'Consultar', notes: 'Modelo compatible disponible.' },
        { name: 'Cambio de bateria', price: 'Consultar', notes: 'PS3, PS4 y PS5.' },
      ],
    },
  ],
}
