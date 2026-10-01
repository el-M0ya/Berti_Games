"""
Cuenta cuantos titulos crudos hay en el listado de superpsx y cuantos
despues de limpiarlos. Sirve para detectar si la limpieza esta juntando
juegos que en realidad son distintos.

Uso: python tools/count_ps5_titles.py
"""
import html
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ps5_suppsx import (  # noqa: E402
    ARTICLE, CATEGORY, H2_LINK, clean_title, http_get, slugify,
)


def main() -> int:
    crudos: list[str] = []
    for page in range(1, 40):
        url = CATEGORY if page == 1 else f"{CATEGORY}page/{page}/"
        try:
            page_html = http_get(url)
        except Exception:
            break
        found = 0
        for block in ARTICLE.findall(page_html):
            m = H2_LINK.search(block)
            if not m:
                continue
            crudos.append(re.sub(r"\s+", " ", html.unescape(m.group(2))).strip())
            found += 1
        if found == 0:
            break

    limpios = [clean_title(t) for t in crudos]
    by_clean = Counter(limpios)
    colapsados = {k: v for k, v in by_clean.items() if v > 1}

    print(f"Titulos en el listado: {len(crudos)}")
    print(f"Titulos despues de limpiar: {len(by_clean)}")
    print(f"Juegos que se juntaron: {len(crudos) - len(by_clean)}\n")

    if colapsados:
        print("Grupos que se juntaron (revisar si son el mismo juego):\n")
        original = {}
        for crudo, limpio in zip(crudos, limpios):
            original.setdefault(limpio, set()).add(crudo)
        for limpio, veces in sorted(colapsados.items(), key=lambda kv: -kv[1])[:25]:
            variantes = "  |  ".join(sorted(original[limpio]))
            print(f"  {veces}x  {limpio}")
            print(f"        <- {variantes[:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
