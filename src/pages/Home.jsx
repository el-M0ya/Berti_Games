import { Link } from 'react-router-dom'
import { CONSOLES } from '../data/consoles.js'
import { getCount, getPreviews, totalCount, prefetch } from '../data/games/loader.js'
import GameCover from '../components/GameCover.jsx'
import ContactSection from '../components/ContactSection.jsx'

export default function Home() {
  const total = totalCount()

  return (
    <>
      <section className="hero">
        <div className="hero__inner">
          <p className="hero__eyebrow">Catalogo de juegos</p>
          <h1 className="hero__title">
            Todos tus juegos
            <br />
            en un solo lugar
          </h1>
          <p className="hero__text">
            Elegi tu consola y mira todo lo que tenemos disponible. Veni al local, probalo y
            llevatelo.
          </p>
          <a className="hero__scroll" href="#consolas">
            Ver consolas
            <span aria-hidden="true">↓</span>
          </a>
        </div>
      </section>

      <section className="consoles" id="consolas">
        <div className="consoles__head">
          <h2 className="section__title">Elegi tu consola</h2>
          <p className="section__sub">{total} juegos disponibles en total</p>
        </div>

        <ul className="consoles__grid">
          {CONSOLES.map((c, i) => {
            const previas = getPreviews(c.slug)
            const cantidad = getCount(c.slug)
            return (
              <li key={c.slug} style={{ '--accent': c.accent, '--i': i }}>
                <Link
                  to={`/consola/${c.slug}`}
                  className="console"
                  onMouseEnter={() => prefetch(c.slug)}
                  onFocus={() => prefetch(c.slug)}
                >
                  <span className="console__glow" aria-hidden="true" />

                  <span className="console__preview" aria-hidden="true">
                    {previas.map((g, gi) => (
                      <span key={g.id} className="console__mini" style={{ '--gi': gi }}>
                        <GameCover game={g} accent={c.accent} />
                      </span>
                    ))}
                  </span>

                  <span className="console__short">{c.short}</span>
                  <span className="console__name">{c.name}</span>
                  <span className="console__tagline">{c.tagline}</span>
                  <span className="console__count">{cantidad} juegos</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </section>

      <ContactSection />
    </>
  )
}
