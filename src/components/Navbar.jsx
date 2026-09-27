import { useState } from 'react'
import { NavLink, Link } from 'react-router-dom'
import { CONSOLES } from '../data/consoles.js'
import { SITE } from '../data/site.js'

export default function Navbar() {
  const [open, setOpen] = useState(false)

  const close = () => setOpen(false)

  return (
    <header className="nav">
      <div className="nav__inner">
        <Link to="/" className="nav__brand" onClick={close}>
          <span className="nav__logo">{SITE.logo}</span>
          <span className="nav__name">{SITE.name}</span>
        </Link>

        <button
          className="nav__toggle"
          aria-label="Abrir menu"
          aria-expanded={open}
          onClick={() => setOpen((v) => !v)}
        >
          <span className={`nav__bars${open ? ' is-open' : ''}`} />
        </button>

        <nav className={`nav__links${open ? ' is-open' : ''}`}>
          <NavLink to="/" end className="nav__link" onClick={close}>
            Inicio
          </NavLink>

          <span className="nav__group">
            Catalogo
            <span className="nav__dropdown">
              {CONSOLES.map((c) => (
                <NavLink
                  key={c.slug}
                  to={`/consola/${c.slug}`}
                  className="nav__link nav__link--child"
                  onClick={close}
                >
                  <span className="nav__dot" style={{ background: c.accent }} />
                  {c.name}
                </NavLink>
              ))}
            </span>
          </span>

          <NavLink to="/pirateo" className="nav__link" onClick={close}>
            Pirateo
          </NavLink>

          <a
            className="nav__cta"
            href={`https://wa.me/${SITE.contact.mobileRaw}`}
            target="_blank"
            rel="noreferrer"
            onClick={close}
          >
            WhatsApp
          </a>
        </nav>
      </div>
    </header>
  )
}
