"""Diagnostico: muestra el titulo crudo de superpsx y el titulo ya limpio,
para ver que se pierde al limpiar. Solo lectura, no escribe nada.

Uso: python tools/debug_ps5_titles.py [paginas]
"""
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_ps5_suppsx import ARTICLE, H2_LINK, CATEGORY, http_get  # noqa: E402


def main() -> int:
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 2

    for page in range(1, pages + 1):
        url = CATEGORY if page == 1 else f"{CATEGORY}page/{page}/"
        page_html = http_get(url)
        for block in ARTICLE.findall(page_html):
            m = H2_LINK.search(block)
            if not m:
                continue
            import html as h
            raw = re.sub(r"\s+", " ", h.unescape(m.group(2))).strip()
            print(f"CRUDO  | {raw}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
