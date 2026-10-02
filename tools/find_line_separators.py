"""
Cuenta separadores de linea Unicode escondidos en los catalogos.

U+2028 (LINE SEPARATOR) y U+2029 (PARAGRAPH SEPARATOR) son separadores de
linea segun Unicode, pero NO son el caracter de salto de linea normal.
JavaScript (desde ES2019) los acepta dentro de un string, asi que el build no
se cae... pero:

  - rompen cualquier parser que los trate como salto de linea
  - en el navegador se ven como un salto, parten el texto
  - si el archivo pasa por algun proceso que normalice texto, se rompe

Los caracteres se arman con chr() a proposito: son invisibles y al escribir
los como literales se terminan borrando (o peor, quedan como cadena vacia y
count('') devuelve el tamano entero del texto).

Vienen de los datos de RAWG/IGDB, no de la web.

Uso: python tools/find_line_separators.py
"""

import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

# codigo -> (nombre, reemplazo). Reemplazo None = no se toca.
REGLAS = {
    0x2028: ("LINE SEPARATOR", " "),
    0x2029: ("PARAGRAPH SEPARATOR", " "),
    0x0085: ("NEXT LINE", " "),
    0x000B: ("LINE TABULATION", " "),
    0x000C: ("FORM FEED", " "),
    0x200B: ("ZERO WIDTH SPACE", ""),
    0xFEFF: ("ZERO WIDTH NO-JOINER", ""),
    0x00A0: ("NO-BREAK SPACE", " "),
    0x202F: ("NARROW NO-BREAK SPACE", " "),
    0x2007: ("FIGURE SPACE", " "),
}


def main() -> int:
    total = Counter()
    por_archivo = {}

    for path in sorted(GAMES.glob("*.js")):
        if path.name == "index.js":
            continue
        texto = path.read_text(encoding="utf-8")
        cuenta = Counter()
        for codigo in REGLAS:
            n = texto.count(chr(codigo))
            if n:
                cuenta[codigo] = n
                total[codigo] += n
        if cuenta:
            por_archivo[path.name] = cuenta

    if not total:
        print("OK: no hay caracteres escondidos.")
        return 0

    print("Caracteres escondidos:\n")
    for codigo, n in total.most_common():
        nombre, reemplazo = REGLAS[codigo]
        que = "se cambia por espacio" if reemplazo == " " else "se borra"
        print(f"  {n:6d}  {nombre:22s} U+{codigo:04X}  -> {que}")

    print("\nPor archivo:")
    for nombre, cuenta in por_archivo.items():
        partes = ", ".join(
            f"U+{codigo:04X}x{n}" for codigo, n in cuenta.items()
        )
        print(f"  {nombre:12s} {partes}")

    return 1


if __name__ == "__main__":
    sys.exit(main())