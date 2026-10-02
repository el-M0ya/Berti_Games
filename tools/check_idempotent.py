"""Comprueba que normalize_catalog.py ya no cambia los archivos al repetirlo.

Este era un bug real: los backslashes de algunas portadas se duplicaban en
cada build (4095, 8191, 16383...). Con el escape arreglado, dos corridas
seguidas tienen que dar exactamente el mismo archivo.

Uso: python tools/check_idempotent.py
"""
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
GAMES = RAIZ / "src" / "data" / "games"


def firma() -> dict:
    salida = {}
    for f in sorted(GAMES.glob("*.js")):
        if f.name == "index.js":
            continue
        salida[f.name] = f.read_text(encoding="utf-8")
    return salida


def max_barras(texto: str) -> int:
    import re
    return max((m.group(1).count("\\") for m in re.finditer(r"^\s{4}cover: (.+),$", texto, re.M)), default=0)


def main() -> int:
    print("Estado inicial:")
    antes = firma()
    for nombre, texto in antes.items():
        print(f"  {nombre:14s} {len(texto):>9,d} bytes  {max_barras(texto):>5d} barras (max)")

    print("\nCorrida 1...")
    subprocess.run([sys.executable, str(RAIZ / "tools" / "normalize_catalog.py")],
                   cwd=RAIZ, capture_output=True)
    primera = firma()

    print("Corrida 2...")
    subprocess.run([sys.executable, str(RAIZ / "tools" / "normalize_catalog.py")],
                   cwd=RAIZ, capture_output=True)
    segunda = firma()

    print("\nEstado final:")
    for nombre, texto in segunda.items():
        print(f"  {nombre:14s} {len(texto):>9,d} bytes  {max_barras(texto):>5d} barras (max)")

    fallos = 0
    for nombre in segunda:
        if primera[nombre] != segunda[nombre]:
            print(f"\n  FALLA {nombre}: sigue cambiando entre corridas")
            fallos += 1
    for nombre, texto in segunda.items():
        if max_barras(texto) > 3:
            print(f"\n  FALLA {nombre}: quedan portadas con {max_barras(texto)} barras")
            fallos += 1

    print()
    print("OK: es idempotente." if fallos == 0 else f"{fallos} problema(s).")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())