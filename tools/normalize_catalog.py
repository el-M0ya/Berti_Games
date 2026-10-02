"""
Fase 0: normaliza los catalogos de `src/data/games/`.

Arregla, sobre los archivos ya llenados:

  1. Generos. RAW G viene como texto en ingles y con varios generos pegados
     por coma ("Action, Shooter, Adventure"). Se separan, se traducen y se
     guardan como lista, para que el filtro de la web tenga valores Limpios.
  2. Jugadores. Ahora mismo el 100% de los juegos tiene "1 jugador", asi que
     ese filtro no descarta nada. "1 jugador" pasa a significar "solo un
     jugador", y los que son cooperativos quedan con 2 y/o 4 jugadores.
  3. Titulos. Se quitan las notas de trabajo que algunas carpetas tienen
     ("(buscar de nuevo, no sale)") y se pasan a mayusculas/minusculas
     legibles. OJO: esto cambia el titulo que se ve en la web.
  4. Campo `favorite`: se agrega en false. Lo editas tu a mano.
  5. Campo `file`: se elimina. Guardaba rutas de tu disco y no lo usa nadie.
  6. Descripciones: las que estan vacias o son demasiado cortas reciben un
     texto generico, en vez de quedar en blanco.

Uso:
  python tools/normalize_catalog.py --dry-run   # solo el informe, no escribe
  python tools/normalize_catalog.py             # aplica los cambios
  python tools/normalize_catalog.py --console ps2
"""

import argparse
import html
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

# slug de consola -> nombre legible, para los textos genericos.
CONSOLE_NAME = {
    "ps1": "PlayStation",
    "ps2": "PlayStation 2",
    "psp": "PlayStation Portable",
    "ps3": "PlayStation 3",
    "xbox360": "Xbox 360",
    "ps4": "PlayStation 4",
    "ps5": "PlayStation 5",
}

# RAWG usa solo estos 20 generos. El mapa los lleva a espanol.
GENRE_MAP = {
    "Action": "Accion",
    "Adventure": "Aventura",
    "RPG": "Rol",
    "Shooter": "Disparadores",
    "Arcade": "Arcade",
    "Indie": "Indie",
    "Sports": "Deportes",
    "Simulation": "Simulacion",
    "Racing": "Carreras",
    "Strategy": "Estrategia",
    "Fighting": "Peleas",
    "Platformer": "Plataformas",
    "Casual": "Casual",
    "Variado": "Variado",
    "Puzzle": "Logica",
    "Family": "Familiar",
    "Board Games": "Tablero",
    "Massively Multiplayer": "MMORPG",
    "Educational": "Educativo",
    "Card": "Cartas",
}

# Ordem de preferencia para quedarse con 3 generos. Los genericos (Indie,
# Casual, Family) van al final porque no ayudan a filtrar.
GENRE_PRIORITY = [
    "Accion", "Aventura", "Rol", "Disparadores", "Carreras", "Deportes",
    "Estrategia", "Peleas", "Plataformas", "Simulacion", "Arcade", "Logica",
    "Tablero", "Cartas", "MMORPG", "Educativo", "Familiar", "Casual",
    "Indie", "Variado",
]

# Siglas que hay que dejar en mayusculas al pasar un titulo a Title Case.
KEEP_UPPER = {
    "FIFA", "NBA", "NFL", "NHL", "MLB", "UFC", "MMA", "GTA", "RPG", "DLC",
    "HD", "UHD", "VR", "PS", "PS2", "PS3", "PS4", "PSP", "XBOX", "ABC",
    "NBC", "CBS", "TBS", "AMC", "MTV", "ESRB", "USA", "PAL", "NTSC",
    # Numeros romanos: "Final Fantasy XIII 2", no "Final Fantasy Xiii 2".
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII", "XIII",
    "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
}

# Palabras que en ingles van en minuscula dentro de un titulo, salvo que
# sean la primera o la ultima. Solo articulos, preposiciones y conjuciones:
# "TWO", "ALL" o "NEW" no van aqui porque son palabras del titulo.
COMMON_WORDS = {
    "A", "AN", "THE", "AND", "OR", "OF", "IN", "ON", "AT", "TO", "FOR",
    "FROM", "BY", "WITH", "AS", "BUT", "NOR",
    "DE", "DEL", "LA", "EL", "LOS", "LAS", "UN", "UNA", "Y", "O", "CON",
    "PARA", "POR", "QUE", "EN", "SU", "AL",
}

# Notas de trabajo, etiquetas tecnicas, regiones e idiomas que aparecen
# entre parentesis en los nombres de carpeta. Se quitan del titulo.
#
# La lista se arms con `python tools/list_title_notes.py`, mirando lo que
# hay de verdad en tus carpetas. NO se borra cualquier parentesis: hay
# subtitulos legitimos como "(Howling Wolf)" o "(Furia de Titanes)" que se
# dejan intactos.
NOTE_WORDS = re.compile(
    r"[\(\[\{][^\)\]\}]*?"
    r"(?:"
    # grabar / quemar / copiar: notas de como sacar el juego
    r"\b(?:no\s*)?grabar\b|\bgrabar\s+(?:el\s+)?(?:de\s+)?(?:arriba|abajo)\b|"
    r"\bno\s*quemar\b|\bquemar\b|\bversion\s+de\s+disco\s+duro\b|"
    r"\bno\s*descomprimir\b|\bdescomprimir\b|\bcopia\b|\bbackup\b|"
    # "este no sirve", "el de arriba si", y similares
    r"\bno\s*sirve\b|\bel\s+de\s+arriba\s+si\b|\bes\s+el\s+mismo\s+de\s+arriba\b|"
    r"\bno\s*se\s*bloquea\b|\broto\b|\bproblemas?\b|\bredundancia\b|"
    r"\bmierda\b|\bojo\b|\bhormigas\b|\busb\s*no\b|"
    r"\bpirat\.?\s*virtual\s*no\b|\bfalta\b|\bpendiente\b|\brevisar\b|\bprobar\b|"
    r"\bbuscar\b|\bre-?buscar\b|"
    # tecnica: chips, discos, accesorios
    r"\bjtag\b|\brgh\b|\bxbla\b|\bmatrix\b|\bhen\s*ok\b|\bkinect\b|\bpsn\b|"
    r"\bu-?draw\b|\bufi\b|\bmicrofono\b|\bmixto\b|\bdemo\b|"
    r"\bno\s*se\s+blockea\b|\bnueva\s*partida\b|"
    # regiones e idiomas (con y sin tilde)
    r"\bpal\b|\bntse\b|\bntsc\b|\beur\b|\busa\b|"
    r"\besp\.?\b|espa(?:ñ|n)ol\b|\beng\b|\bing\.?\b|ingl[eé]s\b|"
    r"\bjap\.?\b|jap[oó]nes\b|\bjp\b|\bjpn\b|"
    r"\bmira\s+(?:arriba|abajo)\b|\bno\s*funciona\b|\brc\b|\beso\b|"
    r"\bnueva\s*partida\b|\bsegunda\s*parte\b|"
    # una sola letra: (J), (U), (E) son codigos de idioma. El parentesis de
    # apertura ya lo consumio el patron de afuera; el de cierre se mira
    # con lookahead para no gastarselo.
    r"\s*[JUE]\s*(?=[\)\]])|"
    # la consola, cuando la carpeta la repite
    r"\bpsp\b|\bps[1-5]\b|\bxbox\b|\bxbox\s?360\b|"
    # etiquetas de genero y edicion (ya las tenemos en el campo genres)
    r"\barcade\b|\bpuzzle\b|\brpg\b|\baventura\b|\bdeporte\w*\b|\bpesca\b|"
    r"\bformula\b|\bcarrera\b|\bbillar\b|\binvestigacion\b|\bnaves\b|"
    r"\bmonta\s+de\s+toros\b|\bfull\b|\botros\b|\bofficial\b|"
    # versiones fisicas
    r"\bcd\b|\bdvd\b|\busb\b|\biso\b|\bdisco\b"
    r")"
    r"[^\)\]\}]*?[\)\]\}]",
    re.I,
)

# Extension de archivo que quedo pegada al nombre de la carpeta.
FILE_EXT = re.compile(
    r"\.(?:rar|zip|7z|iso|bin|cue|pkg|img|mdf|nrg|wbfs|gcm|gcz|cso|rvz"
    r"|chd|m3u|xiso|wad|pbp|exe|msi)(?:\.gz)?\s*$",
    re.I,
)

# Codigo de idioma suelto al final, sin parentesis: "Extinction Ing".
LANG_TAIL = re.compile(
    r"\s+(?:ing|eng|ingles|espa(?:ñ|n)ol|esp|pal|ntsc|jap|jpn|ger|deu"
    r"|fra|fre|ita|por|pt|nld|rus|chi)\s*$",
    re.I,
)

# Versiones entre corchetes: "2[3.41_3.55]", "[v1.02]", "[SLUS-20958]"
VERSION = re.compile(r"[\[\(][^\]\)]*\d[^\]\)]*[\]\)]")

# Notas de trabajo sueltas al final, sin parentesis:
# "CRASH BANDICOT TWIN SANITH buscar"
JUNK_TAIL = re.compile(
    r"\s+(?:"
    r"copia|copia\s*\d+|backup|test|prueba|sin\s*dvd|sin\s*iso|"
    r"no\s*funciona|no\s*juega|no\s*sirve|no\s*grabar|no\s*borrar|dudoso|roto|"
    r"buscar|re-?buscar|falta|pendiente|revisar|probar|problemas?|"
    r"sin\s*caratula|sin\s*portada"
    r")$",
    re.I,
)

MIN_DESC = 40


# --------------------------------------------------------------------------
# Lectura de los .js
# --------------------------------------------------------------------------

def parse_file(path: Path) -> list[dict]:
    """Lee un catalogo sin ejecutarlo. Devuelve la lista de juegos."""
    text = path.read_text(encoding="utf-8")
    body = text[text.index("= [") + 2 : text.rindex("]")]
    juegos = []

    for block in re.split(r"\n  \{\n", body)[1:]:
        g = {}
        for key in ("id", "title", "genre", "description"):
            # Sin re.S a proposito: con DOTALL el ".*" se comia el resto del
            # bloque y el titulo salia con el año y la descripcion pegados.
            m = re.search(rf"^\s{{4}}{key}: '(.*)',?\s*$", block, re.M)
            if m:
                g[key] = js_unescape(m.group(1))
        m = re.search(r"^\s{4}players:\s*\[(.*?)\]", block, re.M)
        if m:
            g["players"] = re.findall(r"'([^']*)'", m.group(1))
        for key in ("year", "cover", "favorite"):
            m = re.search(rf"^\s{{4}}{key}:\s*(.*?),?\s*$", block, re.M)
            if not m:
                continue
            val = m.group(1)
            if key == "year":
                g["year"] = None if val == "null" else int(val)
            elif key == "favorite":
                g["favorite"] = val == "true"
            else:
                # OJO: la portada tambien hay que des-escapar. Si aqui solo
                # se le sacan las comillas de los extremos, las barras se
                # quedan en el valor y js_escape las vuelve a duplicar en la
                # siguiente corrida (4095 -> 8191 -> 16383...).
                g[key] = js_unescape(val.strip().strip("'"))
        g["_block"] = block
        juegos.append(g)

    return juegos


# Si una portada tiene mas de esto, esta rota: son los restos de cuando las
# barras se duplicaban en cada corrida. No hay nada que recuperar, asi que se
# deja vacia y la tarjeta dibuja su portada de respaldo.
BARRAS_ROTAS = re.compile(r"\\{5,}")


def portada_sana(url: str) -> str:
    """Si la URL esta corrupta por el bug de las barras, la descarta."""
    if not url:
        return ""
    if BARRAS_ROTAS.search(url):
        return ""
    return url


def js_unescape(text: str) -> str:
    """
    Pasa de como esta escrito en el archivo a su valor real.

    El orden importa: primero se resuelve la doble barra (que representa una
    barra literal) y despues las comillas escapadas. Si se hace al reves, cada
    corrida duplica las barras.
    """
    marca = "\x00"  # no puede aparecer en una URL ni en un titulo
    text = text.replace("\\\\", marca)
    text = text.replace("\\'", "'").replace('\\"', '"')
    text = text.replace(marca, "\\")
    return text


def js_escape(text: str) -> str:
    """Valor real -> como se escribe en el archivo. Una sola vez."""
    return text.replace("\\", "\\\\").replace("'", "\\'")


def render(slug: str, juegos: list[dict]) -> str:
    label = CONSOLE_NAME.get(slug, slug.upper())
    head = (
        f"/**\n * Catalogo {label}. Normalizado por `tools/normalize_catalog.py`.\n"
        f" * Los titulos y generos los edita ese script o tu a mano.\n */\n\n"
    )
    out = [f"export const {CONST_BY_SLUG.get(slug, slug.upper())}_GAMES = [\n"]
    for g in juegos:
        out.append("  {\n")
        out.append(f"    id: '{js_escape(g['id'])}',\n")
        out.append(f"    title: '{js_escape(g['title'])}',\n")
        out.append(f"    year: {g['year'] if g.get('year') else 'null'},\n")
        out.append(f"    cover: '{js_escape(portada_sana(g.get('cover', '')))}',\n")
        players = ", ".join(f"'{p}'" for p in g["players"])
        out.append(f"    players: [{players}],\n")
        genres = ", ".join(f"'{x}'" for x in g["genres"])
        out.append(f"    genres: [{genres}],\n")
        out.append(f"    favorite: {'true' if g.get('favorite') else 'false'},\n")
        out.append(f"    description: '{js_escape(g['description'])}',\n")
        out.append("  },\n")
    out.append("]\n")
    return head + "".join(out)


CONST_BY_SLUG = {
    "ps1": "PS1",
    "ps2": "PS2",
    "psp": "PSP",
    "ps3": "PS3",
    "xbox360": "XBOX360",
    "ps4": "PS4",
    "ps5": "PS5",
}


# --------------------------------------------------------------------------
# Transformaciones
# --------------------------------------------------------------------------

def normalize_genres(raw: str) -> list[str]:
    """'Action, Shooter, Adventure' -> ['Accion', 'Disparadores', 'Aventura']."""
    if not raw or raw in ("null", "''"):
        return ["Variado"]

    encontrados = []
    for part in raw.split(","):
        nombre = GENRE_MAP.get(part.strip())
        if nombre and nombre not in encontrados:
            encontrados.append(nombre)

    if not encontrados:
        return ["Variado"]

    # Quedarnos con 3, priorizando los generos que mas ayudan a filtrar.
    encontrados.sort(key=lambda x: GENRE_PRIORITY.index(x) if x in GENRE_PRIORITY else 99)
    return encontrados[:3]


def fix_players(players: list[str]) -> list[str]:
    """
    Antes todos los juegos tenian "1 jugador", asi que ese filtro no servia.

    Ahora:
      - solo "1 jugador"            -> juego de un unico jugador
      - "1 jugador" + otros        -> cooperativo: quedan solo 2 y/o 4
    """
    coop = [p for p in players if p != "1 jugador"]
    if not coop:
        return ["1 jugador"]
    return coop


# Caracteres invisibles o de control. Se arman con chr() porque son invisibles
# y escribirlos a mano es pedir que se borren al guardar el archivo.
INVISIBLES = tuple(
    chr(c)
    for c in (
        0x00A0,                            # espacio duro
        0x2002, 0x2003, 0x2007, 0x2009, 0x200A, 0x202F,  # espacios raros
        0x200B, 0x200C, 0x200D, 0x200E, 0x200F,  # zero width y marcas
        0x2060, 0xFEFF,                     # word joiner y BOM
        0x2028, 0x2029,                     # separadores de linea Unicode
        0x0085,                            # next line
        0x000B, 0x000C,                     # line tabulation, form feed
    )
)

# Los que se borran enteros en vez de convertirse en espacio.
INVISIBLES_BORRADOS = frozenset(
    chr(c) for c in (0x200B, 0x200C, 0x200D, 0x200E, 0x200F, 0x2060, 0xFEFF)
)

# Controles C1: restos de Windows-1252 mal decodificados.
C1_FIX = {
    chr(0x93): chr(0x201C), chr(0x94): chr(0x201D),   # comillas
    chr(0x91): chr(0x2018), chr(0x92): chr(0x2019),   # comillas simples
    chr(0x96): chr(0x2013), chr(0x97): chr(0x2014),   # guiones
    chr(0x95): chr(0x2022), chr(0x99): chr(0x2122),   # vineta y marca
}


def clean_invisibles(text: str) -> tuple[str, bool]:
    """Quita lo que se ve como basura pero no es texto.

    Espacios duros, zero width, controles C1 mal decodificados y acentos usados
    como apostrofo.

    Lo importante son los separadores de linea Unicode (U+2028 y U+2029):
    JavaScript los acepta dentro de un string, asi que el build no se cae, pero
    parten el texto en el navegador y rompen cualquier parser que los cuente
    como salto de linea.
    """
    original = text
    for ch in INVISIBLES:
        if ch in INVISIBLES_BORRADOS:
            text = text.replace(ch, "")
        else:
            text = text.replace(ch, " ")
    for malo, bueno in C1_FIX.items():
        text = text.replace(malo, bueno)
    # Acento agudo o grave en mitad de palabra, usado como apostrofo.
    text = re.sub(r"(?<=\w)[\u00b4`\u00b8\u02bc](?=\w)", "'", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip(), text.strip() != original.strip()


def unescape_entities(text: str) -> tuple[str, bool]:
    """
    RAWG devuelve las descripciones con los acentos y comillas escapados, y a
    veces escapados dos veces ("&amp;#39;" en vez de "'"). Una sola pasada no
    alcanza, asi que repetimos hasta que no cambie mas.

    Sin esto, 1.561 descripciones se veian con "&#39;" escrito.
    """
    original = text
    for _ in range(4):
        nuevo = html.unescape(text)
        if nuevo == text:
            break
        text = nuevo
    # Si quedan entidades sueltas (rompe&iacute;n), al menos no mostrar
    # el texto '&...' suelto.
    text = re.sub(r"&#[0-9]+;", "'", text)
    text = re.sub(r"&[a-zA-Z]+;", " ", text)
    return text.strip(), text.strip() != original.strip()


def title_case(palabra: str, primera: bool, ultima: bool) -> str:
    """
    Pasa UNA palabra a Title Case, sin romper la puntuacion.

    "AVATAR." -> "Avatar."   (no se come el punto)
    "H.A.W.X." -> "H.A.W.X."
    "OF" -> "of"            (preposicion, y no es la primera ni la ultima)
    "II" -> "II"            (numero romano, siempre en mayusculas)
    """
    lead = re.match(r"^\W*", palabra).group(0)
    trail = re.search(r"\W*$", palabra).group(0)
    core = palabra[len(lead) : len(palabra) - len(trail) if trail else len(palabra)]

    if not core:
        return palabra

    # Siglas y numeros romanos: como estan.
    if core.upper() in KEEP_UPPER:
        return palabra
    # Solo numeros: "007", "50". Se dejan igual.
    if core.isdigit():
        return palabra

    # Numero pegado a la palabra: "TENKAICHI2" -> "Tenkaichi 2".
    if any(ch.isdigit() for ch in core):
        partes = re.split(r"(?<=[A-Za-z])(?=\d)", core)
        core = " ".join(
            p if (p.upper() in KEEP_UPPER or p.isdigit()) else p.title()
            for p in partes
        )

    # Articulos y preposiciones en minuscula, salvo al principio o al final.
    if core.upper() in COMMON_WORDS and not (primera or ultima):
        return lead + core.lower() + trail

    return lead + core.title() + trail


def clean_title(raw: str) -> tuple[str, bool]:
    """Limpia el titulo. Devuelve (titulo, habia_nota_de_trabajo)."""
    original = raw
    t, _ = clean_invisibles(raw)
    t, _ = unescape_entities(t)

    t = NOTE_WORDS.sub(" ", t)
    t = VERSION.sub(" ", t)
    t = JUNK_TAIL.sub("", t)
    t = FILE_EXT.sub("", t)
    t = LANG_TAIL.sub("", t)
    # Separadores raros -> espacios
    t = re.sub(r"[_\t]+", " ", t)
    # Guion pegado despues de un numero: "007-BLOOD" -> "007 BLOOD".
    # Solo asi, porque "SPIDER-MAN" y "Kung-Fu" son una sola palabra.
    t = re.sub(r"(?<=[0-9])-(?=[A-Za-z])", " ", t)
    t = re.sub(r"\s{2,}", " ", t).strip(" -|,")

    # Si esta todo en mayusculas, lo pasamos a Title Case.
    hay_minusculas = any(c.islower() for c in t)
    if t and not hay_minusculas and any(c.isalpha() for c in t):
        palabras = t.split(" ")
        ultima = len(palabras) - 1
        salida = []
        nueva_frase = True  # al inicio, y despues de un punto
        for i, p in enumerate(palabras):
            salida.append(title_case(p, nueva_frase, i == ultima))
            # Si la palabra anterior cierra una frase, la siguiente capitalize.
            nueva_frase = bool(re.search(r"[.!?]\W*$", p))
        t = " ".join(salida)

    t = re.sub(r"\s{2,}", " ", t).strip()
    return t, NOTE_WORDS.search(original) is not None


def generic_description(generos: list[str], consola: str, title: str) -> str:
    """Texto para los juegos que no tienen descripcion."""
    nombre_consola = CONSOLE_NAME.get(consola, consola.upper())
    genero = generos[0] if generos else "Variado"
    return (
        f"Titulo de {genero.lower()} para {nombre_consola}. "
        f"No tenemos una sinopsis escrita de {title}, "
        f"asi que consultanos por los detalles cuando lo vengas a ver."
    )


def slugify(text: str) -> str:
    s = unicodedata.normalize("NFKD", text.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


# --------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Normaliza los catalogos de juegos.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Muestra el informe sin escribir nada",
    )
    parser.add_argument(
        "--console",
        default="",
        help="Normaliza solo esa consola. Ej: --console ps2",
    )
    args = parser.parse_args()

    # Solo los archivos que son catalogos de verdad. En la carpeta tambien
    # viven index.js y loader.js, que no se tocan.
    archivos = [
        p
        for p in sorted(GAMES.glob("*.js"))
        if "_GAMES = [" in p.read_text(encoding="utf-8")
    ]
    if args.console:
        archivos = [p for p in archivos if p.stem == args.console]
        if not archivos:
            raise SystemExit(f"No hay catalogo para {args.console}.")

    informe = []
    duplicados = []
    for path in archivos:
        slug = path.stem
        juegos = parse_file(path)

        cambios = {"titulos": 0, "notas": 0, "jugadores": 0,
                   "generos": 0, "desc": 0, "sin_favorito": 0, "duplicados": 0,
                   "entidades": 0}
        notas_vistas = []

        for g in juegos:
            # 1. Titulo
            titulo, habia_nota = clean_title(g.get("title", ""))
            if titulo != g.get("title"):
                cambios["titulos"] += 1
            if habia_nota:
                cambios["notas"] += 1
                notas_vistas.append(g.get("title", ""))
            g["title"] = titulo or g.get("title", "")
            if g["title"] != g.get("title", ""):
                g["title"] = g.get("title", "")

            # El id se recalcula si el titulo cambio, para que no queden
            # ids viejos con el nombre viejo.
            nuevo_id = slugify(g["title"])
            if nuevo_id != g.get("id"):
                g["id"] = nuevo_id

            # 2. Generos
            g["genres"] = normalize_genres(g.get("genre", ""))
            if g["genres"] != [g.get("genre")]:
                cambios["generos"] += 1

            # 3. Jugadores
            antes = g.get("players", [])
            g["players"] = fix_players(antes)
            if g["players"] != antes:
                cambios["jugadores"] += 1

            # 4. Favorito
            if "favorite" not in g:
                g["favorite"] = False
                cambios["sin_favorito"] += 1

            # 5. Descripcion: invisibles, entidades y textos demasiado cortos
            desc, _ = clean_invisibles(g.get("description") or "")
            desc, habia_entidad = unescape_entities(desc)
            if habia_entidad:
                cambios["entidades"] += 1
            g["description"] = desc
            if len(desc.strip()) < MIN_DESC:
                g["description"] = generic_description(g["genres"], slug, g["title"])
                cambios["desc"] += 1

        # 7. Si dos juegos terminan con el mismo id, es el mismo juego con el
        #    nombre escrito de otra forma. Nos quedamos con el primero.
        vistos: dict[str, str] = {}
        sin_duplicados = []
        for g in juegos:
            if g["id"] in vistos:
                cambios["duplicados"] += 1
                duplicados.append((slug, g["id"], vistos[g["id"]], g["title"]))
                continue
            vistos[g["id"]] = g["title"]
            sin_duplicados.append(g)
        juegos = sin_duplicados

        if not args.dry_run:
            path.write_text(render(slug, juegos), encoding="utf-8")

        informe.append((slug, len(juegos), cambios, notas_vistas))

    verb = "Analizado" if args.dry_run else "Normalizado"
    print(f"{'consola':9s} {'quedan':>7s} {'titulos':>8s} {'notas':>6s} "
          f"{'jugadores':>10s} {'generos':>8s} {'desc. corta':>12s} "
          f"{'duplicados':>11s} {'entidades':>10s}")
    print("-" * 94)
    tot = {k: 0 for k in ("titulos", "notas", "jugadores", "generos", "desc",
                          "duplicados", "entidades")}
    total = 0
    for slug, n, c, _ in informe:
        print(f"{slug:9s} {n:7d} {c['titulos']:8d} {c['notas']:6d} "
              f"{c['jugadores']:10d} {c['generos']:8d} {c['desc']:12d} "
              f"{c['duplicados']:11d} {c['entidades']:10d}")
        total += n
        for k in tot:
            tot[k] += c[k]
    print("-" * 94)
    print(f"{'TOTAL':9s} {total:7d} {tot['titulos']:8d} {tot['notas']:6d} "
          f"{tot['jugadores']:10d} {tot['generos']:8d} {tot['desc']:12d} "
          f"{tot['duplicados']:11d} {tot['entidades']:10d}")

    if duplicados:
        print(f"\nSe quitaron {len(duplicados)} juegos duplicados "
              f"(mismo titulo escrito de dos formas):\n")
        for slug, ident, guardado, descartado in duplicados:
            print(f"  {slug:9s} {ident}")
            print(f"            quedo:  {guardado}")
            print(f"            se fue:  {descartado}")

    todas_notas = [(s, t) for s, _, _, ns in informe for t in ns]
    if todas_notas:
        print(f"\nSe quitaron {len(todas_notas)} notas de trabajo de los titulos:")
        for slug, t in todas_notas:
            print(f"  {slug:9s} {t}")

    if args.dry_run:
        print("\nDry run: no se escribio nada. Quita --dry-run para aplicar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())