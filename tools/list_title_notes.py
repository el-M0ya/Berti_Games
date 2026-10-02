"""
Lista todos los parentesis que aparecen en los titulos del catalogo, para
ver que notas de trabajo hay y armar el filtro con datos reales en vez de
adivinar.

Uso: python tools/list_title_notes.py
"""
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

PARENS = re.compile(r"[\(\[]([^)\]]{1,60})[\)\]]")


def main() -> int:
    contenidos = Counter()

    for path in sorted(GAMES.glob("*.js")):
        if path.name == "index.js":
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"^\s{4}title: '(.*)',$", text, re.M):
            titulo = m.group(1).replace("\\'", "'")
            for p in PARENS.findall(titulo):
                contenidos[p.strip()] += 1

    print(f"Parentesis distintos en titulos: {len(contenidos)}\n")
    for texto, n in sorted(contenidos.items(), key=lambda kv: -kv[1]):
        print(f"{n:5d}  ({texto})")
    return 0


if __name__ == "__main__":
    sys.exit(main())