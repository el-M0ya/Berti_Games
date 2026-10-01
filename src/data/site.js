/**
 * ============================================================================
 *  DATOS DE CONTACTO  --  EDITA SOLO ESTE ARCHIVO
 * ============================================================================
 *  Pon aqui tus datos reales. Todo el resto de la web los lee de aqui.
 */
export const SITE = {
  name: 'Berti Games',
  logo: 'BG',
  claim: 'Venta de juegos y liberacion de consolas',
  shortDescription:
    'Catalogo de juegos disponibles para PS2, PS3, Xbox 360, PS4 y PS5. Ven y llevatelo.',

  contact: {
    // Numero de celular (whatsapp). Formato internacional sin espacios ni signos.
    mobile: '+53 55924968',
    mobileRaw: '5355924968',
    mobileLabel: 'Movil / WhatsApp',

    // Numero de telefono fijo de la casa.
    landline: '78664865',
    landlineLabel: 'Telefono fijo',

    email: 'bertigames@gmail.com',
    instagram: 'https://instagram.com/bertigames',
    instagramHandle: '@bertigames',
  },

  address: {
    street: 'Campanario #60 e/ San Lázaro y Lagunas',
    floor: 'Bajos',
    city: 'Centro Habana',
    province: 'La Habana',
    zip: '10200',
    country: 'Cuba',
    mapsUrl: 'https://maps.app.goo.gl/8NrPCpitSsfHM7UB9',
  },

  hours: [
    { days: 'Lunes a Sabado', time: '10:00 am - 6:00 pm' },
    { days: 'Domingos', time: 'Cerrado' },
  ],
}

/** Linea formateada para mostrar la direccion en una sola linea. */
export function formatAddress() {
  const a = SITE.address
  return [a.street, a.floor, a.city, a.province].filter(Boolean).join(', ')
}
