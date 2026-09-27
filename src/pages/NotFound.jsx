import { Link } from 'react-router-dom'
import { SITE } from '../data/site.js'

export default function NotFound() {
  return (
    <section className="notfound">
      <p className="hero__eyebrow">Error 404</p>
      <h1 className="notfound__title">No encontramos esa pagina</h1>
      <p className="hero__text">Quiza el link cambio o el juego ya no esta disponible.</p>
      <Link className="btn btn--primary" to="/">
        Volver al inicio
      </Link>
      <p className="notfound__help">
        Necesitas algo? Escribinos al{' '}
        <a href={`https://wa.me/${SITE.contact.mobileRaw}`}>{SITE.contact.mobile}</a>
      </p>
    </section>
  )
}
