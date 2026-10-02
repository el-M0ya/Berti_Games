"""
Saca la lista completa de generos tal como vienen de RAWG, para poder
construir el mapa de traduccion sin inventar nombres.

Uso: python tools/list_raw_genres.py
"""
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

GENRE = re.compile(r"^\s{4}genre:\s*'(.*)',?\s*$", re.M)


def main() -> int:
    tokens = Counter()
    for path in sorted(GAMES.glob("*.js")):
        texto = path.read_text(encoding="utf-8")
        if "_GAMES = [" not in texto:
            continue
        for m in GENRE.finditer(texto):
            raw = m.group(1)
            if raw in ("", "null"):
                continue
            for part in raw.split(","):
                part = part.strip()
                if part:
                    tokens[part] += 1

    print(f"Generos distintos en total: {len(tokens)}\n")
    for name, n in tokens.most_common():
        print(f"{n:7d}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())