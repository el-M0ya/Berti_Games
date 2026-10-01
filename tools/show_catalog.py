"""Muestra los primeros juegos de un JSON de catalogo, para revisarlos a ojo.

Uso: python tools/show_catalog.py games/ps5.json 20
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python tools/show_catalog.py <archivo.json> [cuantos]")
        return 1

    path = ROOT / sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 25

    data = json.loads(path.read_text(encoding="utf-8"))

    for console, games in data.items():
        print(f"\n{console}  ({len(games)} juegos)\n")
        for g in games[:limit]:
            cover = g.get("cover") or ""
            cover = cover[-38:] if cover else "(sin caratula)"
            print(f"  {g['title'][:50]:52s} {cover}")
        if len(games) > limit:
            print(f"  ... y {len(games) - limit} mas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
