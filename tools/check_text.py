"""Revisa los archivos de datos y avisa si se colaron caracteres raros.

Uso:  python tools/check_text.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# La consola de Windows suele ser cp1252: forzamos UTF-8 para poder reportar.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Caracteres permitidos: ASCII + acentuacion espanola + tipografia + emoji.
ALLOWED = set(
    "áéíóúüñÁÉÍÓÚÜÑ"
    "àèìòùâêîôûäëïöç"
    "«»¡¿…·—–“”‘’€°©®™→↓↑←"
)


def is_allowed(ch: str) -> bool:
    if ch in ALLOWED:
        return True
    if ord(ch) < 128:
        return True
    # Emoji y pictogramas (planos fuera de BMP).
    return ord(ch) >= 0x1F000 and ord(ch) <= 0x1FAFF


def main() -> int:
    targets = (
        sorted(ROOT.glob("src/**/*.js"))
        + sorted(ROOT.glob("src/**/*.jsx"))
        + sorted(ROOT.glob("tools/*.py"))
    )
    bad = 0
    for path in targets:
        for num, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for ch in line:
                if not is_allowed(ch):
                    rel = path.relative_to(ROOT)
                    print(f"{rel}:{num}  caracter invalido {ch!r} (U+{ord(ch):04X})")
                    print(f"    {line.strip()[:120]}")
                    bad += 1
    if bad:
        print(f"\n{bad} problema(s) encontrado(s).")
        return 1
    print("OK: todo el texto es valido.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
