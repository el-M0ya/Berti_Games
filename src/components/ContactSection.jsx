import { SITE, formatAddress } from '../data/site.js'

/**
 * Seccion de contacto que aparece al hacer scroll en la pagina de inicio.
 * Todos los datos vienen de `src/data/site.js`.
 */
export default function ContactSection() {
  const { contact, address, hours } = SITE
  const waLink = `https://wa.me/${contact.mobileRaw}?text=${encodeURIComponent(
    'Hola Berti Games, quiero consultar por un juego',
  )}`

  return (
    <section className="contact" id="contacto">
      <div className="contact__head">
        <h2 className="section__title">Contacto</h2>
        <p className="section__sub">
          Escribinos o veni al local. Atendemos de {hours[0].time.split(' - ')[0]} a{' '}
          {hours[0].time.split(' - ')[1]} de lunes a viernes.
        </p>
      </div>

      <div className="contact__grid">
        <div className="info">
          <h3 className="info__title">Telefonos</h3>
          <ul className="info__list">
            <li>
              <span className="info__label">{contact.mobileLabel}</span>
              <a className="info__value" href={`https://wa.me/${contact.mobileRaw}`} target="_blank" rel="noreferrer">
                {contact.mobile}
              </a>
            </li>
            <li>
              <span className="info__label">{contact.landlineLabel}</span>
              <a className="info__value" href={`tel:${contact.landline}`}>
                {contact.landline}
              </a>
            </li>
          </ul>
        </div>

        <div className="info">
          <h3 className="info__title">Direccion</h3>
          <address className="info__address">{formatAddress()}</address>
          <p className="info__extra">
            {address.zip} &middot; {address.country}
          </p>
          <a
            className="info__link"
            href={address.mapsUrl}
            target="_blank"
            rel="noreferrer"
          >
            Ver en el mapa
          </a>
        </div>

        <div className="info">
          <h3 className="info__title">Horario</h3>
          <ul className="info__list">
            {hours.map((h) => (
              <li key={h.days} className="info__row">
                <span className="info__label">{h.days}</span>
                <span
                  className={`info__value${h.time === 'Cerrado' ? ' is-closed' : ''}`}
                >
                  {h.time}
                </span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="contact__actions">
        <a className="btn btn--primary" href={waLink} target="_blank" rel="noreferrer">
          Escribir por WhatsApp
        </a>
        <a className="btn btn--ghost" href={`tel:${contact.landline}`}>
          Llamar al fijo
        </a>
      </div>
    </section>
  )
}
