"""
Resumen del estado actual del catalogo: cuantos juegos hay, que valores
toman los jugadores y los generos, y cuantos favoritos hay puesto.

Uso: python tools/audit_catalog.py
"""
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"


def parse(path: Path) -> list[dict]:
    """Lee el catalogo sin ejecutarlo."""
    text = path.read_text(encoding="utf-8")
    body = text[text.index("= [") + 2 : text.rindex("]")]
    juegos = []

    for block in re.split(r"\n  \{\n", body)[1:]:
        g: dict = {}

        m = re.search(r"^\s{4}title: '(.*)',$", block, re.M)
        if m:
            g["title"] = m.group(1).replace("\\'", "'")

        m = re.search(r"^\s{4}players:\s*\[(.*?)\]", block, re.M)
        if m:
            g["players"] = re.findall(r"'([^']*)'", m.group(1))

        m = re.search(r"^\s{4}genres:\s*\[(.*?)\]", block, re.M)
        if m:
            g["genres"] = re.findall(r"'([^']*)'", m.group(1))

        m = re.search(r"^\s{4}favorite:\s*(true|false)", block, re.M)
        g["favorite"] = bool(m and m.group(1) == "true")

        # La descripcion va hasta la ultima comilla de la linea: puede
        # contener apostrofos escapados por dentro.
        m = re.search(r"^\s{4}description: '(.*)',$", block, re.M)
        g["desc_len"] = len(m.group(1)) if m else 0

        g["has_cover"] = not re.search(r"^\s{4}cover: '',$", block, re.M)
        g["generica"] = "No tenemos una sinopsis escrita" in (m.group(1) if m else "")
        juegos.append(g)

    return juegos


def main() -> int:
    total = 0
    jugadores = Counter()
    generos = Counter()
    favoritos = 0
    sin_cover = 0
    sin_desc = 0
    genericas = 0

    print(f"{'archivo':10s} {'juegos':>7s} {'con foto':>9s} {'sin desc':>9s} "
          f"{'texto gral.':>12s} {'favoritos':>10s}")
    print("-" * 66)

    for path in sorted(GAMES.glob("*.js")):
        if path.name == "index.js":
            continue
        juegos = parse(path)
        if not juegos:
            continue

        total += len(juegos)
        fotos = sum(1 for g in juegos if g["has_cover"])
        sin_cover += len(juegos) - fotos
        sin_desc += sum(1 for g in juegos if g["desc_len"] <= 40)
        genericas += sum(1 for g in juegos if g["generica"])
        favs = sum(1 for g in juegos if g["favorite"])
        favoritos += favs

        for g in juegos:
            jugadores.update(g["players"])
            generos.update(g["genres"])

        print(f"{path.stem:10s} {len(juegos):7d} {fotos:9d} "
              f"{sum(1 for g in juegos if g['desc_len'] <= 40):9d} "
              f"{sum(1 for g in juegos if g['generica']):12d} {favs:10d}")

    print("-" * 66)
    print(f"{'TOTAL':10s} {total:7d} {total - sin_cover:9d} {sin_desc:9d} "
          f"{genericas:12d} {favoritos:10d}")

    print(f"\nCategorias de jugadores ({len(jugadores)}):\n")
    for v, n in jugadores.most_common():
        print(f"  {n:6d}  {v}")

    print(f"\nGeneros ({len(generos)} distintos):\n")
    for v, n in generos.most_common():
        print(f"  {n:6d}  {v}")

    return 0


if __name__ == "__main__":
    sys.exit(main())