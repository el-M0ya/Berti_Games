/**
 * ============================================================================
 *  DATOS DE CONTACTO  --  EDITA SOLO ESTE ARCHIVO
 * ============================================================================
 *  Pon aqui tus datos reales. Todo el resto de la web los lee de aqui.
 */
export const SITE = {
  name: 'Berti Games',
  logo: 'BG',
  claim: 'Alquiler y venta de consolas y juegos',
  shortDescription:
    'Catalogo de juegos disponibles para PS2, PS3, Xbox 360, PS4 y PS5. Veni, probalo y llevatelo.',

  contact: {
    // Numero de celular (whatsapp). Formato internacional sin espacios ni signos.
    mobile: '+54 9 11 5555 1234',
    mobileRaw: '5491155551234',
    mobileLabel: 'Movil / WhatsApp',

    // Numero de telefono fijo de la casa.
    landline: '+54 11 5555 9876',
    landlineLabel: 'Telefono fijo',

    email: 'contacto@bertigames.com',
    instagram: 'https://instagram.com/bertigames',
    instagramHandle: '@bertigames',
  },

  address: {
    street: 'Av. Ejemplo 1234',
    floor: 'Local 5',
    city: 'Ciudad Autonoma de Buenos Aires',
    province: 'Buenos Aires',
    zip: 'C1413',
    country: 'Argentina',
    mapsUrl: 'https://maps.google.com/?q=Av.+Ejemplo+1234',
  },

  hours: [
    { days: 'Lunes a Viernes', time: '10:00 - 20:00' },
    { days: 'Sabados', time: '10:00 - 18:00' },
    { days: 'Domingos', time: 'Cerrado' },
  ],
}

/** Linea formateada para mostrar la direccion en una sola linea. */
export function formatAddress() {
  const a = SITE.address
  return [a.street, a.floor, a.city, a.province].filter(Boolean).join(', ')
}
