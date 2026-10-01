"""
Busca en la web los datos y la caratula de cada juego de `game_scan.json`.

Faena 2 de 2. Necesita internet.

    python tools/fetch_metadata.py --key TU_CLAVE_RAWG

De donde saca la informacion:
  1. RAWG API (recomendado). Gratis, key en https://rawg.io/apidocs
     Trae: titulo oficial, anio, descripcion, generos y la imagen de caratula.
  2. Sin clave: usa la API de Wikipedia como alternativa para el texto.
     La caratula en este caso queda vacia y se dibuja un placeholder.

Como elegir multijugador o un jugador:
  MIRA si la descripcion menciona cooperativo, online, Versus, 2 jugadores...
  Si no dice nada, Assume "1 jugador" (lo mas comun) y te lo marca en el
  reporte para que lo revises.

Salida: reescribe `src/data/games/{consola}.js` listo para la web.
"""

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SCAN_FILE = ROOT / "game_scan.json"
OUT_DIR = ROOT / "src" / "data" / "games"
CACHE_FILE = ROOT / "rawg_cache.json"

# slug de consola -> (constante JS, etiqueta legible)
CONSOLE_INFO = {
    "ps2": ("PS2_GAMES", "PlayStation 2"),
    "psp": ("PSP_GAMES", "PlayStation Portable"),
    "ps3": ("PS3_GAMES", "PlayStation 3"),
    "xbox360": ("XBOX360_GAMES", "Xbox 360"),
    "ps4": ("PS4_GAMES", "PlayStation 4"),
    "ps5": ("PS5_GAMES", "PlayStation 5"),
}

# Consolas que aparecen en los escaneos pero no tienen pagina en la web.
# Se avisan y se ignoran, para que quede claro que fue a proposito.
IGNORED_CONSOLES = {
    "ps1": "no hay apartado para PS1",
    "gc": "no hay apartado para GameCube",
    "wii": "no hay apartado para Wii",
}

# id de plataforma en RAWG para cada consola.
# OJO: estos ids hay que confirmarlos con
#   GET https://api.rawg.io/api/platforms?key=TU_CLAVE
# porque si estan mal la busqueda devuelve resultados de otra plataforma.
RAWG_PLATFORM = {
    "ps2": 8,
    "psp": 13,
    "ps3": 9,
    "xbox360": 49,
    "ps4": 48,
    "ps5": 504,
}

# Palabras que sugieren cooperativo o multijugador.
MULTI_WORDS = (
    "co-op", "coop", "cooperative", "cooperativo", "multijugador", "multiplayer",
    "versus", "online", "2 players", "two players", "split-screen", "splitscreen",
    "competitivo", "battle royale", "team", "equipo de",
)

# Palabras que sugieren juego para uno solo.
SINGLE_WORDS = ("single player", "un jugador", "solo")

# Traduccion de los generos de RAWG a los que usamos en la web.
GENRE_MAP = {
    "Action": "Accion",
    "Adventure": "Aventura",
    "Shooter": "Disparadores",
    "RPG": "Rol",
    "Strategy": "Estrategia",
    "Sports": "Deportes",
    "Racing": "Carreras",
    "Puzzle": "Logica",
    "Platformer": "Plataformas",
    "Fighting": "Peleas",
    "Simulator": "Simulacion",
    "Arcade": "Arcade",
    "Indie": "Indie",
    "Adventure Sports": "Deportes de accion",
    "Card": "Cartas",
    "Board": "Tablero",
    "Music": "Musica",
    "Sandbox": "Sandbox",
    "Tactics": "Tacticas",
    "Roguelike": "Roguelike",
    "MMORPG": "MMORPG",
    "Adventure Sports": "Deportes de accion",
    "Rhythm": "Ritmo",
    "Survival": "Supervivencia",
    "Horror": "Terror",
}

UA = (
    "BertiGamesCatalog/1.0 "
    "(sitio catalogo de juegos; uso personal; contacto via GitHub)"
)


def http_get_json(url: str, timeout: int = 20, retries: int = 3) -> dict:
    """GET a JSON con reintentos y espera creciente ante rate limit (429)."""
    last_error: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(
            url, headers={"User-Agent": UA, "Accept": "application/json"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_error = e
            if e.code in (429, 503):
                wait = 3 * (attempt + 1)
                print(f"    . rate limit, esperando {wait}s")
                time.sleep(wait)
                continue
            raise
        except Exception as e:
            last_error = e
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
                continue
            raise
    raise last_error  # type: ignore[misc]


def polite_pause(seconds: float) -> None:
    """Espera entre consultas para noDEU pegarle a las APIs."""
    if seconds > 0:
        time.sleep(seconds)


def clean_html(raw: str) -> str:
    """Convierte la descripcion de RAWG (HTML) en texto plano."""
    if not raw:
        return ""
    text = re.sub(r"<br\s*/?>", "\n", raw, flags=re.I)
    text = re.sub(r"</p>", "\n\n", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Palabras que no queremos dejar colgando al final de un corte.
DANGLING_WORDS = {
    "de", "del", "la", "el", "los", "las", "un", "una", "y", "o", "u", "en",
    "con", "por", "para", "que", "a", "al", "es", "son", "se", "su", "sus",
    "the", "of", "and", "in", "to", "for", "a", "an",
}


def summarize(text: str, max_chars: int = 320) -> str:
    """Corta la descripcion en una frase o dos, sin cortar a media palabra."""
    if len(text) <= max_chars:
        return text

    cut = text[:max_chars]

    # 1. Preferimos cortar en un fin de frase.
    for sep in (". ", "! ", "? "):
        pos = cut.rfind(sep)
        if pos > max_chars * 0.5:
            return cut[: pos + 1].strip()

    # 2. Si no, en la ultima coma.
    pos = cut.rfind(", ")
    if pos > max_chars * 0.5:
        return cut[:pos].strip() + "."

    # 3. Si no, por palabra, sin dejar preposiciones colgando.
    words = cut.split()
    while words and words[-1].strip(".,;:").lower() in DANGLING_WORDS:
        words.pop()
    if not words:
        words = cut.split()
    return " ".join(words).rstrip(" ,;:") + "..."


def guess_players(text: str) -> tuple[list[str], bool]:
    """Devuelve (etiquetas, hay_duda)."""
    low = text.lower()
    multi = any(w in low for w in MULTI_WORDS)
    single = any(w in low for w in SINGLE_WORDS)

    if multi and single:
        return ["1 jugador", "Multijugador"], True
    if multi:
        return ["1 jugador", "Multijugador"], True
    if single:
        return ["1 jugador"], False
    # Sin pistas: asumimos 1 jugador pero lo marcamos para revisar.
    return ["1 jugador"], True


def pick_cover(raw_background: str) -> str:
    """RAWG manda una sola URL en background_image (a veces varias separadas por ';')."""
    if not raw_background:
        return ""
    # Nos quedamos con la primera y la dejamos en formato "pequena|grande".
    return raw_background.split(";")[0].strip()


def query_rawg(title: str, console_slug: str, key: str) -> dict | None:
    """Busca un juego en RAWG restringido a la plataforma correcta."""
    platform = RAWG_PLATFORM.get(console_slug)
    params = {
        "key": key,
        "search": title,
        "search_precise": "true",
        "page_size": "5",
    }
    if platform:
        params["platforms"] = str(platform)

    url = "https://api.rawg.io/api/games?" + urllib.parse.urlencode(params)
    try:
        data = http_get_json(url)
    except urllib.error.HTTPError as e:
        print(f"    ! RAWG HTTP {e.code}")
        return None
    except Exception as e:  # red caida, timeout, etc.
        print(f"    ! error de red: {e}")
        return None

    results = data.get("results") or []
    return results[0] if results else None


def rawg_to_game(entry: dict, fallback_id: str) -> dict:
    """Convierte un resultado de RAWG en la forma que usa la web."""
    description = clean_html(entry.get("description_raw") or entry.get("description") or "")
    short = summarize(description) or "Sin descripcion disponible."

    genres = [g.get("name", "") for g in entry.get("genres") or [] if g.get("name")]
    genre = " / ".join(dict.fromkeys(GENRE_MAP.get(g, g) for g in genres[:2])) or "Variado"

    players, doubt = guess_players(description + " " + " ".join(genres))

    cover = pick_cover(entry.get("background_image"))

    released = entry.get("released") or ""
    year = int(released[:4]) if released[:4].isdigit() else None

    return {
        "id": fallback_id,
        "title": entry.get("name") or fallback_id,
        "year": year,
        "cover": cover,
        "players": players,
        "genre": genre,
        "description": short,
        "_duda_players": doubt,
    }


def wiki_extract(page_title: str) -> tuple[str, str] | None:
    """Pide el resumen de una pagina de Wikipedia. Devuelve (texto, url)."""
    url = (
        "https://es.wikipedia.org/w/api.php?action=query&prop=extracts"
        "&exintro=1&explaintext=1&redirects=1&format=json&titles="
        + urllib.parse.quote(page_title)
    )
    try:
        data = http_get_json(url)
    except Exception:
        return None

    pages = (data.get("query") or {}).get("pages") or {}
    for page in pages.values():
        # Wikipedia devuelve "-1" como pageid cuando la pagina no existe.
        if page.get("missing") is not None:
            continue
        extract = (page.get("extract") or "").strip()
        if len(extract) > 80:
            return extract, "https://es.wikipedia.org/wiki/" + urllib.parse.quote(
                page.get("title", "")
            )
    return None


def wiki_search(title: str, limit: int = 3) -> str | None:
    """Busca el titulo mas parecido en Wikipedia. Devuelve el titulo de la pagina."""
    url = (
        "https://es.wikipedia.org/w/api.php?action=query&list=search"
        f"&srsearch={urllib.parse.quote(title)}&srlimit={limit}&format=json"
    )
    try:
        data = http_get_json(url)
    except Exception:
        return None

    hits = ((data.get("query") or {}).get("search")) or []
    if not hits:
        return None
    return hits[0].get("title")


def normalize_title(text: str) -> str:
    """
    Deja un titulo comparable: sin acentos, sin puntuacion y sin el
    parentesis final que usa Wikipedia para desambiguar
    ("Demon's Souls (2009 video game)" -> "demonssouls").
    """
    import unicodedata
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text.strip())
    s = unicodedata.normalize("NFKD", text.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]", "", s)


def similar(a: str, b: str) -> float:
    """Que tan parecidas son dos cadenas, de 0 a 1."""
    import difflib
    na = normalize_title(a)
    nb = normalize_title(b)
    if not na or not nb:
        return 0.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


# Fraccion minima de parecido para dar por buena una pagina de Wikipedia.
# Con 0.72 "Demons Souls" ~ "Demon's Souls" pasa, y en cambio
# "High On Life 2" contra el album "Infinity on High" se rechaza.
WIKI_MIN_SIMILARITY = 0.72


def trailing_number(text: str):
    """
    Devuelve el numero de saga al final del titulo, como texto comparable.

    "Assassins Creed II"  -> "II"   (numero romano como palabra suelta)
    "Final Fantasy X"    -> "X"
    "Halo 3"             -> "3"
    "God of War"         -> None

    Sirve para distinguir sagas: "Assassins Creed II" no es lo mismo que
    "Assassin's Creed". Solo mira la ultima palabra, asi "Trifox" no se
    confunde con un numero romano.
    """
    text = re.sub(r"\s*\([^)]*\)\s*$", "", text.strip())
    words = re.findall(r"[A-Za-z0-9]+", text)
    if not words:
        return None
    last = words[-1]
    if last.isdigit():
        return str(int(last))
    if re.fullmatch(r"[ivxlcdm]+", last, re.I) and len(last) <= 6:
        return last.upper()
    return None


def wiki_match_is_trustworthy(query: str, page_title: str) -> bool:
    """
    Decide si la pagina que devolvio la busqueda difusa es el juego que
    buscamos. Exige tres cosas a la vez:

      1. parecido alto (SequenceMatcher >= 0.72), y
      2. que un titulo este contenido en el otro, y
      3. que el numero de saga sea el mismo.

    La segunda regla evita los falsos positivos con titulos cortos: "Trifox"
    contra "Trix" da 0.80 de parecido, pero "trix" no aparece dentro de
    "trifox". La tercera evita mezclar sagas: "Assassins Creed II" contra
    "Assassin's Creed".
    """
    nq = normalize_title(query)
    np_ = normalize_title(page_title)
    if not nq or not np_:
        return False
    if similar(query, page_title) < WIKI_MIN_SIMILARITY:
        return False
    if not (nq in np_ or np_ in nq):
        return False
    if trailing_number(query) != trailing_number(page_title):
        return False
    return True


def wikipedia_fallback(title: str) -> tuple[str, str, str | None] | None:
    """
    Ultimo recurso: resumen de Wikipedia en espanol.

    Devuelve (texto, url, titulo_oficial). El titulo oficial solo se llena
    cuando el match fue exacto (o casi, por un apostolito faltante), porque
    en la busqueda difusa Wikipedia puede devolver otro juego distinto.

    Importante: si la pagina encontrada NO se parece lo suficiente al titulo
    que buscamos, devolvemos None en vez de colgarle una descripcion que
    es de otro juego. Es preferible quedarse sin descripcion.
    """
    for candidate in _title_variants(title):
        result = wiki_extract(candidate)
        if result:
            extract, url = result
            return summarize(extract, 300), url, candidate

    # El titulo tal cual no funciono: buscamos por palabras, pero solo aceptamos
    # el resultado si la pagina se parece bastante a lo que pedimos.
    query = title
    for _ in range(2):
        page = wiki_search(query)
        if not page:
            return None
        if not wiki_match_is_trustworthy(query, page):
            return None
        result = wiki_extract(page)
        if result:
            extract, url = result
            return summarize(extract, 300), url, None
        # Si el primer resultado fue una lista, probamos solo con el nombre base.
        query = re.sub(r"\s*:\s*.*$", "", query)
    return None


def _title_variants(title: str) -> list[str]:
    """Variantes razonables de un titulo mal escaneado."""
    variants = [title]
    # "Demons Souls" -> "Demon's Souls"
    m = re.match(r"^(.*?)s(\s+\S+)$", title)
    if m:
        variants.append(f"{m.group(1)}'s{m.group(2)}")
    # "Marvels Spider-Man" -> "Marvel's Spider-Man"
    m = re.match(r"^(\S+?)(s)(\s+.*)$", title)
    if m and not title.lower().startswith("mgs"):
        variants.append(f"{m.group(1)}'{m.group(2)}{m.group(3)}")
    return variants


def slugify(text: str) -> str:
    """Mismo criterio que scan_games.py, para deduplicar entre archivos."""
    import unicodedata
    s = unicodedata.normalize("NFKD", text.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def js_str(value) -> str:
    if value is None:
        return "''"
    if isinstance(value, (int, float)):
        return str(value)
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def render_js(const: str, label: str, games: list[dict]) -> str:
    head = (
        f"/**\n * Catalogo {label}. Generado por `tools/fetch_metadata.py`.\n"
        f" * Ver `ps2.js` para la forma de cada objeto.\n */\n\n"
    )
    body = [f"export const {const} = [\n"]
    for g in games:
        body.append("  {\n")
        body.append(f"    id: {js_str(g['id'])},\n")
        body.append(f"    title: {js_str(g['title'])},\n")
        body.append(f"    year: {g['year'] if g['year'] else 'null'},\n")
        body.append(f"    cover: {js_str(g.get('cover', ''))},\n")
        players = ", ".join(js_str(p) for p in g["players"])
        body.append(f"    players: [{players}],\n")
        body.append(f"    genre: {js_str(g['genre'])},\n")
        body.append(f"    description: {js_str(g['description'])},\n")
        body.append("  },\n")
    body.append("]\n")
    return head + "".join(body)


def load_cache() -> dict:
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def save_cache(cache: dict) -> None:
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Busca caratulas y descripciones para los juegos escaneados."
    )
    parser.add_argument(
        "--key",
        default="",
        help="Clave de RAWG (https://rawg.io/apidocs). Opcional: sin ella se usa Wikipedia.",
    )
    parser.add_argument(
        "--scan",
        default=str(SCAN_FILE),
        help="Lista generada por scan_games.py (default: game_scan.json)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.1,
        help="Pausa entre consultas en segundos (default: 1.1)",
    )
    parser.add_argument(
        "--out-dir",
        default=str(OUT_DIR),
        help="Carpeta donde se escriben los .js (default: src/data/games)",
    )
    parser.add_argument(
        "--only",
        default="",
        help="Procesa solo esas consolas, separadas por coma. Ej: --only ps2,ps5",
    )
    parser.add_argument(
        "--merge",
        nargs="*",
        default=[],
        metavar="ARCHIVO",
        help="Varios JSON de escaneo a la vez. Se unen y se quitan repetidos por id.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Ignora la cache y vuelve a buscar todo",
    )
    args = parser.parse_args()

    only = {c.strip() for c in args.only.split(",") if c.strip()}

    # Con --merge juntamos varios archivos en una sola lista.
    scan_files = [Path(f) for f in args.merge] if args.merge else [Path(args.scan)]
    for f in scan_files:
        if not f.exists():
            raise SystemExit(f"No existe {f}.")

    scanned: dict[str, list[dict]] = {}
    if len(scan_files) > 1:
        # Al unir, un juego repetido se queda con la version que tenga el
        # campo `cover` (o sea, la que vino del scraper de superpsx).
        for f in scan_files:
            data = json.loads(f.read_text(encoding="utf-8"))
            for console, games in data.items():
                bucket = scanned.setdefault(console, {})
                for g in games:
                    key = g.get("id") or slugify(g.get("title", ""))
                    if key not in bucket or (g.get("cover") and not bucket[key].get("cover")):
                        bucket[key] = g
        scanned = {c: list(b.values()) for c, b in scanned.items()}
        print("Archivos unidos:\n")
        for f in scan_files:
            print(f"  - {f.name}")
        print()
    else:
        scanned = json.loads(scan_files[0].read_text(encoding="utf-8"))

    cache = {} if args.no_cache else load_cache()
    review: list[dict] = []
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for console_slug, entries in scanned.items():
        if console_slug in IGNORED_CONSOLES:
            print(
                f"\n=== {console_slug}: {len(entries)} juegos, ignorados "
                f"({IGNORED_CONSOLES[console_slug]}) ==="
            )
            continue
        if console_slug not in CONSOLE_INFO:
            print(f"\nConsola desconocida, se salta: {console_slug}")
            continue
        if only and console_slug not in only:
            print(f"\n=== {console_slug}: saltada por --only ===")
            continue

        const, label = CONSOLE_INFO[console_slug]
        print(f"\n=== {label} ({len(entries)} juegos) ===")

        result: list[dict] = []
        for i, item in enumerate(entries, 1):
            title = item["title"]
            gid = item["id"]
            key = f"{console_slug}:{gid}"

            print(f"[{i}/{len(entries)}] {title}", end="  ")

            if key in cache:
                game = cache[key]
                print("(cache)")
            else:
                found = None
                if args.key:
                    found = query_rawg(title, console_slug, args.key)
                    polite_pause(args.delay)
                if found:
                    game = rawg_to_game(found, gid)
                    game["_source"] = "rawg"
                else:
                    wiki = wikipedia_fallback(title)
                    if wiki:
                        text, wiki_url, official_title = wiki
                        players, doubt = guess_players(text)
                        game = {
                            "id": gid,
                            "title": official_title or title,
                            "year": None,
                            "cover": "",
                            "players": players,
                            "genre": "Variado",
                            "description": text,
                            "_source": f"wikipedia:{wiki_url}",
                            "_duda_players": doubt,
                        }
                    else:
                        game = {
                            "id": gid,
                            "title": title,
                            "year": None,
                            "cover": "",
                            "players": ["1 jugador"],
                            "genre": "Variado",
                            "description": "Falta la descripcion. Completala a mano cuando puedas.",
                            "_source": "sin-datos",
                            "_duda_players": True,
                        }
                    polite_pause(args.delay)

                # Si el escaneo trajo caratula (vino del scraper de superpsx)
                # y el resultado no tiene, nos quedamos con la del escaneo.
                if not game.get("cover") and item.get("cover"):
                    game["cover"] = item["cover"]
                    game["_cover_from"] = "escaneo"

                cache[key] = game
                print(f"[{game['_source'].split(':')[0]}]")

            if game.get("_duda_players"):
                review.append({
                    "consola": console_slug,
                    "titulo": game["title"],
                    "id": game["id"],
                    "motivo": "no se pudo detectar el modo de juego",
                })

            if not game.get("cover"):
                review.append({
                    "consola": console_slug,
                    "titulo": game["title"],
                    "id": game["id"],
                    "motivo": "sin caratula",
                })

            result.append(game)

        out_file = out_dir / f"{console_slug}.js"
        out_file.write_text(render_js(const, label, result), encoding="utf-8")
        try:
            shown = out_file.relative_to(ROOT)
        except ValueError:
            shown = out_file
        print(f"-> {shown} ({len(result)} juegos)")

    save_cache(cache)

    if review:
        review_file = ROOT / "game_review.json"
        review_file.write_text(
            json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"\n{len(review)} juego(s) para revisar: {review_file.name}")
        print("  - Sin caratula: agrega la URL a mano en src/data/games/")
        print("  - Modo de juego deducido: corrige el campo players si te parece mal")
    else:
        print("\nTodo completo: no hay nada para revisar.")

    print("\nListo. Ahora:  npm run dev")
    return 0


if __name__ == "__main__":
    sys.exit(main())
