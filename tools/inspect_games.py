"""Inspeccion rapida de los JSON de la carpeta games/.

No modifica nada: solo resume que hay adentro para entender el formato.
Uso: python tools/inspect_games.py
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

GAMES = Path(__file__).resolve().parent.parent / "games"


def main() -> int:
    for path in sorted(GAMES.glob("*.json")):
        print("=" * 70)
        print(f"{path.name}  ({path.stat().st_size / 1024:.0f} KB)")
        print("=" * 70)

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            print(f"  JSON invalido: {e}\n")
            continue

        if isinstance(data, dict):
            print(f"  Raiz: objeto con {len(data)} claves -> {list(data.keys())[:12]}")
            for key, value in data.items():
                if isinstance(value, list):
                    print(f"    {key:12s} {len(value):5d} juegos")
        elif isinstance(data, list):
            print(f"  Raiz: lista con {len(data)} elementos")
        else:
            print(f"  Raiz: {type(data).__name__}")
            print()

        # Muestra el primer registro completo para ver los campos disponibles.
        first = None
        if isinstance(data, list) and data:
            first = data[0]
        elif isinstance(data, dict):
            for value in data.values():
                if isinstance(value, list) and value:
                    first = value[0]
                    break

        if isinstance(first, dict):
            print(f"  Campos del primer registro: {list(first.keys())}")
            for k, v in first.items():
                shown = str(v)
                if len(shown) > 70:
                    shown = shown[:70] + "..."
                print(f"    {k:14s} = {shown}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
