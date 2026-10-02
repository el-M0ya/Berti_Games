"""
Cuenta entidades HTML que quedaron sin convertir en los catalogos.

Uso: python tools/list_html_entities.py
"""
import glob
import re
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

# Palabras que NO hay que dejar en mayusculas al pasar a Title Case.
COMMON_UPPER = {
    "OF", "THE", "AND", "OR", "A", "AN", "IN", "ON", "AT", "TO", "FOR",
    "DE", "LA", "EL", "LOS", "LAS", "UN", "UNA", "Y", "O", "CON", "PARA",
    "VS", "V", "II", "III", "IV", "VI", "VII", "VIII", "IX", "X",
    "IS", "IT", "AS", "BY", "FROM", "NEW", "ALL", "ONE",
}


def main() -> int:
    entidades = Counter()
    con_entidad = 0
    total = 0
    ejemplos = []

    for path in sorted(glob.glob(str(ROOT / "src" / "data" / "games" / "*.js"))):
        text = Path(path).read_text(encoding="utf-8")
        for m in re.finditer(r"description: '(.*)',$", text, re.M):
            total += 1
            line = m.group(1)
            found = re.findall(r"&[#a-zA-Z0-9]+;", line)
            if found:
                con_entidad += 1
                entidades.update(found)
                if len(ejemplos) < 5:
                    ejemplos.append(line[max(0, line.find("&") - 60):line.find("&") + 40])

    print(f"descripciones revisadas: {total}")
    print(f"con entidades HTML: {con_entidad}\n")
    for e, n in entidades.most_common(15):
        print(f"  {n:6d}  {e}")

    if ejemplos:
        print("\nejemplos:\n")
        for e in ejemplos:
            print(f"  ...{e}...")

    # Titulos en mayusculas donde la palabra es una comun.
    print(f"\nPalabras comunes que quedarian en mayusculas (Title Case): {len(COMMON_UPPER)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())