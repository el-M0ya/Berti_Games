"""
Audita la cache de RAWG/Wikipedia y busca juegos cuya descripcion no
corresponde con el titulo.

El riesgo: la busqueda difusa de Wikipedia a veces devuelve la pagina de otro
juego (ya lo paso con "High On Life 2", que recibia la descripcion de un
album de Fall Out Boy). Este script encuentra los que quedaron asi.

Usa el mismo filtro que ahora tiene fetch_metadata.py, asi que lo que
marca aqui es exactamente lo que se rechazaria hoy.

Uso: python tools/audit_descriptions.py [consola]
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "rawg_cache.json"

sys.path.insert(0, str(ROOT / "tools"))
from fetch_metadata import wiki_match_is_trustworthy  # noqa: E402


def wiki_titulo(source: str) -> str | None:
    """
    'wikipedia:https://es.wikipedia.org/wiki/007%3A%20Desde_Rusia_con_amor'
    -> '007: Desde Rusia con amor'

    Hay que decodificar la URL: si no, los %20 y los %28%29 rompen la
    comparacion y salen como falsos positivos.
    """
    if not source.startswith("wikipedia:"):
        return None
    url = source.split("wikipedia:", 1)[1]
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    return unquote(slug).replace("_", " ")


def main() -> int:
    if not CACHE.exists():
        raise SystemExit(
            f"No existe {CACHE.name}. Tiene que haber corrido fetch_metadata.py antes."
        )

    cache = json.loads(CACHE.read_text(encoding="utf-8"))

    por_consola: dict[str, list[tuple]] = {}
    total_wiki = 0

    for clave, juego in cache.items():
        consola, _, _ = clave.partition(":")
        source = juego.get("_source", "")
        pagina = wiki_titulo(source)
        if pagina is None:
            continue
        total_wiki += 1

        titulo = juego.get("title", "")
        if wiki_match_is_trustworthy(titulo, pagina):
            continue

        por_consola.setdefault(consola, []).append((titulo, pagina, clave))

    print(f"Entradas en la cache: {len(cache)}")
    print(f"Descripciones que vienen de Wikipedia: {total_wiki}\n")

    if not por_consola:
        print("Ninguna descripcion de Wikipedia queda mal emparejada.")
        return 0

    total_malos = sum(len(v) for v in por_consola.values())
    print(f"DESCRIPCIONES QUE NO CORRESPONDEN: {total_malos}\n")

    for consola in sorted(por_consola):
        casos = por_consola[consola]
        print(f"--- {consola}: {len(casos)} ---")
        for titulo, pagina, clave in sorted(casos)[:40]:
            print(f"  {titulo[:40]:42s} -> Wikipedia: {pagina[:46]}")
        if len(casos) > 40:
            print(f"  ... y {len(casos) - 40} mas")
        print()

    print("Para arreglarlas:")
    print("  1. Borrar esas claves de rawg_cache.json")
    print("  2. Volver a correr fetch_metadata.py (con el filtro ya arreglado)")
    print("     Las que no se Finds, quedan con el texto generico.")
    return 1


if __name__ == "__main__":
    sys.exit(main())