import { Link } from 'react-router-dom'
import { PIRACY, PIRACY_VISIBLE } from '../data/piracy.js'
import { SITE } from '../data/site.js'
import ContactSection from '../components/ContactSection.jsx'

export default function Piracy() {
  if (!PIRACY_VISIBLE) {
    return (
      <section className="notfound">
        <h1 className="notfound__title">Seccion no disponible</h1>
        <Link to="/">Volver al inicio</Link>
      </section>
    )
  }

  return (
    <div className="piracy">
      <header className="page-head page-head--warm">
        <nav className="crumbs">
          <Link to="/">Inicio</Link>
          <span aria-hidden="true">/</span>
          <span>Pirateo</span>
        </nav>
        <h1 className="page-head__title">Pirateo</h1>
        <p className="page-head__sub">{PIRACY.intro}</p>
      </header>

      <div className="services">
        {PIRACY.services.map((s) => (
          <article key={s.id} className="service">
            <header className="service__head">
              <h2 className="service__title">{s.title}</h2>
              <p className="service__console">{s.console}</p>
            </header>

            <p className="service__desc">{s.description}</p>

            <table className="prices">
              <thead>
                <tr>
                  <th>Version</th>
                  <th>Precio</th>
                </tr>
              </thead>
              <tbody>
                {s.versions.map((v) => (
                  <tr key={v.name}>
                    <td>
                      <span className="prices__name">{v.name}</span>
                      {v.notes ? <span className="prices__notes">{v.notes}</span> : null}
                    </td>
                    <td className="prices__value">{v.price}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </article>
        ))}
      </div>

      <p className="piracy__note">{PIRACY.disclaimer}</p>

      <div className="contact__actions">
        <a
          className="btn btn--primary"
          href={`https://wa.me/${SITE.contact.mobileRaw}?text=${encodeURIComponent(
            'Hola, quiero consultar por el servicio de pirateo',
          )}`}
          target="_blank"
          rel="noreferrer"
        >
          Consultar por WhatsApp
        </a>
      </div>

      <ContactSection />
    </div>
  )
}
