"""
Comprueba los duplicados que genera normalize_catalog.py, mostrando el
titulo ORIGINAL de cada juego (antes de limpiar) para que se vea si de
 verdad son el mismo juego o si el script esta borrando de mas.

Uso: python tools/check_duplicates.py [consola]
"""
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

sys.path.insert(0, str(ROOT / "tools"))
from normalize_catalog import clean_title, slugify  # noqa: E402

TITLE = re.compile(r"^\s{4}title: '(.*)',$", re.M)


def titulos_originales(slug: str) -> list[str]:
    """Los titulos del catalogo tal como estaban antes de normalizar."""
    try:
        raw = subprocess.run(
            ["git", "show", f"HEAD:src/data/games/{slug}.js"],
            capture_output=True, text=True, encoding="utf-8", cwd=ROOT, check=True,
        ).stdout
    except Exception:
        return []
    return [m.group(1).replace("\\'", "'") for m in TITLE.finditer(raw)]


def main() -> int:
    solo = sys.argv[1] if len(sys.argv) > 1 else ""
    archivos = sorted(p for p in GAMES.glob("*.js") if p.name != "index.js")
    if solo:
        archivos = [p for p in archivos if p.stem == solo]

    total_dup = 0
    for path in archivos:
        slug = path.stem
        originales = titulos_originales(slug)
        if not originales:
            continue

        grupos: dict[str, list[str]] = defaultdict(list)
        for t in originales:
            limpio, _ = clean_title(t)
            grupos[slugify(limpio)].append(t)

        repetidos = {k: v for k, v in grupos.items() if len(v) > 1}
        if not repetidos:
            continue

        print(f"\n=== {slug}: {len(repetidos)} titulos que se repiten ===\n")
        for ident, variantes in sorted(repetidos.items(), key=lambda kv: -len(kv[1])):
            total_dup += len(variantes) - 1
            print(f"  {ident}")
            for v in variantes:
                print(f"      {v}")

    print(f"\nTotal de juegos que se descartarian: {total_dup}")
    print("\nRevisa que en cada grupo sean el mismo juego. Si alguno no lo es,")
    print("agrega el titulo a KEEP_TITLES en normalize_catalog.py.")
    return 0


if __name__ == "__main__":
    sys.exit(main())