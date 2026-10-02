"""
Busca en los catalogos los juegos cuya descripcion viene de una pagina de
Wikipedia que no corresponde, y les pone el texto generico.

Es una correccion quirurgica: solo toca los juegos que se le digan por id,
sin volver a escribir los archivos enteros (que se perderian los juegos que
no estan en la cache).

    python tools/fix_bad_descriptions.py --dry-run
    python tools/fix_bad_descriptions.py

Los ids salen de `python tools/audit_descriptions.py`.
"""

import argparse
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / "src" / "data" / "games"

sys.path.insert(0, str(ROOT / "tools"))
from normalize_catalog import generic_description, normalize_genres  # noqa: E402

# Juegos cuya descripcion en Wikipedia es de otro juego. Salen del informe de
# audit_descriptions.py.
BAD_DESCRIPTIONS = {
    "ps2": ["ico"],
    "ps4": ["1971-project-helios", "3-on-3-freestyle"],
    "ps5": ["high-on-life-2"],
    "psp": ["101-in-1"],
}

ID = re.compile(r"^\s{4}id: '(.*)',$", re.M)
GENRES = re.compile(r"^\s{4}genres: \[(.*?)\],$", re.M)
TITLE = re.compile(r"^\s{4}title: '(.*)',$", re.M)
DESC = re.compile(r"^(\s{4})description: '(.*)',$", re.M)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    corregidos = 0
    for consola, ids in BAD_DESCRIPTIONS.items():
        path = GAMES / f"{consola}.js"
        if not path.exists():
            continue
        texto = path.read_text(encoding="utf-8")
        bloques = re.split(r"\n  \{\n", texto)
        salida = [bloques[0]]
        n = 0

        for bloque in bloques[1:]:
            m_id = ID.search(bloque)
            if m_id and m_id.group(1) in ids:
                titulo = TITLE.search(bloque).group(1).replace("\\'", "'")
                generos = re.findall(r"'([^']*)'", GENRES.search(bloque).group(1))
                nueva = generic_description(generos, consola, titulo)
                # Conservamos la indentacion que trae el bloque.
                bloque = DESC.sub(
                    lambda mt: f"{mt.group(1)}description: '{nueva}',",
                    bloque,
                    count=1,
                )
                n += 1
                if not args.dry_run:
                    print(f"  {consola} / {m_id.group(1)}: {titulo}")

            salida.append(bloque)

        corregidos += n
        if not args.dry_run and n:
            path.write_text("\n  {\n".join(salida), encoding="utf-8")

    print(f"\n{corregidos} descripcion(es) reemplazada(s) por texto generico.")
    if args.dry_run:
        print("Dry run: no se escribio nada.")
    return 0


if __name__ == "__main__":
    sys.exit(main())