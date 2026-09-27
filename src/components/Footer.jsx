import { Link } from 'react-router-dom'
import { CONSOLES } from '../data/consoles.js'
import { SITE } from '../data/site.js'

export default function Footer() {
  const year = new Date().getFullYear()

  return (
    <footer className="footer">
      <div className="footer__inner">
        <div className="footer__col">
          <p className="footer__brand">{SITE.name}</p>
          <p className="footer__text">{SITE.shortDescription}</p>
        </div>

        <div className="footer__col">
          <p className="footer__title">Catalogo</p>
          <ul className="footer__list">
            {CONSOLES.map((c) => (
              <li key={c.slug}>
                <Link to={`/consola/${c.slug}`}>{c.name}</Link>
              </li>
            ))}
            <li>
              <Link to="/pirateo">Pirateo</Link>
            </li>
          </ul>
        </div>

        <div className="footer__col">
          <p className="footer__title">Contacto</p>
          <ul className="footer__list">
            <li>
              <a href={`tel:${SITE.contact.mobileRaw}`}>{SITE.contact.mobile}</a>
            </li>
            <li>
              <a href={`tel:${SITE.contact.landline}`}>{SITE.contact.landline}</a>
            </li>
            <li>
              <a href={SITE.address.mapsUrl} target="_blank" rel="noreferrer">
                {SITE.address.street}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <div className="footer__bottom">
        <span>
          {year} {SITE.name}. Todos los derechos reservados.
        </span>
        <span>Sitio informativo sin fines de venta online.</span>
      </div>
    </footer>
  )
}
