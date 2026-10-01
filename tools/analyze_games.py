"""
Analiza los JSON de games/ para ver cuantos juegos hay, cuantos se repiten
y cuantos titulos parecen basura (colecciones, carpetas, typos).

Solo lee. No modifica nada.
Uso: python tools/analyze_games.py
"""
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GAMES = Path(__file__).resolve().parent.parent / "games"

# Palabras que delatan que la "carpeta" no es un juego concreto.
JUNK_WORDS = re.compile(
    r"\b(coleccion|collection|pack|pack\s*de|recopilacion|"
    r"3\s*en\s*1|2\s*en\s*1|4\s*en\s*1|5\s*en\s*1|"
    r"varios|multiplos|extras|demos|demo\b|"
    r"juegos?\s*de|sega\s*games|sin\s*dvd|sin\s*iso)\b",
    re.I,
)


def key_of(title: str) -> str:
    return re.sub(r"[^a-z0-9]", "", title.lower())


def main() -> int:
    by_console: dict[str, dict[str, dict]] = {}
    sources: dict[str, list[str]] = {}

    for path in sorted(GAMES.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for console, games in data.items():
            by_console.setdefault(console, {})
            sources.setdefault(console, []).append(path.name)
            for g in games:
                # Si el mismo juego aparece en dos archivos, se queda el primero.
                k = g.get("id") or key_of(g.get("title", ""))
                by_console[console].setdefault(
                    k, {**g, "_src": path.name}
                )

    total = 0
    print(f"{'consola':9s} {'total':>6s} {'sospechosos':>11s}  archivos de origen")
    print("-" * 78)
    for console in sorted(by_console):
        games = list(by_console[console].values())
        total += len(games)
        junk = [
            g for g in games
            if JUNK_WORDS.search(g.get("title", "")) or len(g.get("title", "").strip()) < 4
        ]
        pct = len(junk) / len(games) * 100
        print(
            f"{console:9s} {len(games):6d} {len(junk):6d} ({pct:4.1f}%)  "
            f"{', '.join(sources[console])}"
        )
    print("-" * 78)
    print(f"{'TOTAL':9s} {total:6d}")

    # Muestra de titulos sospechosos para que veas el tipo de problema.
    print("\nEjemplos de titulos que no son juegos concretos:\n")
    for console in sorted(by_console):
        games = list(by_console[console].values())
        junk = [g for g in games if JUNK_WORDS.search(g.get("title", ""))]
        if not junk:
            continue
        print(f"  {console}:")
        for g in junk[:6]:
            print(f"    - {g['title']}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
