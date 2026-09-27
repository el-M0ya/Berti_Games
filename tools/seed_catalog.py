"""
Genera los catalogos de juegos en `src/data/games/*.js`.

Este archivo es la FUENTE de los datos semilla. El script `scan_games.py`
reescribe los mismos archivos con los juegos reales que escanea del disco.

Uso:  python tools/seed_catalog.py
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "data" / "games"

# Cada consola: (slug, constante JS, cabecera de comentario, lista de juegos)
# Un juego es: (id, titulo, anio, players, genre, descripcion)
CATALOGS = {
    "ps2": (
        "PS2_GAMES",
        "PlayStation 2",
        [
            ("grand-theft-auto-san-andreas", "Grand Theft Auto: San Andreas", 2004,
             ["1 jugador"], "Accion",
             "Carl Johnson vuelve a Los Santos. Maneja, cumple misiones para tres bandas y coop de a dos."),
            ("shadow-of-the-colossus", "Shadow of the Colossus", 2005,
             ["1 jugador"], "Accion-aventura",
             "Un joven sube a dieciseis colosos gigantes y decide que parte de cada uno destruye."),
            ("god-of-war-ii", "God of War II", 2005,
             ["1 jugador"], "Accion",
             "Kratos sube al Olimpo, al Hades y al Tartaro en una venganza muy corta."),
            ("devil-may-cry-3", "Devil May Cry 3: Dante's Awakening", 2005,
             ["1 jugador"], "Accion",
             "Dante recupera su tienda de armas en el Infierno. El origen del hack and slash."),
            ("metal-gear-solid-3", "Metal Gear Solid 3: Snake Eater", 2004,
             ["1 jugador"], "Accion y sigilo",
             "Naked Snake infiltra una base sovietica en Siberia con cajas y plataformas."),
            ("resident-evil-4", "Resident Evil 4", 2005,
             ["1 jugador"], "Terror y supervivencia",
             "Leon vuelve a la accion en un pueblo espanol. Camara libre y survival horror moderno."),
            ("final-fantasy-x", "Final Fantasy X", 2001,
             ["1 jugador"], "Rol japones",
             "Tidus y Yuna viajan con guardianes para derrotar a Sin. Turnos en prueba."),
            ("kingdom-hearts-ii", "Kingdom Hearts II", 2005,
             ["1 jugador"], "Rol y accion",
             "Sora sincroniza mas de veinte mundos con Donald y Goofy."),
            ("gran-turismo-4", "Gran Turismo 4", 2004,
             ["1 jugador", "Multijugador", "Local 2-4"], "Simulacion de carreras",
             "Ochocientos coches y conduccion lenta y pesada. Coop local de a tres."),
            ("bully", "Bully", 2006,
             ["1 jugador"], "Aventura abierta",
             "Jimmy Hopkins en una academia. Sandbox escolar con peleas y minijuegos."),
            ("okami", "Okami", 2006,
             ["1 jugador"], "Accion-aventura",
             "Convertite en la diosa del sol y repinta el Japon con el pincel."),
            ("guitar-hero-ii", "Guitar Hero II", 2006,
             ["1 jugador", "Multijugador", "Local 2-5"], "Ritmo y musica",
             "Ochenta temas, siete dificultades y coop local de hasta cinco jugadores."),
        ],
    ),
    "ps3": (
        "PS3_GAMES",
        "PlayStation 3",
        [
            ("grand-theft-auto-v", "Grand Theft Auto V", 2013,
             ["1 jugador", "Multijugador", "Local 2-4"], "Accion",
             "Tres ladrones en Los Santos. El unico GTA V con cooperativo local."),
            ("the-last-of-us", "The Last of Us", 2013,
             ["1 jugador"], "Accion-aventura",
             "Joel escorta a Ellie por una America devastated. Sigilo y recursos contados."),
            ("red-dead-redemption", "Red Dead Redemption", 2010,
             ["1 jugador", "Multijugador", "Local 2-4"], "Accion-aventura",
             "John Marston elige entre la ley y su familia en el oeste americano."),
            ("uncharted-3-drakes-deception", "Uncharted 3: Drake's Deception", 2011,
             ["1 jugador"], "Accion-aventura",
             "Nathan Drake busca el tesoro de Sir Francis Drake. Escalada y persecuciones."),
            ("metal-gear-solid-4", "Metal Gear Solid 4: Guns of the Patriots", 2008,
             ["1 jugador"], "Accion y sigilo",
             "Snake cruza la linea de tiempo. El cierre de la serie original."),
            ("god-of-war-iii", "God of War III", 2010,
             ["1 jugador"], "Accion",
             "Kratos sube hasta la cima del Olimpo para vencer a Zeus."),
            ("infamous-2", "Infamous 2: Heroic Crimes", 2010,
             ["1 jugador"], "Accion",
             "Cole MacGrath usa sus poderes para bien o para mal. Ciudad abierta."),
            ("heavy-rain", "Heavy Rain", 2010,
             ["1 jugador"], "Thriller",
             "Pelicula interactiva de una noche de lluvia, con decisiones y varios finales."),
            ("demons-souls", "Demon's Souls", 2009,
             ["1 jugador", "Multijugador"], "Rol de accion",
             "Mundo en ruinas con muerte permanente e invadaciones. Precursor de Dark Souls."),
            ("littlebigplanet-2", "LittleBigPlanet 2", 2011,
             ["1 jugador", "Multijugador", "Local 2-4"], "Plataformas",
             "Saco, Dani y Lawrence recuperan los cordon de Seda. Sandbox de niveles de fans."),
            ("kingdom-hearts-ii-final-mix", "Kingdom Hearts II Final Mix", 2007,
             ["1 jugador"], "Rol y accion",
             "La edicion de PS2 con mezcla de audio nueva y los niveles finales."),
            ("fifa-14", "FIFA 14", 2013,
             ["1 jugador", "Multijugador", "Local 2-4"], "Deportes",
             "Primer FIFA con motor de nueva generacion y controles de un dedo."),
        ],
    ),
    "xbox360": (
        "XBOX360_GAMES",
        "Xbox 360",
        [
            ("halo-3", "Halo 3", 2007,
             ["1 jugador", "Multijugador", "Local 2-4"], "Disparadores en primera persona",
             "El Covenant llega a la Tierra. Cooperativo de a cuatro en la campana."),
            ("gears-of-war-2", "Gears of War 2", 2008,
             ["1 jugador", "Multijugador", "Local 2-4"], "Disparadores en tercera persona",
             "La Coalicion de la Luz contra la horda. Cobertura y retroceso de camara."),
            ("forza-horizon", "Forza Horizon", 2012,
             ["1 jugador", "Multijugador", "Local 2-4"], "Carreras",
             "Festival de musica y carreras en Mexico, con mas de 250 autos."),
            ("red-dead-redemption", "Red Dead Redemption", 2010,
             ["1 jugador", "Multijugador", "Local 2-4"], "Accion-aventura",
             "Igual que en PS3 pero en Blu-ray y con vibracion en el mando."),
            ("bioshock", "BioShock", 2007,
             ["1 jugador"], "Disparadores en primera persona",
             "Rapture, ciudad submarina de 1946 donde modificas el cuerpo con plasmidios."),
            ("alan-wake", "Alan Wake", 2010,
             ["1 jugador"], "Terror y supervivencia",
             "Un escritor vuelca su novela en Bright Falls. El juego escribe su propia historia."),
            ("perfect-dark", "Perfect Dark", 2010,
             ["1 jugador", "Multijugador", "Local 2-4"], "Espionaje y disparos",
             "Joanna Dark en 2023. Espionaje, sigilo y coop local de a cuatro."),
            ("minecraft", "Minecraft", 2011,
             ["1 jugador", "Multijugador", "Local 2-4"], "Construccion y sandbox",
             "Mundo de cubos. La version de 360 fue la primera con cuevas y aldeas NPC."),
            ("the-elder-scrolls-v-skyrim", "The Elder Scrolls V: Skyrim", 2011,
             ["1 jugador", "Multijugador"], "Rol",
             "Cientos de horas de mundo abierto, PNJs con rutina y dragones."),
            ("rocket-league", "Rocket League", 2015,
             ["1 jugador", "Multijugador", "Local 2-8"], "Deportes",
             "Futbol con autos. Un jugador contra el juego o hasta ocho en local."),
        ],
    ),
    "ps4": (
        "PS4_GAMES",
        "PlayStation 4",
        [
            ("bloodborne", "Bloodborne", 2015,
             ["1 jugador", "Multijugador"], "Accion-aventura",
             "Cazadores en una ciudad metida en una pesadilla. Campana corta y cooperativa online."),
            ("the-last-of-us-part-ii", "The Last of Us Part II", 2020,
             ["1 jugador"], "Accion-aventura",
             "Ellie busca venganza. Mundo denso, sigilo y una historia pesada."),
            ("god-of-war", "God of War", 2018,
             ["1 jugador"], "Accion-aventura",
             "Kratos y Atreus viajan al norte. Ahora tenes que elegir cuando buttonear."),
            ("horizon-zero-dawn", "Horizon Zero Dawn", 2017,
             ["1 jugador"], "Accion-aventura",
             "Aloy caza maquinas en un futuro post apocaliptico. Mundo abierto enorme."),
            ("marvels-spider-man", "Marvels Spider-Man", 2018,
             ["1 jugador"], "Accion-aventura",
             "Peter Parker en la ciudad de Nueva York. Travesia entre tejados y balanceos."),
            ("red-dead-redemption-2", "Red Dead Redemption 2", 2019,
             ["1 jugador", "Multijugador"], "Accion-aventura",
             "Arthur Morgan en 1900. El mejor mundo abierto que se haya hecho."),
            ("the-witcher-3", "The Witcher 3: Wild Hunt", 2015,
             ["1 jugador"], "Rol de accion",
             "Geralt busca a Ciri por un mundo enorme con misiones secundarias excelentes."),
            ("elden-ring", "Elden Ring", 2022,
             ["1 jugador", "Multijugador"], "Rol de accion",
             "Anillo de Elden, mundo abierto y Coop summoned. Difícil a proposito."),
            ("gran-turismo-7", "Gran Turismo 7", 2022,
             ["1 jugador", "Multijugador", "Local 2-4"], "Simulacion de carreras",
             "Grafica de nueva generacion, foto realista y el circuito de Barcellona."),
            ("persona-5", "Persona 5", 2016,
             ["1 jugador"], "Rol japones",
             "Jokers roba corazones en Tokio. Estetica de comic y banda sonora exclusiva."),
        ],
    ),
    "ps5": (
        "PS5_GAMES",
        "PlayStation 5",
        [
            ("demons-souls", "Demons Souls", 2020,
             ["1 jugador", "Multijugador"], "Rol de accion",
             "Remake de PS3 con texturas, audio y animaciones rehechas por completo."),
            ("marvels-spider-man-miles-morales", "Marvels Spider-Man: Miles Morales", 2020,
             ["1 jugador"], "Accion-aventura",
             "Miles Morales en Harlem. Movimientos nuevos y doble tela de traje."),
            ("ratchet-and-clank-rift-apart", "Ratchet and Clank: Rift Apart", 2021,
             ["1 jugador", "Multijugador"], "Plataformas",
             "Dos dimensionalidades viajan juntas. Exclusivo de PS5 con ray tracing."),
            ("horizon-forbidden-west", "Horizon Forbidden West", 2022,
             ["1 jugador"], "Accion-aventura",
             "Aloy va al oeste a salvar a una Familiar. Maquinas Commandants nuevas."),
            ("elden-ring", "Elden Ring", 2022,
             ["1 jugador", "Multijugador"], "Rol de accion",
             "Igual que en PS4 pero con QoL features y mejor rendimiento y ray tracing."),
            ("god-of-war-ragnarok", "God of War Ragnarok", 2022,
             ["1 jugador"], "Accion-aventura",
             "Kratos y Atreus contra Odin. Valhalla y mas de cien enemigos distintos."),
            ("gran-turismo-7", "Gran Turismo 7", 2022,
             ["1 jugador", "Multijugador", "Local 2-4"], "Simulacion de carreras",
             "Igual que en PS4 pero con imagen mucho mas fluida en PS5."),
            ("death-stranding-directors-cut", "Death Stranding Directors Cut", 2022,
             ["1 jugador"], "Aventura",
             "Sam reconecta America al isolation. Entrega paquetes a pie y en moto."),
        ],
    ),
}

HEADER = """/**
 * Catalogo {label}. Lo genera `tools/scan_games.py`.
 * Ver `ps2.js` para la forma de cada objeto.
 */
"""


def js_str(value: str) -> str:
    """Escapa un string para JS usando comillas simples."""
    out = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{out}'"


def render(slug: str, const: str, label: str, games) -> str:
    lines = [HEADER.format(label=label), f"export const {const} = [\n"]
    for gid, title, year, players, genre, description in games:
        lines.append("  {\n")
        lines.append(f"    id: {js_str(gid)},\n")
        lines.append(f"    title: {js_str(title)},\n")
        lines.append(f"    year: {year},\n")
        lines.append("    cover: '',\n")
        players_js = ", ".join(js_str(p) for p in players)
        lines.append(f"    players: [{players_js}],\n")
        lines.append(f"    genre: {js_str(genre)},\n")
        lines.append(f"    description: {js_str(description)},\n")
        lines.append("  },\n")
    lines.append("]\n")
    return "".join(lines)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, (const, label, games) in CATALOGS.items():
        target = OUT / f"{slug}.js"
        target.write_text(render(slug, const, label, games), encoding="utf-8")
        print(f"escrito: {target.relative_to(ROOT)} ({len(games)} juegos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
