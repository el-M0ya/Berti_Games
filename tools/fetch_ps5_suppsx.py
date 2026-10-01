"""
Saca la lista de juegos de PS5 de superpsx.com y la escribe como
`games/ps5.json`, con el mismo formato que producen los otros archivos.

    python tools/fetch_ps5_suppsx.py

Como funciona:
  - Recorre las 37 paginas de https://www.superpsx.com/category/ps5/ps5-games/
  - De cada tarjeta saca el titulo, la caratula y el link al post.
  - Limpia el titulo: en el sitio salen como "High On Life 2 PS5", asi que
    saca el "PS5", el "PKG", el "-PS5" y los codigos al final.
  - Escribe games/ps5.json con {id, title, console, file, cover, source_url}

Nota sobre robots.txt: el sitio permite rastrear el listado y los sitemaps
(solo bloquea la busqueda y wp-json). El script solo usa el listado publico.
Va con pausa entre peticiones para no pegarle al servidor.

Opciones:
  --download-covers   baja las imagenes a public/covers/ps5/ en vez de dejar
                      la URL externa (mas reliable, no depende del hotlink)
  --delay 1.5         pausa entre paginas, en segundos
  --max-pages 50      tope de paginas por seguridad
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
OUT_FILE = ROOT / "games" / "ps5.json"
COVER_DIR = ROOT / "public" / "covers" / "ps5"

BASE_URL = "https://www.superpsx.com"
CATEGORY = f"{BASE_URL}/category/ps5/ps5-games/"

UA = "BertiGamesCatalog/1.0 (catalogo de juegos; uso personal)"

# Una tarjeta del listado. El markup es del tema Soledad de WordPress:
#   <article class="item hentry">
#     <div class="thumbnail"><a data-bgset="CARATULA" href="POST" title="TITULO">
#     <h2 class="penci-entry-title ..."><a href="POST">TITULO</a>
ARTICLE = re.compile(r'<article[^>]*class="[^"]*hentry[^"]*"[^>]*>(.*?)</article>', re.S | re.I)
COVER = re.compile(r'data-bgset="([^"]+)"', re.I)
LINK_TITLE = re.compile(r'<a[^>]*href="([^"]+)"[^>]*title="([^"]*)"', re.S | re.I)
H2_LINK = re.compile(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', re.S | re.I)

# Superpsx solo agrega estas etiquetas al final del titulo. Conviene quitar
# solo eso: si nos pasamos, se pierden partes del nombre real del juego
# (por ejemplo "EA SPORTS FC 26" se convertia en "EA SPORTS").
#
# El prefijo (?:^|\s) es obligatorio: sin el, una alternativa como "on"
# puede comerse el final de una palabra ("Killzone Liberation PS5" se
# quedaba en "Killzone Liberati").
SUFFIX = re.compile(
    r"(?:^|\s)[-–—|]?\s*"
    r"(?:PS\s?[1-5]|PSP|PS\s?Vita|Xbox\s?360|PC|"
    r"PKG|ISO|REPACK|RETAIL|FULL|GOTY)"
    r"\s*$",
    re.I,
)


def http_get(url: str, timeout: int = 30) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return raw.decode("utf-8", errors="replace")


def clean_title(raw: str) -> str:
    """Saca el 'PS5' y las etiquetas de marketing que agrega el sitio."""
    title = html.unescape(raw).strip()
    title = re.sub(r"\s+", " ", title)
    # A veces la etiqueta viene repetida: "... PS5 PS5".
    for _ in range(3):
        before = title
        title = SUFFIX.sub("", title).strip()
        if title == before:
            break
    title = re.sub(r"[\s\-–—_|]+$", "", title)
    # A veces queda una preposicion colgando: "Helldivers for PS5" -> "Helldivers for"
    title = re.sub(
        r"\s+(?:for|on|of|in|and|or|the|a|an|to|with|de|del|la|el|para|con)$",
        "",
        title,
        flags=re.I,
    )
    title = re.sub(r"\s{2,}", " ", title)
    return title.strip()


def slugify(text: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFKD", text.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


def parse_page(page_html: str) -> list[dict]:
    """Saca las tarjetas de una pagina del listado."""
    found: list[dict] = []
    for block in ARTICLE.findall(page_html):
        # La caratula y el link de la miniatura.
        m_thumb = COVER.search(block)
        m_link = LINK_TITLE.search(block)
        # El titulo sale del h2, que es lo mas limpio.
        m_h2 = H2_LINK.search(block)

        if not m_h2:
            continue

        post_url = m_h2.group(1)
        raw_title = m_h2.group(2)
        cover = m_thumb.group(1) if m_thumb else ""

        if m_link and not raw_title.strip():
            raw_title = m_link.group(2)

        title = clean_title(raw_title)
        if len(title) < 2:
            continue

        if post_url.startswith("/"):
            post_url = BASE_URL + post_url

        found.append({
            "id": slugify(title),
            "title": title,
            "console": "ps5",
            "file": "",
            "cover": cover,
            "source_url": post_url,
        })
    return found


def has_next_page(page_html: str) -> bool:
    return f'/{CATEGORY.rstrip("/").split("/")[-2]}/ps5-games/page/' in page_html or "ps5-games/page/" in page_html


def download_covers(games: list[dict]) -> int:
    """Baja las imagenes a public/covers/ps5/ y cambia la URL por la local."""
    COVER_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    for i, g in enumerate(games, 1):
        url = g.get("cover")
        if not url:
            continue
        ext = Path(urllib.parse.urlparse(url).path).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            ext = ".jpg"
        target = COVER_DIR / f"{g['id']}{ext}"
        if target.exists():
            g["cover"] = f"covers/ps5/{target.name}"
            ok += 1
            continue
        try:
            data = http_get(url, timeout=40)
            # Los errores de LiteSpeed devuelven HTML, no imagen.
            if len(data) < 2000 or "<html" in data[:400].lower():
                print(f"    . {g['title'][:38]}: respuesta no es imagen, se deja la URL")
                continue
            target.write_bytes(data.encode("utf-8", errors="surrogateescape"))
            g["cover"] = f"covers/ps5/{target.name}"
            ok += 1
            print(f"[{i}/{len(games)}] {g['title'][:38]}")
        except Exception as e:
            print(f"    . {g['title'][:38]}: {e}")
        time.sleep(0.35)
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Descarga la lista de juegos de PS5 de superpsx.com."
    )
    parser.add_argument(
        "--delay", type=float, default=1.5, help="Pausa entre paginas (default 1.5)"
    )
    parser.add_argument(
        "--max-pages", type=int, default=50, help="Tope de paginas (default 50)"
    )
    parser.add_argument(
        "--download-covers",
        action="store_true",
        help="Baja las caratulas a public/covers/ps5/ en vez de usar URLs externas",
    )
    args = parser.parse_args()

    print(f"Leyendo el listado de PS5 en {CATEGORY}\n")

    games: list[dict] = []
    seen: set[str] = set()
    page = 1

    while page <= args.max_pages:
        url = CATEGORY if page == 1 else f"{CATEGORY}page/{page}/"
        try:
            page_html = http_get(url)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print(f"Pagina {page}: 404, termino el listado.")
                break
            print(f"Pagina {page}: error HTTP {e.code}, se corta aqui.")
            break
        except Exception as e:
            print(f"Pagina {page}: error de red ({e}), se corta aqui.")
            break

        found = parse_page(page_html)
        if not found:
            print(f"Pagina {page}: sin resultados, termino el listado.")
            break

        nuevos = 0
        for g in found:
            if g["id"] in seen:
                continue
            seen.add(g["id"])
            games.append(g)
            nuevos += 1

        print(f"Pagina {page:3d}: {len(found):3d} tarjetas, {nuevos:3d} nuevas "
              f"(total {len(games)})")

        # Si la pagina no trae siguiente, paramos.
        if "ps5-games/page/" not in page_html or nuevos == 0:
            if nuevos == 0:
                print("No aparecen juegos nuevos: fin del listado.")
                break

        page += 1
        time.sleep(args.delay)

    if not games:
        print("\nNo se encontro ningun juego. Revisa si cambio el markup del sitio.")
        return 1

    print(f"\nTotal: {len(games)} juegos de PS5")

    if args.download_covers:
        print("\nDescargando caratulas...\n")
        ok = download_covers(games)
        print(f"\n{ok}/{len(games)} caratulas guardadas en {COVER_DIR}")
    else:
        con_cubierta = sum(1 for g in games if g["cover"])
        print(f"{con_cubierta} juegos con caratula (URL externa)")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps({"ps5": games}, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"\nEscrito: {OUT_FILE.relative_to(ROOT)}")

    print(
        "\nSiguiente paso:  python tools/fetch_metadata.py --key TU_CLAVE "
        "--scan games/ps5.json"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
