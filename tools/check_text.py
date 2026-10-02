"""
Revisa los archivos del proyecto y avisa si se colaron caracteres raros.

Este archivo existe para cazar el texto roto: se cuelan tokens de otros
idiomas o caracteres de otro alfabeto en los archivos que escribimos a mano.
Antes de llenar los catalogos, esas mezclas Saltaban a simple vista.

    ROTO:  "Escenario en el tercero persona"   (chino dentro de frase)

Excepcion a proposito: `src/data/games/*.js`. Esos archivos se generan
importando datos de RAWG, y su texto es legitimamente raro: nombres originales
en japones o cirlico, macrones en la romanizacion, simbolos como el corazon
o el signo de la cabecera de un juego. Ahi solo se avisa de lo que no tiene
discusion posible, que son los caracteres invisibles y de control (y que
`tools/normalize_catalog.py` ya limpia).

Uso:  python tools/check_text.py
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent

# ASCII + acentuacion espanola + puntuacion tipografica.
ALLOWED = set(
    "áéíóúüñÁÉÍÓÚÜÑ"
    "àèìòùâêîôûäëïöç"
    "«»¡¿…·—–“”‘’€°©®™→↓↑←•"
)

# Caracteres invisibles o de control. Van como escapes para que este archivo
# no los contenga de verdad.
INVISIBLE = {
    "\u00a0",           # espacio duro
    "\u2002", "\u2003", "\u2009", "\u200a",  # espacios raros
    "\u200b", "\u200c", "\u200d",            # zero width
    "\u200e", "\u200f",                      # marcas de direccion
    "\u2060", "\ufeff",                      # word joiner y BOM
}

# Controles C1: restos de Windows-1252 mal decodificados.
C1_CONTROLS = {chr(c) for c in range(0x80, 0xA0)}


def is_allowed(ch: str) -> bool:
    if ch in ALLOWED:
        return True
    if ord(ch) < 128:
        return True
    # Emoji y pictogramas.
    return 0x1F000 <= ord(ch) <= 0x1FAFF


def revisar(path: Path):
    """Devuelve [(linea, caracter, texto)] con lo dudoso en un archivo."""
    # Los catalogos, sean los de src/data/games o los partidos de
    # src/data/generated, vienen importados de una API externa: su texto es
    # legitimamente raro y solo se avisa de lo invisible o de control.
    partes = path.parts
    es_catalogo = "games" in partes or "generated" in partes
    problemas = []

    for num, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        for ch in line:
            if is_allowed(ch):
                continue
            if es_catalogo and ch not in INVISIBLE and ch not in C1_CONTROLS:
                continue  # dato importado: puede traer alfabetos raros
            problemas.append((num, ch, line))
            break  # una vez por linea alcanza para el informe

    return problemas


def main() -> int:
    targets = (
        sorted(ROOT.glob("src/**/*.js"))
        + sorted(ROOT.glob("src/**/*.jsx"))
        + sorted(ROOT.glob("tools/*.py"))
    )

    total = 0
    for path in targets:
        for num, ch, line in revisar(path):
            rel = path.relative_to(ROOT)
            print(f"{rel}:{num}  caracter sospechoso {ch!r} (U+{ord(ch):04X})")
            print(f"    {line.strip()[:110]}")
            total += 1

    if total:
        print(f"\n{total} problema(s) encontrado(s).")
        return 1
    print("OK: todo el texto es valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())