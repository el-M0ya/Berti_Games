"""
Parte los catalogos en archivos pequenos para que la web no descargue de una.

    python tools/split_catalog.py

El problema: con 7.800 juegos, el bundle pesa 3,8 MB y el visitante se lo
baja entero antes de ver nada. Y el 53% de eso son las descripciones, que
solo hacen falta cuando alguien abre la ficha de un juego.

Que genera en `src/data/generated/`:

    counts.js          numero de juegos y 3 caratulas por consola (diminuto)
    indices/ps2.js     lo justo para dibujar las tarjetas
    descriptions/ps2.js  las descripciones, que se cargan al abrir una ficha

Los archivos originales de `src/data/games/` no se tocan: siguen siendo la
fuente de la que se edita a mano (por ejemplo, para marcar favoritos).
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"
OUT = ROOT / "src" / "data" / "generated"
INDICES = OUT / "indices"
DESCS = OUT / "descriptions"

CONST = {
    "ps1": "PS1",
    "ps2": "PS2",
    "psp": "PSP",
    "ps3": "PS3",
    "xbox360": "XBOX360",
    "ps4": "PS4",
    "ps5": "PS5",
}

# Cuantas caratulas se muestran en la portada.
PREVIAS = 3


def parse(path: Path) -> list[dict]:
    """Lee un catalogo normalizado."""
    text = path.read_text(encoding="utf-8")
    body = text[text.index("= [") + 2 : text.rindex("]")]
    juegos = []
    for block in re.split(r"\n  \{\n", body)[1:]:
        g = {}
        for key in ("id", "title", "cover"):
            m = re.search(rf"^\s{{4}}{key}: '(.*)',$", block, re.M)
            g[key] = m.group(1).replace("\\'", "'") if m else ""
        m = re.search(r"^\s{4}year:\s*(.*?),?$", block, re.M)
        g["year"] = None if not m or m.group(1) == "null" else int(m.group(1))
        m = re.search(r"^\s{4}players:\s*\[(.*?)\]", block, re.M)
        g["players"] = re.findall(r"'([^']*)'", m.group(1)) if m else []
        m = re.search(r"^\s{4}genres:\s*\[(.*?)\]", block, re.M)
        g["genres"] = re.findall(r"'([^']*)'", m.group(1)) if m else []
        m = re.search(r"^\s{4}favorite:\s*(true|false)", block, re.M)
        g["favorite"] = bool(m and m.group(1) == "true")
        m = re.search(r"^\s{4}description: '(.*)',$", block, re.M)
        g["description"] = m.group(1).replace("\\'", "'") if m else ""
        juegos.append(g)
    return juegos


def js(value) -> str:
    if value is None:
        return "null"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def main() -> int:
    INDICES.mkdir(parents=True, exist_ok=True)
    DESCS.mkdir(parents=True, exist_ok=True)

    counts = {}
    previews = {}
    favoritos = {}

    for path in sorted(GAMES.glob("*.js")):
        slug = path.stem
        if slug not in CONST:
            continue
        # Solo los catalogos de verdad (en la carpeta tambien hay index.js
        # y loader.js, que no se tocan).
        if "_GAMES = [" not in path.read_text(encoding="utf-8"):
            continue

        juegos = parse(path)
        const = CONST[slug]
        counts[slug] = len(juegos)

        # Las tres primeras que salgan en la portada.
        previews[slug] = [
            {"id": g["id"], "title": g["title"], "cover": g["cover"]}
            for g in juegos[:PREVIAS]
        ]

        favoritos[slug] = [g["id"] for g in juegos if g["favorite"]]

        # Indice: lo justo para pintar las tarjetas. Sin descripcion y sin
        # favoritos (esos van aparte).
        lineas = [
            f"/**\n * Indice de {slug.upper()}: lo minimo para las tarjetas.\n"
            f" * Generado por `tools/split_catalog.py`. No editar a mano.\n */\n\n",
            f"export const {const}_INDEX = [\n",
        ]
        for g in juegos:
            players = ", ".join(js(p) for p in g["players"])
            genres = ", ".join(js(x) for x in g["genres"])
            lineas.append(
                f"  {{ id: {js(g['id'])}, title: {js(g['title'])}, "
                f"year: {g['year'] if g['year'] else 'null'}, "
                f"cover: {js(g['cover'])}, players: [{players}], genres: [{genres}] }},\n"
            )
        lineas.append("]\n")
        (INDICES / f"{slug}.js").write_text("".join(lineas), encoding="utf-8")

        # Descripciones: en un objeto id -> texto.
        lineas = [
            f"/**\n * Descripciones de {slug.upper()}.\n"
            f" * Generado por `tools/split_catalog.py`. No editar a mano.\n */\n\n",
            f"export const {const}_DESCRIPCIONES = {{\n",
        ]
        for g in juegos:
            lineas.append(f"  {js(g['id'])}: {js(g['description'])},\n")
        lineas.append("}\n")
        (DESCS / f"{slug}.js").write_text("".join(lineas), encoding="utf-8")

    # Conteos y previas: un solo archivo diminuto para la portada.
    out = [
        "/**\n * Conteos y caratulas de muestra. Para la portada, que no tiene\n"
        " * que cargar los catalogos enteros.\n * Generado por"
        " `tools/split_catalog.py`.\n */\n\n",
        f"export const CONSOLE_COUNTS = {json.dumps(counts, indent=2)}\n\n",
        "export const CONSOLE_PREVIEWS = {\n",
    ]
    for slug, lista in previews.items():
        out.append(f"  {slug}: [\n")
        for p in lista:
            out.append(f"    {{ id: {js(p['id'])}, title: {js(p['title'])}, cover: {js(p['cover'])} }},\n")
        out.append("  ],\n")
    out.append("}\n")
    (OUT / "counts.js").write_text("".join(out), encoding="utf-8")

    # Los favoritos en un archivo aparte, chico y editable a mano.
    out = [
        "/**\n * Juegos destacados.\n *\n"
        " * ARCHIVO GENERADO. No lo edites a mano: cada build lo reescribe\n"
        " * y esta carpeta esta en .gitignore, asi que se perderia.\n"
        " *\n"
        " * Para cambiar los destacados se edita el catalogo de verdad\n"
        " * (src/data/games/ps2.js y demas) o se usa:\n"
        " *     python tools/mark_favorites.py --add <id>\n"
        " *     python tools/mark_favorites.py --remove <id>\n"
        " *     python tools/mark_favorites.py --list\n"
        " *\n"
        " * Los visitantes no pueden tocar esto: es codigo.\n */\n\n",
        "export const FAVORITES = {\n",
    ]
    total = 0
    for slug, lista in favoritos.items():
        total += len(lista)
        out.append(f"  {slug}: [\n")
        for i in lista:
            out.append(f"    {js(i)},\n")
        out.append("  ],\n")
    out.append("}\n")
    (OUT / "favorites.js").write_text("".join(out), encoding="utf-8")

    # Resumen del peso.
    total_idx = sum(p.stat().st_size for p in INDICES.glob("*.js"))
    total_desc = sum(p.stat().st_size for p in DESCS.glob("*.js"))
    chico = (OUT / "counts.js").stat().st_size + (OUT / "favorites.js").stat().st_size

    print("Catalogos partidos:\n")
    print(f"{'consola':9s} {'juegos':>7s} {'indice':>9s} {'descripciones':>15s}")
    print("-" * 46)
    for slug in sorted(counts):
        idx = (INDICES / f"{slug}.js").stat().st_size
        desc = (DESCS / f"{slug}.js").stat().st_size
        print(f"{slug:9s} {counts[slug]:7d} {idx / 1024:8.0f}KB {desc / 1024:14.0f}KB")
    print("-" * 46)
    print(f"{'TOTAL':9s} {sum(counts.values()):7d} {total_idx / 1024:8.0f}KB {total_desc / 1024:14.0f}KB")
    print(f"\ncounts.js + favorites.js: {chico / 1024:.1f} KB (se carga siempre)")
    print(f"{total} juego(s) marcado(s) como destacado.")
    print("\nLa portada carga eso. Cada consola carga su indice al entrar,")
    print("y las descripciones solo al abrir una ficha.")
    return 0


if __name__ == "__main__":
    sys.exit(main())