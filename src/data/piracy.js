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
    'Liberamos consolas para poder jugar tus juegos favoritos. Trabajo prolijo, con garantia y sin perderte los juegos digitales que tanto buscas.',

  disclaimer:
    'Servicio tecnico de liberación de consolas. Los precios de los servicios se confirman por WhatsApp segun el modelo exacto de la consola.',

  /** Grupos de servicios: cada uno tiene sus versiones/precios. */
  services: [
    {
      id: 'Pirateo_PS2',
      title: 'Pirateo PS2',
      console: 'PS2',
      icon: 'chip',
      description:
        'Liberacion de consolas PS2 mediante la Memory Card',
      versions: [
        { name: 'PS2 Slim', price: 'Consultar', notes: '' },
        { name: 'PS2 Fat', price: 'Consultar', notes: '' },
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
  ],
}
